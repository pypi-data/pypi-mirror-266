""" A basic DMT Enum"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING:
    from .package import Package

class EnumDescription:
    """ " A basic DMT Enum"""

    def __init__(self, enum_dict: Dict, parent: Package) -> None:
        self.parent = parent
        self.blueprint = enum_dict
        self.name = self.blueprint["name"]
        self.description = enum_dict.get("description","")
        values = enum_dict["values"]
        labels = enum_dict["labels"]
        self.enum_values = []
        self.default = enum_dict.get("default",values[0])
        for i, value in enumerate(values):
            self.enum_values.append({
                "value": value,
                "label": labels[i]
            })

    def get_path(self):
        """ Get full path to blueprint """
        parent = self.parent
        if parent:
            return parent.get_path() + "/" + self.name
        # Then we are at root
        return "/" + self.name

    def get_parent(self) -> Package:
        """ Get parent package """
        return self.parent
