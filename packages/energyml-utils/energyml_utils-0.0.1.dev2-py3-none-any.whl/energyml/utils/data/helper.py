# Copyright (c) 2023-2024 Geosiris.
# SPDX-License-Identifier: Apache-2.0
import inspect
import sys
from typing import Any, Optional, Callable, Literal, List, Union, Tuple

from .hdf import get_hdf5_path_from_external_path, HDF5FileReader, get_hdf_reference, get_crs_obj
from ..epc import Epc, get_obj_identifier
from ..introspection import snake_case, get_object_attribute_no_verif, \
    search_attribute_matching_name_with_path, search_attribute_matching_name, flatten_concatenation, \
    search_attribute_in_upper_matching_name

_ARRAY_NAMES_ = [
    "BooleanArrayFromDiscretePropertyArray",
    "BooleanArrayFromIndexArray",
    "BooleanConstantArray",
    "BooleanExternalArray",
    "BooleanHdf5Array",
    "BooleanXmlArray",
    "CompoundExternalArray",
    "DasTimeArray",
    "DoubleConstantArray",
    "DoubleHdf5Array",
    "DoubleLatticeArray",
    "ExternalDataArray",
    "FloatingPointConstantArray",
    "FloatingPointExternalArray",
    "FloatingPointLatticeArray",
    "FloatingPointXmlArray",
    "IntegerArrayFromBooleanMaskArray",
    "IntegerConstantArray",
    "IntegerExternalArray",
    "IntegerHdf5Array",
    "IntegerLatticeArray",
    "IntegerRangeArray",
    "IntegerXmlArray",
    "JaggedArray",
    "ParametricLineArray",
    "ParametricLineFromRepresentationLatticeArray",
    "Point2DHdf5Array",
    "Point3DFromRepresentationLatticeArray",
    "Point3DHdf5Array",
    "Point3DLatticeArray",
    "Point3DParametricArray",
    "Point3DZvalueArray",
    "ResqmlJaggedArray",
    "StringConstantArray",
    "StringExternalArray",
    "StringHdf5Array",
    "StringXmlArray"
]


def get_array_reader_function(array_type_name: str) -> Optional[Callable]:
    """
    Returns the name of the potential appropriate function to read an object with type is named :param array_type_name
    :param array_type_name: the initial type name
    :return:
    """
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if name == f"read_{snake_case(array_type_name)}":
            return obj
    return None


def _array_name_mapping(array_type_name: str) -> str:
    """
    Transform the type name to match existing reader function
    :param array_type_name:
    :return:
    """
    array_type_name = array_type_name.replace("3D", "3d").replace("2D", "2d")
    if array_type_name.endswith("ConstantArray"):
        return "ConstantArray"
    elif "External" in array_type_name or "Hdf5" in array_type_name:
        return "ExternalArray"
    elif array_type_name.endswith("XmlArray"):
        return "XmlArray"
    elif "Jagged" in array_type_name:
        return "JaggedArray"
    elif "Lattice" in array_type_name:
        if "Integer" in array_type_name or "Double" in array_type_name:
            return "int_double_lattice_array"
    return array_type_name


def read_array(
        energyml_array: Any,
        root_obj: Optional[Any] = None,
        path_in_root: Optional[str] = None,
        epc: Optional[Epc] = None
) -> List[Any]:
    """
    Read an array and return a list. The array is read depending on its type. see. :py:func:`energyml.utils.data.helper.get_supported_array`
    :param energyml_array:
    :param root_obj:
    :param path_in_root:
    :param epc:
    :return:
    """
    if isinstance(energyml_array, list):
        return energyml_array
    array_type_name = _array_name_mapping(type(energyml_array).__name__)

    reader_func = get_array_reader_function(array_type_name)
    if reader_func is not None:
        return reader_func(
            energyml_array=energyml_array,
            root_obj=root_obj,
            path_in_root=path_in_root,
            epc=epc,
        )
    else:
        print(f"Type {array_type_name} is not supported: function read_{snake_case(array_type_name)} not found")
        raise Exception(f"Type {array_type_name} is not supported\n\t{energyml_array}: \n\tfunction read_{snake_case(array_type_name)} not found")


def get_supported_array() -> List[str]:
    """
    Return a list of the supported arrays for the use of :py:func:`energyml.utils.data.helper.read_array` function.
    :return:
    """
    return [x for x in _ARRAY_NAMES_ if get_array_reader_function(_array_name_mapping(x)) is not None]


