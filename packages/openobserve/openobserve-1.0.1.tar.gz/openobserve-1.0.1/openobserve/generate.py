import platform
import socket
import inspect


def debug_data() -> object:
    debug = {
        'hostname': socket.gethostname(),
        'user_name': socket.gethostname(),
        'system': platform.system(),
        'system_architecture': platform.machine(),
        'system_version': platform.version(),
        'system_release': platform.release(),
        'python_version': platform.python_version()
    }

    try:
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back
        info = inspect.getframeinfo(caller_frame)
        debug['filename'] = info.filename
        debug['lineno'] = info.lineno
    except:
        pass

    return debug
