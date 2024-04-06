# django-sites-extra [![PyPi license](https://img.shields.io/pypi/l/django-sites-extra.svg)](https://pypi.python.org/pypi/django-sites-extra)

[![PyPi status](https://img.shields.io/pypi/status/django-sites-extra.svg)](https://pypi.python.org/pypi/django-sites-extra)
[![PyPi version](https://img.shields.io/pypi/v/django-sites-extra.svg)](https://pypi.python.org/pypi/django-sites-extra)
[![PyPi python version](https://img.shields.io/pypi/pyversions/django-sites-extra.svg)](https://pypi.python.org/pypi/django-sites-extra)
[![PyPi downloads](https://img.shields.io/pypi/dm/django-sites-extra.svg)](https://pypi.python.org/pypi/django-sites-extra)
[![PyPi downloads](https://img.shields.io/pypi/dw/django-sites-extra.svg)](https://pypi.python.org/pypi/django-sites-extra)
[![PyPi downloads](https://img.shields.io/pypi/dd/django-sites-extra.svg)](https://pypi.python.org/pypi/django-sites-extra)

## GitHub ![GitHub release](https://img.shields.io/github/tag/DLRSP/django-sites-extra.svg) ![GitHub release](https://img.shields.io/github/release/DLRSP/django-sites-extra.svg)

## Test [![codecov.io](https://codecov.io/github/DLRSP/django-sites-extra/coverage.svg?branch=main)](https://codecov.io/github/DLRSP/django-sites-extra?branch=main) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/DLRSP/django-sites-extra/main.svg)](https://results.pre-commit.ci/latest/github/DLRSP/django-sites-extra/main) [![gitthub.com](https://github.com/DLRSP/django-sites-extra/actions/workflows/ci.yaml/badge.svg)](https://github.com/DLRSP/django-sites-extra/actions/workflows/ci.yaml)

## Check Demo Project
* Check the demo repo on [GitHub](https://github.com/DLRSP/example/tree/django-sites-extra)

## Requirements
-   Python 3.8+ supported.
-   Django 3.2+ supported.

## Setup
1. Install from **pip**:
    ```shell
    pip install django-sites-extra
    ```
2. Modify `settings.py` by adding the app to `INSTALLED_APPS`:
    ```python
    INSTALLED_APPS = [
        # ...
        "sites_extra",
        # ...
    ]
    ```
3. Execute Django's command `migrate` inside your project's root:
    ```shell
    python manage.py migrate
    Running migrations:
      Applying sites_extra.0001_initial... OK
    ```
4. Modify `settings.py` by adding the app's context processor to `TEMPLATES`:
   ```python
   TEMPLATES = [
       {
           # ...
           "OPTIONS": {
               "context_processors": [
                   # ...
                   "sites_extra.context_processors.info",
                   # ...
               ],
           },
       },
   ]
   ```
5. Optionally, but sugguested, the Django's Current Site middleware is enabled inside `settings.py`:
   ```python
   MIDDLEWARE = (
       # ...
       "django.contrib.sites.middleware.CurrentSiteMiddleware",
       # ...
   )
   ```
## Run Example Project

```shell
git clone --depth=50 --branch=django-sites-extra https://github.com/DLRSP/example.git DLRSP/example
cd DLRSP/example
python manage.py runserver
```

Now browser the app @ http://127.0.0.1:8000
