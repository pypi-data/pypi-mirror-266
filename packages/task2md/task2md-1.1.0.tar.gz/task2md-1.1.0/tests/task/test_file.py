# -*- coding: utf-8 -*-
# flake8: noqa

from task2md.template.file import File

HEADER_FULL = """
#
# @description: A set of tasks to lint different types of files.
# @tags: lint, docker, CI
# @authors: FX Soubirou <soubirou@yahoo.fr>, FXS <fxs@example.com>
# File :material-bookmark-check:/:material-bookmark-remove:
# @file-raw: https://gitlab.com/op_so/task/task-templates/-/raw/main/Taskfile.d/lint.yml
# @file-ui: https://gitlab.com/op_so/task/task-templates/-/blob/main/Taskfile.d/lint.yml
# @home: https://gitlab.com/op_so/task/task-templates
# @links: [pre-commit](https://pre-commit.com/)
# @license: MIT
# status: draft(:material-draw:), beta(:material-beta:),
#         stable(:material-check-circle:), deprecated(:material-delete:)
# @status: stable
# @deprecated-tasks:

"""

VARS4 = """

vars:
  IMAGE_HADOLINT: hadolint/hadolint  # Default image for lint:docker task
  IMAGE_YAMLINT: jfxs/ansible
  IMAGE_VALE:  # Default image for # lint:vale task
  IMAGE_DEFAULT:

"""

VARS_HEADER = """
| Variables | Description | Default value |
| --------- | ----------- | ------------- |
"""

TASKS = """
tasks:
  all:
    desc: 'Linter for files, markdown, yaml extensions. Arguments: [FIX|F=y|Y] [MEX|M=\"#node_modules\"] (*)'
    summary: |
      [LINT] Linter for files.
      Usage: task lint:all [FIX|F=<y|Y>] [MEX|M='"#node_modules"']

      Arguments:
        FIX | F  Fix files (optional, by default no)
        MEX | M  Makdown exlude directories with single quotes example: MEX='"#node_modules" "#.node_cache"' (see: https://github.com/DavidAnson/markdownlint-cli2)

      Notes:
        - Only git versionned files are checked for generic files. Use MEX argument for Mardown files and .yamlint for YAML files to exclude.
        - Check git tracked files,
        - otherwise (empty git list), all files not in a directory starting by dot

      Requirements:
        - markdownlint-cli2 or docker
        - yamllint or docker
    silent: true

  file:
    desc: "Linter for files. Arguments: [FIX|F=y|Y] (*)"
    summary: |
      [LINT] Linter for files.
      Usage: task lint:file [FIX|F=<y|Y>]

      Arguments:
        FIX | F  Fix files (optional, by default no)

      Notes:
        - Check git tracked files,
        - otherwise (empty git list), all files not in a directory starting by dot
    silent: true

"""

TASKS_LIST_HEADER = """
| Tasks | Description |
| ----- | ----------- |
"""


