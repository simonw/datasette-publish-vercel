from click.testing import CliRunner
from datasette import cli
from unittest import mock
import os
import pathlib
import re
import subprocess


@mock.patch("shutil.which")
def test_publish_now_requires_now_cli(mock_which):
    mock_which.return_value = False
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.db", "w").write("data")
        result = runner.invoke(
            cli.cli, ["publish", "now2", "test.db", "--project", "foo"]
        )
        assert result.exit_code == 1
        assert "Publishing to Zeit Now requires now to be installed" in result.output


@mock.patch("shutil.which")
def test_publish_now_requires_project(mock_which):
    mock_which.return_value = True
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.db", "w").write("data")
        result = runner.invoke(cli.cli, ["publish", "now2", "test.db"])
        assert result.exit_code == 2
        assert "Missing option '--project'" in result.output


@mock.patch("shutil.which")
@mock.patch("datasette_publish_now.run")
def test_publish_now(mock_run, mock_which):
    mock_which.return_value = True
    mock_run.return_value = mock.Mock(0)
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.db", "w").write("data")
        result = runner.invoke(
            cli.cli, ["publish", "now2", "test.db", "--project", "foo"],
        )
        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [mock.call(["now", "--confirm", "--no-clipboard", "--prod"]),]
        )


@mock.patch("shutil.which")
@mock.patch("datasette_publish_now.run")
def test_publish_now_public(mock_run, mock_which):
    mock_which.return_value = True
    mock_run.return_value = mock.Mock(0)
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.db", "w").write("data")
        result = runner.invoke(
            cli.cli, ["publish", "now2", "test.db", "--project", "foo", "--public"],
        )
        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [mock.call(["now", "--confirm", "--no-clipboard", "--prod", "--public"]),]
        )


@mock.patch("shutil.which")
@mock.patch("datasette_publish_now.run")
def test_publish_now_generate(mock_run, mock_which, tmpdir):
    mock_which.return_value = True
    mock_run.return_value = mock.Mock(0)
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.db", "w").write("data")
        result = runner.invoke(
            cli.cli,
            [
                "publish",
                "now2",
                "test.db",
                "--project",
                "foo",
                "--public",
                "--generate-dir",
                tmpdir / "out",
            ],
        )
        assert result.exit_code == 0
        assert not mock_run.called
    # Test that the correct files were generated
    filenames = set(os.listdir(tmpdir / "out"))
    assert {"requirements.txt", "index.py", "now.json", "test.db"} == filenames


def test_help_in_readme(request):
    # Ensure the --help output embedded in the README is up-to-date
    readme_path = pathlib.Path(__file__).parent.parent / "README.md"
    readme = readme_path.read_text()
    block_re = re.compile("```(.*)```", re.DOTALL)
    expected = block_re.search(readme).group(1).strip()
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["publish", "now2", "--help"], terminal_width=88)
    actual = "$ datasette publish now2 --help\n\n{}".format(result.output)

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
