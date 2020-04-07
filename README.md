# datasette-publish-now

[![PyPI](https://img.shields.io/pypi/v/datasette-publish-now.svg)](https://pypi.org/project/datasette-publish-now/)
[![CircleCI](https://circleci.com/gh/simonw/datasette-publish-now.svg?style=svg)](https://circleci.com/gh/simonw/datasette-publish-now)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-publish-now/blob/master/LICENSE)

Datasette plugin for publishing data using [Zeit Now](https://now.io/).

## Installation

Install this plugin in the same environment as Datasette.

    $ pip install datasette-publish-now

## Usage

First, install the Zeit Now CLI tool by [following their instructions](https://zeit.co/download).

Run `now login` to login to (or create) an account.

Now you can use `datasette publish now` to publish your data:

    datasette publish now2 my-database.db --project=my-database

The `--project` argument is required - it specifies the project name that should be used for your deployment. This will be used as part of the deployment's URL.

### Other options

* `--no-prod` deploys to the project without updating the "production" URL alias to point to that new deployment. Without that option all deploys go directly to production.
* `--debug` enables the Now CLI debug output
* `--token` allows you to pass a Now authentication token, rather than needing to first run `now login' to configure the tool

### Full help

**Warning:** Some of these options are not yet implemented in the alpha version of this plugin. In particular, the following do not yet work:

* `--extra-options`
* `--static`
* `--plugin-secret`
* `--version-note`

```
$ datasette publish now2 --help
Usage: datasette publish now2 [OPTIONS] [FILES]...

Options:
  -m, --metadata FILENAME         Path to JSON/YAML file containing metadata
                                  to publish

  --extra-options TEXT            Extra options to pass to datasette serve
  --branch TEXT                   Install datasette from a GitHub branch e.g.
                                  master

  --template-dir DIRECTORY        Path to directory containing custom
                                  templates

  --plugins-dir DIRECTORY         Path to directory containing custom plugins
  --static MOUNT:DIRECTORY        Serve static files from this directory at
                                  /MOUNT/...

  --install TEXT                  Additional packages (e.g. plugins) to
                                  install

  --plugin-secret <TEXT TEXT TEXT>...
                                  Secrets to pass to plugins, e.g. --plugin-
                                  secret datasette-auth-github client_id xxx

  --version-note TEXT             Additional note to show on /-/versions
  --title TEXT                    Title for metadata
  --license TEXT                  License label for metadata
  --license_url TEXT              License URL for metadata
  --source TEXT                   Source label for metadata
  --source_url TEXT               Source URL for metadata
  --about TEXT                    About label for metadata
  --about_url TEXT                About URL for metadata
  --token TEXT                    Auth token to use for deploy
  --project PROJECT               Zeit Now project name to use  [required]
  --no-prod                       Don't deploy directly to production
  --debug                         Enable Now CLI debug output
  --help                          Show this message and exit.
```