def get_not_supported_array():
    """
    Return a list of the NOT supported arrays for the use of :py:func:`energyml.utils.data.helper.read_array` function.
    :return:
    """
    return [x for x in _ARRAY_NAMES_ if get_array_reader_function(_array_name_mapping(x)) is None]


def read_constant_array(
        energyml_array: Any,
        root_obj: Optional[Any] = None,
        path_in_root: Optional[str] = None,
        epc: Optional[Epc] = None
) -> List[Any]:
    """
    Read a constant array ( BooleanConstantArray, DoubleConstantArray, FloatingPointConstantArray, IntegerConstantArray ...)
    :param energyml_array:
    :param root_obj:
    :param path_in_root:
    :param epc:
    :return:
    """
    # print(f"Reading constant array\n\t{energyml_array}")

    value = get_object_attribute_no_verif(energyml_array, "value")
    count = get_object_attribute_no_verif(energyml_array, "count")

    # print(f"\tValue : {[value for i in range(0, count)]}")

    return [value for i in range(0, count)]


def read_xml_array(
        energyml_array: Any,
        root_obj: Optional[Any] = None,
        path_in_root: Optional[str] = None,
        epc: Optional[Epc] = None
) -> List[Any]:
    """
    Read a xml array ( BooleanXmlArray, FloatingPointXmlArray, IntegerXmlArray, StringXmlArray ...)
    :param energyml_array:
    :param root_obj:
    :param path_in_root:
    :param epc:
    :return:
    """
    values = get_object_attribute_no_verif(energyml_array, "values")
    # count = get_object_attribute_no_verif(energyml_array, "count_per_value")
    return values


def read_jagged_array(
        energyml_array: Any,
        root_obj: Optional[Any] = None,
        path_in_root: Optional[str] = None,
        epc: Optional[Epc] = None
) -> List[Any]:
    """
    Read a jagged array
    :param energyml_array:
    :param root_obj:
    :param path_in_root:
    :param epc:
    :return:
    """
    elements = read_array(
        energyml_array=get_object_attribute_no_verif(energyml_array, "elements"),
        root_obj=root_obj,
        path_in_root=path_in_root + ".elements",
        epc=epc,
    )
    cumulative_length = read_array(
        energyml_array=read_array(get_object_attribute_no_verif(energyml_array, "cumulative_length")),
        root_obj=root_obj,
        path_in_root=path_in_root + ".cumulative_length",
        epc=epc,
    )

    res = []
    previous = 0
    for cl in cumulative_length:
        res.append(elements[previous: cl])
        previous = cl
    return res


def read_external_array(
        energyml_array: Any,
        root_obj: Optional[Any] = None,
        path_in_root: Optional[str] = None,
        epc: Optional[Epc] = None
) -> List[Any]:
    """
    Read an external array (BooleanExternalArray, BooleanHdf5Array, DoubleHdf5Array, IntegerHdf5Array, StringExternalArray ...)
    :param energyml_array:
    :param root_obj:
    :param path_in_root:
    :param epc:
    :return:
    """
    hdf5_path = get_hdf5_path_from_external_path(
                external_path_obj=energyml_array,
                path_in_root=path_in_root,
                root_obj=root_obj,
                epc=epc,
    )
    h5_reader = HDF5FileReader()
    path_in_external = get_hdf_reference(energyml_array)[0]

    result_array = h5_reader.read_array(hdf5_path, path_in_external)

    if path_in_root.lower().endswith("points") and len(result_array) > 0 and len(result_array[0]) == 3:
        crs = get_crs_obj(
            context_obj=energyml_array,
            path_in_root=path_in_root,
            root_obj=root_obj,
            epc=epc,
        )
        zincreasing_downward = is_z_reversed(crs)

        if zincreasing_downward:
            result_array = list(map(lambda p: [p[0], p[1], -p[2]], result_array))

    return result_array


def read_int_double_lattice_array(
        energyml_array: Any,
        root_obj: Optional[Any] = None,
        path_in_root: Optional[str] = None,
        epc: Optional[Epc] = None
):
    """
    Read DoubleLatticeArray or IntegerLatticeArray.
    :param energyml_array:
    :param root_obj:
    :param path_in_root:
    :param epc:
    :return:
    """
    start_value = get_object_attribute_no_verif(energyml_array, "start_value")
    offset = get_object_attribute_no_verif(energyml_array, "offset")

    result = []

    # if len(offset) == 1:
    #     pass
    # elif len(offset) == 2:
    #     pass
    # else:
    raise Exception(f"{type(energyml_array)} read with an offset of length {len(offset)} is not supported")

    # return result


