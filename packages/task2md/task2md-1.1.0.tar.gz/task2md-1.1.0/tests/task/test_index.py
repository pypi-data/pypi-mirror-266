# -*- coding: utf-8 -*-

from task2md.template.file import File
from task2md.template.header import Header
from task2md.template.index import Index


class TestFile:
    def test_index_init(self) -> None:
        i = Index()
        assert i.task_files == []

    def test_index_to_md(self) -> None:
        h1 = Header()
        h1.description = "desc1"
        h1.tags = ["tag11", "tag12", "tag13"]
        f1 = File(path="my_dir/lint1.yml", header=h1)
        h2 = Header()
        h2.description = "desc2"
        h2.tags = ["tag21", "tag22"]
        f2 = File(path="my_dir/lint2.yml", header=h2)

        i = Index()
        i.task_files.append(f1)
        i.task_files.append(f2)
        assert len(i.task_files) == 2

        output = i.to_md()
        assert "# Available task templates" in output
        assert "| Templates | Description | Tags   |" in output
        assert "| [lint1](lint1) | desc1 | tag11, tag12, tag13 |" in output
        assert "| [lint2](lint2) | desc2 | tag21, tag22 |" in output
