# -*- coding:utf-8 -*-
import importlib


def reload_import_module(imp_package_path, **kwargs):
    imp_module = importlib.import_module('.', imp_package_path)
    importlib.reload(imp_module)
    module_list = []
    for arg in kwargs.values():
        module_list.append(getattr(imp_module, arg))
    return tuple(module_list)
