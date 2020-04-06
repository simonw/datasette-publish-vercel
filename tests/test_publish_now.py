from click.testing import CliRunner
from datasette import cli
from unittest import mock


@mock.patch("shutil.which")
def test_publish_now_requires_now_cli(mock_which):
    mock_which.return_value = False
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("test.db", "w").write("data")
        result = runner.invoke(cli.cli, ["publish", "now2", "test.db"])
        assert result.exit_code == 1
        assert "Publishing to Zeit Now requires now to be installed" in result.output
