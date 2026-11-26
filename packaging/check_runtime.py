"""
Checks that a Java runtime made with jlink can run the interpreter through JPype.

    python packaging/check_runtime.py <runtime folder> <interpreter.jar>

The build workflow runs it before packaging, so a missing Java module fails the build
instead of the first run on a user's computer.
"""
import os
import sys

import jpype

LIBRARIES = (
    ("bin", "server", "jvm.dll"),
    ("lib", "server", "libjvm.so"),
    ("lib", "server", "libjvm.dylib"),
)

PROGRAM = """.constant
.end-constant

.main
    BIPUSH 65
    OUT
    HALT
.end-main
"""


def main() -> int:
    runtime, jar = sys.argv[1], sys.argv[2]
    jvm = next((os.path.join(runtime, *lib) for lib in LIBRARIES if os.path.isfile(os.path.join(runtime, *lib))), None)
    if jvm is None:
        print(f"No JVM library in {runtime}")
        return 1
    os.environ["PATH"] = os.path.join(runtime, "bin") + os.pathsep + os.environ.get("PATH", "")

    jpype.startJVM("-Xmx256m", jvmpath=jvm, classpath=[jar], convertStrings=False)
    version = jpype.JClass("java.lang.System").getProperty("java.version")
    print(f"JVM {version} started from {jvm}")

    session_class = jpype.JClass("xyz.atom7.bridge.DebugSession")
    session = session_class.create("ijvm", PROGRAM)
    session.start(False)
    output = ""
    for _ in range(50):
        update = session.awaitUpdate(200)
        if update is None:
            continue
        output += str(update.getOutput())
        if update.isTerminal():
            print(f"Program ended: state {update.getState()}, exit code {update.getExitCode()}, output {output!r}")
            message = update.getMessage()
            if message is not None:
                print(f"Message: {message}")
            break
    else:
        print("The program did not end")
        return 1
    if "A" not in output:
        print("The program did not print the expected output")
        return 1
    print("Runtime check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
