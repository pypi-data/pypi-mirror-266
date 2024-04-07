

from typing import Dict
from dmtgen.common.blueprint import Blueprint
from dmtgen.common.blueprint_attribute import BlueprintAttribute

from .common import to_type_name, to_field_name
from . import simos

H5_FUNCTION_TYPES = {"number": "Double", "double": "Double", "string": "String", "integer": "Int"}

def create_model(blueprint: Blueprint):
    """Create hdf5 model from blueprint"""
    model = {
        "load": __create_load_model(blueprint),
        "save": __create_save_model(blueprint)
    }

    attributes = []

    maxdim = 0
    for attribute in blueprint.all_attributes.values():
        if attribute.is_array():
            model["has_array"] = True
            maxdim = max(maxdim, len(attribute.dimensions))
        attr_model = {
            "name": attribute.name,
            "is_optional": attribute.optional,
            "save": __create_attribute_save(blueprint,attribute),
            "load": __create_attribute_load(blueprint,attribute).rstrip().lstrip(),
        }
        attributes.append(attr_model)

    # TODO REMOVE WHEN DONE!
    for i, attribute in enumerate(attributes):
        if attribute["name"] == "name":
            attributes.append(attributes.pop(i))
            break
    for i, attribute in enumerate(attributes):
        if attribute["name"] == "description":
            attributes.append(attributes.pop(i))
            break

    model["attributes"] = attributes
    return model


def __create_load_model(blueprint: Blueprint) -> Dict:
    """Create HDF5 load model from blueprint"""
    model = {}
    inits = []
    if simos.has_array(blueprint) or simos.has_single_string(blueprint):
        inits.append("integer :: sv")

    __temp_variables_for_int_or_boolean_variables(blueprint,inits)

    if simos.has_atomic_array(blueprint):
        inits.append("integer, dimension(:), allocatable :: diml")

    if simos.has_boolean(blueprint):
        inits.append("integer :: logicalToIntSingle")

    if simos.has_boolean_array(blueprint) or simos.has_non_atomic_array(blueprint):
        inits.append("integer :: idx1")

    if simos.has_single_string(blueprint):
        inits.append("integer :: strSize")

    if simos.has_non_atomic_array(blueprint):
        inits.append("integer :: idx, idxMod")
        inits.append("integer :: subGroupIndex2")
        inits.append("integer :: orderSize,orderRank, ordInd, arrDimSize")
        inits.append("integer, dimension(:), allocatable :: arrDim")
        inits.append("integer, dimension(1) :: orderDim")
        inits.append("character(kind=c_char), allocatable :: order_arr(:,:)")
        inits.append("type(String) :: orderList")
        inits.append("type(String), allocatable ::listOfNames(:)")

    if simos.has_non_atomic_array(blueprint) or simos.has_single_string(blueprint):
        inits.append("character(kind=c_char), allocatable :: cc_a(:)")

    if simos.has_non_atomic(blueprint):
        inits.append("integer :: subGroupIndex")

    model["inits"] = inits
    return model

def __create_save_model(blueprint: Blueprint) -> Dict:
    """Create HDF5 save model from blueprint"""
    model = {}
    inits = []

    if simos.has_array(blueprint) or simos.has_single_string(blueprint):
        inits.append("integer :: sv")
        inits.append("integer, dimension(:), allocatable :: diml")

    if simos.has_boolean(blueprint):
        inits.append("integer :: logicalToIntSingle")


    if simos.has_non_atomic(blueprint):
        inits.append("integer :: subGroupIndex")

    __temp_index_variables_for_saving_and_loading(blueprint,inits)

    if simos.has_non_atomic_array(blueprint):
        inits.append("integer :: subGroupIndex2")
        inits.append("type(String) :: orderList")

    model["inits"] = inits
    model["order"]=__create_save_order(blueprint)
    return model

