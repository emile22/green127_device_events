from pathlib import Path
import os
import subprocess
import sys

project_dir = Path(__file__).resolve().parent
project_python = project_dir / ".venv" / "Scripts" / "python.exe"
arguments = sys.argv[1:] or ["--once"]
if project_python.is_file() and os.path.normcase(sys.executable) != os.path.normcase(str(project_python)):
    result = subprocess.run(
        [str(project_python), str(Path(__file__).resolve()), *arguments],
        cwd=project_dir,
        check=False,
    )
    raise SystemExit(result.returncode)

sys.path.insert(0, str(project_dir / "src"))

from green_controller.cli import main


if __name__ == "__main__":
    raise SystemExit(main(arguments))
