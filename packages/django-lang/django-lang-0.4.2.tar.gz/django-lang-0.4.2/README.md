# django-lang [![PyPi license](https://img.shields.io/pypi/l/django-lang.svg)](https://pypi.python.org/pypi/django-lang)

[![PyPi status](https://img.shields.io/pypi/status/django-lang.svg)](https://pypi.python.org/pypi/django-lang)
[![PyPi version](https://img.shields.io/pypi/v/django-lang.svg)](https://pypi.python.org/pypi/django-lang)
[![PyPi python version](https://img.shields.io/pypi/pyversions/django-lang.svg)](https://pypi.python.org/pypi/django-lang)
[![PyPi downloads](https://img.shields.io/pypi/dm/django-lang.svg)](https://pypi.python.org/pypi/django-lang)
[![PyPi downloads](https://img.shields.io/pypi/dw/django-lang.svg)](https://pypi.python.org/pypi/django-lang)
[![PyPi downloads](https://img.shields.io/pypi/dd/django-lang.svg)](https://pypi.python.org/pypi/django-lang)

## GitHub ![GitHub release](https://img.shields.io/github/tag/DLRSP/django-lang.svg) ![GitHub release](https://img.shields.io/github/release/DLRSP/django-lang.svg)

## Test [![codecov.io](https://codecov.io/github/DLRSP/django-lang/coverage.svg?branch=main)](https://codecov.io/github/DLRSP/django-lang?branch=main) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/DLRSP/django-lang/main.svg)](https://results.pre-commit.ci/latest/github/DLRSP/django-lang/main) [![gitthub.com](https://github.com/DLRSP/django-lang/actions/workflows/ci.yaml/badge.svg)](https://github.com/DLRSP/django-lang/actions/workflows/ci.yaml)

## Check Demo Project
* Check the demo repo on [GitHub](https://github.com/DLRSP/example/tree/django-lang)

## Requirements
-   Python 3.8+ supported.
-   Django 3.2+ supported.

## Setup
1. Install from **pip**:
    ```shell
    pip install django-lang
    ```
2. Modify `settings.py` by adding the app to `INSTALLED_APPS`:
    ```python
    INSTALLED_APPS = [
        # ...
        "lang",
        # ...
    ]
    ```
3. Modify `settings.py` by adding the app to `INSTALLED_APPS`:
    ``` python title="settings.py" hl_lines="12"
    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [os.path.join(PROJECT_DIR, "templates")],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "lang.context_processors.from_settings",
                ],
            },
        },
    ]
    ```
4. Modify your project's base template `base.html` to include language's switcher styles:
    ```html
    <head>
        ...
        <link rel="stylesheet" type="text/css" href="{% static 'lang/css/nav-link.css' %}">
        ...
    </head>
    ```
5. Modify your project's base template `base.html` to include attributes using `translate_url` template's tag:
    ```html
    <head>
        ...
        <meta name="language" content="{{ LANGUAGE_CODE }}" />
        {% include "hreflang.html" %}
        ...
    </head>
    ```
6. Modify your project's nav template `nav.html` to include language's switcher:
    ```html
    <nav class="navbar">
        ...
        <ul class="nav navbar-nav">
            {% include "nav-link.html" %}
        </ul>
        ...
    </nav>
    ```


## Run Example Project

```shell
git clone --depth=50 --branch=django-lang https://github.com/DLRSP/example.git DLRSP/example
cd DLRSP/example
python manage.py runserver
```

Now browser the app @ http://127.0.0.1:8000

## References

- [brainstorm.it](https://brainstorm.it/snippets/django-language-switching/) - Language's switching
- [hakibenita.com](https://hakibenita.com/django-multi-language-site-hreflang) - Url's translation for "hreflang" html's attributes
