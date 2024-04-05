import enum
import inspect
import logging
import types
import typing
from types import GenericAlias
from typing import Callable

from pyconfig_extension import guard
from pyconfig_extension.abstracts.binder.binder_options import BinderOptions
from pyconfig_extension.abstracts.binder.binding_point import BindingPoint
from pyconfig_extension.abstracts.iconfiguration import IConfiguration, IConfigurationSection


def get(configuration: IConfiguration, klass_type: type, configure_options: Callable[[BinderOptions], None]) -> object:
    guard.check_none(configuration)

    options = BinderOptions()
    if configure_options is not None:
        configure_options(options)

    if isinstance(configuration,
                  IConfigurationSection) and configuration.value is None and klass_type in default_values:
        return default_values[klass_type]
    binding_point = BindingPoint()
    bind_instance(klass_type, binding_point, configuration, options)
    return binding_point.value


def bind_instance(klass_type: type, binding_point: BindingPoint, config: IConfiguration, options: BinderOptions):
    if klass_type == IConfigurationSection:
        binding_point.try_set_value(config)
        return
    if isinstance(config, IConfigurationSection) and config.value is None and _is_optional(klass_type):
        binding_point.try_set_value(None)
        return
    if isinstance(config, IConfigurationSection) and config.value is not None:
        check, result, error = try_convert_value(klass_type, config.value, config.path)
        if check:
            if error is not None:
                raise error
            binding_point.try_set_value(result)
            return

    if config is not None and len(config.get_children()) > 0:
        if binding_point.value is None:
            if binding_point.is_readonly:
                return
            instance = create_instance(klass_type, config, options)
            binding_point.set_value(instance)

        instance = binding_point.value
        if _is_list(klass_type):
            bind_collection(instance, config, options, klass_type)
        elif _is_set(klass_type):
            bind_set(instance, config, options, klass_type)
        elif _is_dictionary(klass_type):
            bind_dictionary(instance, config, options, klass_type)
        else:
            bind_properties(instance, config, options)
    elif config is not None and len(config.get_children()) == 0 \
            and klass_type not in default_values and \
            not (_is_list(klass_type) or _is_set(klass_type) or _is_dictionary(klass_type)):
        if binding_point.value is None:
            if binding_point.is_readonly:
                return
            instance = create_instance(klass_type, config, options)
            binding_point.set_value(instance)
        instance = binding_point.value
        bind_properties(instance, config, options)


def _is_list(klass_type: type):
    return issubclass(klass_type, list) or \
        (isinstance(klass_type, GenericAlias) and issubclass(klass_type.__origin__, list))


def _is_set(klass_type: type):
    return issubclass(klass_type, set) or \
        (isinstance(klass_type, GenericAlias) and issubclass(klass_type.__origin__, set))


def _is_dictionary(klass_type: type):
    return issubclass(klass_type, dict) or \
        (isinstance(klass_type, GenericAlias) and issubclass(klass_type.__origin__, dict))


def create_instance(klass_type: type, config: IConfiguration, options: BinderOptions):
    return klass_type()


default_values = {
    int: 0,
    float: 0.0,
    str: "",
    bool: False,
    bytes: b"",
    bytearray: bytearray(),
    complex: 0 + 0j
    # Add more types as needed
}


def try_convert_value(klass_type: type, value: str, path: str) -> tuple[bool, object, Exception]:
    error = None
    if klass_type == object:
        return True, value, error
    if klass_type == str:
        return True, value, error
    if klass_type == bool:
        if value.lower() == "true":
            return True, True, error
        elif value.lower() == "false":
            return True, False, error
        else:
            error = ValueError(f"invalid value format for value = {value} , path = {path}")
            return False, None, error
    if _is_optional(klass_type):
        args: tuple = klass_type.__args__
        if types.NoneType in args and len(value) == 0:
            return True, None, None
        types_without_nones = [f for f in args if f != types.NoneType]
        if len(types_without_nones) != 1:
            raise ValueError("Union types can just be with None")
        return try_convert_value(types_without_nones[0], value, path)
    val = klass_type(value)
    return True, val, error


