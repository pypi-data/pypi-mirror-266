# flake8: noqa: DJ12

import os
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Iterable, List, Optional, Union

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView, RedirectURLMixin
from django.db import models
from django.db.models import JSONField
from django.db.models.fields import CharField, TextField
from django.forms.forms import BaseForm
from django.forms.models import ModelForm, ModelFormMetaclass, fields_for_model
from django.http import HttpRequest, HttpResponse
from django.utils.functional import classproperty, lazy
from django.utils.translation import gettext as _
from django.views.generic import CreateView, UpdateView
from django.views.generic.edit import DeleteView, ModelFormMixin

import reversion
from django_ical.feedgenerator import ITEM_ELEMENT_FIELD_MAP
from dynamic_preferences.settings import preferences_settings
from dynamic_preferences.types import FilePreference
from guardian.admin import GuardedModelAdmin
from guardian.core import ObjectPermissionChecker
from icalendar import Calendar
from material.base import Fieldset, Layout, LayoutNode
from polymorphic.base import PolymorphicModelBase
from polymorphic.models import PolymorphicModel
from rules.contrib.admin import ObjectPermissionsModelAdmin

from aleksis.core.managers import (
    AlekSISBaseManager,
    AlekSISBaseManagerWithoutMigrations,
    PolymorphicBaseManager,
    SchoolTermRelatedQuerySet,
)

from .util.core_helpers import ExtendedICal20Feed

if TYPE_CHECKING:
    from .models import Person


class _ExtensibleModelBase(models.base.ModelBase):
    """Ensure predefined behaviour on model creation.

    This metaclass serves the following purposes:

     - Register all AlekSIS models with django-reverseion
    """

    def __new__(mcls, name, bases, attrs):
        mcls = super().__new__(mcls, name, bases, attrs)

        if "Meta" not in attrs or not attrs["Meta"].abstract:
            # Register all non-abstract models with django-reversion
            mcls = reversion.register(mcls)

            mcls.extra_permissions = []

        return mcls


def _generate_one_to_one_proxy_property(field, subfield):
    def getter(self):
        if hasattr(self, field.name):
            related = getattr(self, field.name)
            return getattr(related, subfield.name)
        # Related instane does not exist
        return None

    def setter(self, val):
        if hasattr(self, field.name):
            related = getattr(self, field.name)
        else:
            # Auto-create related instance (but do not save)
            related = field.related_model()
            setattr(related, field.remote_field.name, self)
            # Ensure the related model is saved later
            self._save_reverse = getattr(self, "_save_reverse", []) + [related]
        setattr(related, subfield.name, val)

    return property(getter, setter)


