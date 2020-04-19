from datasette import hookimpl
from datasette.publish.common import (
    add_common_publish_arguments_and_options,
    fail_if_publish_binary_not_installed,
)
from datasette.utils import temporary_docker_directory
from subprocess import run
import click
import json
import os
import re
import shutil

INDEX_PY = """
from datasette.app import Datasette
import json


metadata = dict()
try:
    metadata = json.load(open("metadata.json"))
except Exception:
    pass

app = Datasette([], {database_files}, metadata=metadata{extras}).app()
""".strip()

project_name_re = re.compile(r"^[a-z0-9][a-z0-9-]{1,51}$")


class ProjectName(click.ParamType):
    name = "project"

    def convert(self, value, param, ctx):
        if not project_name_re.match(value):
            self.fail(
                "Project name must be alphanumeric, max 52 chars, cannot begin with a hyphen"
            )
        return value


@hookimpl
def publish_subcommand(publish):
    @publish.command()
    @add_common_publish_arguments_and_options
    @click.option("--token", help="Auth token to use for deploy")
    @click.option(
        "--project",
        type=ProjectName(),
        help="Zeit Now project name to use",
        required=True,
    )
    @click.option(
        "--no-prod", is_flag=True, help="Don't deploy directly to production",
    )
    @click.option(
        "--debug", is_flag=True, help="Enable Now CLI debug output",
    )
    @click.option(
        "--public", is_flag=True, help="Publish source with Now CLI --public",
    )
    @click.option(
        "--generate-dir",
        type=click.Path(dir_okay=True, file_okay=False),
        help="Output generated application files here",
    )
    def now2(
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
        title,
        license,
        license_url,
        source,
        source_url,
        about,
        about_url,
        token,
        project,
        no_prod,
        debug,
        public,
        generate_dir,
    ):
        fail_if_publish_binary_not_installed(
            "now", "Zeit Now", "https://zeit.co/download"
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
            extra_metadata,
            port=8080,
        ):
            # We don't actually want the Dockerfile
            os.remove("Dockerfile")
            open("now.json", "w").write(
                json.dumps(
                    {
                        "name": project,
                        "version": 2,
                        "builds": [{"src": "index.py", "use": "@now/python"}],
                        "routes": [{"src": "(.*)", "dest": "index.py"}],
                    },
                    indent=4,
                )
            )
            extras = []
            if template_dir:
                extras.append('template_dir="{}"'.format(template_dir))
            if plugins_dir:
                extras.append('plugins_dir="{}"'.format(plugins_dir))

            open("index.py", "w").write(
                INDEX_PY.format(
                    database_files=json.dumps([os.path.split(f)[-1] for f in files]),
                    extras=", {}".format(", ".join(extras)) if extras else "",
                )
            )
            datasette_install = "datasette"
            if branch:
                datasette_install = "https://github.com/simonw/datasette/archive/{}.zip".format(
                    branch
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
                click.echo("To deploy using Zeit Now, run the following:")
                click.echo("    cd {}".format(generate_dir), err=True)
                click.echo("    now --prod".format(generate_dir), err=True)
            else:
                # Run the deploy with now
                cmd = ["now", "--confirm", "--no-clipboard"]
                if debug:
                    cmd.append("--debug")
                if not no_prod:
                    cmd.append("--prod")
                if public:
                    cmd.append("--public")
                if token:
                    cmd.extend(["--token", token])
                run(cmd)
