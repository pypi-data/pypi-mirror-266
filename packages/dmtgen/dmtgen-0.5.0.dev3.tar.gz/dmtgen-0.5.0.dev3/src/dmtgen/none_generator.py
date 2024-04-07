"""Basic generator, one template, one output file"""

from pathlib import Path
from typing import Dict
from jinja2.environment import Template
from .package_generator import PackageGenerator
from .template_generator import TemplateBasedGenerator


class NoneGenerator(TemplateBasedGenerator):
    """Do not generate anything, meaning the given tempate is not used for anything"""

    def generate(self,package_generator: PackageGenerator, template : Template, outputfile: Path, config: Dict):
        """Do nothing"""
