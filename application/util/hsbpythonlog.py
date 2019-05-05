import ctypes
import sys

loglib = ctypes.cdll.LoadLibrary("/huishoubao/loglib/lib/libhsbpythonlog.so")


def log_initialize(strModelName=str(), bDebugModel=False):
    initialize = loglib.log_initialize_py
    initialize.argtypes = [ctypes.c_char_p, ctypes.c_bool]
    initialize.restype = ctypes.c_bool
    return initialize(strModelName.encode(), bDebugModel)


def log_debug(strLog=str()):
    f = sys._getframe(1)
    debug = loglib.log_debug_py
    debug.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    debug(strLog.encode(), f.f_code.co_filename.encode(), f.f_code.co_name.encode(), f.f_lineno)


def log_info(strLog=str()):
    f = sys._getframe(1)
    info = loglib.log_info_py
    info.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    info(strLog.encode(), f.f_code.co_filename.encode(), f.f_code.co_name.encode(), f.f_lineno)


def log_warn(strLog=str()):
    f = sys._getframe(1)
    warn = loglib.log_warn_py
    warn.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    warn(strLog.encode(), f.f_code.co_filename.encode(), f.f_code.co_name.encode(), f.f_lineno)


def log_error(strLog=str()):
    f = sys._getframe(1)
    error = loglib.log_error_py
    error.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    error(strLog.encode(), f.f_code.co_filename.encode(), f.f_code.co_name.encode(), f.f_lineno)


def log_fatal(strLog=str()):
    f = sys._getframe(1)
    fatal = loglib.log_fatal_py
    fatal.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    fatal(strLog.encode(), f.f_code.co_filename.encode(), f.f_code.co_name.encode(), f.f_lineno)


def log_report(strLog=str()):
    report = loglib.log_report_py
    report.argtypes = [ctypes.c_char_p]
    report(strLog.encode())


def log_set_ndc(strMsg=str()):
    set_ndc = loglib.log_set_ndc_py
    set_ndc.argtypes = [ctypes.c_char_p]
    set_ndc(strMsg)


def log_clr_ndc():
    clr_ndc = loglib.log_clr_ndc_py
    clr_ndc()


def log_get_ndc():
    get_ndc = loglib.log_get_ndc_py
    get_ndc.restype = ctypes.c_char_p
    return get_ndc()


def log_get_errinfo():
    get_errinfo = loglib.log_get_errinfo_py
    get_errinfo.restype = ctypes.c_char_p
    return get_errinfo()