class ExtensibleModel(models.Model, metaclass=_ExtensibleModelBase):
    """Base model for all objects in AlekSIS apps.

    This base model ensures all objects in AlekSIS apps fulfill the
    following properties:

     * `versions` property to retrieve all versions of the model from reversion
     * Allow injection of fields and code from AlekSIS apps to extend
       model functionality.

    Injection of fields and code
    ============================

    After all apps have been loaded, the code in the `model_extensions` module
    in every app is executed. All code that shall be injected into a model goes there.

    :Example:

    .. code-block:: python

       from datetime import date, timedelta

       from aleksis.core.models import Person

       @Person.property
       def is_cool(self) -> bool:
           return True

       @Person.property
       def age(self) -> timedelta:
           return self.date_of_birth - date.today()

    For a more advanced example, using features from the ORM, see AlekSIS-App-Chronos
    and AlekSIS-App-Alsijil.

    :Date: 2019-11-07
    :Authors:
        - Dominik George <dominik.george@teckids.org>
    """

    # Defines a material design icon associated with this type of model
    icon_ = "radiobox-blank"

    managed_by_app_label = models.CharField(
        max_length=255,
        verbose_name="App label of app responsible for managing this instance",
        editable=False,
        blank=True,
    )

    extended_data = JSONField(default=dict, editable=False)

    extra_permissions = []

    objects = AlekSISBaseManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Ensure all functionality of our extensions that needs saving gets it."""
        # For auto-created remote syncable fields
        if hasattr(self, "_save_reverse"):
            for related in self._save_reverse:
                related.save()
            del self._save_reverse

        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Get the URL o a view representing this model instance."""
        pass

    @property
    def versions(self) -> list[tuple[str, tuple[Any, Any]]]:
        """Get all versions of this object from django-reversion.

        Includes diffs to previous version.
        """
        versions = reversion.models.Version.objects.get_for_object(self)

        versions_with_changes = []
        for i, version in enumerate(versions):
            diff = {}
            if i > 0:
                prev_version = versions[i - 1]

                for k, val in version.field_dict.items():
                    prev_val = prev_version.field_dict.get(k, None)
                    if prev_val != val:
                        diff[k] = (prev_val, val)

            versions_with_changes.append((version, diff))

        return versions_with_changes

    @classmethod
    def _safe_add(cls, obj: Any, name: Optional[str]) -> None:
        # Decide the name for the attribute
        if name is None:
            prop_name = obj.__name__
        else:
            if name.isidentifier():
                prop_name = name
            else:
                raise ValueError(f"{name} is not a valid name.")

        # Verify that attribute name does not clash with other names in the class
        if hasattr(cls, prop_name):
            raise ValueError(f"{prop_name} already used.")

        # Let Django's model magic add the attribute if we got here
        cls.add_to_class(name, obj)

    @classmethod
    def property_(cls, func: Callable[[], Any], name: Optional[str] = None) -> None:
        """Add the passed callable as a property."""
        cls._safe_add(property(func), name or func.__name__)

    @classmethod
    def method(cls, func: Callable[[], Any], name: Optional[str] = None) -> None:
        """Add the passed callable as a method."""
        cls._safe_add(func, name or func.__name__)

    @classmethod
    def class_method(cls, func: Callable[[], Any], name: Optional[str] = None) -> None:
        """Add the passed callable as a classmethod."""
        cls._safe_add(classmethod(func), name or func.__name__)

    @classmethod
    def get_filter_fields(cls) -> List[str]:
        """Get names of all text-searchable fields of this model."""
        fields = []
        for field in cls.syncable_fields():
            if isinstance(field, (CharField, TextField)):
                fields.append(field.name)
        return fields

    @classmethod
    def syncable_fields(
        cls, recursive: bool = True, exclude_remotes: list = None
    ) -> list[models.Field]:
        """Collect all fields that can be synced on a model.

        If recursive is True, it recurses into related models and generates virtual
        proxy fields to access fields in related models."""
        if not exclude_remotes:
            exclude_remotes = []

        fields = []
        for field in cls._meta.get_fields():
            if field.is_relation and field.one_to_one and recursive:
                if ExtensibleModel not in field.related_model.__mro__:
                    # Related model is not extensible and thus has no syncable fields
                    continue
                if field.related_model in exclude_remotes:
                    # Remote is excluded, probably to avoid recursion
                    continue

                # Recurse into related model to get its fields as well
                for subfield in field.related_model.syncable_fields(
                    recursive, exclude_remotes + [cls]
                ):
                    # generate virtual field names for proxy access
                    name = f"_{field.name}__{subfield.name}"
                    verbose_name = (
                        f"{field.name} ({field.related_model._meta.verbose_name})"
                        " → {subfield.verbose_name}"
                    )

                    if not hasattr(cls, name):
                        # Add proxy properties to handle access to related model
                        setattr(cls, name, _generate_one_to_one_proxy_property(field, subfield))

                    # Generate a fake field class with enough API to detect attribute names
                    fields.append(
                        type(
                            "FakeRelatedProxyField",
                            (),
                            {
                                "name": name,
                                "verbose_name": verbose_name,
                                "to_python": lambda v: subfield.to_python(v),  # noqa: B023
                            },
                        )
                    )
            elif field.editable and not field.auto_created:
                fields.append(field)

        return fields

    @classmethod
    def syncable_fields_choices(cls) -> tuple[tuple[str, str]]:
        """Collect all fields that can be synced on a model."""
        return tuple(
            [(field.name, field.verbose_name or field.name) for field in cls.syncable_fields()]
        )

    @classmethod
    def syncable_fields_choices_lazy(cls) -> Callable[[], tuple[tuple[str, str]]]:
        """Collect all fields that can be synced on a model."""
        return lazy(cls.syncable_fields_choices, tuple)

    @classmethod
    def add_permission(cls, name: str, verbose_name: str):
        """Dynamically add a new permission to a model."""
        cls.extra_permissions.append((name, verbose_name))

    def set_object_permission_checker(self, checker: ObjectPermissionChecker):
        """Annotate a ``ObjectPermissionChecker`` for use with permission system."""
        self._permission_checker = checker


