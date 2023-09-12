import platform
from nicegui import ui
import nicesheet
import serial


def get_system_info():
    return {
        "system": {
            "platform": platform.platform(),
            "system": platform.system(),
            "system_release": platform.release(),
            "system_version": platform.version(),
            "machine": platform.machine(),
        },

        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "compiler": platform.python_compiler(),
            "architecture": platform.architecture()[0],
        },

        "dependencies": {
            "nicesheets": nicesheet.__version__,
            "pyserial": serial.__version__,
        },
    }
