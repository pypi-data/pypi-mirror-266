import logging
from typing import Any, Dict, Optional
from urllib.parse import urlsplit, unquote, urlunsplit

from django import template, urls
from django.urls import Resolver404, resolve, reverse
from django.utils.translation import override

register = template.Library()

logger = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def translate_url(context: Dict[str, Any], language: Optional[str]) -> str:
    """
    Given the context of the current page, try to get its translated version in
    the `language` (either by i18n_patterns or by translated regex).
    Return the original URL if no translated version is found.

    Usage:
        {% translate_url 'en' %}
    """
    request = context["request"]

    # set session's iteration to avoid circular calls
    try:
        if hasattr(request.session, f"translated_iter_{language}"):
            if getattr(request.session, f"translated_iter_{language}") > 0:
                return getattr(request.session, f"translated_url_{language}")
        setattr(request.session, f"translated_iter_{language}", 1)
    except Exception as err:
        raise Exception(f"Avoid circular execution! [{err}]")

    if hasattr(request.session, f"translated_url_{language}"):
        logger.debug(
            f"session has translated_url_{language}: {getattr(request.session, f'translated_url_{language}')}"
        )
        return getattr(request.session, f"translated_url_{language}")
    url = request.build_absolute_uri()
    try:
        parsed = urlsplit(url)
        match = resolve(unquote(parsed.path))
    except Resolver404:
        pass
    else:
        with override(language):
            try:
                view = match.func(request, **match.kwargs)
                if hasattr(view, "url"):
                    translated_url = urlunsplit(
                        (
                            parsed.scheme,
                            parsed.netloc,
                            view.url,
                            parsed.query,
                            parsed.fragment,
                        )
                    )
                else:
                    view_url = urlunsplit(
                        (
                            parsed.scheme,
                            parsed.netloc,
                            reverse(
                                match.url_name, args=match.args, kwargs=match.kwargs
                            ),
                            parsed.query,
                            parsed.fragment,
                        )
                    )
                    translated_url = urls.translate_url(view_url, language)
                setattr(request.session, f"translated_url_{language}", translated_url)
                return translated_url
            except Exception as err:
                logger.debug(f"Translate url exception: [{err}]")
                pass

    translated_url = urls.translate_url(url, language)
    setattr(request.session, f"translated_url_{language}", translated_url)
    return translated_url