class _ExtensiblePolymorphicModelBase(_ExtensibleModelBase, PolymorphicModelBase):
    """Base class for extensible, polymorphic models."""


class ExtensiblePolymorphicModel(
    ExtensibleModel, PolymorphicModel, metaclass=_ExtensiblePolymorphicModelBase
):
    """Model class for extensible, polymorphic models."""

    objects = PolymorphicBaseManager()

    class Meta:
        abstract = True
        base_manager_name = "objects"


class PureDjangoModel:
    """No-op mixin to mark a model as deliberately not using ExtensibleModel."""

    pass


class GlobalPermissionModel(models.Model):
    """Base model for global permissions.

    This base model ensures that global permissions are not managed."""

    class Meta:
        default_permissions = ()
        abstract = True
        managed = False


class _ExtensibleFormMetaclass(ModelFormMetaclass):
    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)

        # Enforce a default for the base layout for forms that o not specify one
        base_layout = x.layout.elements if hasattr(x, "layout") else []

        x.base_layout = base_layout
        x.layout = Layout(*base_layout)

        return x


class ExtensibleForm(ModelForm, metaclass=_ExtensibleFormMetaclass):
    """Base model for extensible forms.

    This mixin adds functionality which allows
    - apps to add layout nodes to the layout used by django-material

    :Add layout nodes:

    .. code-block:: python

        from material import Fieldset

        from aleksis.core.forms import ExampleForm

        node = Fieldset("field_name")
        ExampleForm.add_node_to_layout(node)

    """

    @classmethod
    def add_node_to_layout(cls, node: Union[LayoutNode, str]):
        """Add a node to `layout` attribute.

        :param node: django-material layout node (Fieldset, Row etc.)
        :type node: LayoutNode
        """
        cls.base_layout.append(node)
        cls.layout = Layout(*cls.base_layout)

        visit_nodes = [node]
        while visit_nodes:
            current_node = visit_nodes.pop()
            if isinstance(current_node, Fieldset):
                visit_nodes += node.elements
            else:
                field_name = (
                    current_node if isinstance(current_node, str) else current_node.field_name
                )
                field = fields_for_model(cls._meta.model, [field_name])[field_name]
                cls._meta.fields.append(field_name)
                cls.base_fields[field_name] = field
                setattr(cls, field_name, field)


class BaseModelAdmin(GuardedModelAdmin, ObjectPermissionsModelAdmin):
    """A base class for ModelAdmin combining django-guardian and rules."""

    pass


class SuccessMessageMixin(ModelFormMixin):
    success_message: Optional[str] = None

    def form_valid(self, form: BaseForm) -> HttpResponse:
        if self.success_message:
            messages.success(self.request, self.success_message)
        return super().form_valid(form)


class SuccessNextMixin(RedirectURLMixin):
    redirect_field_name = "next"

    def get_success_url(self) -> str:
        return LoginView.get_redirect_url(self) or super().get_success_url()


class AdvancedCreateView(SuccessMessageMixin, CreateView):
    pass


class AdvancedEditView(SuccessMessageMixin, UpdateView):
    pass


class AdvancedDeleteView(DeleteView):
    """Common confirm view for deleting.

    .. warning ::

        Using this view, objects are deleted permanently after confirming.
        We recommend to include the mixin :class:`reversion.views.RevisionMixin`
        from `django-reversion` to enable soft-delete.
    """

    success_message: Optional[str] = None

    def form_valid(self, form):
        r = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return r


class SchoolTermRelatedExtensibleModel(ExtensibleModel):
    """Add relation to school term."""

    school_term = models.ForeignKey(
        "core.SchoolTerm",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Linked school term"),
        blank=True,
        null=True,
    )

    objects = AlekSISBaseManagerWithoutMigrations.from_queryset(SchoolTermRelatedQuerySet)()

    class Meta:
        abstract = True


class SchoolTermRelatedExtensibleForm(ExtensibleForm):
    """Extensible form for school term related data.

    .. warning::
        This doesn't automatically include the field `school_term` in `fields` or `layout`,
        it just sets an initial value.
    """

    def __init__(self, *args, **kwargs):
        from aleksis.core.models import SchoolTerm  # noqa

        if "instance" not in kwargs:
            kwargs["initial"] = {"school_term": SchoolTerm.current}

        super().__init__(*args, **kwargs)


