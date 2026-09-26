"""TRACE — AI-Powered Bitcoin Transaction Traffic Forensic Intelligence Workstation.

SIH26146 | National Technical Research Organisation (NTRO)
100% Offline Air-Gapped Desktop Application
"""
import os
import sys
import subprocess
from pathlib import Path

# Ensure application root is in python module search path
APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# Auto-detect and route to local virtual environment if invoked via global python
venv_win = APP_ROOT / ".venv" / "Scripts" / "python.exe"
venv_linux = APP_ROOT / ".venv" / "bin" / "python"
venv_python = venv_win if venv_win.exists() else (venv_linux if venv_linux.exists() else None)

if venv_python and Path(sys.executable).resolve() != venv_python.resolve():
    if os.environ.get("TRACE_VENV_LAUNCHED") != "1":
        os.environ["TRACE_VENV_LAUNCHED"] = "1"
        try:
            main_script = str(APP_ROOT / "main.py")
            cmd = [str(venv_python), main_script] + [a for a in sys.argv[1:] if a != main_script]
            res = subprocess.run(cmd, cwd=str(APP_ROOT))
            sys.exit(res.returncode)
        except Exception:
            pass

# Fallback: Append venv site-packages if present
venv_site = APP_ROOT / ".venv" / "Lib" / "site-packages"
if venv_site.exists() and str(venv_site) not in sys.path:
    sys.path.insert(0, str(venv_site))

from app.application import TRACEApplication
from ui.main_window import MainWindow


def main():
    """Launch TRACE Native Desktop Application."""
    app = TRACEApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
