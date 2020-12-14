from click.testing import CliRunner
from datasette import cli
from unittest import mock
import os
import pathlib
import pytest
import re
import subprocess
import textwrap


@mock.patch("shutil.which")
def test_publish_vercel_requires_vercel_cli(mock_which):
    mock_which.return_value = False
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.db", "w").write("data")
        result = runner.invoke(
            cli.cli, ["publish", "vercel", "test.db", "--project", "foo"]
        )
        assert result.exit_code == 1
        assert "Publishing to Vercel requires vercel to be installed" in result.output


@mock.patch("shutil.which")
def test_publish_vercel_requires_project(mock_which):
    mock_which.return_value = True
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.db", "w").write("data")
        result = runner.invoke(cli.cli, ["publish", "vercel", "test.db"])
        assert result.exit_code == 2
        assert "Missing option '--project'" in result.output


@mock.patch("shutil.which")
@mock.patch("datasette_publish_vercel.run")
def test_publish_vercel(mock_run, mock_which):
    mock_which.return_value = True
    mock_run.return_value = mock.Mock(0)
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.db", "w").write("data")
        result = runner.invoke(
            cli.cli,
            ["publish", "vercel", "test.db", "--project", "foo", "--secret", "S"],
        )
        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mock.call(
                    [
                        "vercel",
                        "--confirm",
                        "--no-clipboard",
                        "--prod",
                        "--env",
                        "DATASETTE_SECRET=S",
                    ]
                ),
            ]
        )


@mock.patch("shutil.which")
@mock.patch("datasette_publish_vercel.run")
def test_publish_vercel_public(mock_run, mock_which):
    mock_which.return_value = True
    mock_run.return_value = mock.Mock(0)
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.db", "w").write("data")
        result = runner.invoke(
            cli.cli,
            [
                "publish",
                "vercel",
                "test.db",
                "--project",
                "foo",
                "--public",
                "--secret",
                "S",
            ],
        )
        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mock.call(
                    [
                        "vercel",
                        "--confirm",
                        "--no-clipboard",
                        "--prod",
                        "--public",
                        "--env",
                        "DATASETTE_SECRET=S",
                    ]
                ),
            ]
        )


@mock.patch("shutil.which")
@mock.patch("datasette_publish_vercel.run")
def test_publish_vercel_token(mock_run, mock_which):
    mock_which.return_value = True
    mock_run.return_value = mock.Mock(0)
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.db", "w").write("data")
        result = runner.invoke(
            cli.cli,
            [
                "publish",
                "vercel",
                "test.db",
                "--project",
                "foo",
                "--token",
                "xyz",
                "--secret",
                "S",
            ],
        )
        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mock.call(
                    [
                        "vercel",
                        "--confirm",
                        "--no-clipboard",
                        "--prod",
                        "--token",
                        "xyz",
                        "--env",
                        "DATASETTE_SECRET=S",
                    ]
                ),
            ]
        )


@pytest.fixture(scope="session")
@mock.patch("shutil.which")
@mock.patch("datasette_publish_vercel.run")
def generated_app_dir(mock_run, mock_which, tmp_path_factory):
    appdir = os.path.join(tmp_path_factory.mktemp("generated-app"), "app")
    mock_which.return_value = True
    mock_run.return_value = mock.Mock(0)
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.db", "w").write("data")
        static_dir = pathlib.Path(".") / "static"
        static_dir.mkdir()
        (static_dir / "my.css").write_text("body { color: red }")
        result = runner.invoke(
            cli.cli,
            [
                "publish",
                "vercel",
                "test.db",
                "--project",
                "foo",
                "--public",
                "--static",
                "static:static",
                "--setting",
                "default_page_size",
                "10",
                "--setting",
                "sql_time_limit_ms",
                "2000",
                "--generate-dir",
                appdir,
            ],
        )
        assert result.exit_code == 0, result.output
        assert not mock_run.called
    return appdir


def test_publish_vercel_generate(generated_app_dir):
    # Test that the correct files were generated
    filenames = set(os.listdir(generated_app_dir))
    assert {
        "requirements.txt",
        "static",
        "index.py",
        "now.json",
        "test.db",
    } == filenames
    index_py = open(os.path.join(generated_app_dir, "index.py")).read()
    assert index_py.strip() == (
        textwrap.dedent(
            """
    from datasette.app import Datasette
    import json
    import pathlib

    static_mounts = [
        (static, str((pathlib.Path(".") / static).resolve()))
        for static in ["static"]
    ]

    metadata = dict()
    try:
        metadata = json.load(open("metadata.json"))
    except Exception:
        pass

    app = Datasette(
        [],
        ["test.db"],
        static_mounts=static_mounts,
        metadata=metadata,
        cors=True,
        config={"default_page_size": 10, "sql_time_limit_ms": 2000}
    ).app()
    """
        ).strip()
    )


def test_publish_vercel_static(generated_app_dir):
    assert (
        "body { color: red }"
        == (pathlib.Path(generated_app_dir) / "static" / "my.css").read_text()
    )


def test_publish_vercel_requirements(generated_app_dir):
    requirements = set(
        l.strip()
        for l in open(os.path.join(generated_app_dir, "requirements.txt")).readlines()
        if l.strip()
    )
    assert {"datasette", "pysqlite3-binary"} == requirements


def test_help_in_readme(request):
    # Ensure the --help output embedded in the README is up-to-date
    readme_path = pathlib.Path(__file__).parent.parent / "README.md"
    readme = readme_path.read_text()
    block_re = re.compile("```(.*)```", re.DOTALL)
    expected = block_re.search(readme).group(1).strip()
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["publish", "vercel", "--help"], terminal_width=88)
    actual = "$ datasette publish vercel --help\n\n{}".format(result.output)

    if request.config.getoption("--rewrite-readme"):
        readme_path.write_text(
            block_re.sub(
                "```\n{}```".format(actual).replace("Usage: cli", "Usage: datasette"),
                readme,
            )
        )
        return

    # actual has "Usage: cli package [OPTIONS] FILES"
    # because it doesn't know that cli will be aliased to datasette
    expected = expected.replace("Usage: datasette", "Usage: cli")
    assert (
        expected.strip() == actual.strip()
    ), "README out of date - try runnning: pytest --rewrite-readme"
