# flake8: noqa: DJ01
import base64
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any, Iterable, Iterator, List, Optional, Sequence, Union
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Q, QuerySet
from django.dispatch import receiver
from django.forms.widgets import Media
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.functional import classproperty
from django.utils.translation import gettext_lazy as _

import customidenticon
from cachalot.api import cachalot_disabled
from cache_memoize import cache_memoize
from calendarweek import CalendarWeek
from celery.result import AsyncResult
from celery_progress.backend import Progress
from ckeditor.fields import RichTextField
from django_celery_results.models import TaskResult
from django_ical.utils import build_rrule_from_recurrences_rrule, build_rrule_from_text
from dynamic_preferences.models import PerInstancePreferenceModel
from guardian.shortcuts import get_objects_for_user
from icalendar import vCalAddress, vText
from icalendar.prop import vRecur
from invitations import signals
from invitations.base_invitation import AbstractBaseInvitation
from invitations.models import Invitation
from model_utils import FieldTracker
from model_utils.models import TimeStampedModel
from oauth2_provider.models import (
    AbstractAccessToken,
    AbstractApplication,
    AbstractGrant,
    AbstractIDToken,
    AbstractRefreshToken,
)
from phonenumber_field.modelfields import PhoneNumberField
from polymorphic.models import PolymorphicModel
from recurrence.fields import RecurrenceField
from timezone_field import TimeZoneField

from aleksis.core.data_checks import (
    DataCheck,
)

from .managers import (
    AlekSISBaseManagerWithoutMigrations,
    GroupManager,
    GroupQuerySet,
    HolidayQuerySet,
    InstalledWidgetsDashboardWidgetOrderManager,
    PolymorphicBaseManager,
    SchoolTermQuerySet,
    UninstallRenitentPolymorphicManager,
)
from .mixins import (
    CalendarEventMixin,
    ExtensibleModel,
    ExtensiblePolymorphicModel,
    GlobalPermissionModel,
    PureDjangoModel,
    RegistryObject,
    SchoolTermRelatedExtensibleModel,
)
from .tasks import send_notification
from .util.core_helpers import generate_random_code, get_site_preferences, now_tomorrow
from .util.email import send_email
from .util.model_helpers import ICONS

if TYPE_CHECKING:
    from django.contrib.auth.models import User

FIELD_CHOICES = (
    ("BooleanField", _("Boolean (Yes/No)")),
    ("CharField", _("Text (one line)")),
    ("DateField", _("Date")),
    ("DateTimeField", _("Date and time")),
    ("DecimalField", _("Decimal number")),
    ("EmailField", _("E-mail address")),
    ("IntegerField", _("Integer")),
    ("GenericIPAddressField", _("IP address")),
    ("NullBooleanField", _("Boolean or empty (Yes/No/Neither)")),
    ("TextField", _("Text (multi-line)")),
    ("TimeField", _("Time")),
    ("URLField", _("URL / Link")),
)


class SchoolTerm(ExtensibleModel):
    """School term model.

    This is used to manage start and end times of a school term and link data to it.
    """

    objects = AlekSISBaseManagerWithoutMigrations.from_queryset(SchoolTermQuerySet)()

    name = models.CharField(verbose_name=_("Name"), max_length=255)

    date_start = models.DateField(verbose_name=_("Start date"))
    date_end = models.DateField(verbose_name=_("End date"))

    @classmethod
    @cache_memoize(3600)
    def get_current(cls, day: Optional[date] = None):
        if not day:
            day = timezone.now().date()
        try:
            return cls.objects.on_day(day).first()
        except SchoolTerm.DoesNotExist:
            return None

    @classproperty
    def current(cls):
        return cls.get_current()

    def clean(self):
        """Ensure there is only one school term at each point of time."""
        if self.date_end < self.date_start:
            raise ValidationError(_("The start date must be earlier than the end date."))

        qs = SchoolTerm.objects.within_dates(self.date_start, self.date_end)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(
                _("There is already a school term for this time or a part of this time.")
            )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("School term")
        verbose_name_plural = _("School terms")
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_school_term_name"),
            models.UniqueConstraint(
                fields=["date_start", "date_end"],
                name="unique_school_term_dates",
            ),
        ]


