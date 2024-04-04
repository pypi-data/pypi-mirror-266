from django.conf import settings
from django.utils import translation

import graphene

from ..models import CustomMenu
from ..util.core_helpers import get_site_preferences
from ..util.frontend_helpers import get_language_cookie
from .custom_menu import CustomMenuType
from .site_preferences import SitePreferencesType


class LanguageType(graphene.ObjectType):
    code = graphene.String(required=True)
    name = graphene.String(required=True)
    name_local = graphene.String(required=True)
    name_translated = graphene.String(required=True)
    bidi = graphene.Boolean(required=True)
    cookie = graphene.String(required=True)


class SystemPropertiesType(graphene.ObjectType):
    current_language = graphene.String(required=True)
    default_language = graphene.Field(LanguageType)
    available_languages = graphene.List(LanguageType)
    site_preferences = graphene.Field(SitePreferencesType)
    custom_menu_by_name = graphene.Field(CustomMenuType)

    def resolve_current_language(parent, info, **kwargs):
        return info.context.LANGUAGE_CODE

    @staticmethod
    def resolve_default_language(root, info, **kwargs):
        code = settings.LANGUAGE_CODE
        return translation.get_language_info(code) | {"cookie": get_language_cookie(code)}

    def resolve_available_languages(parent, info, **kwargs):
        return [
            translation.get_language_info(code) | {"cookie": get_language_cookie(code)}
            for code, name in settings.LANGUAGES
        ]

    def resolve_site_preferences(root, info, **kwargs):
        return get_site_preferences()

    def resolve_custom_menu_by_name(root, info, name, **kwargs):
        return CustomMenu.get_default(name)
