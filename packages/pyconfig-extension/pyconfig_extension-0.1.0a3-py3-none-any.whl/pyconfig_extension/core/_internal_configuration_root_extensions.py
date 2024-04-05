from functools import cmp_to_key

from pyconfig_extension.abstracts.iconfiguration import IConfigurationSection
from pyconfig_extension.abstracts.iconfiguration_root import IConfigurationRoot
import pyconfig_extension.abstracts.configuration_path as path_conf
from pyconfig_extension.core.configuration_key_comparer import compare


def get_children_implementation(root: IConfigurationRoot, path: str | None) -> list[IConfigurationSection]:
    providers = root.providers
    if not any(providers):
        return []

    children_keys = providers[0].get_child_keys([], path)

    for i in range(1, len(providers)):
        children_keys = providers[i].get_child_keys(children_keys, path)

    children_keys.sort(key=cmp_to_key(compare))
    # ignore case distinct
    dict_no_case: dict[str, str] = {}
    for children_key in children_keys:
        if children_key.lower() not in dict_no_case:
            dict_no_case[children_key.lower()] = children_key

    list_no_case = list(dict_no_case.values())

    children: list[IConfigurationSection] = []
    for key in list_no_case:
        section_key = key if path is None else path_conf.combine(path, key)
        child = root.get_section(section_key)
        children.append(child)
    return children
