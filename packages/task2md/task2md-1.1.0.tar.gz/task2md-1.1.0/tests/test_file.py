# -*- coding: utf-8 -*-

import os
import pathlib
from shutil import rmtree

from click.testing import CliRunner

from task2md import task2md


class TestFile:
    def get_output_content(self, output_path: str) -> str:
        file_out = pathlib.Path(output_path)
        with open(file_out) as f:
            return f.read()

    def test_file_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(task2md.cli, ["file", "--help"])
        assert result.exit_code == 0
        assert "file [OPTIONS]" in result.stdout

    def test_file_missing_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(task2md.cli, ["file"])
        assert result.exit_code == 2
        assert "Error: Missing option" in result.stdout

    def test_file_short_options_default_dir(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            task2md.cli,
            ["file", "-i", "tests/files/lint.yml"],
        )
        assert result.exit_code == 0
        assert "Task documentation generated: lint.md" in result.stdout
        output = self.get_output_content("lint.md")
        assert "tags:" in output
        assert "  - lint" in output
        assert " * :material-check-circle: Status: stable" in output
        assert " * :material-license: License: MIT" in output
        assert "| [`lint:all`](#lintall) " in output
        assert "| `IMAGE_HADOLINT` |" in output
        assert "| Default image for lint:docker task |" in output
        assert "| `hadolint/hadolint` |" in output
        assert "## :simple-task: lint:all" in output
        assert "[LINT] Linter" in output
        assert "Usage: task" in output
        assert "| Arguments | Description |" in output
        assert "| Fix files (optional, by default no) |" in output
        assert "| `MEX " in output
        assert "Notes:" in output
        assert "starting by dot" in output
        assert '!!! info "Requirements:' in output
        assert "    - yamllint or docker" in output
        os.remove("lint.md")

    def test_file_long_options_default_dir(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            task2md.cli,
            ["file", "--input", "tests/files/lint.yml"],
        )
        assert result.exit_code == 0
        assert "Task documentation generated: lint.md" in result.stdout
        output = self.get_output_content("lint.md")
        assert "| `IMAGE_HADOLINT` |" in output
        os.remove("lint.md")

    def test_file_dir_create_short_options(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            task2md.cli,
            ["file", "-i", "tests/files/lint.yml", "-d", ".tmp-not-exist"],
        )
        assert result.exit_code == 0
        assert "Task documentation generated: lint.md" in result.stdout
        assert os.path.exists(".tmp-not-exist/lint.md")
        output = self.get_output_content(".tmp-not-exist/lint.md")
        assert "| `IMAGE_HADOLINT` |" in output
        rmtree(".tmp-not-exist")

    def test_file_dir_create_long_options(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            task2md.cli,
            ["file", "--input", "tests/files/lint.yml", "--dir", ".tmp-not-exist"],
        )
        assert result.exit_code == 0
        assert "Task documentation generated: lint.md" in result.stdout
        assert os.path.exists(".tmp-not-exist/lint.md")
        output = self.get_output_content(".tmp-not-exist/lint.md")
        assert "| `IMAGE_HADOLINT` |" in output
        rmtree(".tmp-not-exist")

    def test_file_not_found(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            task2md.cli,
            ["file", "--input", "tests/files/not-exist.yml"],
        )
        assert result.exit_code == 2
        assert "File 'tests/files/not-exist.yml' does not exist" in result.stdout

    def test_file_wrong_file(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            task2md.cli,
            ["file", "--input", "/bin/sh"],
        )
        assert result.exit_code == 1
        assert "Error on reading file /bin/sh" in result.stdout

    def test_file_empty(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            task2md.cli,
            ["file", "-i", "tests/files/empty.yml"],
        )
        assert result.exit_code == 0
        assert "Task documentation generated: empty.md" in result.stdout
        os.remove("empty.md")