class Person(ExtensibleModel):
    """Person model.

    A model describing any person related to a school, including, but not
    limited to, students, teachers and guardians (parents).
    """

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")
        permissions = (
            ("view_address", _("Can view address")),
            ("view_contact_details", _("Can view contact details")),
            ("view_photo", _("Can view photo")),
            ("view_avatar", _("Can view avatar image")),
            ("view_person_groups", _("Can view persons groups")),
            ("view_personal_details", _("Can view personal details")),
        )
        constraints = [
            models.UniqueConstraint(
                fields=["short_name"], condition=~Q(short_name=""), name="unique_short_name"
            ),
            models.UniqueConstraint(fields=["email"], condition=~Q(email=""), name="unique_email"),
        ]

    icon_ = "account-outline"

    SEX_CHOICES = [("f", _("female")), ("m", _("male")), ("x", _("other"))]

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="person",
        verbose_name=_("Linked user"),
    )

    first_name = models.CharField(verbose_name=_("First name"), max_length=255)
    last_name = models.CharField(verbose_name=_("Last name"), max_length=255)
    additional_name = models.CharField(
        verbose_name=_("Additional name(s)"), max_length=255, blank=True
    )

    short_name = models.CharField(
        verbose_name=_("Short name"),
        max_length=255,
        blank=True,
    )

    street = models.CharField(verbose_name=_("Street"), max_length=255, blank=True)
    housenumber = models.CharField(verbose_name=_("Street number"), max_length=255, blank=True)
    postal_code = models.CharField(verbose_name=_("Postal code"), max_length=255, blank=True)
    place = models.CharField(verbose_name=_("Place"), max_length=255, blank=True)

    phone_number = PhoneNumberField(verbose_name=_("Home phone"), blank=True)
    mobile_number = PhoneNumberField(verbose_name=_("Mobile phone"), blank=True)

    email = models.EmailField(verbose_name=_("E-mail address"), blank=True)

    date_of_birth = models.DateField(verbose_name=_("Date of birth"), blank=True, null=True)
    place_of_birth = models.CharField(verbose_name=_("Place of birth"), max_length=255, blank=True)
    sex = models.CharField(verbose_name=_("Sex"), max_length=1, choices=SEX_CHOICES, blank=True)

    photo = models.ImageField(
        verbose_name=_("Photo"),
        blank=True,
        null=True,
        help_text=_(
            "This is an official photo, used for official documents and for internal use cases."
        ),
    )

    avatar = models.ImageField(
        verbose_name=_("Display picture / Avatar"),
        blank=True,
        null=True,
        help_text=_("This is a picture or an avatar for public display."),
    )

    guardians = models.ManyToManyField(
        "self",
        verbose_name=_("Guardians / Parents"),
        symmetrical=False,
        related_name="children",
        blank=True,
    )

    primary_group = models.ForeignKey(
        "Group", models.SET_NULL, null=True, blank=True, verbose_name=_("Primary group")
    )

    description = models.TextField(verbose_name=_("Description"), blank=True)

    def get_absolute_url(self) -> str:
        return reverse("person_by_id", args=[self.id])

    @property
    def primary_group_short_name(self) -> Optional[str]:
        """Return the short_name field of the primary group related object."""
        if self.primary_group:
            return self.primary_group.short_name

    @primary_group_short_name.setter
    def primary_group_short_name(self, value: str) -> None:
        """
        Set the primary group related object by a short name.

        It uses the first existing group
        with this short name it can find, creating one
        if it can't find one.
        """
        group, created = Group.objects.get_or_create(short_name=value, defaults={"name": value})
        self.primary_group = group

    @property
    def full_name(self) -> str:
        """Full name of person in last name, first name order."""
        return f"{self.last_name}, {self.first_name}"

    @property
    def addressing_name(self) -> str:
        """Full name of person in format configured for addressing."""
        if self.preferences["notification__addressing_name_format"] == "last_first":
            return f"{self.last_name}, {self.first_name}"
        elif self.preferences["notification__addressing_name_format"] == "first_last":
            return f"{self.first_name} {self.last_name}"

    @property
    def mail_sender(self) -> str:
        """E-mail sender in "Name <email>" format."""
        return f'"{self.addressing_name}" <{self.email}>'

    @property
    def mail_sender_via(self) -> str:
        """E-mail sender for via addresses, in "Name via Site <email>" format."""
        site_mail = get_site_preferences()["mail__address"]
        site_name = get_site_preferences()["general__title"]

        return f'"{self.addressing_name} via {site_name}" <{site_mail}>'

    @property
    def age(self):
        """Age of the person at current time."""
        return self.age_at(timezone.now().date())

    def age_at(self, today):
        if self.date_of_birth:
            years = today.year - self.date_of_birth.year
            if self.date_of_birth.month > today.month or (
                self.date_of_birth.month == today.month and self.date_of_birth.day > today.day
            ):
                years -= 1
            return years

    @property
    def dashboard_widgets(self):
        return [
            w.widget
            for w in DashboardWidgetOrder.objects.filter(person=self, widget__active=True).order_by(
                "order"
            )
        ]

    @property
    def unread_notifications(self) -> QuerySet:
        """Get all unread notifications for this person."""
        return self.notifications.filter(read=False, send_at__lte=timezone.now())

    @property
    def unread_notifications_count(self) -> int:
        """Return the count of unread notifications for this person."""
        return self.unread_notifications.count()

    @property
    def initials(self):
        initials = ""
        if self.first_name:
            initials += self.first_name[0]
        if self.last_name:
            initials += self.last_name[0]
        return initials.upper() or "?"

    user_info_tracker = FieldTracker(fields=("first_name", "last_name", "email", "user_id"))

    @property
    @cache_memoize(60 * 60)
    def identicon_url(self):
        identicon = customidenticon.create(self.full_name, border=35)
        base64_data = base64.b64encode(identicon).decode("ascii")
        return f"data:image/png;base64,{base64_data}"

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return self.identicon_url

    def get_vcal_address(self, role: str = "REQ-PARTICIPANT") -> Optional[vCalAddress]:
        """Return a vCalAddress object for this person."""
        if not self.email:
            # vCalAddress requires an email address
            return None
        vcal = vCalAddress(f"MAILTO:{self.email}")
        vcal.params["cn"] = vText(self.full_name)
        vcal.params["ROLE"] = vText(role)
        return vcal

    def save(self, *args, **kwargs):
        # Determine all fields that were changed since last load
        changed = self.user_info_tracker.changed()

        super().save(*args, **kwargs)

        if self.pk is None or bool(changed):
            if "user_id" in changed:
                # Clear groups of previous Django user
                previous_user = changed["user_id"]
                if previous_user is not None:
                    get_user_model().objects.get(pk=previous_user).groups.clear()

            if self.user:
                if "first_name" in changed or "last_name" in changed or "email" in changed:
                    # Synchronise user fields to linked User object to keep it up to date
                    self.user.first_name = self.first_name
                    self.user.last_name = self.last_name
                    self.user.email = self.email
                    self.user.save()

                if "user_id" in changed:
                    # Synchronise groups to Django groups
                    for group in self.member_of.union(self.owner_of.all()).all():
                        group.save(force=True)

        # Select a primary group if none is set
        self.auto_select_primary_group()

    def __str__(self) -> str:
        return self.full_name

    @classmethod
    def maintain_default_data(cls):
        # Ensure we have an admin user
        user = get_user_model()
        if not user.objects.filter(is_superuser=True).exists():
            admin = user.objects.create_superuser(**settings.AUTH_INITIAL_SUPERUSER)
            admin.save()

    def auto_select_primary_group(
        self, pattern: Optional[str] = None, field: Optional[str] = None, force: bool = False
    ) -> None:
        """Auto-select the primary group among the groups the person is member of.

        Uses either the pattern passed as argument, or the pattern configured system-wide.

        Does not do anything if either no pattern is defined or the user already has
        a primary group, unless force is True.
        """
        pattern = pattern or get_site_preferences()["account__primary_group_pattern"]
        field = field or get_site_preferences()["account__primary_group_field"]

        if pattern and (force or not self.primary_group):
            self.primary_group = self.member_of.filter(**{f"{field}__regex": pattern}).first()

    def notify_about_changed_data(
        self, changed_fields: Iterable[str], recipients: Optional[List[str]] = None
    ):
        """Notify (configured) recipients about changed data of this person."""
        context = {"person": self, "changed_fields": changed_fields}
        recipients = recipients or [
            get_site_preferences()["account__person_change_notification_contact"]
        ]
        send_email(
            template_name="person_changed",
            from_email=self.mail_sender_via,
            headers={
                "Reply-To": self.mail_sender,
                "Sender": self.mail_sender,
            },
            recipient_list=recipients,
            context=context,
        )


class DummyPerson(Person):
    """A dummy person that is not stored into the database.

    Used to temporarily inject a Person object into a User.
    """

    class Meta:
        managed = False
        proxy = True

    is_dummy = True

    def save(self, *args, **kwargs):
        # Do nothing, not even call Model's save(), so this is never persisted
        pass


