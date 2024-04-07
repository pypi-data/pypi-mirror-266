"""Basic generator, one template, one output file"""

import codecs
from pathlib import Path
from typing import Dict
from dmtgen import TemplateBasedGenerator
from dmtgen.package_generator import PackageGenerator
from dmtgen.common.package import Package
from dmtgen.common.blueprint_attribute import BlueprintAttribute
from inflection import underscore
from .graph import Graph
class BasicTemplateGenerator(TemplateBasedGenerator):
    """Basic generator, one template, one output file"""

    types = {"number": "real(dp)", "double": "real(dp)", "string": "character(:)", "char": "character",
            "integer": "integer", "short": "short", "boolean": "logical"}

    default_values = {"number": "0.0", "boolean": ".false.", "integer": "0"}

    def generate(self, package_generator: PackageGenerator, template, outputfile: Path, config: Dict):
        """Basic generator, one template, one output file"""

        model = {}
        etypes = {}
        pkg: Package = package_generator.root_package
        dependencies = {}
        for blueprint in pkg.blueprints:
            etype = {}
            name = blueprint.name
            ftype = underscore(name)+"_t"
            etype["name"] = name
            etype["type"] = ftype
            etype["path"] = blueprint.get_path()
            etype["description"] = blueprint.description
            etype["formatted_description"] = self.__format_description(blueprint.description)
            etype["has_description"] = len(blueprint.description) > 0
            etype["file_basename"] = name.lower()
            attributes = []
            etype["attributes"]=attributes
            attribute_deps = set()
            for attribute in blueprint.all_attributes.values():
                attributes.append(self.__to_attribute_dict(attribute, pkg, attribute_deps))
            dependencies[name]=attribute_deps
            etypes[name]=etype

        model["types"] = self.__sort(etypes, dependencies)

        with codecs.open(outputfile, "w", "utf-8") as file:
            file.write(template.render(model))

    def __to_attribute_dict(self,attribute: BlueprintAttribute, pkg: Package, attribute_deps):
        fieldname =underscore(attribute.name)
        fieldname_temp = fieldname + "_temp" # We need a temp variable (allocatable) to assign to static arrays (non-allocatable)

        if attribute.is_array():
            dimensions = attribute.dimensions
            array_rank = len(dimensions)
            shape = ",".join(attribute.dimensions).replace("*", ":")
            shape_temp = ','.join(array_rank*[':'])
        else:
            dimensions = None
            array_rank = 0
            shape = ''
            shape_temp = ''

        if attribute.is_primitive():
            atype = self.__map(attribute.type, self.types)
            # integer :: index
            # character(:), allocatable :: name
            allocatable = attribute.is_variable_array() or attribute.is_string()
            if allocatable:
                type_init = atype + ", allocatable :: " + fieldname
                type_init_allocatable_temp = atype + ", allocatable :: " + fieldname_temp
            else:
                type_init = atype + " :: " + fieldname
                type_init_allocatable_temp = atype + ", allocatable :: " + fieldname_temp # We need an allocatable temp variable to assign to static arrays

            if attribute.is_array():
                type_init += '(' + shape + ')'
                type_init_allocatable_temp += '(' + shape_temp + ')'

            if not allocatable:
                default = self.__find_default_value(attribute)
                if default is not None:
                    type_init += " = " + default

        else:

            if array_rank > 1:
                raise ValueError("Only one-dimensional derived type arrays are supported")

            bp=pkg.get_blueprint(attribute.type)
            attribute_deps.add(bp.name)
            atype = underscore(bp.name)+"_t"

            allocatable = attribute.is_variable_array() or attribute.optional

            if allocatable:
                type_init = "type(" + atype + "), allocatable :: " + fieldname
                type_init_allocatable_temp = "type(" + atype + "), allocatable :: " + fieldname_temp # We need an allocatable temp variable to assign to static arrays
            else:
                type_init = "type(" + atype + ") :: " + fieldname
                type_init_allocatable_temp = "type(" + atype + "), allocatable :: " + fieldname_temp # We need an allocatable temp variable to assign to static arrays

            if attribute.is_array():
                type_init += '(' + shape + ')'
                type_init_allocatable_temp += '(' + shape_temp + ')'

        if len(attribute.description) > 0:
            has_description = True
        else:
            has_description = False

        return {
            "name": attribute.name,
            "fieldname": fieldname,
            "fieldname_temp": fieldname_temp,
            "is_required": attribute.is_required(),
            "type" : atype,
            "is_primitive" : attribute.is_primitive(),
            "is_many" : attribute.is_array(),
            "array_rank" : array_rank, # Number of dimensions in array
            "has_dynamic_shape" : attribute.is_variable_array(), # True if at least one dimension is *
            "shape" : shape, # Shape of array
            "type_init" : type_init,
            "type_init_allocatable_temp" : type_init_allocatable_temp,
            "description" : attribute.description,
            "has_description" : has_description
        }

    def __sort(self, etypes, dependencies):
        vertices = [x["name"] for x in etypes.values()]
        graph = Graph(vertices)
        for etype in etypes.values():
            name = etype["name"]
            for dep in dependencies[name]:
                graph.addEdge(dep,name)
        sorted_types = list()
        sorted_names = graph.sort()
        for name in sorted_names:
            sorted_types.append(etypes[name])
        return sorted_types

    def __map(self, key, values):
        converted = values[key]
        if not converted:
            raise ValueError("Unkown type " + key)
        return converted

    def __find_default_value(self, attribute: BlueprintAttribute):
        default_value = attribute.get("default")
        if default_value is not None:
            return self.__convert_default(attribute,default_value)
        return default_value

    def __convert_default(self,attribute: BlueprintAttribute, default_value):
        # converts json value to fortran value
        if isinstance(default_value,str):
            if default_value == '' or default_value == '""':
                return '""'
            elif attribute.type == 'integer':
                return default_value
            elif attribute.type == 'number':
                return default_value + "_dp"
            elif attribute.type == 'boolean':
                conversion = {
                    "false": ".false.",
                    "true": ".true.",
                }
                return conversion.get(default_value, default_value)
            else:
                return "'" + default_value + "'"

    @staticmethod
    def first_to_upper(string: str):
        """ Make sure the first letter is uppercase """
        return string[:1].upper() + string[1:]

    @staticmethod
    def __format_description(desc: str):
        if len(desc) > 0:
            lst = desc.splitlines()
            flst = ['!! ' + s for s in lst]
            return flst
        else:
            return [desc]
