import datetime as dt
import platform
from typing import Dict


def system_describe(
        enable_cpu_freq: bool = False
) -> Dict:
    import psutil

    uname = platform.uname()
    virtual_memory = psutil.virtual_memory()
    return {
        "timestamp": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "platform_system": uname.system,
        "platform_processor": uname.processor,
        "platform_version": uname.version,
        "virtual_memory_total": virtual_memory.total,
        "virtual_memory_available": virtual_memory.available,
        "virtual_memory_active": virtual_memory.active,
        "virtual_memory_inactive": virtual_memory.inactive,
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_cores_logical": psutil.cpu_count(logical=True),
        **(
            {} if not enable_cpu_freq else [{
                "cpu_freq_max": cpu_freq.max,
                "cpu_freq_min": cpu_freq.min,
                "cpu_freq_current": cpu_freq.current,
            } for cpu_freq in [psutil.cpu_freq()]][-1]
        )
    }