class Group(SchoolTermRelatedExtensibleModel):
    """Group model.

    Any kind of group of persons in a school, including, but not limited
    classes, clubs, and the like.
    """

    objects = GroupManager.from_queryset(GroupQuerySet)()

    class Meta:
        ordering = ["short_name", "name"]
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
        permissions = (
            ("assign_child_groups_to_groups", _("Can assign child groups to groups")),
            ("view_group_stats", _("Can view statistics about group.")),
        )
        constraints = [
            models.UniqueConstraint(
                fields=["school_term", "name"], name="unique_school_term_name_group"
            ),
            models.UniqueConstraint(
                fields=["school_term", "short_name"], name="unique_school_term_short_name_group"
            ),
        ]

    icon_ = "account-multiple-outline"

    name = models.CharField(verbose_name=_("Long name"), max_length=255)
    short_name = models.CharField(  # noqa
        verbose_name=_("Short name"),
        max_length=255,
        blank=True,
        null=True,
    )

    members = models.ManyToManyField(
        "Person",
        related_name="member_of",
        blank=True,
        through="PersonGroupThrough",
        verbose_name=_("Members"),
    )
    owners = models.ManyToManyField(
        "Person", related_name="owner_of", blank=True, verbose_name=_("Owners")
    )

    parent_groups = models.ManyToManyField(
        "self",
        related_name="child_groups",
        symmetrical=False,
        verbose_name=_("Parent groups"),
        blank=True,
    )

    group_type = models.ForeignKey(
        "GroupType",
        on_delete=models.SET_NULL,
        related_name="type",
        verbose_name=_("Type of group"),
        null=True,
        blank=True,
    )

    photo = models.ImageField(
        verbose_name=_("Photo"),
        blank=True,
        null=True,
        help_text=_(
            "This is an official photo, used for official documents and for internal use cases."
        ),
    )
    avatar = models.ImageField(
        verbose_name=_("Display picture / Avatar"),
        blank=True,
        null=True,
        help_text=_("This is a picture or an avatar for public display."),
    )

    def get_absolute_url(self) -> str:
        return reverse("group_by_id", args=[self.id])

    @property
    def announcement_recipients(self):
        """Flat list of all members and owners to fulfill announcement API contract."""
        return list(self.members.all()) + list(self.owners.all())

    @property
    def get_group_stats(self) -> dict:
        """Get stats about a given group"""
        stats = {}

        stats["members"] = len(self.members.all())

        ages = [person.age for person in self.members.filter(date_of_birth__isnull=False)]

        if ages:
            stats["age_avg"] = sum(ages) / len(ages)
            stats["age_range_min"] = min(ages)
            stats["age_range_max"] = max(ages)

        return stats

    def __str__(self) -> str:
        if self.school_term:
            return f"{self.name} ({self.short_name}) ({self.school_term})"
        else:
            return f"{self.name} ({self.short_name})"

    group_info_tracker = FieldTracker(fields=("name", "short_name"))

    def save(self, force: bool = False, *args, **kwargs):
        # Determine state of object in relation to database
        dirty = self.pk is None or bool(self.group_info_tracker.changed())

        super().save(*args, **kwargs)

        if force or dirty:
            # Synchronise group to Django group with same name
            dj_group, _ = DjangoGroup.objects.get_or_create(name=self.name)
            dj_group.user_set.set(
                list(
                    self.members.filter(user__isnull=False)
                    .values_list("user", flat=True)
                    .union(self.owners.filter(user__isnull=False).values_list("user", flat=True))
                )
            )
            dj_group.save()

    @property
    def django_group(self):
        """Get Django group for this group."""
        dj_group, _ = DjangoGroup.objects.get_or_create(name=self.name)
        return dj_group


class PersonGroupThrough(ExtensibleModel):
    """Through table for many-to-many relationship of group members.

    It does not have any fields on its own; these are generated upon instantiation
    by inspecting the additional fields selected for the linked group.
    """

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)


@receiver(models.signals.m2m_changed, sender=PersonGroupThrough)
@receiver(models.signals.m2m_changed, sender=Group.owners.through)
def save_group_on_m2m_changed(
    sender: Union[PersonGroupThrough, Group.owners.through],
    instance: models.Model,
    action: str,
    reverse: bool,
    model: models.Model,
    pk_set: Optional[set],
    **kwargs,
) -> None:
    """Ensure user and group data is synced to Django's models.

    AlekSIS maintains personal information and group meta-data / membership
    in its Person and Group models. As third-party libraries have no knowledge
    about this, we need to keep django.contrib.auth in sync.

    This signal handler triggers a save of group objects whenever a membership
    changes. The save() code will decide whether to update the Django objects
    or not.
    """
    if action not in ("post_add", "post_remove", "post_clear"):
        # Only trigger once, after the change was applied to the database
        return

    if reverse:
        # Relationship was changed on the Person side, saving all groups
        # that have been touched there
        for group in model.objects.filter(pk__in=pk_set):
            group.save(force=True)
    else:
        # Relationship was changed on the Group side
        instance.save(force=True)


