"""
Starts the packaged app and checks that it is still running after a few seconds.

    python packaging/smoke_test.py <executable> [seconds]

The app has no console, so the script prints the error.log that the app writes in the user data folder.
On Linux it needs a display: run it with xvfb-run.
"""
import os
import subprocess
import sys
import time


def log_folders() -> list:
    home = os.path.expanduser("~")
    return [
        os.path.join(os.environ.get("APPDATA", home), "Assembly Stdio"),
        os.path.join(home, "Library", "Application Support", "Assembly Stdio"),
        os.path.join(os.environ.get("XDG_DATA_HOME", os.path.join(home, ".local", "share")), "Assembly Stdio"),
    ]


def print_logs() -> None:
    for folder in log_folders():
        for root, _dirs, files in os.walk(folder):
            if "error.log" in files:
                log = os.path.join(root, "error.log")
                print(f"== {log}")
                with open(log, "r", encoding="utf-8", errors="replace") as f:
                    print(f.read() or "(empty)")


def main() -> int:
    executable = os.path.abspath(sys.argv[1])
    seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    # The working folder is the one of the executable, as when a user opens it from the file manager.
    process = subprocess.Popen([executable], cwd=os.path.dirname(executable))
    time.sleep(seconds)
    code = process.poll()
    print_logs()
    if code is not None:
        print(f"The app closed after start, with exit code {code}")
        return 1
    process.kill()
    process.wait()
    print(f"The app was still running after {seconds} seconds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
