#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Code generator for fortran runtime library
'''

import shutil
from pathlib import Path
from typing import Dict

from dmtgen import BaseGenerator, TemplateBasedGenerator,NoneGenerator

from .simos.simos_generator import SimosEntityGenerator
from .basic_template_generator import BasicTemplateGenerator


class RuntimeGenerator(BaseGenerator):
    """ Generates a fortran runtime library to access the entities as plain objects """

    # @override
    def get_template_generator(self, template: Path, config: Dict) -> TemplateBasedGenerator:
        """ Override in subclasses """
        if config.get("simos", False):
            # Only generate simos entities
            if template.name == "simos.F90.jinja":
                return SimosEntityGenerator()
            return NoneGenerator()
        else:
            if template.name == "simos.F90.jinja":
                # Skip simos template
                return NoneGenerator()
            return BasicTemplateGenerator()

    def copy_templates(self, template_root: Path, output_dir: Path):
        """Copy template folder to output folder"""
        shutil.copytree(str(template_root), str(output_dir),  dirs_exist_ok=True)