class Activity(ExtensibleModel, TimeStampedModel):
    """Activity of a user to trace some actions done in AlekSIS in displayable form."""

    user = models.ForeignKey(
        "Person", on_delete=models.CASCADE, related_name="activities", verbose_name=_("User")
    )

    title = models.CharField(max_length=150, verbose_name=_("Title"))
    description = models.TextField(max_length=500, verbose_name=_("Description"))

    app = models.CharField(max_length=100, verbose_name=_("Application"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")


class Notification(ExtensibleModel, TimeStampedModel):
    """Notification to submit to a user."""

    sender = models.CharField(max_length=100, verbose_name=_("Sender"))
    recipient = models.ForeignKey(
        "Person",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Recipient"),
    )

    title = models.CharField(max_length=150, verbose_name=_("Title"))
    description = models.TextField(max_length=500, verbose_name=_("Description"))
    link = models.URLField(blank=True, verbose_name=_("Link"))

    icon = models.CharField(
        max_length=50, choices=ICONS, verbose_name=_("Icon"), default="information-outline"
    )

    send_at = models.DateTimeField(default=timezone.now, verbose_name=_("Send notification at"))

    read = models.BooleanField(default=False, verbose_name=_("Read"))
    sent = models.BooleanField(default=False, verbose_name=_("Sent"))

    def __str__(self):
        return str(self.title)

    def save(self, **kwargs):
        super().save(**kwargs)
        if not self.sent and self.send_at <= timezone.now():
            self.send()
            super().save(**kwargs)

    def send(self, resend: bool = False) -> Optional[AsyncResult]:
        """Send the notification to the recipient."""
        if not self.sent or resend:
            return send_notification.delay(self.pk, resend=resend)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")


class AnnouncementQuerySet(models.QuerySet):
    """Queryset for announcements providing time-based utility functions."""

    def relevant_for(self, obj: Union[models.Model, models.QuerySet]) -> models.QuerySet:
        """Get all relevant announcements.

        Get a QuerySet with all announcements relevant for a certain Model (e.g. a Group)
        or a set of models in a QuerySet.
        """
        if isinstance(obj, models.QuerySet):
            ct = ContentType.objects.get_for_model(obj.model)
            pks = list(obj.values_list("pk", flat=True))
        else:
            ct = ContentType.objects.get_for_model(obj)
            pks = [obj.pk]

        return self.filter(recipients__content_type=ct, recipients__recipient_id__in=pks)

    def at_time(self, when: Optional[datetime] = None) -> models.QuerySet:
        """Get all announcements at a certain time."""
        when = when or timezone.now()

        # Get announcements by time
        announcements = self.filter(valid_from__lte=when, valid_until__gte=when)

        return announcements

    def on_date(self, when: Optional[date] = None) -> models.QuerySet:
        """Get all announcements at a certain date."""
        when = when or timezone.now().date()

        # Get announcements by time
        announcements = self.filter(valid_from__date__lte=when, valid_until__date__gte=when)

        return announcements

    def within_days(self, start: date, stop: date) -> models.QuerySet:
        """Get all announcements valid for a set of days."""
        # Get announcements
        announcements = self.filter(valid_from__date__lte=stop, valid_until__date__gte=start)

        return announcements

    def for_person(self, person: Person) -> List:
        """Get all announcements for one person."""
        # Filter by person
        announcements_for_person = []
        for announcement in self:
            if person in announcement.recipient_persons:
                announcements_for_person.append(announcement)

        return announcements_for_person


class Announcement(ExtensibleModel):
    """Announcement model.

    Persistent announcement to display to groups or persons in various places during a
    specific time range.
    """

    objects = models.Manager.from_queryset(AnnouncementQuerySet)()

    title = models.CharField(max_length=150, verbose_name=_("Title"))
    description = models.TextField(max_length=500, verbose_name=_("Description"), blank=True)
    link = models.URLField(blank=True, verbose_name=_("Link to detailed view"))

    valid_from = models.DateTimeField(
        verbose_name=_("Date and time from when to show"), default=timezone.now
    )
    valid_until = models.DateTimeField(
        verbose_name=_("Date and time until when to show"),
        default=now_tomorrow,
    )

    @property
    def recipient_persons(self) -> Sequence[Person]:
        """Return a list of Persons this announcement is relevant for."""
        persons = []
        for recipient in self.recipients.all():
            persons += recipient.persons
        return persons

    def get_recipients_for_model(self, obj: Union[models.Model]) -> Sequence[models.Model]:
        """Get all recipients.

        Get all recipients for this announcement
        with a special content type (provided through model)
        """
        ct = ContentType.objects.get_for_model(obj)
        return [r.recipient for r in self.recipients.filter(content_type=ct)]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")


class AnnouncementRecipient(ExtensibleModel):
    """Announcement recipient model.

    Generalisation of a recipient for an announcement, used to wrap arbitrary
    objects that can receive announcements.

    Contract: Objects to serve as recipient have a property announcement_recipients
    returning a flat list of Person objects.
    """

    announcement = models.ForeignKey(
        Announcement, on_delete=models.CASCADE, related_name="recipients"
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    recipient_id = models.PositiveIntegerField()
    recipient = GenericForeignKey("content_type", "recipient_id")

    @property
    def persons(self) -> Sequence[Person]:
        """Return a list of Persons selected by this recipient object.

        If the recipient is a Person, return that object. If not, it returns the list
        from the announcement_recipients field on the target model.
        """
        if isinstance(self.recipient, Person):
            return [self.recipient]
        else:
            return getattr(self.recipient, "announcement_recipients", [])

    def __str__(self):
        return str(self.recipient)

    class Meta:
        verbose_name = _("Announcement recipient")
        verbose_name_plural = _("Announcement recipients")


class DashboardWidget(RegistryObject, PolymorphicModel, PureDjangoModel):
    """Base class for dashboard widgets on the index page."""

    objects = UninstallRenitentPolymorphicManager()

    @staticmethod
    def get_media(widgets: Union[QuerySet, Iterable]):
        """Return all media required to render the selected widgets."""
        media = Media()
        for widget in widgets:
            media = media + widget.media
        return media

    template = None
    template_broken = "core/dashboard_widget/dashboardwidget_broken.html"
    media = Media()

    title = models.CharField(max_length=150, verbose_name=_("Widget Title"))
    active = models.BooleanField(verbose_name=_("Activate Widget"))
    broken = models.BooleanField(verbose_name=_("Widget is broken"), default=False)

    size_s = models.PositiveSmallIntegerField(
        verbose_name=_("Size on mobile devices"),
        help_text=_("<= 600 px, 12 columns"),
        validators=[MaxValueValidator(12)],
        default=12,
    )
    size_m = models.PositiveSmallIntegerField(
        verbose_name=_("Size on tablet devices"),
        help_text=_("> 600 px, 12 columns"),
        validators=[MaxValueValidator(12)],
        default=12,
    )
    size_l = models.PositiveSmallIntegerField(
        verbose_name=_("Size on desktop devices"),
        help_text=_("> 992 px, 12 columns"),
        validators=[MaxValueValidator(12)],
        default=6,
    )
    size_xl = models.PositiveSmallIntegerField(
        verbose_name=_("Size on large desktop devices"),
        help_text=_("> 1200 px>, 12 columns"),
        validators=[MaxValueValidator(12)],
        default=4,
    )

    def _get_context_safe(self, request):
        if self.broken:
            return {"title": self.title}
        return self.get_context(request)

    def get_context(self, request):
        """Get the context dictionary to pass to the widget template."""
        raise NotImplementedError("A widget subclass needs to implement the get_context method.")

    def get_template(self):
        """Get template.

        Get the template to render the widget with. Defaults to the template attribute,
        but can be overridden to allow more complex template generation scenarios. If
        the widget is marked as broken, the template_broken attribute will be returned.
        """
        if self.broken:
            return self.template_broken
        if not self.template:
            raise NotImplementedError("A widget subclass needs to define a template.")
        return self.template

    def __str__(self):
        return self.title

    class Meta:
        permissions = (("edit_default_dashboard", _("Can edit default dashboard")),)
        verbose_name = _("Dashboard Widget")
        verbose_name_plural = _("Dashboard Widgets")


class ExternalLinkWidget(DashboardWidget):
    template = "core/dashboard_widget/external_link_widget.html"

    url = models.URLField(verbose_name=_("URL"))
    icon_url = models.URLField(verbose_name=_("Icon URL"))

    def get_context(self, request):
        return {"title": self.title, "url": self.url, "icon_url": self.icon_url}

    class Meta:
        verbose_name = _("External link widget")
        verbose_name_plural = _("External link widgets")


class StaticContentWidget(DashboardWidget):
    template = "core/dashboard_widget/static_content_widget.html"

    content = RichTextField(verbose_name=_("Content"))

    def get_context(self, request):
        return {"title": self.title, "content": self.content}

    class Meta:
        verbose_name = _("Static content widget")
        verbose_name_plural = _("Static content widgets")


class DashboardWidgetOrder(ExtensibleModel):
    widget = models.ForeignKey(
        DashboardWidget, on_delete=models.CASCADE, verbose_name=_("Dashboard widget")
    )
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, verbose_name=_("Person"), null=True, blank=True
    )
    order = models.PositiveIntegerField(verbose_name=_("Order"))
    default = models.BooleanField(default=False, verbose_name=_("Part of the default dashboard"))

    objects = InstalledWidgetsDashboardWidgetOrderManager()

    @classproperty
    def default_dashboard_widgets(cls):
        """Get default order for dashboard widgets."""
        return [
            w.widget
            for w in cls.objects.filter(person=None, default=True, widget__active=True).order_by(
                "order"
            )
        ]

    class Meta:
        verbose_name = _("Dashboard widget order")
        verbose_name_plural = _("Dashboard widget orders")


class CustomMenu(ExtensibleModel):
    """A custom menu to display in the footer."""

    name = models.CharField(max_length=100, verbose_name=_("Menu ID"))

    def __str__(self):
        return self.name if self.name != "" else self.id

    @classmethod
    @cache_memoize(3600)
    def get_default(cls, name):
        """Get a menu by name or create if it does not exist."""
        menu, _ = cls.objects.prefetch_related("items").get_or_create(name=name)
        return menu

    class Meta:
        verbose_name = _("Custom menu")
        verbose_name_plural = _("Custom menus")
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_menu_name"),
        ]


class CustomMenuItem(ExtensibleModel):
    """Single item in a custom menu."""

    menu = models.ForeignKey(
        CustomMenu, models.CASCADE, verbose_name=_("Menu"), related_name="items"
    )
    name = models.CharField(max_length=150, verbose_name=_("Name"))
    url = models.URLField(verbose_name=_("Link"))
    icon = models.CharField(max_length=50, blank=True, choices=ICONS, verbose_name=_("Icon"))

    def __str__(self):
        return f"[{self.menu}] {self.name}"

    class Meta:
        verbose_name = _("Custom menu item")
        verbose_name_plural = _("Custom menu items")
        constraints = [
            models.UniqueConstraint(fields=["menu", "name"], name="unique_name_per_menu"),
        ]

    def get_absolute_url(self):
        return reverse("admin:core_custommenuitem_change", args=[self.id])


class DynamicRoute(RegistryObject):
    """Define a dynamic route.

    Dynamic routes should be used to register Vue routes dynamically, e. g.
    when an app is supposed to show menu items for dynamically creatable objects.
    """


class GroupType(ExtensibleModel):
    """Group type model.

    Descriptive type of a group; used to tag groups and for apps to distinguish
    how to display or handle a certain group.
    """

    name = models.CharField(verbose_name=_("Title of type"), max_length=50)
    description = models.CharField(verbose_name=_("Description"), max_length=500)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Group type")
        verbose_name_plural = _("Group types")
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_group_type_name"),
        ]