class PublicFilePreferenceMixin(FilePreference):
    """Uploads a file to the public namespace."""

    upload_path = "public"

    def get_upload_path(self):
        return os.path.join(
            self.upload_path, preferences_settings.FILE_PREFERENCE_UPLOAD_DIR, self.identifier()
        )


class RegistryObject:
    """Generic registry to allow registration of subclasses over all apps."""

    _registry: ClassVar[Optional[dict[str, type["RegistryObject"]]]] = None
    name: ClassVar[str] = ""

    def __init_subclass__(cls):
        if getattr(cls, "_registry", None) is None:
            cls._registry = {}
        else:
            if not cls.name:
                cls.name = cls.__name__
            cls._register()

    @classmethod
    def _register(cls: type["RegistryObject"]):
        if cls.name and cls.name not in cls._registry:
            cls._registry[cls.name] = cls

    @classproperty
    def registered_objects_dict(cls) -> dict[str, type["RegistryObject"]]:
        """Get dict of registered objects."""
        return cls._registry

    @classproperty
    def registered_objects_list(cls) -> list[type["RegistryObject"]]:
        """Get list of registered objects."""
        return list(cls._registry.values())

    @classmethod
    def get_object_by_name(cls, name: str) -> Optional[type["RegistryObject"]]:
        """Get registered object by name."""
        return cls.registered_objects_dict.get(name)


class ObjectAuthenticator(RegistryObject):
    def authenticate(self, request, obj):
        raise NotImplementedError()


