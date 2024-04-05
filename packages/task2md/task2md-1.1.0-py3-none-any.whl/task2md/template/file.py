# -*- coding: utf-8 -*-

import re
from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import BaseModel

from task2md.template.header import Header
from task2md.template.task import Task
from task2md.template.variable import Variable
from task2md.util.dir import Dir


class File(BaseModel):
    """File Task content class"""

    path: str = ""
    content: str = ""
    yaml: Dict[str, Any] = {}
    header: Header = Header()
    global_variables: List[Variable] = []
    tasks: List[Task] = []
    parsed: bool = False

    def get_filename(self) -> str:
        """Get filename without extension

        Returns:
            str: The filename
        """
        return Path(self.path).stem

    def generate(self, dir: Dir) -> None:
        """Generate markdown file in output directory

        Args:
            dir (Dir): The dir object
        """
        self.load()
        self.parse()
        output = self.to_md()

        output_filename = f"{dir.path}/{self.get_filename()}.md"

        with open(output_filename, "w") as f:
            f.write(output)

    def load(self) -> None:
        """Load file content from path"""
        with open(self.path) as f:
            self.content = f.read()

    def parse(self) -> None:
        """Parse yaml content"""

        yaml_content = yaml.safe_load(self.content)

        if (yaml_content is not None) and isinstance(yaml_content, dict):
            self.yaml = yaml_content

        # 1 - Parse header:
        header_lines = re.findall(r"# @.*", self.content, flags=re.MULTILINE)
        self.header.parse(header_lines)

        # 2 - Parse vars:
        if ("vars" in self.yaml) and (self.yaml["vars"] is not None):
            sorted_keys = sorted(self.yaml["vars"].keys())
            for name in sorted_keys:
                v = Variable(name=name)
                if (self.yaml["vars"][name] is not None) and isinstance(
                    self.yaml["vars"][name], str
                ):
                    v.value = self.yaml["vars"][name]

                # Get comment if any
                line_var = re.findall(
                    r"^  " + v.name + ": .*$", self.content, flags=re.MULTILINE
                )
                if len(line_var) > 0:
                    # Remove name and value of line
                    desc = line_var[0].replace("  " + v.name + ": " + v.value, "")
                    # if # remove -> description
                    if "#" in desc:
                        value_desc = desc.split("#", 1)
                        v.description = value_desc[1].strip()

                self.global_variables.append(v)

        # 3 - Parse tasks:
        if ("tasks" in self.yaml) and (self.yaml["tasks"] is not None):
            sorted_keys = sorted(self.yaml["tasks"].keys())
            for name in sorted_keys:
                # Get task only if desc is defined
                if (
                    ("desc" in self.yaml["tasks"][name])
                    and (self.yaml["tasks"][name]["desc"] is not None)
                    and isinstance(self.yaml["tasks"][name]["desc"], str)
                    and (len(self.yaml["tasks"][name]["desc"]) > 0)
                ):
                    t = Task(name=name, desc=self.yaml["tasks"][name]["desc"])
                    if (
                        ("summary" in self.yaml["tasks"][name])
                        and (self.yaml["tasks"][name]["summary"] is not None)
                        and isinstance(self.yaml["tasks"][name]["summary"], str)
                        and (len(self.yaml["tasks"][name]["summary"]) > 0)
                    ):
                        t.summary = self.yaml["tasks"][name]["summary"]

                    self.tasks.append(t)

        self.parsed = True

    def to_md(self) -> str:
        """Return the content of the file in markdown

        Returns:
            str: Markdown content
        """
        output = ""
        # Tag
        output += self.tags_to_md()

        # Top
        output += f"---\n\n# {self.get_filename()}\n\n"
        output += self.header.description + "\n\n"
        output += f'!!! info "{self.get_filename()} template details"\n\n'
        output += self.header_to_md()

        # Tasks list
        output += "## :material-list-box: List of tasks\n"
        output += self.tasks_list_to_md() + "\n"

        # Global variables
        output += "## :material-variable: global variables\n"
        output += self.global_variables_to_md() + "\n"

        # Tasks details
        output += self.tasks_details_to_md()

        return output

    def tags_to_md(self) -> str:
        """Return the tags list

        Returns:
            str: markdown content
        """
        output = ""
        if len(self.header.tags) > 0:
            output += "---\ntags:\n"
            for tag in self.header.tags:
                output += f"  - {tag}\n"

        return output

    def header_to_md(self) -> str:
        """Return the header data

        Returns:
            str: markdown content
        """
        match self.header.status:
            case "stable":
                status_icon = "material-check-circle"
                status_label = "stable"
            case "deprecated":
                status_icon = "material-delete"
                status_label = "deprecated"
            case "beta":
                status_icon = "material-beta"
                status_label = "beta"
            case _:
                status_icon = "material-draw"
                status_label = "draft"

        output = ""
        output += f"    * :{status_icon}: Status: {status_label}\n"
        output += (
            "    * :material-bookmark-check: File: ["
            + self.header.file_raw
            + "]("
            + self.header.file_ui
            + ")\n"
        )
        output += (
            "    * :material-home: Home: ["
            + self.header.home
            + "]("
            + self.header.home
            + ")\n"
        )
        output += f"    * :material-license: License: {self.header.license}\n\n"

        return output

    def tasks_list_to_md(self) -> str:
        """Return the Tasks list to a markdown table

        Returns:
            str: markdown table
        """
        output = """
| Tasks | Description |
| ----- | ----------- |
"""
        for task in self.tasks:
            file_name = self.get_filename()
            escape_task_desc = task.desc.replace("|", r"\|")
            output += (
                f"| [`{file_name}:{task.name}`](#{file_name}{task.name})"
                f" | {escape_task_desc} |\n"
            )

        return output

    def global_variables_to_md(self) -> str:
        """Return the global variables to a markdown table

        Returns:
            str: markdown table
        """
        output = """
| Variables | Description | Default value |
| --------- | ----------- | ------------- |
"""

        if len(self.global_variables) == 0:
            # Empty variable to generate a line with no value
            v = Variable()
            output += v.to_md() + "\n"
        else:
            for var in self.global_variables:
                output += var.to_md() + "\n"

        return output

    def tasks_details_to_md(self) -> str:
        """Return the Tasks details

        Returns:
            str: List of tasks details
        """
        output = ""

        for task in self.tasks:
            output += task.to_md(self.get_filename())

        return output
