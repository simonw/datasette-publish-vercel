# datasette-publish-now

[![PyPI](https://img.shields.io/pypi/v/datasette-publish-now.svg)](https://pypi.org/project/datasette-publish-now/)
[![GitHub changelog](https://img.shields.io/github/v/release/simonw/datasette-publish-now?include_prereleases&label=changelog)](https://github.com/simonw/datasette-publish-now/releases)
[![CircleCI](https://circleci.com/gh/simonw/datasette-publish-now.svg?style=svg)](https://circleci.com/gh/simonw/datasette-publish-now)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-publish-now/blob/master/LICENSE)

Datasette plugin for publishing data using [Vercel](https://vercel.com/).

## Installation

Install this plugin in the same environment as Datasette.

    $ pip install datasette-publish-now

## Usage

First, install the Vercel CLI tool by [following their instructions](https://vercel.com/download).

Run `now login` to login to (or create) an account.

Now you can use `datasette publish now` to publish your data:

    datasette publish now my-database.db --project=my-database

The `--project` argument is required - it specifies the project name that should be used for your deployment. This will be used as part of the deployment's URL.

### Other options

* `--no-prod` deploys to the project without updating the "production" URL alias to point to that new deployment. Without that option all deploys go directly to production.
* `--debug` enables the Now CLI debug output
* `--token` allows you to pass a Now authentication token, rather than needing to first run `now login` to configure the tool
* `--public` runs `now --public` to publish the application source code at `/_src` e.g. https://datasette-public.now.sh/_src and make recent logs visible at `/_logs` e.g. https://datasette-public.now.sh/_logs
* `--generate-dir` - by default this tool generates a new Now app in a temporary directory, deploys it and then deletes the directory. Use `--generate-dir=my-app` to output the generated application files to a new directory of your choice instead. You can then deploy it by running `now` in that directory.

### Full help

**Warning:** Some of these options are not yet implemented by this plugin. In particular, the following do not yet work:

* `--extra-options`
* `--static`
* `--plugin-secret`
* `--version-note`

```
$ datasette publish now --help

Usage: datasette publish now [OPTIONS] [FILES]...

Options:
  -m, --metadata FILENAME         Path to JSON/YAML file containing metadata to publish
  --extra-options TEXT            Extra options to pass to datasette serve
  --branch TEXT                   Install datasette from a GitHub branch e.g. master
  --template-dir DIRECTORY        Path to directory containing custom templates
  --plugins-dir DIRECTORY         Path to directory containing custom plugins
  --static MOUNT:DIRECTORY        Serve static files from this directory at /MOUNT/...
  --install TEXT                  Additional packages (e.g. plugins) to install
  --plugin-secret <TEXT TEXT TEXT>...
                                  Secrets to pass to plugins, e.g. --plugin-secret
                                  datasette-auth-github client_id xxx

  --version-note TEXT             Additional note to show on /-/versions
  --secret TEXT                   Secret used for signing secure values, such as signed
                                  cookies

  --title TEXT                    Title for metadata
  --license TEXT                  License label for metadata
  --license_url TEXT              License URL for metadata
  --source TEXT                   Source label for metadata
  --source_url TEXT               Source URL for metadata
  --about TEXT                    About label for metadata
  --about_url TEXT                About URL for metadata
  --token TEXT                    Auth token to use for deploy
  --project PROJECT               Vercel project name to use  [required]
  --no-prod                       Don't deploy directly to production
  --debug                         Enable Now CLI debug output
  --public                        Publish source with Now CLI --public
  --generate-dir DIRECTORY        Output generated application files here
  --help                          Show this message and exit.
```