class CalendarEventMixin(RegistryObject):
    """Mixin for calendar feeds.

    This mixin can be used to create calendar feeds for objects. It can be used
    by adding it to a model or another object. The basic attributes of the calendar
    can be set by either setting the attributes of the class or by implementing
    the corresponding class methods. Please notice that the class methods are
    overriding the attributes. The following attributes are mandatory:

    - name: Unique name for the calendar feed
    - verbose_name: Shown name of the feed

    The respective class methods have a `get_` prefix and are called without any arguments.
    There are also some more attributes. Please refer to the class signature for more
    information.

    The list of objects used to create the calendar feed have to be provided by
    the method `get_objects` class method. It's mandatory to implement this method.

    To provide the data for the events, a certain set of class methods can be implemented.
    The following iCal attributes are supported:

    guid, title, description, link, class, created, updateddate, start_datetime, end_datetime,
    location, geolocation, transparency, organizer, attendee, rrule, rdate, exdate, valarm, status

    Additionally, the color attribute is supported. The color has to be an RGB
    color in the format #ffffff.

    To deploy extra meta data for AlekSIS' own calendar frontend, you can add a
    dictionary for the meta attribute.

    To implement a method for a certain attribute, the name of the method has to be
    `value_<your_attribute>`. For example, to implement the `title` attribute, the
    method `value_title` has to be implemented. The method has to return the value
    for the attribute. The method is called with the reference object as argument.
    """

    name: str = ""  # Unique name for the calendar feed
    verbose_name: str = ""  # Shown name of the feed
    link: str = ""  # Link for the feed, optional
    description: str = ""  # Description of the feed, optional
    color: str = "#222222"  # Color of the feed, optional
    permission_required: str = ""

    @classmethod
    def get_verbose_name(cls, request: Optional[HttpRequest] = None) -> str:
        """Return the verbose name of the calendar feed."""
        return cls.verbose_name

    @classmethod
    def get_link(cls, request: Optional[HttpRequest] = None) -> str:
        """Return the link of the calendar feed."""
        return cls.link

    @classmethod
    def get_description(cls, request: Optional[HttpRequest] = None) -> str:
        """Return the description of the calendar feed."""
        return cls.description

    @classmethod
    def get_language(cls, request: Optional[HttpRequest] = None) -> str:
        """Return the language of the calendar feed."""
        if request:
            return request.LANGUAGE_CODE
        return settings.LANGUAGE_CODE

    @classmethod
    def get_color(cls, request: Optional[HttpRequest] = None) -> str:
        """Return the color of the calendar feed.

        The color has to be an RGB color in the format #ffffff.
        """
        return cls.color

    @classmethod
    def get_enabled(cls, request: HttpRequest | None = None) -> bool:
        """Return whether the calendar is visible in the frontend."""
        if cls.permission_required and request:
            return request.user.has_perm(cls.permission_required)
        return True

    @classmethod
    def create_event(
        cls,
        reference_object: Any,
        feed: ExtendedICal20Feed,
        request: Optional[HttpRequest] = None,
        params: Optional[dict[str, any]] = None,
    ) -> dict[str, Any]:
        """Create an event for the given reference object and add it to the feed."""
        values = {}
        for field in cls.get_event_field_names():
            field_value = cls.get_event_field_value(
                reference_object, field, request=request, params=params
            )
            if field_value is not None:
                values[field] = field_value
        feed.add_item(**values)
        return values

    @classmethod
    def start_feed(
        cls, request: Optional[HttpRequest] = None, params: Optional[dict[str, any]] = None
    ) -> ExtendedICal20Feed:
        """Start the feed and return it."""
        feed = ExtendedICal20Feed(
            title=cls.get_verbose_name(request=request),
            link=cls.get_link(request=request),
            description=cls.get_description(request=request),
            language=cls.get_language(request=request),
            color=cls.get_color(request=request),
        )
        return feed

    @classmethod
    def get_objects(
        cls, request: Optional[HttpRequest] = None, params: Optional[dict[str, any]] = None
    ) -> Iterable:
        """Return the objects to create the calendar feed for."""
        raise NotImplementedError

    @classmethod
    def create_feed(
        cls, request: Optional[HttpRequest] = None, params: Optional[dict[str, any]] = None
    ) -> ExtendedICal20Feed:
        """Create the calendar feed with all events."""
        feed = cls.start_feed(request=request, params=params)

        for reference_object in cls.get_objects(request=request, params=params):
            cls.create_event(reference_object, feed, request=request, params=params)

        return feed

    @classmethod
    def get_calendar_object(
        cls, request: Optional[HttpRequest] = None, params: Optional[dict[str, any]] = None
    ) -> Calendar:
        """Return the calendar object."""
        feed = cls.create_feed(request=request, params=params)
        return feed.get_calendar_object()

    @classmethod
    def get_single_events(
        cls,
        start: datetime | None = None,
        end: datetime | None = None,
        request: HttpRequest | None = None,
        params: dict[str, any] | None = None,
        with_reference_object: bool = False,
    ):
        """Get single events for this calendar feed."""
        feed = cls.create_feed(request=request, params=params)
        return feed.get_single_events(start, end, with_reference_object=with_reference_object)

    @classmethod
    def get_event_field_names(cls) -> list[str]:
        """Return the names of the fields to be used for the feed."""
        return [field_map[0] for field_map in ITEM_ELEMENT_FIELD_MAP]

    @classmethod
    def get_event_field_value(
        cls,
        reference_object,
        field_name: str,
        request: HttpRequest | None = None,
        params: dict[str, Any] | None = None,
    ) -> any:
        """Return the value for the given field name."""
        method_name = f"value_{field_name}"
        if hasattr(cls, method_name) and callable(getattr(cls, method_name)):
            return getattr(cls, method_name)(reference_object, request=request)
        return None

    @classmethod
    def value_link(cls, reference_object, request: HttpRequest | None = None) -> str:
        return ""

    @classmethod
    def value_color(cls, reference_object, request: HttpRequest | None = None) -> str:
        return cls.get_color(request=request)

    @classproperty
    def valid_feed(cls) -> bool:
        """Return if the feed is valid."""
        return cls.name != cls.__name__

    @classproperty
    def valid_feeds(cls):
        """Return a list of valid feeds."""
        return [feed for feed in cls.registered_objects_list if feed.valid_feed]

    @classproperty
    def valid_feed_names(cls) -> list[str]:
        """Return a list of valid feed names."""
        return [feed.name for feed in cls.valid_feeds]

    @classmethod
    def get_object_by_name(cls, name):
        return cls.registered_objects_dict.get(name)

    @classmethod
    def get_activated(cls, person: "Person") -> bool:
        return cls.name in person.preferences["calendar__activated_calendars"]

    @classmethod
    def get_enabled_feeds(cls, request: HttpRequest | None = None):
        return [feed for feed in cls.valid_feeds if feed.get_enabled(request)]
