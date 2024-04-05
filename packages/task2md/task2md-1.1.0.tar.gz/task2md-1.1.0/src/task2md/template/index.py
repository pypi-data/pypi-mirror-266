# -*- coding: utf-8 -*-

from typing import List

from pydantic import BaseModel

from task2md.template.file import File
from task2md.util.dir import Dir


class Index(BaseModel):
    """Index markdown templates list class"""

    task_files: List[File] = []

    def generate(self, dir: Dir) -> None:
        """Generate markdown file in output directory

        Args:
            dir (Dir): The dir object
        """
        output = self.to_md()

        output_filename = f"{dir.path}/index.md"

        with open(output_filename, "w") as f:
            f.write(output)

    def to_md(self) -> str:
        """Return the content of the file in markdown

        Returns:
            str: Markdown content
        """
        output = """
# Available task templates

List of templates:

| Templates | Description | Tags   |
| --------- | ----------- | ------ |
"""
        for file in self.task_files:
            name = file.get_filename()
            description = file.header.description
            tags = ", ".join(file.header.tags)

            output += f"| [{name}]({name}) | {description} | {tags} |\n"

        return output + "\n"
