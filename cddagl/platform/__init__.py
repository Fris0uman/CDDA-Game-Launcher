import platform

if platform.system() == "Linux":
    from .linux import *
else:
    from .windows.win32 import *
    from .windows.lib import *
