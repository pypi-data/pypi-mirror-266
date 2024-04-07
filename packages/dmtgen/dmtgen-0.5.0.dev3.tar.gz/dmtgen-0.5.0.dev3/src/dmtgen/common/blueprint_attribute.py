""" " A basic SIMOS Attribute"""
from __future__ import annotations
from typing import Dict
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .blueprint import Blueprint

class BlueprintAttribute:
    """ " A basic SIMOS Attribute"""

    # pylint: disable=too-many-instance-attributes
    def __init__(self, content: Dict, parent: Blueprint) -> None:
        self.content = content
        name = content["name"]
        if len(name)==0:
            raise ValueError("Attribute has no name")
        self.name = name
        if "description" not in content:
            content["description"] = ""
        self.description = content["description"].replace('"',"'")
        dims=content.get("dimensions")
        if dims:
            self.dimensions = dims.split(",")
        else:
            self.dimensions = []

        atype = content["attributeType"]
        self.__parent = parent
        package = parent.parent
        self.__type = package.resolve_type(atype)
        self.__optional = self.content.get("optional",True)
        self.__is_primitive = atype in ['boolean', 'number', 'string', 'integer']
        self.__is_enum = self.content.get("enumType",None) is not None
        self.__is_blueprint = not (self.__is_primitive or self.__is_enum)
        self.__is_array = len(self.dimensions)>0
        self.__is_string = self.type == "string"
        self.__is_boolean = self.type == "boolean"
        self.__is_integer = self.type == "integer"
        self.__is_number = self.type == "number"
        self.__is_contained = content.get("contained",True)

    @property
    def parent(self) -> Blueprint:
        """The parent blueprint"""
        return self.__parent

    @property
    def type(self) -> str:
        """The type of the attribute"""
        return self.__type

    @property
    def optional(self) -> bool:
        """Is this an optional attribute"""
        return self.__optional

    @property
    def contained(self) -> bool:
        """Is this a contained attribute"""
        return self.__is_contained

    def is_primitive(self) -> bool:
        """Is this a primitive type"""
        return self.__is_primitive

    def is_enum(self) -> bool:
        """Is this an enum type"""
        return self.__is_enum

    def is_blueprint(self) -> bool:
        """Is this a blueprint type"""
        return self.__is_blueprint

    def is_string(self) -> bool:
        """Is this a string"""
        return self.__is_string

    def is_boolean(self) -> bool:
        """Is this a boolean"""
        return self.__is_boolean

    def is_integer(self) -> bool:
        """Is this an integer"""
        return self.__is_integer

    def is_number(self) -> bool:
        """Is this a number"""
        return self.__is_number

    def is_optional(self) -> bool:
        """Is an optional relation"""
        return self.__optional

    def is_required(self) -> bool:
        """Is a required relation"""
        return not self.__optional

    def is_array(self) -> bool:
        """Is this an array"""
        return self.__is_array

    def is_fixed_array(self) -> bool:
        """Is this a fixed array"""
        return self.__is_array and "*" not in self.dimensions

    def is_variable_array(self) -> bool:
        """Is this a variable array"""
        return self.__is_array and "*" in self.dimensions

    def get(self, key, default=None):
        """Return the content value or an optional default"""
        return self.content.get(key,default)

    def as_dict(self) -> Dict:
        """Return the attribute as a dictionary"""
        return dict(self.content)
