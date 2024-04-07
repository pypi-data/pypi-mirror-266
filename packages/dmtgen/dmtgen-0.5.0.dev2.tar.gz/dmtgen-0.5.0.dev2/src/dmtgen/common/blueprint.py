"""Blueprint class for SIMOS"""
from __future__ import annotations
from typing import Dict, Sequence
from typing import TYPE_CHECKING
from .blueprint_attribute import BlueprintAttribute
if TYPE_CHECKING:
    from .package import Package

class Blueprint:
    """ " A basic SIMOS Blueprint"""

    # pylint: disable=too-many-instance-attributes
    def __init__(self, content: Dict, parent: Package) -> None:
        self.parent = parent
        self.content = content
        self.name: str = self.content["name"]
        self.description: str = content.get("description",None)
        attributes = {}
        for a_dict in content.get("attributes",[]):
            attribute = BlueprintAttribute(a_dict, self)
            attributes[attribute.name]=attribute
        self.__abstract = content.get("abstract",False)
        self.__attributes = attributes
        self.__extends = content.get("extends",[])
        # We will resolve this later
        self.__extensions = None


    @property
    def attributes(self) -> Sequence[BlueprintAttribute]:
        """Attributes"""
        return self.__attributes.values()

    @property
    def all_attributes(self) -> Dict[str,BlueprintAttribute]:
        """All combined attributes for the blueprint and its extensions"""
        # First we collect the extensions, since these may be overridden
        atributes = {}
        for extension in self.extensions:
            atributes.update(extension.all_attributes)
        # Then we add ours
        atributes.update(self.__attributes)
        return atributes

    @property
    def extensions(self) -> Sequence[Blueprint]:
        """Extensions"""
        if self.__extensions is not None:
            return self.__extensions

        self.__extensions =  [self.__resolve(extension) for extension in self.__extends]
        return self.__extensions

    def __resolve(self,extension: str):
        package: Package = self.parent
        return package.get_blueprint(extension)

    def is_abstract(self) -> bool:
        """If the blueprint represent an abstract type. 
        In object oriented terms, this would be an interface or abstract class."""
        return self.__abstract

    def get_path(self):
        """ Get full path to blueprint"""
        parent = self.parent
        if parent:
            return parent.get_path() + "/" + self.name
        # Then we are at root
        return self.name

    def get_attribute(self, name:str) -> BlueprintAttribute:
        """ Return the attribute if it exists, otherwise None"""
        return self.all_attributes.get(name,None)