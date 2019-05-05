import importlib
import pkgutil


def import_module_star(module, des_module=None):
    """
    from xx import *
    """
    for k, v in module.__dict__.iteritems():
        if not k.startswith("_"):
            des_module.__dict__[k] = v


def import_sub_module(module, star=False, des_module=None):
    """
    import all sub_modules of module xx
    """
    for loader, name, is_pkg in pkgutil.iter_modules(module.__path__):
        if not is_pkg:
        # ignore xx.yy if xx.yy is still package
            sub_module = importlib.import_module(module.__name__ + "." + name)
            # from xx import yy
            if star:
                import_module_star(sub_module, des_module)
                # from xx.yy import *
