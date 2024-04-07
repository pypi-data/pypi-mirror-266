
from collections import OrderedDict
from typing import Set

from dmtgen.common.blueprint_attribute import BlueprintAttribute
from dmtgen.common.package import Blueprint, Package
from inflection import humanize
from . import hdf5_model as hdf5
from . import resize_model as resize
from .common import to_type_name,to_field_name,to_module_name,to_type_path
from .simos import is_destroyable,has_default_init,is_allocatable


types = {"number": "real(dp)", "double": "real(dp)", "string": "character(:)", "char": "character",
            "integer": "integer", "short": "short", "boolean": "logical"}

def create_model(blueprint: Blueprint, config: dict):
    """Create entity model from blueprint"""
    model = {}
    if config is None:
        config = {}
    attr_name = blueprint.name
    model["name"] = attr_name
    attr_name = blueprint.name
    module = to_module_name(blueprint)
    model["name"] = attr_name
    model["type"] = blueprint.name
    model["module"] = module
    model["path"] = blueprint.get_path().replace("/",":")
    model["description"] = blueprint.description
    model["file_basename"] = attr_name.lower()
    # TODO: When blueprint is shared, shouldnt everything be shared?
    is_shared = blueprint.content.get("shared", False)
    model["is_shared"] = is_shared
    model["is_writable"] = blueprint.content.get("writable", False)
    attributes = []
    model["attributes"]=attributes

    all_attributes = blueprint.all_attributes
    model["has_name"] = all_attributes.get("name") is not None

    model["hdf5"] = hdf5.create_model(blueprint)
    model["resize"] = resize.create_model(blueprint)
    attribute_deps = OrderedDict()
    for attribute in blueprint.all_attributes.values():
        attributes.append(__to_attribute_dict(blueprint, attribute, attribute_deps,config))

    # TODO REMOVE WHEN DONE
    # Move name and description to the end
    for i, attribute in enumerate(attributes):
        if attribute["name"] == "name":
            # attribute["description"] = "variable name for named accessing"
            attributes.append(attributes.pop(i))
            break
    for i, attribute in enumerate(attributes):
        if attribute["name"] == "description":
            # attribute["description"] = "instance description"
            attributes.append(attributes.pop(i))
            break

    model["dependencies"]= [__create_dependency(dep) for dep in attribute_deps]
    return model


def __create_dependency(dep: Blueprint):
    return {"name": dep.name, "type": to_type_name(dep), "module": to_module_name(dep), "type_path": to_type_path(dep)}

def __to_attribute_dict(blueprint: Blueprint,attribute: BlueprintAttribute, attribute_deps: Set[Blueprint], config: dict):
    atype = __to_attribute_type(blueprint,attribute, attribute_deps, config)

    type_init = __attribute_init(attribute,atype)
    if len(attribute.description)==0:
        attribute.description = humanize(attribute.name)

    if attribute.is_string() and attribute.is_array():
        raise ValueError("String arrays are not supported")

    adict = {
        "name": attribute.name,
        "fieldname": to_field_name(attribute.name),
        "is_required": attribute.is_required(),
        "type" : atype,
        "is_optional" : attribute.optional,
        "is_primitive" : attribute.is_primitive(),
        "is_string" : attribute.is_string(),
        "is_array" : attribute.is_array(),
        "type_init" : type_init,
        "is_allocatable" : is_allocatable(attribute),
        "has_default_init" : has_default_init(attribute),
        "is_destroyable" : is_destroyable(attribute),
        "is_variable_array" : attribute.is_variable_array(),
        "description" : attribute.description
    }

    is_shared = attribute.content.get("shared", False)
    # However name is always shared if blueprint is shared
    if attribute.name == "name" and blueprint.content.get("shared", False):
        is_shared = True

    adict["is_shared"] = is_shared

    if is_destroyable(attribute):
        adict["destroy"] = __attribute_destroy(attribute)

    if attribute.is_variable_array():
        adict["dimension_names"] = __dimension_names(attribute)

    return adict

def __to_attribute_type(blueprint: Blueprint,attribute: BlueprintAttribute, attribute_deps: Set[Blueprint], config: dict):
    if attribute.is_primitive():
        if attribute.is_string() and config.get("use_string", True):
            return "type(String)"
        return __map(attribute.type, types)
    else:
        pkg: Package = blueprint.parent
        bp = pkg.get_blueprint(attribute.type)
        atype = to_type_path(bp)
        attribute_deps[bp]=bp
        return atype


def __dimension_names(attribute: BlueprintAttribute):
    return __names("idx", len(attribute.dimensions))

def __names(name, ndim):
    return ", ".join([name+str(i+1) for i in range(ndim)])

def __attribute_destroy(attribute: BlueprintAttribute):
    if attribute.is_variable_array() and (attribute.is_blueprint() or attribute.is_string()):
        dims = __dimension_names(attribute)
        # FIXME: This is a hack to get the first dimension name
        dim = "idx1"
        if dim != dims:
            raise ValueError("Only one dimension is supported")
        name = attribute.name
        return f"""
        !Internal variables
        integer :: {dims}
        if (allocated(this%{name})) then
            do {dim} = 1,size(this%{name}, 1)
                call this%{name}({dim})%destroy()
            end do
            deallocate(this%{name})
        end if""".lstrip()
    if attribute.is_string() or not attribute.is_primitive():
        return f"call this%{attribute.name}%destroy()"
    else:
        return f"if (allocated(this%{attribute.name})) deallocate(this%{attribute.name})"


def __attribute_init(attribute: BlueprintAttribute,atype: str):
    field_name = to_field_name(attribute.name)
    if attribute.is_blueprint():
        atype = f"type({atype})"
    if attribute.is_array():
        dims = ",".join(attribute.dimensions).replace("*", ":")
        if attribute.is_variable_array():
            return f"{atype}, dimension({dims}), allocatable, public :: {field_name}"
        else:
            return f"{atype}, dimension({dims}), public :: {field_name}"
    elif attribute.is_primitive():
        type_init = atype + ", public :: " + field_name
        if not attribute.is_string():
            default = __find_default_value(attribute)
            if default:
                type_init += " = " + str(default)

        return type_init
    else:
        if is_allocatable(attribute):
            return atype + ", allocatable, public :: " + field_name
        else:
            return atype + ", public :: " + field_name

def __map(key, values):
    converted = values[key]
    if not converted:
        raise ValueError("Unkown type " + key)
    return converted

def __find_default_value(attribute: BlueprintAttribute):
    default_value = attribute.get("default")
    if default_value is not None:
        return __convert_default(attribute,default_value)
    return default_value

def __convert_default(attribute: BlueprintAttribute, default_value):
    # converts json value to fortran value
    if isinstance(default_value,str):
        if default_value == '' or default_value == '""':
            return '""'
        elif attribute.is_integer():
            return int(default_value)
        elif attribute.is_number():
            return float(default_value)
        elif attribute.is_boolean():
            conversion = {
                "false": ".false.",
                "true": ".true.",
            }
            return conversion.get(default_value, default_value)
        else:
            return "'" + default_value + "'"