def __temp_variables_for_int_or_boolean_variables(blueprint: Blueprint, inits: list):
    for attribute in blueprint.all_attributes.values():
        if attribute.is_integer() or attribute.is_boolean():
            if attribute.is_array():
                ndim = len(attribute.dimensions)
                dims = __ops(":", ndim)
                inits.append(f"integer, dimension({dims}), allocatable :: tmp_int_matrix{ndim}")

def __temp_index_variables_for_saving_and_loading(blueprint: Blueprint, inits: list):
    # FIXME
    if simos.has_array(blueprint):
        inits.append("integer :: idx1")

def __ops(op, ndim):
    return ",".join([op for i in range(ndim)])


def __create_attribute_save(blueprint: Blueprint, attribute: BlueprintAttribute):
    name = attribute.name
    field_name = to_field_name(name)
    if not attribute.contained:
        raise NotImplementedError("Only contained attributes are supported")
    body = []
    if attribute.is_primitive():
        __create_primitive_save(body,blueprint,attribute,field_name)
    else:
        __create_entity_save(body,blueprint,attribute)
    model = {
        "body": body
    }
    if attribute.optional or attribute.is_string():
        model["optional_statement"] = __create_is_set_statement(attribute)
    return model

def __add_simple_error_check(body: list,field_name):
    body.append("if (H5A_IS_ERROR(errorj)) then")
    body.append(f"error_message = 'Error during saving of {field_name}'")
    body.append("call throw(io_exception(error_message))")
    body.append("  return")
    body.append("end if")


def __create_primitive_save(body: list, blueprint: Blueprint, attribute: BlueprintAttribute, field_name: str):
    if attribute.is_array():
        __create_primitive_array_save(body,blueprint,attribute)
    else:
        __create_primitive_single_save(body,attribute,field_name)

def __create_primitive_single_save(body: list, attribute: BlueprintAttribute, field_name: str):
    if attribute.is_string():
        body.append(f"errorj = H5A_writeStringWithLength(groupIndex, '{field_name}' // c_null_char,this%{field_name}%toChars() // c_null_char)")
        __add_simple_error_check(body,field_name)
    elif attribute.is_boolean():
        block = __boolean_save(attribute)
        body.extend(block.rstrip().splitlines())
    else:
        f_name = H5_FUNCTION_TYPES[attribute.type]
        body.append(f"errorj = H5A_Write{f_name}(groupIndex, '{field_name}' // c_null_char,this%{field_name})")
        __add_simple_error_check(body,field_name)

def __create_primitive_array_save(body: list, blueprint: Blueprint, attribute: BlueprintAttribute):
    res =  __primitive_array_save(blueprint,attribute).lstrip().rstrip()
    body.extend(res.splitlines())

def __create_entity_save(body: list,blueprint, attribute: BlueprintAttribute):
    if attribute.is_array():
        __create_entity_array_save(body,blueprint, attribute)
    else:
        __create_entity_single_save(body,attribute)

def __create_entity_array_save(body: list,blueprint, attribute: BlueprintAttribute):
    block = __entity_array_save(blueprint, attribute)
    body.extend(block.rstrip().splitlines())

def __create_entity_single_save(body: list, attribute: BlueprintAttribute):
    block = __entity_single_save(attribute)
    body.extend(block.rstrip().splitlines())

def __entity_single_save(attribute: BlueprintAttribute):
    name = attribute.name
    # FIXME: Why not allocatable??
    if True or attribute.is_required():
        return f"""
        if (this%{name}%isValid()) then
            subGroupIndex = H5A_OpenOrCreateEntity(groupIndex, '{name}' // c_null_char)
            call this%{name}%save_HDF5(subGroupIndex)
            errorj=H5A_CloseEntity(subGroupIndex)
            if (exception_occurred()) return
        else
            error_message = 'Error during saving of {name}'        &
                + ' - a non-optional object is invalid'
            call throw(io_exception(error_message))
            return
        end if
        """
    else:
        return f"""
        if(allocated(this%{name})) then
            if (this%{name}%isValid()) then
                subGroupIndex = H5A_OpenOrCreateEntity(groupIndex, '{name}' // c_null_char)
                call this%{name}%save_HDF5(subGroupIndex)
                errorj=H5A_CloseEntity(subGroupIndex)
                if (exception_occurred()) return
            else
                error_message = 'Error during saving of {name}'        &
                + ' - a non-optional object is invalid'
                call throw(io_exception(error_message))
                return
            end if
        end if
        """

