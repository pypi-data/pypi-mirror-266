# Copyright (c) 2023-2024 Geosiris.
# SPDX-License-Identifier: Apache-2.0
from io import BytesIO
from typing import Optional, Any

import energyml
from xsdata.exceptions import ParserError
from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import JsonSerializer
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from .introspection import get_class_from_name
from .xml import get_class_name_from_xml, get_tree


def read_energyml_xml_bytes_as_class(file: bytes, obj_class: type) -> Any:
    """
    Read an xml file into the instance of type :param:`obj_class`.
    :param file:
    :param obj_class:
    :return:
    """
    parser = XmlParser()
    try:
        return parser.from_bytes(file, obj_class)
    except ParserError as e:
        print(f"Failed to parse file {file} as class {obj_class}")
        raise e


def read_energyml_xml_bytes(file: bytes) -> Any:
    """
    Read an xml file. The type of object is searched from the xml root name.
    :param file:
    :return:
    """
    return read_energyml_xml_bytes_as_class(
        file, get_class_from_name(get_class_name_from_xml(get_tree(file)))
    )


def read_energyml_xml_io(file: BytesIO, obj_class: Optional[type] = None) -> Any:
    if obj_class is not None:
        return read_energyml_xml_bytes_as_class(file.getbuffer(), obj_class)
    else:
        return read_energyml_xml_bytes(file.getbuffer())


def read_energyml_xml_str(file_content: str) -> Any:
    parser = XmlParser()
    # from energyml.resqml.v2_2.resqmlv2 import TriangulatedSetRepresentation
    return parser.from_string(
        file_content,
        get_class_from_name(get_class_name_from_xml(get_tree(file_content))),
    )  # , TriangulatedSetRepresentation)


def read_energyml_xml_file(file_path: str) -> Any:
    xml_content = ""
    with open(file_path, "r") as f:
        xml_content = f.read()
    parser = XmlParser()
    # from energyml.resqml.v2_2.resqmlv2 import TriangulatedSetRepresentation
    # return parser.parse(file_path)  # , TriangulatedSetRepresentation)
    return parser.parse(
        file_path,
        get_class_from_name(get_class_name_from_xml(get_tree(xml_content))),
    )


def serialize_xml(obj) -> str:
    context = XmlContext(
        # element_name_generator=text.camel_case,
        # attribute_name_generator=text.kebab_case
    )
    serializer_config = SerializerConfig(indent="  ")
    serializer = XmlSerializer(context=context, config=serializer_config)
    return serializer.render(obj)


def serialize_json(obj) -> str:
    context = XmlContext(
        # element_name_generator=text.camel_case,
        # attribute_name_generator=text.kebab_case
    )
    serializer_config = SerializerConfig(indent="  ")
    serializer = JsonSerializer(context=context, config=serializer_config)
    return serializer.render(obj)
