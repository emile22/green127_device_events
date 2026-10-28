import subprocess
import sys


def main() -> int:
    tests = subprocess.run([sys.executable, "-m", "pytest", "-v"], check=False)
    if tests.returncode != 0:
        return tests.returncode

    print("\nAll tests passed. Starting the GREEN runtime...\n", flush=True)
    runtime = subprocess.run([sys.executable, "-m", "green"], check=False)
    return runtime.returncode


if __name__ == "__main__":
    raise SystemExit(main())