def __entity_array_save(blueprint: Blueprint, attribute: BlueprintAttribute):
    name = attribute.name
    bp_name = blueprint.name
    field_name = to_field_name(name)
    return f"""
    call orderList%destroy()
    if (allocated(this%{field_name})) then
        if (size(this%{field_name}) > 0) then
            if (allocated(diml)) deallocate(diml)
            allocate(diml(1),stat=sv)
            if (sv.ne.0) then
                errorj=-1
                error_message = 'Error during saving of {bp_name}, error when trying to allocat&
                    &e diml array for {field_name}'
                call throw(illegal_state_exception(error_message%toChars()))
                return
            end if
            diml=shape(this%{field_name})
            subGroupIndex = H5A_OpenOrCreateEntity(groupIndex, '{name}' // c_null_char)
            do idx1 = 1,size(this%{field_name}, 1)
                if (this%{field_name}(idx1)%isValid()) then
                    str = '{name}_' // to_string(idx1)
                    subGroupIndex2 = H5A_OpenOrCreateEntity(subGroupIndex, str%toChars() // c_null_char)
                    call this%{field_name}(idx1)%save_hdf5(subGroupIndex2)
                    errorj=H5A_CloseEntity(subGroupIndex2)
                    if (exception_occurred()) return
                    if (.not.(orderList%isEmpty())) then
                        orderList=orderList+','
                    end if
                    orderList=orderList + str
                end if
            end do
            errorj = H5A_writeStringWithLength(subGroupIndex, 'name' // c_null_char, '{attribute.description}' // c_null_char)
            if (H5A_IS_ERROR(errorj)) then
                error_message = 'Error during saving of {name}'
                call throw(io_exception(error_message))
                return
            end if
            errorj = H5A_SetDim(subGroupIndex,size(diml,1), diml)
            if (H5A_IS_ERROR(errorj)) then
                error_message = 'Error during saving of {name}'
                call throw(io_exception(error_message))
                return
            end if
            deallocate(diml)
            if (.not.(orderList%isEmpty())) then
                errorj=h5a_setOrder(subGroupIndex,orderList%toChars() // c_null_char)
                if (H5A_IS_ERROR(errorj)) then
                    error_message = 'Error during saving of {name}'
                    call throw(io_exception(error_message))
                    return
                end if
            end if
            call orderList%destroy()
            errorj=H5A_CloseEntity(subGroupIndex)
        end if
    end if
    """

def __create_is_set_statement(attribute: BlueprintAttribute):
    name = attribute.name
    field_name = to_field_name(name)
    if attribute.is_string():
        return f".not.(this%{field_name}%isEmpty())"

    return f"this%is_set_{field_name}"

