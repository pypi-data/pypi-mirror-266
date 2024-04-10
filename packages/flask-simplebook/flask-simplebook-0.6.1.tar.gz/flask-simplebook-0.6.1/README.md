# flask-simplebook

This is the flask companion application to the SimpleBook MediaWiki extension.

It handles all the administration of pdf creation.  To that end, it is comprised of
two parts:

* A flask webserver to communicate with mediawiki
* A rq worker task to manage mw2pdf

# Installation

## Pre-requisistes

The API uses [redis](https://redis.io/) and expects you to have a redis server running on `localhost:6379`.
Install through whatever means is best for your organization, but on debian based systems, installing
via apt and starting as part of services is sufficient:

```
$ apt install redis
```

## Installing from pypi

From a directory where you want to host the project, install via pipenv:

```
$ pipenv install flask-simplebook
$ pipenv install gunicorn
```

## Configuring

Configuration is done via environment variables.  The following are available:

* `SIMPLE_BOOK_DATA_DIR` - The directory where created pdfs should be stored
* `SIMPLE_BOOK_FONT` - An optional font location on disk for the title page fonts. **Note:** Fonts for
  the wiki pages are handled by the css (and webfonts) configured in mediawiki.  This only handles
  fonts for the title page and headers of the pages.  SimpleBook ships with the free Roboto and SourceCodepro
  fonts, and so proprietary and other fonts need to be managed by the sysadmin
* `SIMPLE_BOOK_LOGO` - An optional logo for the title page of the books.  Should point to a place on
  disk that can be accessed by mw2pdf

## Running

Start the flask server:

```
$ pipenv run gunicorn --bind 127.0.0.1:3333 simplebook.wsgi:app
```

And also the rq worker:

```
$ pipenv run rq worker
```

# Developing

When running in development, install from the local Pipfile:

```
$ cd flask-simplebook
$ pipenv install
```

And then start as above in two terminals:

```
$ pipenv run gunicorn --bind 127.0.0.1:3333 simplebook.wsgi:app
$ pipenv run rq worker
```

You can also install via to another directory via `pipenv install -e`
