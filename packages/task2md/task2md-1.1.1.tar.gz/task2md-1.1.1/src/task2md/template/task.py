# -*- coding: utf-8 -*-

import re
from typing import ClassVar, List

from pydantic import BaseModel


class Argument(BaseModel):
    """Task argument class"""

    label: str = ""
    value: str = ""


class Task(BaseModel):
    """Task class"""

    LINE_ARG: ClassVar[str] = "Arguments:"
    PATTERN_ARG: ClassVar[str] = r"([\w-]+\s*[|]\s*[\w-]*): (.*)"
    LINE_REQ: ClassVar[str] = "Requirements:"
    PATTERN_REQ: ClassVar[str] = r"(-\s.*)"

    name: str = ""
    desc: str = ""
    summary: str = ""
    summary_head: str = ""
    summary_args: List[Argument] = []
    summary_req: List[str] = []
    summary_comments: str = ""
    parsed: bool = False

    def parse(self) -> None:
        """Parse the Task summary"""
        # Head - get beginning until blank line
        lines = self.summary.splitlines()
        head: List[str] = []
        for line in lines:
            if line.strip():
                head.append(line)
            else:
                break

        self.summary_head = "\n".join(head) + "\n"
        # Get partial summary without head lines
        count_line_head = len(head)
        index_partial_summary = max(0, count_line_head)
        partial_summary_lines = lines[index_partial_summary:]
        partial_summary_lines_count = len(partial_summary_lines)

        # Arguments
        found_arguments = False
        for i, line in enumerate(partial_summary_lines):
            if (line.strip() == Task.LINE_ARG) and (
                (i + 1) < partial_summary_lines_count
            ):
                found_arguments = True
                # Parse arguments
                args_summary_lines = partial_summary_lines[(i + 1) :]
                for j, line_arg in enumerate(args_summary_lines):
                    match = re.search(Task.PATTERN_ARG, line_arg.strip())
                    if match:
                        label, value = match.groups()
                        arg = Argument(label=label.strip(), value=value.strip())
                        self.summary_args.append(arg)
                    else:
                        break
            if found_arguments:
                del partial_summary_lines[i : (i + j + 2)]
                break

        # Requirements
        partial_summary_lines_count = len(partial_summary_lines)
        found_req = False
        for i, line in enumerate(partial_summary_lines):
            if (line.strip() == Task.LINE_REQ) and (
                (i + 1) < partial_summary_lines_count
            ):
                found_req = True
                # Parse req
                req_summary_lines = partial_summary_lines[(i + 1) :]
                for j, line_req in enumerate(req_summary_lines):
                    match = re.search(Task.PATTERN_REQ, line_req.strip())
                    if match:
                        req = match.groups()
                        self.summary_req.append(req[0])
                    else:
                        break
            if found_req:
                del partial_summary_lines[i : (i + j + 2)]
                break

        # Comments
        self.summary_comments = (
            "\n".join(partial_summary_lines).strip().replace("\n", "  \n")
        )

        self.parsed = True

    def to_md(self, file_name: str) -> str:
        """Return the details of the task

        Args:
            file_name (str): File_name of the task file.

        Returns:
            str: Markdown of the task details
        """
        self.parse()
        output = f"\n## :simple-task: {file_name}:{self.name}\n\n"

        output += f"{self.desc} \n\n"
        output += "```shell\n"
        output += self.summary_head
        output += "```\n"

        # Arguments
        output += """
| Arguments | Description |
| --------- | ----------- |
"""
        if len(self.summary_args) == 0:
            output += "| - | - |\n"
        else:
            for arg in self.summary_args:
                output += f"| `{arg.label}` | {arg.value} |\n"
        output += "\n"

        # Comments
        output += f"{self.summary_comments}\n\n"

        # Requirements
        output += '!!! info "Requirements:"\n\n'
        if len(self.summary_req) == 0:
            output += "    - None\n"
        else:
            for req in self.summary_req:
                output += f"    {req}\n"

        return output
