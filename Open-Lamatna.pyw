"""Open Lamatna with the installed Python; no batch file or PowerShell is invoked."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().with_name('launcher.py')), run_name='__main__')
