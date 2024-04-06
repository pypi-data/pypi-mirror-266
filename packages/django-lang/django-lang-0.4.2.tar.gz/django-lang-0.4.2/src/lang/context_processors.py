"""
Context processors for django-lang app
"""

from typing import Any, Dict

from django.conf import settings


def from_settings(request) -> Dict[str, Any]:
    return {
        "DEFAULT_LANGUAGE_CODE": getattr(settings, attr, None)
        for attr in ("LANGUAGE_CODE",)
    }
