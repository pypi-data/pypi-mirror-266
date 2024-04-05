# -*- coding: utf-8 -*-
# flake8: noqa

from task2md.template.task import Task

TASK1 = """[LINT] Linter for files.
Usage: task lint:all [FIX|F=<y|Y>] [MEX|M='"#node_modules"']

Arguments:
  FIX |  F:  Fix files (optional, by default no)
  MEX | M: Makdown exlude directories with single quotes example: MEX='"#node_modules" "#.node_cache"' (see: https://github.com/DavidAnson/markdownlint-cli2)

Notes:
  - Only git versionned files are checked for generic files. Use MEX argument for Markdown files and .yamlint for YAML files to exclude.
  - Check git tracked files,
  - otherwise (empty git list), all files not in a directory starting by dot

Requirements:
  - markdownlint-cli2 or docker
  - yamllint or docker

"""


class TestTask:
    def test_task_init(self) -> None:
        t = Task()
        assert t.name == ""
        assert t.desc == ""
        assert t.summary == ""
        assert t.summary_head == ""
        assert t.summary_args == []
        assert t.summary_req == []
        assert t.summary_comments == ""
        assert not t.parsed

    def test_task_parse(self) -> None:
        t = Task()
        t.name = "All"
        t.desc = "Description for All"
        t.summary = TASK1
        t.parse()
        assert (
            t.summary_head
            == """[LINT] Linter for files.
Usage: task lint:all [FIX|F=<y|Y>] [MEX|M='"#node_modules"']
"""
        )
        assert len(t.summary_args) == 2
        assert t.summary_args[0].label == "FIX |  F"
        assert t.summary_args[0].value == "Fix files (optional, by default no)"
        assert t.summary_args[1].label == "MEX | M"
        assert len(t.summary_req) == 2
        assert t.summary_req[0] == "- markdownlint-cli2 or docker"
        assert t.summary_req[1] == "- yamllint or docker"
        assert "Notes:" in t.summary_comments
        assert "starting by dot" in t.summary_comments
        assert t.parsed

    def test_task_to_md(self) -> None:
        t = Task()
        t.name = "All"
        t.desc = "Description for All"
        t.summary = TASK1
        t.parse()
        md = t.to_md("lint")
        assert "## :simple-task: lint:All" in md
        assert "[LINT] Linter" in md
        assert "Usage: task" in md
        assert "| Arguments | Description |" in md
        assert "| Fix files (optional, by default no) |" in md
        assert "| `MEX " in md
        assert "Notes:" in md
        assert "starting by dot" in md
        assert '!!! info "Requirements:' in md
        assert "    - yamllint or docker" in md
