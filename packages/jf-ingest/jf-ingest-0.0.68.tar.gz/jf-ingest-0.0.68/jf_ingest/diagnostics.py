import json
import logging
import os
import shutil
import subprocess
import threading
import time
from collections import namedtuple
from datetime import datetime, timedelta
from functools import wraps
from io import TextIOWrapper

import psutil
import pytz

_DIAGNOSTICS_FILE: TextIOWrapper = None


def _diagnostics_file_closed():
    return isinstance(_DIAGNOSTICS_FILE, TextIOWrapper) and _DIAGNOSTICS_FILE.closed


"""
The diagnostics module is used to capture diagnostics data
for agent runs. When running for Managed Ingest we do not
need to use any of this logic. For unity's sake we will
run the shared functions (so far only capture_timing),
but output nothing
"""

logger = logging.getLogger(__name__)


def _write_diagnostic(obj):
    # If there is no diagnostics file to write to, do nothing
    if not _DIAGNOSTICS_FILE:
        logger.debug(f"No diagnostics file is set")
        return

    json.dump(obj, _DIAGNOSTICS_FILE)
    _DIAGNOSTICS_FILE.write("\n")  # facilitate parsing
    _DIAGNOSTICS_FILE.flush()


def capture_agent_version():
    git_head_hash = os.getenv("SHA")
    build_timestamp = os.getenv("BUILDTIME")
    _write_diagnostic({"type": "agent_version", "sha": git_head_hash, "timestamp": build_timestamp})


# NOTE: This is the only function that is called from within the jf_ingest module!
# (as of 8/2/2023 -Gavin)
def capture_timing(*args, **kwargs):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = pytz.utc.localize(datetime.utcnow()).isoformat()
            if "func_name_override" in kwargs:
                func_name = kwargs.pop("func_name_override")
            else:
                func_name = func.__name__
            ret = func(*args, **kwargs)
            end_time = pytz.utc.localize(datetime.utcnow()).isoformat()
            diag_obj = {
                "type": "func_timing",
                "name": func_name,
                "start": start_time,
                "end": end_time,
            }
            if ret is not None:
                try:
                    diag_obj["num_items"] = len(ret)
                except TypeError:
                    if type(ret) is int:
                        diag_obj["num_items"] = ret
            _write_diagnostic(diag_obj)
            return ret

        return wrapper

    return actual_decorator


def capture_run_args(run_mode, config_file, outdir, prev_output_dir):
    _write_diagnostic(
        {
            "type": "run_args",
            "run_mode": run_mode,
            "config_file": config_file,
            "outdir": outdir,
            "prev_output_dir": prev_output_dir,
        }
    )


def capture_outdir_size(outdir):
    _write_diagnostic(
        {
            "type": "outdir_size",
            "size_kb": int(
                subprocess.check_output(["du", "-sk", outdir]).split()[0].decode("utf-8")
            ),
        }
    )


def continually_gather_system_diagnostics(kill_event, outdir):
    def _flush_cached_readings(cached_readings):
        if not cached_readings:
            return
        _write_diagnostic(
            {
                "type": "sys_resources_60s",
                "start": pytz.utc.localize(cached_readings[0].time).isoformat(),
                "end": pytz.utc.localize(cached_readings[-1].time).isoformat(),
                "cpu_pct": ["%.2f" % r.cpu_pct for r in cached_readings],
                "mem_used_gb": ["%.2f" % r.memory_used_gb for r in cached_readings],
                "mem_pct": ["%.2f" % r.memory_pct for r in cached_readings],
                "disk_used_gb": ["%.2f" % r.disk_used_gb for r in cached_readings],
                "disk_pct": ["%.2f" % r.disk_pct for r in cached_readings],
            }
        )

    SysReading = namedtuple(
        "SysReading",
        ("time", "cpu_pct", "memory_used_gb", "memory_pct", "disk_used_gb", "disk_pct"),
    )

    now = datetime.utcnow()
    readings = threading.local()
    readings.cached_readings = []
    readings.last_reading_time = None
    readings.last_flush_time = now

    while True:
        if kill_event.is_set():
            _flush_cached_readings(readings.cached_readings)
            readings.cached_readings = []
            return
        else:
            now = datetime.utcnow()
            if not readings.last_reading_time or (now - readings.last_reading_time) > timedelta(
                seconds=60
            ):
                cpu = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = shutil.disk_usage(outdir)
                readings.cached_readings.append(
                    SysReading(
                        now,
                        cpu / 100,
                        (memory.total - memory.available) / (1024**3),
                        (memory.total - memory.available) / memory.total,
                        disk.used / (1024**3),
                        disk.used / disk.total,
                    )
                )
                readings.last_reading_time = now

            if now - readings.last_flush_time > timedelta(seconds=300):
                _flush_cached_readings(readings.cached_readings)
                readings.cached_readings = []
                readings.last_flush_time = now

            # Keep the sleep short so that the thread's responsive to the kill_event
            time.sleep(1)


def open_file(outdir):
    global _DIAGNOSTICS_FILE
    try:
        if _DIAGNOSTICS_FILE is None:
            _DIAGNOSTICS_FILE = open(os.path.join(outdir, "diagnostics.json"), "a")
        elif _diagnostics_file_closed():
            _DIAGNOSTICS_FILE = open(os.path.join(outdir, "diagnostics.json"), "a")
        else:
            logger.debug(f"Diagnostics file is already open")
    except Exception as e:
        # These messages are left at the DEBUG level for a better UX in agent
        logger.debug(f"Error opening Diagnostics file. Diagnostics will not be written. Error: {e}")


def close_file():
    try:
        global _DIAGNOSTICS_FILE
        if _DIAGNOSTICS_FILE is None:
            logger.debug("Diagnostics file is already closed")
        elif _diagnostics_file_closed():
            logger.debug("Diagnostics file is already closed")
        else:
            logger.debug("Closing diagnostics file")
            _DIAGNOSTICS_FILE.close()
        _DIAGNOSTICS_FILE = None
    except Exception as e:
        # These messages are left at the DEBUG level for a better UX in agent
        logger.debug(f"Error closing Diagnostics file. Diagnostics will not be written. Error: {e}")
