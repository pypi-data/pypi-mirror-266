# -*- coding: utf-8 -*-

import os
import pathlib
from shutil import rmtree

from click.testing import CliRunner

from task2md import task2md


class TestDir:
    def get_output_content(self, output_path: str) -> str:
        file_out = pathlib.Path(output_path)
        with open(file_out) as f:
            return f.read()

    def test_dir_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(task2md.cli, ["dir", "--help"])
        assert result.exit_code == 0
        assert "dir [OPTIONS]" in result.stdout

    def test_dir_missing_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(task2md.cli, ["dir"])
        assert result.exit_code == 2
        assert "Error: Missing option" in result.stdout

    def test_dir_short_options_default_dir(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            task2md.cli,
            ["dir", "-i", "tests/files"],
        )
        assert result.exit_code == 0
        assert "Task documentation generated: empty.md" in result.stdout
        assert "Task documentation generated: lint.md" in result.stdout
        assert "Index documentation generated: index.md" in result.stdout
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
        output_index = self.get_output_content("index.md")
        assert (
            "| [lint](lint) | A set of tasks to lint different types of files. "
            "| lint, docker, CI |" in output_index
        )
        assert "| [empty](empty) | - |  |" in output_index
        os.remove("empty.md")
        os.remove("lint.md")
        os.remove("index.md")

    def test_dir_long_options_default_dir(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            task2md.cli,
            ["dir", "--input", "tests/files"],
        )
        assert result.exit_code == 0
        assert "Task documentation generated: empty.md" in result.stdout
        assert "Task documentation generated: lint.md" in result.stdout
        assert "Index documentation generated: index.md" in result.stdout
        output = self.get_output_content("lint.md")
        assert "| `IMAGE_HADOLINT` |" in output
        os.remove("empty.md")
        os.remove("lint.md")
        os.remove("index.md")

    def test_dir_dir_create_short_options(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            task2md.cli,
            ["dir", "-i", "tests/files", "-d", ".tmp-not-exist"],
        )
        assert result.exit_code == 0
        assert "Task documentation generated: empty.md" in result.stdout
        assert "Task documentation generated: lint.md" in result.stdout
        assert "Index documentation generated: index.md" in result.stdout
        assert os.path.exists(".tmp-not-exist/lint.md")
        output = self.get_output_content(".tmp-not-exist/lint.md")
        assert "| `IMAGE_HADOLINT` |" in output
        rmtree(".tmp-not-exist")

    def test_dir_dir_create_long_options(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            task2md.cli,
            ["dir", "--input", "tests/files", "--dir", ".tmp-not-exist"],
        )
        assert result.exit_code == 0
        assert "Task documentation generated: empty.md" in result.stdout
        assert "Task documentation generated: lint.md" in result.stdout
        assert "Index documentation generated: index.md" in result.stdout
        assert os.path.exists(".tmp-not-exist/lint.md")
        output = self.get_output_content(".tmp-not-exist/lint.md")
        assert "| `IMAGE_HADOLINT` |" in output
        rmtree(".tmp-not-exist")

    def test_dir_not_found(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            task2md.cli,
            ["dir", "--input", "tests/not-exist"],
        )
        assert result.exit_code == 2
        assert "Directory 'tests/not-exist' does not exist" in result.stdout

    def test_dir_no_yml_file(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            task2md.cli,
            ["dir", "--input", "tests"],
        )
        assert result.exit_code == 0
        assert "No yaml file found in: tests" in result.stdout
