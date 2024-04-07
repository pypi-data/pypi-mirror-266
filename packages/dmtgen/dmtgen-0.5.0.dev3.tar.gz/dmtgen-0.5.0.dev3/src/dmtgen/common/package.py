""" " A basic SIMOS package"""


from __future__ import annotations
import json

import os
import re
from pathlib import Path
from typing import List, Sequence,Dict

from .enum_description import EnumDescription
from .blueprint import Blueprint

class Package:
    """ " A basic SIMOS package"""

    # pylint: disable=too-many-instance-attributes
    def __init__(self, pkg_dir: Path, parent: Package, config: Dict=None) -> None:
        self.package_dir = pkg_dir
        self.version = 0
        self.name = pkg_dir.name
        self.aliases = {"core":"system/SIMOS"}
        self.parent = parent
        self.__blueprints = {}
        self.__enums = {}
        self.__packages = {}
        self.__dependencies = {}
        if parent is None and config is not None:
            # This is a root package and we might have dependencies
            dependencies: dict = config.get('dependencies', {})
            for alias,location in dependencies.items():
                self.__dependencies[alias] = Package(Path(location),None)

        self.__read_package(pkg_dir)

    def __read_package(self, pkg_dir: Path):
        blueprints = {}
        enums = {}
        self.__blueprints = blueprints
        self.__enums = enums

        # First we need to check for a package.json file
        pkg_filename = "package.json"
        package_file = pkg_dir / pkg_filename
        if package_file.exists():
            # Use with to ensure file is closed
            with open(package_file, encoding="utf-8") as file:
                package = json.load(file)
                self.__read_package_info(package)

        for file in pkg_dir.glob("*.json"):
            if file.name == pkg_filename:
                continue

            if file.name == "__versions__.json":
                self.__read_version(entity)
            else:
                with open(file, encoding="utf-8") as file:
                    entity = json.load(file)
                    etype = self.resolve_type(entity["type"])
                    if etype == "system/SIMOS/Blueprint":
                        blueprint = Blueprint(entity, self)
                        name = blueprint.name
                        blueprints[name] = blueprint
                    elif etype == "system/SIMOS/Enum":
                        enum = EnumDescription(entity, self)
                        name = enum.name
                        enums[name] = enum
                    else:
                        raise ValueError("Unhandled entity type: " + etype)

        for folder in pkg_dir.glob("*/"):
            if folder.is_dir():
                sub_package = Package(folder,self)
                sub_package.parent = self
                self.__packages[sub_package.name] = sub_package

    def __read_version(self,versions: dict):
        self.version = versions.get(self.name,None)

    def __read_package_info(self,pkg: dict):
        self.name=pkg.get("name",self.name)
        meta=pkg.get("_meta_")
        if meta:
            self.version = meta.get("version")
            deps = meta.get("dependencies",[])
            for dep in deps:
                alias = dep.get("alias")
                if alias:
                    self.aliases[alias]=dep.get("address")

    def resolve_type(self, etype:str) -> str:
        """Resolve type to full path"""
        if etype.startswith("."):
            # This is a relative path
            path = self.get_path() + "/" + etype
            path = os.path.normpath(path).replace("\\","/")
            return path
        idx=etype.find(":")
        if idx > 0:
            alias = etype[:idx].lower()
            adress = self.aliases.get(alias,alias)
            return adress + "/" + etype[idx+1:]
        return etype


    def get_path(self) -> str:
        """ Get full type path to package """
        parent = self.get_parent()
        if parent:
            return parent.get_path() + "/" + self.name
        # Then we are root
        return self.name

    def get_paths(self) -> List[str]:
        """ Get full type path to package """
        parent = self.get_parent()
        if parent:
            parent_paths = parent.get_paths()
            parent_paths.append(self.name)
            return parent_paths
        # Then we are root
        return [self.name]

    @property
    def blueprints(self) -> Sequence[Blueprint]:
        """All blueprints in package"""
        return self.__blueprints.values()

    @property
    def enums(self) -> Sequence[EnumDescription]:
        """All enums in package"""
        return self.__enums.values()

    def blueprint(self, name:str) -> Blueprint:
        """Get blueprint by name"""
        blueprint = self.__blueprints.get(name,None)
        if not blueprint:
            raise ValueError(f"Blueprint not found \"{name}\" in {self.name}")
        return blueprint

    def enum(self, name:str) -> EnumDescription:
        """Get enum by name"""
        enum = self.__enums.get(name,None)
        if not enum:
            raise ValueError(f"Enum not found \"{name}\" in {self.name}")
        return enum


    @property
    def packages(self) -> Sequence[Package]:
        """Attributes"""
        return list(self.__packages.values())

    def package(self, name:str) -> Package:
        """Attributes"""
        pkg = self.__packages.get(name,None)
        if not pkg:
            raise ValueError(f"package not found \"{name}\" in {self.name}")
        return pkg

    def get_parent(self) -> Package:
        """Get parent package"""
        return self.parent

    def get_root(self) -> Package:
        """Get root package"""
        parent: Package = self.parent
        if parent:
            return parent.get_root()
        # No parent so we are root
        return self


    def get_blueprint(self, path:str) -> Blueprint:
        """Get Blueprint from path"""
        path = self.resolve_type(path)
        idx=path.find(":")
        if idx > 0:
            alias = path[:idx].lower()
            adress = self.aliases[alias]
            path = adress + "/" + path[idx+1:]

        parts = re.split("/",path)
        bp_name = parts.pop()
        package = self.__get_package(parts)
        return package.blueprint(bp_name)

    def get_enum(self, path:str) -> EnumDescription:
        """Get enum from path"""
        path = self.resolve_type(path)
        parts = re.split("/",path)
        enum_name = parts.pop()
        package = self.__get_package(parts)
        return package.enum(enum_name)

    def __get_package(self, parts: Sequence[str]) -> Package:
        package: Package = None
        for part in parts:
            if part == '.':
                raise ValueError("Relative path not allowed. Should have been resolved by now.")
            if part == '':
                continue
            if part == 'system':
                # pylint: disable=import-outside-toplevel
                from .system_package import system_package
                package =  system_package
            elif package is None:
                # Use the root package to resolve
                root_package: Package = self.get_root()
                if part == root_package.name:
                    package = root_package
                else:
                    package = root_package.__dependencies.get(part,None)
                    if not package:
                        raise ValueError(f"Package not found \"{part}\" in {root_package.name} or dependencies.")
            else:
                package = package.package(part)
        return package
