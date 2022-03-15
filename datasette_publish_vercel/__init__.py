from datasette import hookimpl
from datasette.publish.common import (
    add_common_publish_arguments_and_options,
    fail_if_publish_binary_not_installed,
)
from datasette.utils import (
    temporary_docker_directory,
    value_as_boolean,
    ValueAsBooleanError,
)
from subprocess import run
import click
from click.types import CompositeParamType
import json
import os
import pathlib
import re
import shutil

INDEX_PY = """
import asyncio
from datasette.app import Datasette
import json
import pathlib
import os

static_mounts = [
    (static, str((pathlib.Path(".") / static).resolve()))
    for static in {statics}
]

metadata = dict()
try:
    metadata = json.load(open("metadata.json"))
except Exception:
    pass

secret = os.environ.get("DATASETTE_SECRET")

ds = Datasette(
    [],
    {database_files},
    static_mounts=static_mounts,
    metadata=metadata{extras},
    secret=secret,
    cors=True,
    settings={settings}
)
asyncio.run(ds.invoke_startup())
app = ds.app()
""".strip()

project_name_re = re.compile(r"^[a-z0-9][a-z0-9-]{1,51}$")


class Setting(CompositeParamType):
    name = "setting"
    arity = 2

    def convert(self, config, param, ctx):
        from datasette.app import DEFAULT_SETTINGS

        name, value = config
        if name not in DEFAULT_SETTINGS:
            self.fail(
                f"{name} is not a valid option (--help-config to see all)",
                param,
                ctx,
            )
            return
        # Type checking
        default = DEFAULT_SETTINGS[name]
        if isinstance(default, bool):
            try:
                return name, value_as_boolean(value)
            except ValueAsBooleanError:
                self.fail(f'"{name}" should be on/off/true/false/1/0', param, ctx)
                return
        elif isinstance(default, int):
            if not value.isdigit():
                self.fail(f'"{name}" should be an integer', param, ctx)
                return
            return name, int(value)
        elif isinstance(default, str):
            return name, value
        else:
            # Should never happen:
            self.fail("Invalid option")


class ProjectName(click.ParamType):
    name = "project"

    def convert(self, value, param, ctx):
        if not project_name_re.match(value):
            self.fail(
                "Project name must be lowercase, alphanumeric, max 52 chars, cannot begin with a hyphen"
            )
        return value


def add_vercel_options(cmd):
    for decorator in reversed(
        (
            click.option("--token", help="Auth token to use for deploy"),
            click.option(
                "--project",
                type=ProjectName(),
                help="Vercel project name to use",
                required=True,
            ),
            click.option(
                "--scope",
                help="Optional Vercel scope (e.g. a team name)",
            ),
            click.option(
                "--no-prod",
                is_flag=True,
                help="Don't deploy directly to production",
            ),
            click.option(
                "--debug",
                is_flag=True,
                help="Enable Vercel CLI debug output",
            ),
            click.option(
                "--public",
                is_flag=True,
                help="Publish source with Vercel CLI --public",
            ),
            click.option(
                "--generate-dir",
                type=click.Path(dir_okay=True, file_okay=False),
                help="Output generated application files and stop without deploying",
            ),
            click.option(
                "--generate-vercel-json",
                is_flag=True,
                help="Output generated vercel.json file and stop without deploying",
            ),
            click.option(
                "--vercel-json",
                type=click.File(),
                help="Custom vercel.json file to use instead of generating one",
            ),
            click.option(
                "--setting",
                "settings",
                type=Setting(),
                help="Setting, see docs.datasette.io/en/stable/settings.html",
                multiple=True,
            ),
        )
    ):
        cmd = decorator(cmd)
    return cmd