class GlobalPermissions(GlobalPermissionModel):
    """Container for global permissions."""

    class Meta(GlobalPermissionModel.Meta):
        permissions = (
            ("view_system_status", _("Can view system status")),
            ("manage_data", _("Can manage data")),
            ("impersonate", _("Can impersonate")),
            ("search", _("Can use search")),
            ("change_site_preferences", _("Can change site preferences")),
            ("change_person_preferences", _("Can change person preferences")),
            ("change_group_preferences", _("Can change group preferences")),
            ("test_pdf", _("Can test PDF generation")),
            ("invite", _("Can invite persons")),
            ("view_birthday_calendar", _("Can view birthday calendar")),
        )


class PersonPreferenceModel(PerInstancePreferenceModel, PureDjangoModel):
    """Preference model to hold pereferences valid for a person."""

    instance = models.ForeignKey(Person, on_delete=models.CASCADE)

    class Meta(PerInstancePreferenceModel.Meta):
        app_label = "core"


class GroupPreferenceModel(PerInstancePreferenceModel, PureDjangoModel):
    """Preference model to hold pereferences valid for members of a group."""

    instance = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta(PerInstancePreferenceModel.Meta):
        app_label = "core"


class DataCheckResult(ExtensibleModel):
    """Save the result of a data check for a specific object."""

    data_check = models.CharField(
        max_length=255,
        verbose_name=_("Related data check task"),
        choices=DataCheck.data_checks_choices,
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    related_object = GenericForeignKey("content_type", "object_id")

    solved = models.BooleanField(default=False, verbose_name=_("Issue solved"))
    sent = models.BooleanField(default=False, verbose_name=_("Notification sent"))

    @property
    def related_check(self) -> DataCheck:
        return DataCheck.registered_objects_dict[self.data_check]

    def solve(self, solve_option: str = "default"):
        self.related_check.solve(self, solve_option)

    def __str__(self):
        return f"{self.related_object}: {self.related_check.problem_name}"

    class Meta:
        verbose_name = _("Data check result")
        verbose_name_plural = _("Data check results")
        permissions = (
            ("run_data_checks", _("Can run data checks")),
            ("solve_data_problem", _("Can solve data check problems")),
        )


class PersonInvitation(AbstractBaseInvitation, PureDjangoModel):
    """Custom model for invitations to allow to generate invitations codes without email address."""

    email = models.EmailField(verbose_name=_("E-Mail address"), blank=True)
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, blank=True, related_name="invitation", null=True
    )

    def __str__(self) -> str:
        return f"{self.email} ({self.inviter})"

    @classmethod
    def create(cls, email, inviter=None, **kwargs):
        length = get_site_preferences()["auth__invite_code_length"]
        packet_size = get_site_preferences()["auth__invite_code_packet_size"]
        code = generate_random_code(length, packet_size)

        instance = cls.objects.create(email=email, inviter=inviter, key=code, **kwargs)
        return instance

    def send_invitation(self, request, **kwargs):
        """Send the invitation email to the person."""
        invite_url = reverse("invitations:accept-invite", args=[self.key])
        invite_url = request.build_absolute_uri(invite_url).replace("/django", "")
        context = kwargs
        context.update(
            {
                "invite_url": invite_url,
                "site_name": get_site_preferences()["general__title"],
                "email": self.email,
                "inviter": self.inviter,
                "person": self.person,
            },
        )

        send_email(template_name="invitation", recipient_list=[self.email], context=context)

        self.sent = timezone.now()
        self.save()

        signals.invite_url_sent.send(
            sender=self.__class__,
            instance=self,
            invite_url_sent=invite_url,
            inviter=self.inviter,
        )

    key_expired = Invitation.key_expired
    send_invitation = send_invitation


