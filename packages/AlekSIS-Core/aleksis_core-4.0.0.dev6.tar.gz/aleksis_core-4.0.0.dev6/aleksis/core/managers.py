from datetime import date
from typing import TYPE_CHECKING, Union

from django.apps import apps
from django.db.models import QuerySet
from django.db.models.manager import Manager

from calendarweek import CalendarWeek
from polymorphic.managers import PolymorphicManager, PolymorphicQuerySet

if TYPE_CHECKING:
    from .models import SchoolTerm


class AlekSISBaseManager(Manager):
    """Base manager for AlekSIS model customisation."""

    def unmanaged(self) -> QuerySet:
        """Get instances that are not managed by any particular app."""
        return super().get_queryset().filter(managed_by_app_label="")

    def managed_by_app(self, app_label: str) -> QuerySet:
        """Get instances managed by a particular app."""
        return super().get_queryset().filter(managed_by_app_label=app_label)

    def managed_and_unmanaged(self) -> QuerySet:
        """Get managed and unmanaged instances managed."""
        return super().get_queryset()

    def get_queryset(self) -> QuerySet:
        return self.unmanaged()


class AlekSISBaseManagerWithoutMigrations(AlekSISBaseManager):
    """AlekSISBaseManager for auto-generating managers just by query sets."""

    use_in_migrations = False


class DateRangeQuerySetMixin:
    """QuerySet with custom query methods for models with date ranges.

    Filterable fields: date_start, date_end
    """

    def within_dates(self, start: date, end: date):
        """Filter for all objects within a date range."""
        return self.filter(date_start__lte=end, date_end__gte=start)

    def in_week(self, wanted_week: CalendarWeek):
        """Filter for all objects within a calendar week."""
        return self.within_dates(wanted_week[0], wanted_week[6])

    def on_day(self, day: date):
        """Filter for all objects on a certain day."""
        return self.within_dates(day, day)


class SchoolTermQuerySet(QuerySet, DateRangeQuerySetMixin):
    """Custom query set for school terms."""


class SchoolTermRelatedQuerySet(QuerySet):
    """Custom query set for all models related to school terms."""

    def within_dates(self, start: date, end: date) -> "SchoolTermRelatedQuerySet":
        """Filter for all objects within a date range."""
        return self.filter(school_term__date_start__lte=end, school_term__date_end__gte=start)

    def in_week(self, wanted_week: CalendarWeek) -> "SchoolTermRelatedQuerySet":
        """Filter for all objects within a calendar week."""
        return self.within_dates(wanted_week[0], wanted_week[6])

    def on_day(self, day: date) -> "SchoolTermRelatedQuerySet":
        """Filter for all objects on a certain day."""
        return self.within_dates(day, day)

    def for_school_term(self, school_term: "SchoolTerm") -> "SchoolTermRelatedQuerySet":
        return self.filter(school_term=school_term)

    def for_current_school_term_or_all(self) -> "SchoolTermRelatedQuerySet":
        """Get all objects related to current school term.

        If there is no current school term, it will return all objects.
        """
        from aleksis.core.models import SchoolTerm

        current_school_term = SchoolTerm.current
        if current_school_term:
            return self.for_school_term(current_school_term)
        else:
            return self

    def for_current_school_term_or_none(self) -> Union["SchoolTermRelatedQuerySet", None]:
        """Get all objects related to current school term.

        If there is no current school term, it will return `None`.
        """
        from aleksis.core.models import SchoolTerm

        current_school_term = SchoolTerm.current
        if current_school_term:
            return self.for_school_term(current_school_term)
        else:
            return None


class GroupManager(AlekSISBaseManagerWithoutMigrations):
    """Manager adding specific methods to groups."""

    def get_queryset(self):
        """Ensure all related data is loaded as well."""
        return Manager.get_queryset(self).select_related("school_term")


class GroupQuerySet(SchoolTermRelatedQuerySet):
    pass


class UninstallRenitentPolymorphicManager(PolymorphicManager):
    """A custom manager for django-polymorphic that filters out submodels of unavailable apps."""

    def get_queryset(self):
        DashboardWidget = apps.get_model("core", "DashboardWidget")
        if self.model is DashboardWidget:
            return super().get_queryset().instance_of(*self.model.__subclasses__())
        else:
            # Called on subclasses
            return super().get_queryset()


class InstalledWidgetsDashboardWidgetOrderManager(Manager):
    """A manager that only returns DashboardWidgetOrder objects with an existing widget."""

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get the DashboardWidget model class without importing it to avoid a circular import
        DashboardWidget = queryset.model.widget.field.related_model  # noqa
        dashboard_widget_pks = DashboardWidget.objects.all().values("id")

        # [obj["id"] for obj in list(Person.objects.all().values("id"))]
        return super().get_queryset().filter(widget_id__in=dashboard_widget_pks)


class PolymorphicBaseManager(AlekSISBaseManagerWithoutMigrations, PolymorphicManager):
    """Default manager for extensible, polymorphic models."""


class HolidayQuerySet(DateRangeQuerySetMixin, PolymorphicQuerySet):
    """QuerySet with custom query methods for holidays."""

    def get_all_days(self) -> list[date]:
        """Get all days included in the selected holidays."""
        holiday_days = []
        for holiday in self:
            holiday_days += list(holiday.get_days())
        return holiday_days
