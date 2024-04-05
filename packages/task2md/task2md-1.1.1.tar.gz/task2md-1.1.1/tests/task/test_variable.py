# -*- coding: utf-8 -*-

from task2md.template.variable import Variable


class TestVariable:
    def test_variable_blank(self) -> None:
        v = Variable()
        assert v.name == ""
        assert v.value == ""
        assert v.description == ""
        assert v.to_md() == "|  -  |  -  |  -  |"

    def test_variable_to_md(self) -> None:
        v = Variable(name="name1", value="value1", description="desc1")
        assert v.name == "name1"
        assert v.value == "value1"
        assert v.description == "desc1"
        assert v.to_md() == "| `name1` | desc1 | `value1` |"
