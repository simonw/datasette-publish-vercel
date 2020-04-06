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

INDEX_PY = """
from datasette.app import Datasette

app = Datasette([], {database_files}{extras}).app()
""".strip()


@hookimpl
def publish_subcommand(publish):
    @publish.command()
    @add_common_publish_arguments_and_options
    @click.option(
        "-n",
        "--name",
        default="datasette",
        help="Application name to use when deploying",
    )
    @click.option("--token", help="Auth token to use for deploy")
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
        name,
        token,
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
            name or "datasette-now-v2",
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
                "\n".join([datasette_install] + list(install))
            )
            run(["now"])