def _publish_vercel(
    files,
    metadata,
    extra_options,
    branch,
    template_dir,
    plugins_dir,
    static,
    install,
    plugin_secret,
    version_note,
    secret,
    title,
    license,
    license_url,
    source,
    source_url,
    about,
    about_url,
    token,
    project,
    scope,
    no_prod,
    debug,
    public,
    generate_dir,
    generate_vercel_json,
    vercel_json,
    settings,
):
    if vercel_json and generate_vercel_json:
        raise click.ClickException(
            "Cannot use both --vercel-json and --generate-vercel-json"
        )
    fail_if_publish_binary_not_installed(
        "vercel", "Vercel", "https://vercel.com/download"
    )
    extra_metadata = {
        "title": title,
        "license": license,
        "license_url": license_url,
        "source": source,
        "source_url": source_url,
        "about": about,
        "about_url": about_url,
    }

    if generate_dir:
        generate_dir = str(pathlib.Path(generate_dir).resolve())

    vercel_json_content = json.dumps(
        {
            "name": project,
            "version": 2,
            "builds": [{"src": "index.py", "use": "@vercel/python"}],
            "routes": [{"src": "(.*)", "dest": "index.py"}],
        },
        indent=4,
    )
    if generate_vercel_json:
        click.echo(vercel_json_content)
        return

    if vercel_json:
        vercel_json_content = vercel_json.read()
        try:
            json.loads(vercel_json_content)
        except ValueError:
            raise click.ClickException("--vercel-json contents must be valid JSON")

    with temporary_docker_directory(
        files,
        "datasette-now-v2",
        metadata,
        extra_options,
        branch,
        template_dir,
        plugins_dir,
        static,
        install,
        False,
        version_note,
        secret,
        extra_metadata,
        port=8080,
    ):
        # We don't actually want the Dockerfile
        os.remove("Dockerfile")
        open("vercel.json", "w").write(vercel_json_content)
        extras = []
        if template_dir:
            extras.append('template_dir="templates"')
        if plugins_dir:
            extras.append('plugins_dir="plugins"')

        statics = [item[0] for item in static]

        open("index.py", "w").write(
            INDEX_PY.format(
                database_files=json.dumps([os.path.split(f)[-1] for f in files]),
                extras=", {}".format(", ".join(extras)) if extras else "",
                statics=json.dumps(statics),
                settings=json.dumps(dict(settings) or {}),
            )
        )
        datasette_install = "datasette"
        if branch:
            datasette_install = (
                "https://github.com/simonw/datasette/archive/{}.zip".format(branch)
            )
        open("requirements.txt", "w").write(
            "\n".join([datasette_install, "pysqlite3-binary"] + list(install))
        )
        if generate_dir:
            # Copy these to the specified directory
            shutil.copytree(".", generate_dir)
            click.echo(
                "Your generated application files have been written to:", err=True
            )
            click.echo("    {}\n".format(generate_dir), err=True)
            click.echo("To deploy using Vercel, run the following:")
            click.echo("    cd {}".format(generate_dir), err=True)
            click.echo("    vercel --prod".format(generate_dir), err=True)
        else:
            # Run the deploy with Vercel
            cmd = ["vercel", "--confirm", "--no-clipboard"]
            if debug:
                cmd.append("--debug")
            if not no_prod:
                cmd.append("--prod")
            if public:
                cmd.append("--public")
            if token:
                cmd.extend(["--token", token])
            if scope:
                cmd.extend(["--scope", scope])
            # Add the secret
            cmd.extend(["--env", "DATASETTE_SECRET={}".format(secret)])
            run(cmd)


@hookimpl
def publish_subcommand(publish):
    @publish.command()
    @add_common_publish_arguments_and_options
    @add_vercel_options
    def vercel(*args, **kwargs):
        "Publish to https://vercel.com/"
        _publish_vercel(*args, **kwargs)

    @publish.command()
    @add_common_publish_arguments_and_options
    @add_vercel_options
    def now(*args, **kwargs):
        "Alias for 'datasette publish vercel'"
        _publish_vercel(*args, **kwargs)