def __primitive_array_save(blueprint: Blueprint, attribute: BlueprintAttribute):
    name = attribute.name
    bp_name = blueprint.name
    f_name = H5_FUNCTION_TYPES[attribute.type]
    dims = attribute.dimensions
    ndim = len(dims)
    if ndim > 1:
        sdim = f"diml({ndim}:1:-1)"
    else:
        sdim = "diml"

    if attribute.is_variable_array():
        return f"""
    if (allocated(this%{name})) then
        if (allocated(diml)) deallocate(diml)
        allocate(diml({ndim}),stat=sv)
        if (sv.ne.0) then
            errorj=-1
            error_message = 'Error during saving of {bp_name}, error when trying to allocate diml&
                & array for {name}'
            call throw(illegal_state_exception(error_message%toChars()))
            return
        end if
        diml=shape(this%{name})
        errorj = H5A_Write{f_name}Array(groupIndex, '{name}' // c_null_char,{ndim},{sdim},this%{name})
        if (H5A_IS_ERROR(errorj)) then
            error_message = 'Error during saving of {name}'
            call throw(io_exception(error_message))
            return
        end if
        deallocate(diml)
    end if
    """
    else:
        return f"""
    if (allocated(diml)) deallocate(diml)
    allocate(diml({ndim}),stat=sv)
    if (sv.ne.0) then
        errorj=-1
        error_message = 'Error during saving of {bp_name}, error when trying to allocate diml&
            & array for {name}'
        call throw(illegal_state_exception(error_message%toChars()))
        return
    end if
    diml=shape(this%{name})
    errorj = H5A_Write{f_name}Array(groupIndex, '{name}' // c_null_char,{ndim},{sdim},this%{name})
    if (H5A_IS_ERROR(errorj)) then
        error_message = 'Error during saving of {name}'
        call throw(io_exception(error_message))
        return
    end if
    deallocate(diml)
    """

def __has_settable(attribute: BlueprintAttribute):
    if attribute.is_array() or attribute.is_string():
        return False
    if attribute.is_primitive():
        return attribute.is_optional()
    return False

def __boolean_save(attribute: BlueprintAttribute):
    name = attribute.name
    field_name = to_field_name(name)
    return f"""
if (this%{field_name}) then
    logicalToIntSingle=1
else
    logicalToIntSingle=0
end if
errorj = H5A_WriteInt(groupIndex, '{name}' // c_null_char,logicalToIntSingle)
if (H5A_IS_ERROR(errorj)) then
    error_message = 'Error during saving of {name}'
    call throw(io_exception(error_message))
    return
end if""".rstrip().lstrip()


