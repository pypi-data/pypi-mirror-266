from graphene_django import DjangoObjectType
from guardian.shortcuts import get_objects_for_user

from ..models import GroupType
from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    DjangoFilterMixin,
    PermissionsTypeMixin,
)


class GroupTypeType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = GroupType
        fields = [
            "id",
            "name",
            "description",
        ]

    @classmethod
    def get_queryset(cls, queryset, info):
        return get_objects_for_user(info.context.user, "core.view_grouptype", GroupType)


class GroupTypeBatchCreateMutation(BaseBatchCreateMutation):
    class Meta:
        model = GroupType
        permissions = ("core.create_grouptype_rule",)
        only_fields = (
            "name",
            "description",
        )


class GroupTypeBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = GroupType
        permissions = ("core.delete_grouptype_rule",)


class GroupTypeBatchPatchMutation(BaseBatchPatchMutation):
    class Meta:
        model = GroupType
        permissions = ("core.change_grouptype_rule",)
        only_fields = (
            "id",
            "name",
            "description",
        )
