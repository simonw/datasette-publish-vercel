from click.testing import CliRunner
from datasette import cli
from unittest import mock
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
