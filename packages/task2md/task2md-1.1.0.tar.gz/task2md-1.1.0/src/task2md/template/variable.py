# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Variable(BaseModel):
    """Global variable class"""

    name: str = ""
    value: str = ""
    description: str = ""

    def to_md(self) -> str:
        """Return the details of the variable

        Returns:
            str: Markdown columns of the variable details
        """
        if self.name == "":
            name = " - "
        else:
            name = f"`{self.name}`"
        if self.description == "":
            description = " - "
        else:
            description = self.description
        if self.value == "":
            value = " - "
        else:
            value = f"`{self.value}`"

        return f"| {name} | {description} | {value} |"
