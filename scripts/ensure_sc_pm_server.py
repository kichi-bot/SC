"""Start the local SC PM grader server (127.0.0.1:8765) only if it is not already serving.

Run from a logon / daily scheduled task (pythonw, no console) so that the 4:00 Codex
sync can always open http://127.0.0.1:8765/html/sc_pm_grader.html and export the
public progress JSON. If something already listens on the port, nothing happens.
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8765
SERVER = Path(__file__).resolve().with_name("sc_pm_server.py")


def listening() -> bool:
    try:
        with socket.create_connection((HOST, PORT), timeout=1.5):
            return True
    except OSError:
        return False


def main() -> int:
    if listening():
        return 0
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    executable = str(pythonw if pythonw.exists() else sys.executable)
    flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    subprocess.Popen(
        [executable, str(SERVER)],
        cwd=str(SERVER.parent.parent),
        creationflags=flags,
        close_fds=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(20):
        time.sleep(0.25)
        if listening():
            return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
