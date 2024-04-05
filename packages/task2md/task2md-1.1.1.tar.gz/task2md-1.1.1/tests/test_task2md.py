# -*- coding: utf-8 -*-

from click.testing import CliRunner

from task2md import task2md


class TestTask2Md:
    def test_task2md_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(task2md.cli, ["--help"])
        assert result.exit_code == 0
        assert "[OPTIONS]" in result.stdout

    def test_task2md_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(task2md.cli, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.stdout