class PDFFile(ExtensibleModel):
    """Link to a rendered PDF file."""

    def _get_default_expiration():  # noqa
        return timezone.now() + timedelta(minutes=get_site_preferences()["general__pdf_expiration"])

    person = models.ForeignKey(
        to=Person,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Owner"),
        related_name="pdf_files",
    )
    expires_at = models.DateTimeField(
        verbose_name=_("File expires at"), default=_get_default_expiration
    )
    html_file = models.FileField(
        upload_to="pdfs/", verbose_name=_("Generated HTML file"), blank=True, null=True
    )
    file = models.FileField(
        upload_to="pdfs/", blank=True, null=True, verbose_name=_("Generated PDF file")
    )

    def __str__(self):
        return f"{self.person} ({self.pk})"

    class Meta:
        verbose_name = _("PDF file")
        verbose_name_plural = _("PDF files")


class TaskUserAssignment(ExtensibleModel):
    task_result = models.ForeignKey(
        TaskResult, on_delete=models.CASCADE, verbose_name=_("Task result")
    )
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, verbose_name=_("Task user")
    )

    title = models.CharField(max_length=255, verbose_name=_("Title"))
    back_url = models.URLField(verbose_name=_("Back URL"), blank=True)
    progress_title = models.CharField(max_length=255, verbose_name=_("Progress title"), blank=True)
    error_message = models.TextField(verbose_name=_("Error message"), blank=True)
    success_message = models.TextField(verbose_name=_("Success message"), blank=True)
    redirect_on_success_url = models.URLField(verbose_name=_("Redirect on success URL"), blank=True)
    additional_button_title = models.CharField(
        max_length=255, verbose_name=_("Additional button title"), blank=True
    )
    additional_button_url = models.URLField(verbose_name=_("Additional button URL"), blank=True)
    additional_button_icon = models.CharField(
        max_length=255, verbose_name=_("Additional button icon"), blank=True
    )
    result_fetched = models.BooleanField(default=False, verbose_name=_("Result fetched"))

    @classmethod
    def create_for_task_id(cls, task_id: str, user: "User") -> "TaskUserAssignment":
        # Use get_or_create to ensure the TaskResult exists
        # django-celery-results will later add the missing information
        with cachalot_disabled():
            result, __ = TaskResult.objects.get_or_create(task_id=task_id)
        return cls.objects.create(task_result=result, user=user)

    def get_progress(self) -> dict[str, any]:
        """Get progress information for this task."""
        progress = Progress(AsyncResult(self.task_result.task_id))
        return progress.get_info()

    def get_progress_with_meta(self) -> dict[str, any]:
        """Get progress information for this task."""
        progress = self.get_progress()
        progress["meta"] = self
        return progress

    def create_notification(self) -> Optional[Notification]:
        """Create a notification for this task."""
        progress = self.get_progress()
        if progress["state"] == "SUCCESS":
            title = _("Background task completed successfully")
            description = _("The background task '{}' has been completed successfully.").format(
                self.title
            )
            icon = "check-circle-outline"

        elif progress["state"] == "FAILURE":
            title = _("Background task failed")
            description = _("The background task '{}' has failed.").format(self.title)
            icon = "alert-octagon-outline"
        else:
            # Task not yet finished
            return

        link = urljoin(settings.BASE_URL, self.get_absolute_url())

        notification = Notification(
            sender=_("Background task"),
            recipient=self.user.person,
            title=title,
            description=description,
            link=link,
            icon=icon,
        )
        notification.save()
        return notification

    def get_absolute_url(self) -> str:
        return f"/celery_progress/{self.task_result.task_id}"

    class Meta:
        verbose_name = _("Task user assignment")
        verbose_name_plural = _("Task user assignments")


class UserAdditionalAttributes(models.Model, PureDjangoModel):
    """Additional attributes for Django user accounts.

    These attributes are explicitly linked to a User, not to a Person.
    """

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="additional_attributes",
        verbose_name=_("Linked user"),
    )

    attributes = models.JSONField(verbose_name=_("Additional attributes"), default=dict)

    def __str__(self):
        return str(self.user)

    @classmethod
    def get_user_attribute(
        cls, username: str, attribute: str, default: Optional[Any] = None
    ) -> Any:
        """Get a user attribute for a user by name."""
        try:
            attributes = cls.objects.get(user__username=username)
        except cls.DoesNotExist:
            return default

        return attributes.attributes.get(attribute, default)

    @classmethod
    def set_user_attribute(cls, username: str, attribute: str, value: Any):
        """Set a user attribute for a user by name.

        Raises DoesNotExist if a username for a non-existing Django user is passed.
        """
        user = get_user_model().objects.get(username=username)
        attributes, __ = cls.objects.update_or_create(user=user)

        attributes.attributes[attribute] = value
        attributes.save()


class OAuthApplication(AbstractApplication):
    """Modified OAuth application class that supports Grant Flows configured in preferences."""

    # Override grant types to make field optional
    authorization_grant_type = models.CharField(
        max_length=32, choices=AbstractApplication.GRANT_TYPES, blank=True
    )

    # Optional list of alloewd scopes
    allowed_scopes = ArrayField(
        models.CharField(max_length=255),
        verbose_name=_("Allowed scopes that clients can request"),
        null=True,
        blank=True,
    )

    icon = models.ImageField(
        verbose_name=_("Icon"),
        blank=True,
        null=True,
        help_text=_(
            "This image will be shown as icon in the authorization flow. It should be squared."
        ),
    )

    def allows_grant_type(self, *grant_types: set[str]) -> bool:
        allowed_grants = get_site_preferences()["auth__oauth_allowed_grants"]

        return bool(set(allowed_grants) & set(grant_types))

    def get_absolute_url(self):
        return reverse("oauth2_application", args=[self.id])


class OAuthGrant(AbstractGrant):
    """Placeholder for customising the Grant model."""

    pass


class OAuthAccessToken(AbstractAccessToken):
    """Placeholder for customising the AccessToken model."""

    pass


class OAuthIDToken(AbstractIDToken):
    """Placeholder for customising the IDToken model."""

    pass


class OAuthRefreshToken(AbstractRefreshToken):
    """Placeholder for customising the RefreshToken model."""

    pass


class Room(ExtensibleModel):
    short_name = models.CharField(verbose_name=_("Short name"), max_length=255)
    name = models.CharField(verbose_name=_("Long name"), max_length=255)

    icon_ = "door"

    def __str__(self) -> str:
        return f"{self.name} ({self.short_name})"

    def get_absolute_url(self) -> str:
        return reverse("timetable", args=["room", self.id])

    class Meta:
        permissions = (("view_room_timetable", _("Can view room timetable")),)
        ordering = ["name", "short_name"]
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")
        constraints = [
            models.UniqueConstraint(fields=["short_name"], name="unique_room_short_name"),
        ]


