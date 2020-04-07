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
