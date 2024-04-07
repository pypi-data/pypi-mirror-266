"""Basic generator, one template, one output file"""

import codecs
from pathlib import Path
from typing import Dict
from dmtgen import TemplateBasedGenerator
from dmtgen.package_generator import PackageGenerator
from dmtgen.common.package import Package
from dmtgen.common.blueprint import Blueprint
from jinja2 import Template
from .entity_model import create_model


class SimosEntityGenerator(TemplateBasedGenerator):
    """Basic generator, one template, one output file"""

    def generate(
        self,
        package_generator: PackageGenerator,
        template: Template,
        outputfile: Path,
        config: Dict,
    ):
        """Generate blueprint class"""
        outputdir = outputfile.parents[0]
        root_package = package_generator.root_package
        self.__generate_package(root_package, template, outputdir,config)

    def __generate_package(self, package: Package, template, pkg_dir,config):
        for blueprint in package.blueprints:
            self.__generate_entity(blueprint, package, template, pkg_dir,config)

        for package in package.packages:
            name = package.name
            sub_dir = pkg_dir / name
            self.__generate_package(package, template, sub_dir,config)

    def __generate_entity(
        self, blueprint: Blueprint, package: Package, template: Template, outputdir: Path, config: Dict
    ):
        outputdir.mkdir(exist_ok=True)
        model = {}
        package_name = package.name
        model["package_name"] = package_name
        model["description"] = package_name + " - Generated types"

        entity_model = create_model(blueprint,config)
        filename = entity_model["file_basename"] + ".F90"
        user_defined = {}
        entity_model["user_defined"] = user_defined

        outputfile = outputdir / filename
        if outputfile.exists():
            self.__find_user_defined(outputfile,user_defined)

        # Render the template first to ensure no errors in the template
        rendered_template = template.render(type=entity_model)
        with codecs.open(outputfile, "w", "utf-8") as file:
            file.write(rendered_template)

    def __find_user_defined(self, outputfile,user_defined):
        # Keep all lines between  "!@@@@@ USER DEFINED section START @@@@@" and "!@@@@@ USER DEFINED section END @@@@@"
        with codecs.open(outputfile, "r", "utf-8") as file:
            # Read all lines in the file, new line is
            lines = file.readlines()
            read_next = False
            for line in lines:
                line = line.rstrip()
                if "!@@@@@ USER DEFINED" in line:
                    if read_next:
                        # We are done
                        read_next = False
                        continue
                    else:
                    # find next word in part
                        part = line.split("!@@@@@ USER DEFINED")[1]
                        section = part.split()[0].lower()
                        user_defined[section] = []
                        read_next = True
                        continue
                if read_next:
                    user_defined[section].append(line)

        # clean up the user defined section
        for section in user_defined:
            user_defined[section] = "\n".join(user_defined[section])