def _is_optional(klass_type) -> bool:
    return typing.get_origin(klass_type) == types.UnionType or typing.get_origin(klass_type) == typing.Union


def bind_properties(instance, configuration: IConfiguration, options: BinderOptions):
    annotations = get_all_properties(type(instance))
    for property_name in annotations:
        property_type = annotations[property_name]
        bind_property(property_name, property_type, instance, configuration, options)


def bind_property(property_name: str, property_type, instance, config: IConfiguration, options: BinderOptions):
    def initial_provider_for_property():
        if hasattr(instance, property_name):
            return getattr(instance, property_name)

    property_binding_point = BindingPoint(initial_provider_for_property, is_readonly=False)
    section = config.get_section(property_name)
    bind_instance(property_type, property_binding_point, section, options)
    if property_binding_point.value is not None or not hasattr(instance, property_name):
        val = property_binding_point.value
        setattr(instance, property_name, val)


def get_all_properties(klass_type: type):
    mro = inspect.getmro(klass_type)
    annotations = {}
    for cls in mro:
        class_annotations = inspect.get_annotations(cls)
        annotations.update(class_annotations)
    res = {k: v for k, v in annotations.items() if not k.startswith("_")}
    return res


def get_collection_arg_type(klass_type):
    if isinstance(klass_type, GenericAlias):
        return klass_type.__args__[0]
    if issubclass(klass_type, list) and hasattr(klass_type, "__orig_bases__"):
        return get_collection_arg_type(klass_type.__orig_bases__[0])
    raise NotImplementedError


def bind_collection(collection: list, config: IConfiguration, options: BinderOptions, klass_type: type):
    arg_type = get_collection_arg_type(klass_type)
    for section in config.get_children():
        try:
            item_binding_point = BindingPoint()
            bind_instance(arg_type, item_binding_point, section, options)
            if item_binding_point.has_new_value:
                collection.append(item_binding_point.value)
        except Exception as ex:
            logging.error(msg="", exc_info=ex)


def bind_set(collection: set, config: IConfiguration, options: BinderOptions, klass_type: type):
    arg_type = get_collection_arg_type(klass_type)
    for section in config.get_children():
        try:
            item_binding_point = BindingPoint()
            bind_instance(arg_type, item_binding_point, section, options)
            if item_binding_point.has_new_value:
                collection.add(item_binding_point.value)
        except Exception as ex:
            logging.error(msg="", exc_info=ex)


def bind_dictionary(dict_instance: dict, config: IConfiguration, options: BinderOptions, klass_type: type):
    assert isinstance(klass_type, GenericAlias)
    key_type = klass_type.__args__[0]
    value_type = klass_type.__args__[1]
    if not _is_valid_type_for_key_dict(key_type):
        raise ValueError("dictionary key type should be int or string")
    for child in config.get_children():
        try:
            key = get_key_value(child.key, key_type)

            def initial_value_provider_func():
                if key in dict_instance:
                    return dict_instance[key]
                return None

            value_binding_point = BindingPoint(initial_value_provider_func, False)
            bind_instance(value_type, value_binding_point, child, options)
            if value_binding_point.has_new_value:
                dict_instance[key] = value_binding_point.value
        except Exception as ex:
            logging.error("", ex)


def get_key_value(key: str, key_type: type):
    if issubclass(key_type, str):
        return key
    if issubclass(key_type, enum.Enum):
        for mem in key_type._member_map_:
            if mem.lower() == key.lower():
                return key_type[mem]
        raise ValueError(f"invalid enum value  key  {key} for type {key_type}")
    return key_type(key)


def _is_valid_type_for_key_dict(klass_type: type):
    return klass_type == int or \
        klass_type == str or \
        issubclass(klass_type, enum.Enum)