def _point_as_array(point: Any) -> List:
    """
    Transform a point that has "coordinate1", "coordinate2", "coordinate3" as attributes into a list.
    :param point:
    :return:
    """
    return [
        get_object_attribute_no_verif(point, "coordinate1"),
        get_object_attribute_no_verif(point, "coordinate2"),
        get_object_attribute_no_verif(point, "coordinate3"),
    ]


def prod_n_tab(val: Union[float, int, str], tab: List[Union[float, int, str]]):
    """
    Multiply every value of the list 'tab' by the constant 'val'
    :param val:
    :param tab:
    :return:
    """
    return list(map(lambda x: x*val, tab))


def sum_lists(l1: List, l2: List):
    """
    Sums 2 lists values.

    Example:
        [1,1,1] and [2,2,3,6] gives : [3,3,4,6]

    :param l1:
    :param l2:
    :return:
    """
    return [l1[i] + l2[i] for i in range(min(len(l1), len(l2)))]+max(l1, l2, key=len)[min(len(l1), len(l2)):]


def read_point3d_zvalue_array(
        energyml_array: Any,
        root_obj: Optional[Any] = None,
        path_in_root: Optional[str] = None,
        epc: Optional[Epc] = None
):
    """
    Read a Point3D2ValueArray
    :param energyml_array:
    :param root_obj:
    :param path_in_root:
    :param epc:
    :return:
    """
    supporting_geometry = get_object_attribute_no_verif(energyml_array, "supporting_geometry")
    sup_geom_array = read_array(
        energyml_array=supporting_geometry,
        root_obj=root_obj,
        path_in_root=path_in_root + ".SupportingGeometry",
        epc=epc,
    )

    zvalues = get_object_attribute_no_verif(energyml_array, "zvalues")
    zvalues_array = flatten_concatenation(read_array(
        energyml_array=zvalues,
        root_obj=root_obj,
        path_in_root=path_in_root + ".ZValues",
        epc=epc,
    ))

    count = 0

    for i in range(len(sup_geom_array)):
        try:
            sup_geom_array[i][2] = zvalues_array[i]
        except Exception as e:
            if count == 0:
                print(e, f": {i} is out of bound of {len(zvalues_array)}")
                count = count + 1

    return sup_geom_array


def read_point3d_from_representation_lattice_array(
        energyml_array: Any,
        root_obj: Optional[Any] = None,
        path_in_root: Optional[str] = None,
        epc: Optional[Epc] = None
):
    """
    Read a Point3DFromRepresentationLatticeArray.

    Note: Only works for Grid2DRepresentation.

    :param energyml_array:
    :param root_obj:
    :param path_in_root:
    :param epc:
    :return:
    """
    supporting_rep_identifier = get_obj_identifier(get_object_attribute_no_verif(energyml_array, "supporting_representation"))
    print(f"energyml_array : {energyml_array}\n\t{supporting_rep_identifier}")
    supporting_rep = epc.get_object_by_identifier(supporting_rep_identifier)

    # TODO chercher un pattern \.*patch\.*.[d]+ pour trouver le numero du patch dans le path_in_root puis lire le patch
    # print(f"path_in_root {path_in_root}")

    result = []
    if "grid2d" in str(type(supporting_rep)).lower():
        patch_path, patch = search_attribute_matching_name_with_path(supporting_rep, "Grid2dPatch")[0]
        points = read_grid2d_patch(
            patch=patch,
            grid2d=supporting_rep,
            path_in_root=patch_path,
            epc=epc,
        )
        # TODO: take the points by there indices from the NodeIndicesOnSupportingRepresentation
        result = points

    else:
        raise Exception(f"Not supported type {type(energyml_array)} for object {type(root_obj)}")
    # pour trouver les infos qu'il faut
    return result


def read_grid2d_patch(
        patch: Any,
        grid2d: Optional[Any] = None,
        path_in_root: Optional[str] = None,
        epc: Optional[Epc] = None
) -> List:
    points_path, points_obj = search_attribute_matching_name_with_path(patch, "Geometry.Points")[0]

    return read_array(
        energyml_array=points_obj,
        root_obj=grid2d,
        path_in_root=path_in_root + points_path,
        epc=epc,
    )


