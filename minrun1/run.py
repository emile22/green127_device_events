import subprocess
import sys
from collections.abc import Callable


def pause_for_review(message: str, input_fn: Callable[[str], str]) -> None:
    try:
        input_fn(message)
    except EOFError:
        pass


def main() -> int:
    tests = subprocess.run([sys.executable, "-m", "pytest", "-v"], check=False)
    if tests.returncode != 0:
        pause_for_review("\nTests failed. Press ENTER to close and review the trace...", input)
        return tests.returncode

    print("\nAll tests passed. Starting the GREEN runtime...\n", flush=True)
    runtime = subprocess.run([sys.executable, "-m", "green"], check=False)
    pause_for_review("\nGREEN runtime ended. Press ENTER to close and review the trace...", input)
    return runtime.returncode


if __name__ == "__main__":
    raise SystemExit(main())