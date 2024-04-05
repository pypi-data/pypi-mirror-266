# -*- coding: utf-8 -*-
import re
from typing import ClassVar, List

from pydantic import BaseModel


class Header(BaseModel):
    """Header Task file class"""

    PATTERN: ClassVar[str] = r"@([\w-]+): (.*)"

    description: str = "-"
    tags: List[str] = []
    authors: List[str] = []
    file_raw: str = ""
    file_ui: str = ""
    home: str = ""
    links: List[str] = []
    license: str = ""
    status: str = ""
    deprecated_tasks: List[str] = []

    def parse(self, header_lines: List[str]) -> None:
        """Parse the header comment of a Task file

        Args:
            header_lines (List[str]): List of header lines
        """
        for line in header_lines:
            match = re.search(Header.PATTERN, line)
            if match:
                label, value = match.groups()
                match label.strip():
                    case "description":
                        self.description = value.strip()
                    case "tags":
                        self.tags = Header.string2list(value)
                    case "authors":
                        self.authors = Header.string2list(value)
                    case "file-raw":
                        self.file_raw = value.strip()
                    case "file-ui":
                        self.file_ui = value.strip()
                    case "home":
                        self.home = value.strip()
                    case "links":
                        self.links = Header.string2list(value)
                    case "license":
                        self.license = value.strip()
                    case "status":
                        self.status = value.strip()
                    case "deprecated-tasks":
                        self.deprecated_tasks = Header.string2list(value)

    @classmethod
    def string2list(cls, input: str) -> List[str]:
        """Split a string with comma separator

        Args:
            input (str): string to split

        Returns:
            List[str]: A list of string
        """
        list = input.split(",")
        output = []
        for element in list:
            output.append(element.strip())

        return output
