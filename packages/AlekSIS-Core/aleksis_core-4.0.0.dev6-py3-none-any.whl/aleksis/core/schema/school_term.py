from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext as _

from graphene_django import DjangoObjectType

from ..models import SchoolTerm
from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    DjangoFilterMixin,
    PermissionsTypeMixin,
)


class SchoolTermType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = SchoolTerm
        filter_fields = {
            "name": ["icontains", "exact"],
            "date_start": ["exact", "lt", "lte", "gt", "gte"],
            "date_end": ["exact", "lt", "lte", "gt", "gte"],
        }
        fields = ("id", "name", "date_start", "date_end")

    @classmethod
    def get_queryset(cls, queryset, info, **kwargs):
        if not info.context.user.has_perm("core.view_schoolterm_rule"):
            raise PermissionDenied

        return queryset


class SchoolTermBatchCreateMutation(BaseBatchCreateMutation):
    class Meta:
        model = SchoolTerm
        permissions = ("core.create_school_term_rule",)
        only_fields = ("id", "name", "date_start", "date_end")

    @classmethod
    def validate(cls, root, info, input, inputs):  # noqa
        for input in inputs:  # noqa
            date_start = input.get("date_start")
            date_end = input.get("date_end")
            if date_end < date_start:
                raise ValidationError(_("The start date must be earlier than the end date."))

            qs = SchoolTerm.objects.within_dates(date_start, date_end)
            if qs.exists():
                raise ValidationError(
                    _("There is already a school term for this time or a part of this time.")
                )


class SchoolTermBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = SchoolTerm
        permissions = ("core.delete_school_term_rule",)


class SchoolTermBatchPatchMutation(BaseBatchPatchMutation):
    class Meta:
        model = SchoolTerm
        permissions = ("core.edit_school_term_rule",)
        only_fields = ("id", "name", "date_start", "date_end")
