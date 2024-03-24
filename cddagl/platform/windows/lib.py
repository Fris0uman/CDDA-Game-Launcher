from pywintypes import error as pywintypes_error, com_error as pywintypes_com_error
import winutils

def prelaunch_platform_fix():
    # fix_pywin32_loading
    try:
        import pywintypes
    except ImportError:
        import sys
        sys.path.append(r'win32')
        sys.path.append(r'win32\lib')
        import pywin32_bootstrap
