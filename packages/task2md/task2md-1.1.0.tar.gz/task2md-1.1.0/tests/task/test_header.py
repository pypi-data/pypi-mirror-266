# -*- coding: utf-8 -*-


from task2md.template.header import Header

VARS_HEADER_FULL = """
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


class TestFile:
    def test_header_init(self) -> None:
        h = Header()
        assert h.description == "-"
        assert h.tags == []
        assert h.file_raw == ""

    def test_header_parse(self) -> None:
        lines = VARS_HEADER_FULL.splitlines()
        h = Header()
        h.parse(lines)
        assert h.description == "A set of tasks to lint different types of files."
        assert h.tags == ["lint", "docker", "CI"]
        assert h.authors == ["FX Soubirou <soubirou@yahoo.fr>", "FXS <fxs@example.com>"]
        assert (
            h.file_raw
            == "https://gitlab.com/op_so/task/task-templates/-/raw/main/Taskfile.d/lint.yml"  # noqa: E501
        )
        assert (
            h.file_ui
            == "https://gitlab.com/op_so/task/task-templates/-/blob/main/Taskfile.d/lint.yml"  # noqa: E501
        )
        assert h.home == "https://gitlab.com/op_so/task/task-templates"
        assert h.links == ["[pre-commit](https://pre-commit.com/)"]
        assert h.license == "MIT"
        assert h.status == "stable"
        assert h.deprecated_tasks == []
