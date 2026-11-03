from pathlib import Path
import os
import subprocess
import sys


project_dir = Path(__file__).resolve().parent
python_relative_path = (
    Path(".venv") / "Scripts" / "python.exe"
    if os.name == "nt"
    else Path(".venv") / "bin" / "python"
)
project_python = project_dir / python_relative_path
arguments = sys.argv[1:]

if project_python.is_file() and Path(sys.executable).resolve() != project_python.resolve():
    result = subprocess.run(
        [str(project_python), str(Path(__file__).resolve()), *arguments],
        cwd=project_dir,
        check=False,
    )
    raise SystemExit(result.returncode)

sys.path.insert(0, str(project_dir / "src"))

from green_gap_tool.cli import main


if __name__ == "__main__":
    raise SystemExit(main(arguments))