class TestFile:
    def test_file_init(self) -> None:
        f = File(content=VARS4)
        assert f.content == VARS4
        assert f.yaml == {}
        assert f.global_variables == []
        assert f.parsed is False

    def test_file_error_yaml(self) -> None:
        error_yaml = """

           ::%XgD

        """
        f = File(content=error_yaml)
        f.parse()
        assert f.yaml == {}
        assert f.global_variables == []
        assert f.parsed is True

    def test_file_empty(self) -> None:
        empty = """

        """
        f = File(content=empty)
        f.parse()
        assert f.yaml == {}
        assert f.global_variables == []
        assert f.parsed is True

    def test_file_get_filename(self) -> None:
        f = File(content="", path="my_dir/lint.yml")
        assert f.get_filename() == "lint"
        assert f.parsed is False

    def test_file_get_filename_no_extension(self) -> None:
        f = File(content="", path="my_dir/lint")
        assert f.get_filename() == "lint"
        assert f.parsed is False

    def test_file_get_filename_no_dir(self) -> None:
        f = File(content="", path="lint.yml")
        assert f.get_filename() == "lint"
        assert f.parsed is False

    def test_file_header(self) -> None:
        f = File(content=HEADER_FULL, path="my_dir/lint.yml")
        f.parse()
        assert f.global_variables == []
        assert f.header.license == "MIT"
        assert (
            f.header.description == "A set of tasks to lint different types of files."
        )
        assert f.header.tags == ["lint", "docker", "CI"]
        assert f.parsed is True

    def test_file_vars_blank(self) -> None:
        vars1 = """

        vars:

        """
        f = File(content=vars1)
        f.parse()
        assert f.global_variables == []
        assert f.parsed is True

    def test_file_vars_parse(self) -> None:
        f = File(content=VARS4)
        f.parse()
        assert len(f.global_variables) == 4
        assert f.global_variables[0].name == "IMAGE_DEFAULT"
        assert f.global_variables[0].value == ""
        assert f.global_variables[1].name == "IMAGE_HADOLINT"
        assert f.global_variables[1].value == "hadolint/hadolint"
        assert f.global_variables[1].description == "Default image for lint:docker task"
        assert f.global_variables[2].name == "IMAGE_VALE"
        assert f.global_variables[2].value == ""
        assert f.global_variables[2].description == "Default image for # lint:vale task"
        assert f.global_variables[3].name == "IMAGE_YAMLINT"
        assert f.global_variables[3].value == "jfxs/ansible"
        assert f.global_variables[3].description == ""
        assert f.parsed is True

    def test_file_tasks_blank(self) -> None:
        task = """

        tasks:

        """
        f = File(content=task)
        f.parse()
        assert f.tasks == []
        assert f.parsed is True

    def test_file_tasks_parse(self) -> None:
        f = File(content=TASKS)
        f.parse()
        assert len(f.tasks) == 2
        assert f.tasks[0].name == "all"
        assert (
            f.tasks[0].desc
            == 'Linter for files, markdown, yaml extensions. Arguments: [FIX|F=y|Y] [MEX|M="#node_modules"] (*)'
        )
        assert "Usage: task lint:all" in f.tasks[0].summary
        assert f.tasks[1].name == "file"
        assert f.tasks[1].desc == "Linter for files. Arguments: [FIX|F=y|Y] (*)"
        assert "Usage: task lint:file [FIX|F=<y|Y>]" in f.tasks[1].summary
        assert f.parsed is True

    # to_md()
    def test_file_global_variables_to_md_blank(self) -> None:
        vars1 = """

        vars:

        """
        f = File(content=vars1)
        f.parse()
        assert f.global_variables == []

        ref = VARS_HEADER + "|  -  |  -  |  -  |" + "\n"
        assert f.global_variables_to_md() == ref

    def test_file_tags_to_md(self) -> None:
        f = File(content=HEADER_FULL)
        f.parse()
        output = f.tags_to_md()

        assert "tags:" in output
        assert "  - lint" in output
        assert "  - CI" in output
        assert "  - docker" in output

    def test_file_header_to_md(self) -> None:
        f = File(content=HEADER_FULL)
        f.parse()
        output = f.header_to_md()
        assert "    * :material-check-circle: Status: stable" in output
        assert (
            "    * :material-bookmark-check: File: [https://gitlab.com/op_so/task/task-templates/-/raw/main/Taskfile.d/lint.yml](https://gitlab.com/op_so/task/task-templates/-/blob/main/Taskfile.d/lint.yml)"
            in output
        )
        assert (
            "    * :material-home: Home: [https://gitlab.com/op_so/task/task-templates](https://gitlab.com/op_so/task/task-templates)"
            in output
        )
        assert "    * :material-license: License: MIT" in output

    def test_file_tasks_list_to_md(self) -> None:
        f = File(content=TASKS, path="my_dir/lint.yml")
        f.parse()
        output = f.tasks_list_to_md()

        assert TASKS_LIST_HEADER in output
        assert (
            r'| [`lint:all`](#lintall) | Linter for files, markdown, yaml extensions. Arguments: [FIX\|F=y\|Y] [MEX\|M="#node_modules"] (*) |'
            in output
        )
        assert "| [`lint:file`](#lintfile) | Linter for files" in output

    def test_file_global_variables_to_md(self) -> None:
        f = File(content=VARS4)
        f.parse()
        assert len(f.global_variables) == 4
        output = f.global_variables_to_md()

        assert VARS_HEADER in output
        assert "| `IMAGE_DEFAULT` |" in output
        assert "| Default image for # lint:vale task |" in output
        assert "| `hadolint/hadolint` |" in output

    def test_file_to_md(self) -> None:
        f = File(content=(HEADER_FULL + VARS4), path="my_dir/lint.yml")
        f.parse()
        output = f.to_md()

        assert "tags:" in output
        assert "  - lint" in output
        assert "# lint" in output
        assert "A set of tasks to lint different types of files." in output
        assert '!!! info "lint template details"' in output
        assert "    * :material-license: License: MIT" in output
        assert "global variables" in output
        assert VARS_HEADER in output
        assert "| `IMAGE_DEFAULT` |" in output
        assert "| Default image for # lint:vale task |" in output
        assert "| `hadolint/hadolint` |" in output
