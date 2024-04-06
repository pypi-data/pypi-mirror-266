import flag
from django import template
from django.conf import settings
from django.utils import translation

register = template.Library()


@register.filter
def get_language_info_list_ex(request):
    """
    Sample result:

        [{'bidi': False,
        'code': 'en',
        'flag': '🇬🇧',
        'is_current': False,
        'name': 'English',
        'name_local': 'English',
        'name_translated': 'Inglese'},
        {'bidi': False,
        'code': 'it',
        'flag': '🇮🇹',
        'is_current': True,
        'name': 'Italian',
        'name_local': 'italiano',
        'name_translated': 'Italiano'},
        {'bidi': False,
        'code': 'es',
        'flag': '🇪🇸',
        'is_current': False,
        'name': 'Spanish',
        'name_local': 'español',
        'name_translated': 'Spagnolo'}]
    """
    data = []

    # From django.templatetags.i18n.GetLanguageInfoListNode
    def get_language_info(language):
        # ``language`` is either a language code string or a sequence
        # with the language code as its first item
        if len(language[0]) > 1:
            return translation.get_language_info(language[0])
        else:
            return translation.get_language_info(str(language))

    flag_map = {
        "en": "gb",
    }

    # Es: 'es'
    current_language = translation.get_language()

    # Es: [('en', 'Inglés'), ('it', 'Italiano'), ('es', 'Español')]
    # languages = [(k, translation.gettext(v)) for k, v in settings.LANGUAGES]
    for language in settings.LANGUAGES:
        # Es: {'bidi': False, 'code': 'es', 'name': 'Spanish',
        #      'name_local': 'español', 'name_translated': 'Español'}
        info = get_language_info(language)

        code = info["code"]
        info["is_current"] = code == current_language

        # This requires emoji-country-flag Python package
        info["flag"] = flag.flag(flag_map.get(code, code))
        data.append(info)

    return data