def read_point3d_lattice_array(
        energyml_array: Any,
        root_obj: Optional[Any] = None,
        path_in_root: Optional[str] = None,
        epc: Optional[Epc] = None
) -> List:
    """
    Read a Point3DLatticeArray.

    Note: If a CRS is found and its 'ZIncreasingDownward' is set to true or its

    :param energyml_array:
    :param root_obj:
    :param path_in_root:
    :param epc:
    :return:
    """
    result = []
    origin = _point_as_array(get_object_attribute_no_verif(energyml_array, "origin"))
    offset = get_object_attribute_no_verif(energyml_array, "offset")

    if len(offset) == 2:
        slowest = offset[0]
        fastest = offset[1]

        crs_sa_count = search_attribute_in_upper_matching_name(
            obj=energyml_array,
            name_rgx="SlowestAxisCount",
            root_obj=root_obj,
            current_path=path_in_root,
        )

        crs_fa_count = search_attribute_in_upper_matching_name(
            obj=energyml_array,
            name_rgx="FastestAxisCount",
            root_obj=root_obj,
            current_path=path_in_root,
        )

        crs = get_crs_obj(
            context_obj=energyml_array,
            path_in_root=path_in_root,
            root_obj=root_obj,
            epc=epc,
        )
        zincreasing_downward = is_z_reversed(crs)

        slowest_vec = _point_as_array(get_object_attribute_no_verif(slowest, "offset"))
        slowest_spacing = read_array(get_object_attribute_no_verif(slowest, "spacing"))
        slowest_table = list(map(lambda x: prod_n_tab(x, slowest_vec), slowest_spacing))

        fastest_vec = _point_as_array(get_object_attribute_no_verif(fastest, "offset"))
        fastest_spacing = read_array(get_object_attribute_no_verif(fastest, "spacing"))
        fastest_table = list(map(lambda x: prod_n_tab(x, fastest_vec), fastest_spacing))

        slowest_size = len(slowest_table)
        fastest_size = len(fastest_table)

        if len(crs_sa_count) > 0 and len(crs_fa_count) and crs_sa_count[0] == fastest_size:
            print("reversing order")
            # if offset were given in the wrong order
            tmp_table = slowest_table
            slowest_table = fastest_table
            fastest_table = tmp_table

            tmp_size = slowest_size
            slowest_size = fastest_size
            fastest_size = tmp_size

        for i in range(slowest_size):
            for j in range(fastest_size):
                previous_value = origin
                # to avoid a sum of the parts of the array at each iteration, I take the previous value in the same line
                # number i and add the fastest_table[j] value

                if j > 0:
                    if i > 0:
                        line_idx = i * fastest_size  # numero de ligne
                        previous_value = result[line_idx + j - 1]
                    else:
                        previous_value = result[j - 1]
                    if zincreasing_downward:
                        result.append(sum_lists(previous_value, slowest_table[i - 1]))
                    else:
                        result.append(sum_lists(previous_value, fastest_table[j - 1]))
                else:
                    if i > 0:
                        prev_line_idx = (i - 1) * fastest_size  # numero de ligne precedent
                        previous_value = result[prev_line_idx]
                        if zincreasing_downward:
                            result.append(sum_lists(previous_value, fastest_table[j - 1]))
                        else:
                            result.append(sum_lists(previous_value, slowest_table[i - 1]))
                    else:
                        result.append(previous_value)
    else:
        raise Exception(f"{type(energyml_array)} read with an offset of length {len(offset)} is not supported")

    return result


def is_z_reversed(crs: Optional[Any]) -> bool:
    """
    Returns True if the Z axe is reverse (ZIncreasingDownward=='True' or VerticalAxis.Direction=='down')
    :param crs:
    :return: By default, False is returned (if 'crs' is None)
    """
    reverse_z_values = False
    if crs is not None:
        # resqml 201
        zincreasing_downward = search_attribute_matching_name(crs, "ZIncreasingDownward")
        if len(zincreasing_downward) > 0:
            reverse_z_values = zincreasing_downward[0]

        # resqml >= 22
        vert_axis = search_attribute_matching_name(crs, "VerticalAxis.Direction")
        if len(vert_axis) > 0:
            reverse_z_values = vert_axis[0].lower() == "down"

    return reverse_z_values


# def read_boolean_constant_array(
#         energyml_array: Any,
#         root_obj: Optional[Any] = None,
#         path_in_root: Optional[str] = None,
#         epc: Optional[Epc] = None
# ):
#     print(energyml_array)