class CalendarEvent(CalendarEventMixin, ExtensiblePolymorphicModel):
    """A planned event in a calendar.

    To make use of this model, you need to inherit from this model.
    Every subclass of this model represents a certain calendar (feed).
    It therefore needs to set the basic attributes of the calendar like
    described in the documentation of `CalendarEventMixin`.

    Furthermore, every `value_*` method from `CalendarEventMixin`
    can be implemented to provide additional data (either static or dynamic).
    Some like start and end date are pre-implemented in this model. Others, like
    `value_title` need to be implemented in the subclass. Some methods are
    also optional, like `value_location` or `value_description`.
    Please refer to the documentation of `CalendarEventMixin` for more information.
    """

    datetime_start = models.DateTimeField(
        verbose_name=_("Start date and time"), null=True, blank=True
    )
    datetime_end = models.DateTimeField(verbose_name=_("End date and time"), null=True, blank=True)
    timezone = TimeZoneField(verbose_name=_("Timezone"), null=True, blank=True)
    date_start = models.DateField(verbose_name=_("Start date"), null=True, blank=True)
    date_end = models.DateField(verbose_name=_("End date"), null=True, blank=True)
    recurrences = RecurrenceField(verbose_name=_("Recurrences"), null=True, blank=True)
    amends = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Amended base event"),
        related_name="amended_by",
    )

    def provide_list_in_timezone(self, seq):
        """Provide a list of datetimes in the saved timezone."""
        return [dt.astimezone(self.timezone) if isinstance(dt, datetime) else dt for dt in seq]

    @classmethod
    def value_title(
        cls, reference_object: "CalendarEvent", request: HttpRequest | None = None
    ) -> str:
        """Return the title of the calendar event."""
        raise NotImplementedError()

    @classmethod
    def value_start_datetime(
        cls, reference_object: "CalendarEvent", request: HttpRequest | None = None
    ) -> Union[datetime, date]:
        """Return the start datetime of the calendar event."""
        if reference_object.datetime_start:
            return reference_object.datetime_start.astimezone(reference_object.timezone)
        return reference_object.date_start

    @classmethod
    def value_end_datetime(
        cls, reference_object: "CalendarEvent", request: HttpRequest | None = None
    ) -> Union[datetime, date, None]:
        """Return the end datetime of the calendar event."""
        if reference_object.datetime_end:
            return reference_object.datetime_end.astimezone(reference_object.timezone)
        if reference_object.date_end == reference_object.date_start:
            # Rule for all day events: If the event is only one day long,
            # the end date has to be empty
            return None
        return reference_object.date_end

    @classmethod
    def value_rrule(
        cls, reference_object: "CalendarEvent", request: HttpRequest | None = None
    ) -> Optional[vRecur]:
        """Return the rrule of the calendar event."""
        if not reference_object.recurrences or not reference_object.recurrences.rrules:
            return None
        # iCal only supports one RRULE per event as per RFC 5545 (change to older RFC 2445)
        return build_rrule_from_recurrences_rrule(reference_object.recurrences.rrules[0])

    @classmethod
    def value_rdate(
        cls, reference_object: "CalendarEvent", request: HttpRequest | None = None
    ) -> Optional[list[datetime]]:
        """Return the rdate of the calendar event."""
        if not reference_object.recurrences:
            return None
        return reference_object.provide_list_in_timezone(reference_object.recurrences.rdates)

    @classmethod
    def value_exrule(
        cls, reference_object: "CalendarEvent", request: HttpRequest | None = None
    ) -> Optional[list[vRecur]]:
        """Return the exrule of the calendar event."""
        if not reference_object.recurrences or not reference_object.recurrences.exrules:
            return None
        return [build_rrule_from_recurrences_rrule(r) for r in reference_object.recurrences.exrules]

    @classmethod
    def value_exdate(
        cls, reference_object: "CalendarEvent", request: HttpRequest | None = None
    ) -> Optional[list[datetime]]:
        """Return the exdate of the calendar event."""
        if not reference_object.recurrences:
            return None
        return reference_object.provide_list_in_timezone(reference_object.recurrences.exdates)

    @classmethod
    def value_unique_id(
        cls, reference_object: "CalendarEvent", request: HttpRequest | None = None
    ) -> str:
        """Return an unique identifier for an event."""
        if reference_object.amends:
            return cls.value_unique_id(reference_object.amends, request=request)
        return f"{cls.name}-{reference_object.id}"

    @classmethod
    def value_recurrence_id(
        cls, reference_object: "CalendarEvent", request: HttpRequest | None = None
    ) -> Optional[Union[datetime, date]]:
        """Return the recurrence id of the calendar event."""
        if reference_object.amends:
            return reference_object.amends.value_start_datetime(reference_object, request=request)
        return None

    @classmethod
    def value_color(
        cls, reference_object: "CalendarEvent", request: HttpRequest | None = None
    ) -> str:
        """Return the color of the calendar."""
        return cls.get_color(request)

    @classmethod
    def value_reference_object(
        cls, reference_object: "CalendarEvent", request: HttpRequest | None = None
    ):
        """Return the reference object itself."""
        return reference_object

    @classmethod
    def get_objects(
        cls, request: HttpRequest | None = None, params: dict[str, any] | None = None
    ) -> Iterable:
        """Return all objects that should be included in the calendar."""
        return cls.objects.instance_of(cls)

    def save(self, *args, **kwargs):
        if (
            self.datetime_start
            and self.datetime_end
            and self.datetime_start.tzinfo != self.datetime_end.tzinfo
        ):
            self.datetime_end = self.datetime_end.astimezone(self.datetime_start.tzinfo)
        if self.datetime_start and self.datetime_end:
            self.timezone = self.datetime_start.tzinfo
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Calendar Event")
        verbose_name_plural = _("Calendar Events")
        constraints = [
            models.CheckConstraint(
                check=~Q(datetime_start__isnull=True, date_start__isnull=True),
                name="datetime_start_or_date_start",
            ),
            models.CheckConstraint(
                check=~Q(datetime_end__isnull=True, date_end__isnull=True),
                name="datetime_end_or_date_end",
            ),
            models.CheckConstraint(
                check=~Q(datetime_start__isnull=False, timezone__isnull=True),
                name="timezone_if_datetime_start",
            ),
            models.CheckConstraint(
                check=~Q(datetime_end__isnull=False, timezone__isnull=True),
                name="timezone_if_datetime_end",
            ),
        ]
        ordering = ["datetime_start", "date_start", "datetime_end", "date_end"]


class FreeBusy(CalendarEvent):
    pass


