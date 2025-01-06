########## win32 ##########
find_process_with_file_handle = None
get_downloads_directory = None
activate_window = None
process_id_from_path = None
wait_for_pid = None
get_documents_directory = None
# get_ui_locale = None
# SimpleNamedPipe = None
# SingleInstance = None
write_named_pipe = None

def get_ui_locale():
    return 'en_US'

def get_documents_directory():
    return "/home/armor/tmp"

class SingleInstance:
    def __init__(self):
        pass

    def aleradyrunning(self):
        return False

class SimpleNamedPipe:
    def __init__(self, pipe_name):
        pass

    def connect(self):
        pass

    def read(self):
        pass

    def write(self, data):
        pass

def prelaunch_platform_fix():
    pass

########## lib ##########
pywintypes_error = None
pywintypes_com_error = None

winutils = None