def __create_attribute_load(blueprint: Blueprint,attribute: BlueprintAttribute):
    """Create hdf5 load code"""
    name = attribute.name
    atype = attribute.type
    ftype = to_type_name(blueprint)
    field_name = to_field_name(name)

    def __primitive_single_load():
        if atype == "boolean":
            return __boolean_load()
        elif atype == "string":
            return __string_load()

        h5_type = H5_FUNCTION_TYPES[atype]
        if __has_settable(attribute):
            return f"""
        this%is_set_{field_name} = .true.
        error = H5A_Read{h5_type}(groupIndex, '{name}' // c_null_char, this%{field_name})
        if (H5A_IS_ERROR(error)) then
            this%is_set_{field_name} = .false.
        end if""".rstrip()
        else:
            return f"""
        error = H5A_Read{h5_type}(groupIndex, '{name}' // c_null_char, this%{field_name})
        if (H5A_IS_ERROR(error)) then
            error_message = 'Error during loading of {ftype}' +        &
                    ' - failed to load property {name}'
            call throw(io_exception(error_message))
            return
        end if""".rstrip()

    def __primitive_array_load():
        dims = attribute.dimensions
        ndim = len(dims)
        # diml(5),diml(4),diml(3),diml(2),diml(1)
        aldim = ",".join([f"diml({ndim-i})" for i in range(ndim)])
        h5_type = H5_FUNCTION_TYPES[atype]
        if simos.is_allocatable(attribute):
            return f"""
            if (allocated(diml)) deallocate(diml)
            allocate(diml({ndim}),stat=sv)
            if (sv.ne.0) then
                error=-1
                error_message = 'Error during loading of {ftype}, error when trying to allocate dim&
                    &l array for {name}'
                call throw(illegal_state_exception(error_message%toChars()))
                return
            end if
            error = H5A_GetArrayDims(groupIndex,'{name}' // c_null_char, diml)
            if (error >= 0) then
            if (allocated(this%{name})) deallocate(this%{name})
            allocate(this%{name}({aldim}),stat=sv)
            if (sv.ne.0) then
                error=-1
                error_message = 'Error during loading of {ftype}, error when trying to allocat&
                    &e array for {name}'
                call throw(illegal_state_exception(error_message%toChars()))
                return
            end if
            error = H5A_Read{h5_type}Array(groupIndex,'{name}' // c_null_char, this%{field_name})
            if (H5A_IS_ERROR(error)) then
                error_message = 'Error during loading of {ftype}' +        &
                        ' - failed to load property {name}'
                call throw(io_exception(error_message))
                return
            end if
            end if
            deallocate(diml)
            """.rstrip()
        else:
            return f"""
            if (allocated(diml)) deallocate(diml)
            allocate(diml({ndim}),stat=sv)
            if (sv.ne.0) then
                error=-1
                error_message = 'Error during loading of {ftype}, error when trying to allocate dim&
                    &l array for {name}'
                call throw(illegal_state_exception(error_message%toChars()))
                return
            end if
            error = H5A_GetArrayDims(groupIndex,'{name}' // c_null_char, diml)
            error = H5A_Read{h5_type}Array(groupIndex,'{name}' // c_null_char, this%{field_name})
            if (H5A_IS_ERROR(error)) then
                error_message = 'Error during loading of {ftype}' +        &
                        ' - failed to load property {name}'
                call throw(io_exception(error_message))
                return
            end if
            deallocate(diml)
            """.rstrip()

    def __boolean_load():
        if __has_settable(attribute):
            return f"""
        this%is_set_{name} = .true.
        error = H5A_ReadInt(groupIndex, '{name}' // c_null_char, logicalToIntSingle)
        if (H5A_IS_ERROR(error)) then
            this%is_set_{name} = .false.
        else
            this%{field_name} = logicalToIntSingle == 1
        end if""".rstrip()
        else:
            return f"""
        error = H5A_ReadInt(groupIndex, '{name}' // c_null_char, logicalToIntSingle)
        if (H5A_IS_ERROR(error)) then
            error_message = 'Error during loading of {ftype}.{name}'
            call throw(io_exception(error_message))
            return
        end if
        this%{field_name} = logicalToIntSingle == 1""".rstrip()

    def __string_load():
        if __has_settable(attribute):
            return f"""
        this%is_set_{name} = .true.
        error= H5A_getStringLength(groupIndex, '{name}' // c_null_char,strSize)
        if (error.ge.0) then
            this%is_set_{name} = .false.
        end if""".rstrip()
        else:
            return f"""
        error= H5A_getStringLength(groupIndex, '{name}' // c_null_char,strSize)
        if (error.ge.0) then
            if (allocated(cc_a)) deallocate(cc_a)
            allocate(character :: cc_a(strSize+1),stat=sv)
            if (sv.ne.0) then
                error=-1
                error_message = 'Error during loading of {ftype}, error when trying to alloca&
                    &te name for {name}'
                call throw(illegal_state_exception(error_message%toChars()))
                return
            end if
            error = H5A_ReadStringWithLength(groupIndex, '{name}' // c_null_char,cc_a)
            cc_a(strSize+1) = c_null_char
            this%{field_name}=String(cc_a)
            this%{field_name}=this%{name}%trim()
            deallocate(cc_a)
            if (H5A_IS_ERROR(error)) then
            error_message = 'Error during loading of {ftype}'        &
                    + ' - failed to open property {name}'
            call throw(io_exception(error_message))
                return
            end if
        end if""".rstrip()

    def __entity_array_load():
        # TODO: CLEANUP!!!
        return f"""
        call orderList%destroy()
        ! Open the array group
        subGroupIndex = H5A_OpenEntity(groupIndex,'{name}' // c_null_char)
        if (subGroupIndex.gt.0) then
            ! Read the order attribute
            error = H5A_GetOrderRank(subGroupIndex,orderRank)
            if (H5A_IS_ERROR(error)) then
                error_message = 'Error during reading of order rank of '        &
                        + ' property {name} for {ftype}'
                call throw(io_exception(error_message))
                return
            end if
            if (orderRank /= 1) then
                error_message = 'Error during loading of {ftype}'        &
                        + ' - order rank must be 1 for array {name}'
                call throw(io_exception(error_message))
                return
            end if
            error = H5A_GetOrderDim(subGroupIndex,orderDim)
            if (H5A_IS_ERROR(error)) then
                error_message = 'Error during loading of {ftype}'        &
                        + ' - order att. dimension could not be read for array: {name}'
                call throw(io_exception(error_message))
                return
            end if
            error = H5A_GetOrderSize(subGroupIndex,orderSize)
            if (H5A_IS_ERROR(error)) then
                error_message = 'Error during loading of {ftype}'        &
                        + ' - order not found for array {name}'
                call throw(io_exception(error_message))
                return
            end if
            if (orderDim(1).gt.1) then
                if (allocated(order_arr)) deallocate(order_arr)
                allocate(character :: order_arr(orderSize, orderDim(1)),stat=sv)
                if (sv.ne.0) then
                    error=-1
                    error_message = 'Error during loading of {ftype}, error when trying to alloca&
                        &te orderList for {name}'
                    call throw(illegal_state_exception(error_message%toChars()))
                    return
                end if
                error = H5A_GetOrderArray(subGroupIndex, order_arr)
                if (H5A_IS_ERROR(error)) then
                    error_message = 'Error during loading of {ftype} - '        &
                            + ' could not get array order of property {name}'
                    call throw(io_exception(error_message))
                    return
                end if
                if (allocated(listOfNames)) deallocate(listOfNames)
                allocate(listOfNames(orderDim(1)),stat=sv)
                if (sv.ne.0) then
                    error=-1
                    error_message = 'Error during loading of {ftype}, error when trying to alloca&
                        &te listOfNames for {name}'
                    call throw(illegal_state_exception(error_message%toChars()))
                    return
                end if
                if (allocated(cc_a)) deallocate(cc_a)
                allocate(character :: cc_a(orderSize+1),stat=sv)
                if (sv.ne.0) then
                    error=-1
                    error_message = 'Error during loading of {ftype}, error when trying to alloca&
                        &te orderList for {name}'
                    call throw(illegal_state_exception(error_message%toChars()))
                    return
                end if
                do ordInd=1,orderDim(1)
                    cc_a(1:orderSize)=order_arr(:,ordInd)
                    cc_a(orderSize+1)=c_null_char
                    listOfNames(ordInd)=String(cc_a)
                    listOfNames(ordInd) = listOfNames(ordInd)%trim()
                end do
                deallocate(order_arr)
            else
                if (allocated(cc_a)) deallocate(cc_a)
                allocate(character :: cc_a(orderSize+1),stat=sv)
                if (sv.ne.0) then
                    error=-1
                    error_message = 'Error during loading of {ftype}, error when trying to alloca&
                        &te orderList for {name}'
                    call throw(illegal_state_exception(error_message%toChars()))
                    return
                end if
                error = H5A_GetOrder(subGroupIndex, cc_a)
                if (H5A_IS_ERROR(error)) then
                    error_message = 'Error during loading of {ftype}'        &
                                 // ' - could not get order of property {name}'
                    call throw(io_exception(error_message))
                    return
                	end if
                cc_a(orderSize+1) = c_null_char
                orderList=String(cc_a)
                deallocate(cc_a)
                listOfNames = orderList%split(',')
            end if
            ! Read the arrDim attribute
            error = H5A_GetDimSize(subGroupIndex,arrDimSize)
            if (error < 0) then
                arrDimSize = 1
                error = 0
            end if
            if (arrDimSize /= 1) then
                    error_message = 'Error during loading of {ftype},'        &
                                   //' arrDim length is not consistent with the data model'        &
                                   //' for array: {name}'
                    call throw(io_exception(error_message))
                    return
            end if
            if (allocated(arrDim)) deallocate(arrDim)
            allocate(arrDim(arrDimSize),stat=sv)
            if (sv.ne.0) then
                error=-1
                error_message = 'Error during loading of {ftype}, error when trying to alloca&
                    &te arrDim array for {name}'
                call throw(illegal_state_exception(error_message%toChars()))
                return
            end if
            error = H5A_GetDim(subGroupIndex, arrDim)
            if (error < 0) then
                if (arrDimSize == 1) then
                    arrDim(1) = size(listOfNames)
                    error = 0
                else
                    error_message = 'Error during loading of {ftype}'        &
                            + ' - arrDim was not found for array {name}'
                    call throw(io_exception(error_message))
                end if
            end if
            ! Allocate the array
            if (allocated(this%{field_name})) deallocate(this%{field_name})
            allocate(this%{field_name}(arrDim(1)),stat=sv)
            if (sv.ne.0) then
                error=-1
                error_message = 'Error during loading of {ftype}, error when trying to alloca&
                    &te {name}'
                call throw(illegal_state_exception(error_message%toChars()))
                return
            end if
            ! Read each component
            do idx=1,size(listOfNames)
                subGroupIndex2 = H5A_OpenEntity(subGroupIndex, listOfNames(idx)%toChars() // c_null_char)
                idxMod = idx
                idx1 = idxMod
                if (subGroupIndex2.gt.0) then
                    call this%{field_name}(idx1)%default_init(listOfNames(idx)%toChars())
                    call this%{field_name}(idx1)%load_HDF5(subGroupIndex2)
                    error=H5A_CloseEntity(subGroupIndex2)
                    if (exception_occurred()) return
                else
                    error_message = 'Error during loading of {ftype}'        &
                            + ' - group not found: ' // listOfNames(idx)%toChars()
                    call throw(io_exception(error_message))
                    return
                end if
            end do
            if (allocated(listOfNames)) deallocate(listOfNames)
        else
            allocate(this%{field_name}(0))
        end if
        call orderList%destroy()
        error=H5A_CloseEntity(subGroupIndex)
        """

    def __entity_single_load():
        if attribute.optional:
            return f"""
        this%is_set_{name} = .true.
        subGroupIndex = H5A_OpenEntity(groupIndex,'{name}' // c_null_char)
        if (H5A_IS_ERROR(subGroupIndex)) then
            this%is_set_{name} = .false.
        end if
        if (subGroupIndex>0) then
            call this%{field_name}%default_init('{name}')
            call this%{field_name}%load_HDF5(subGroupIndex)
            error=H5A_CloseEntity(subGroupIndex)
            if (exception_occurred()) return
        end if"""
        else:
            return f"""
        subGroupIndex = H5A_OpenEntity(groupIndex,'{name}' // c_null_char)
        if (H5A_IS_ERROR(subGroupIndex)) then
            error_message = 'Error during loading of {ftype}'        &
                    + ' - failed to open property {name}'
            call throw(io_exception(error_message))
            return
        end if
        if (subGroupIndex>0) then
            call this%{field_name}%default_init('{name}')
            call this%{field_name}%load_HDF5(subGroupIndex)
            error=H5A_CloseEntity(subGroupIndex)
            if (exception_occurred()) return
        else
            error_message = 'Error during loading of {ftype}'        &
                    + ' - failed to open property {name}'
            call throw(io_exception(error_message))
            return
        end if"""

    if attribute.is_primitive():
        if attribute.is_array():
            return __primitive_array_load()
        return __primitive_single_load()
    else:
        if attribute.is_array():
            return __entity_array_load()
        return __entity_single_load()


def __create_save_order(blueprint: Blueprint):
    """Create save order code"""
    attr= blueprint.all_attributes
    res = "errorj = h5a_setOrder(groupIndex,'&\n"
    offset = "                    "
    for a in attr.values():
        res += f"{offset}{a.name},&\n"
    res += f"{offset}'// c_null_char)"
    return res