class BirthdayEvent(CalendarEventMixin):
    """A calendar feed with all birthdays."""

    name = "birthdays"
    verbose_name = _("Birthdays")
    permission_required = "core.view_birthday_calendar"

    @classmethod
    def value_title(cls, reference_object: Person, request: HttpRequest | None = None) -> str:
        return _("{}'s birthday").format(reference_object.addressing_name)

    @classmethod
    def value_description(cls, reference_object: Person, request: HttpRequest | None = None) -> str:
        return ("{name} was born on {birthday}.").format(
            name=reference_object.addressing_name,
            birthday=date_format(reference_object.date_of_birth),
        )

    @classmethod
    def value_start_datetime(
        cls, reference_object: Person, request: HttpRequest | None = None
    ) -> date:
        return reference_object.date_of_birth

    @classmethod
    def value_rrule(cls, reference_object: Person, request: HttpRequest | None = None) -> vRecur:
        return build_rrule_from_text("FREQ=YEARLY")

    @classmethod
    def value_unique_id(cls, reference_object: Person, request: HttpRequest | None = None) -> str:
        return f"birthday-{reference_object.id}"

    @classmethod
    def value_meta(cls, reference_object: Person, request: HttpRequest | None = None) -> dict:
        return {
            "name": reference_object.addressing_name,
            "date_of_birth": reference_object.date_of_birth.isoformat(),
        }

    @classmethod
    def get_color(cls, request: HttpRequest | None = None) -> str:
        return get_site_preferences()["calendar__birthday_color"]

    @classmethod
    def get_objects(
        cls, request: HttpRequest | None = None, params: dict[str, any] | None = None
    ) -> QuerySet:
        qs = Person.objects.filter(date_of_birth__isnull=False)
        if request:
            qs = qs.filter(
                Q(pk=request.user.person.pk)
                | Q(pk__in=get_objects_for_user(request.user, "core.view_personal_details", qs))
            )
        return qs


class Holiday(CalendarEvent):
    """Holiday model for keeping track of school holidays."""

    name = "holidays"
    verbose_name = _("Holidays")
    permission_required = "core.view_holiday_calendar"

    @classmethod
    def value_title(cls, reference_object: "Holiday", request: HttpRequest | None = None) -> str:
        return reference_object.holiday_name

    @classmethod
    def value_description(
        cls, reference_object: "Holiday", request: HttpRequest | None = None
    ) -> str:
        return ""

    @classmethod
    def get_color(cls, request: HttpRequest | None = None) -> str:
        return get_site_preferences()["calendar__holiday_color"]

    objects = PolymorphicBaseManager.from_queryset(HolidayQuerySet)()

    holiday_name = models.CharField(verbose_name=_("Name"), max_length=255)

    def get_days(self) -> Iterator[date]:
        """Get all days included in the holiday."""
        delta = self.date_end - self.date_start
        for i in range(delta.days + 1):
            yield self.date_start + timedelta(days=i)

    @classmethod
    def in_week(cls, week: CalendarWeek) -> dict[int, Optional["Holiday"]]:
        """Get the holidays that are active in a given week."""
        per_weekday = {}
        holidays = Holiday.objects.in_week(week)

        for weekday in range(0, 7):
            holiday_date = week[weekday]
            filtered_holidays = list(
                filter(
                    lambda h: holiday_date >= h.date_start and holiday_date <= h.date_end,
                    holidays,
                )
            )
            if filtered_holidays:
                per_weekday[weekday] = filtered_holidays[0]

        return per_weekday

    @classmethod
    def get_ex_dates(cls, datetime_start, datetime_end, recurrence):
        """Get the dates to exclude for holidays."""
        recurrence.dtstart = recurrence.dtstart.astimezone(timezone.get_current_timezone())
        holiday_dates = [
            h["DTSTART"].dt
            for h in Holiday.get_single_events(start=datetime_start, end=datetime_end)
        ]
        exdates = [
            h.astimezone(timezone.utc)
            for h in recurrence.occurrences()
            if h.date() in holiday_dates
        ]
        return exdates

    def __str__(self) -> str:
        return self.holiday_name

    class Meta:
        verbose_name = _("Holiday")
        verbose_name_plural = _("Holidays")
        permissions = [("view_holiday_calendar", _("Can view holiday calendar"))]


class PersonalEvent(CalendarEvent):
    name = "personal"
    verbose_name = _("Personal events")

    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"), blank=True)
    location = models.CharField(max_length=255, verbose_name=_("Location"), blank=True)

    owner = models.ForeignKey(
        Person,
        related_name="owned_events",
        on_delete=models.CASCADE,
        verbose_name=_("Owner"),
    )
    persons = models.ManyToManyField(Person, related_name="+", blank=True)
    groups = models.ManyToManyField(Group, related_name="+", blank=True)

    @classmethod
    def get_color(cls, request: HttpRequest | None = None) -> str:
        return get_site_preferences()["calendar__personal_event_color"]

    @classmethod
    def value_title(
        cls, reference_object: "PersonalEvent", request: HttpRequest | None = None
    ) -> str:
        """Return the title of the calendar event."""
        return reference_object.title

    @classmethod
    def value_description(
        cls, reference_object: "PersonalEvent", request: HttpRequest | None = None
    ) -> str:
        """Return the description of the calendar event."""
        return reference_object.description

    @classmethod
    def value_location(
        cls, reference_object: "PersonalEvent", request: HttpRequest | None = None
    ) -> str:
        """Return the location of the calendar event."""
        return reference_object.location

    @classmethod
    def value_meta(
        cls, reference_object: "PersonalEvent", request: HttpRequest | None = None
    ) -> dict[str, any]:
        """Get the meta of the event."""

        return {
            "id": reference_object.id,
            "owner": {
                "id": reference_object.owner.pk,
                "full_name": reference_object.owner.full_name,
            },
            "persons": [
                {
                    "id": p.pk,
                    "full_name": p.full_name,
                }
                for p in reference_object.persons.all()
            ],
            "groups": [
                {"id": g.pk, "name": g.name, "short_name": g.short_name}
                for g in reference_object.groups.all()
            ],
            "description": reference_object.description,
            "recurrences": str(reference_object.recurrences),
            "can_edit": request.user.has_perm("core.edit_personal_event_rule", reference_object),
            "can_delete": request.user.has_perm(
                "core.delete_personal_event_rule", reference_object
            ),
        }

    @classmethod
    def get_objects(
        cls, request: HttpRequest | None = None, params: dict[str, any] | None = None
    ) -> QuerySet:
        qs = super().get_objects(request=request, params=params)
        if request:
            qs = qs.filter(
                Q(owner=request.user.person)
                | Q(persons=request.user.person)
                | Q(groups__members=request.user.person)
            ).distinct()
        return qs


class Organisation(ExtensibleModel):
    name = models.CharField(verbose_name=_("Name"), max_length=255)
    email = models.CharField(verbose_name=_("Email"), max_length=255)

    related_group = models.ForeignKey(
        Group, on_delete=models.CASCADE, verbose_name=_("Related group")
    )

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name = _("Organisation")
        verbose_name_plural = _("Organisations")
