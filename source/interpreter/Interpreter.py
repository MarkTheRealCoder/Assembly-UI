import faulthandler
import os
import subprocess
import sys
from typing import NamedTuple, Optional

import jpype

from source.filesystem import find_path
from source.filesystem.Folder import app_root
from source.filesystem.documents import Document, FT
from source.interface import Settings
from source.platform import isWindows


class InterpreterUpdate(NamedTuple):
    """ Decoded payload of a state update sent by the Java session. """
    state: str
    terminal: bool
    exit_code: int
    message: Optional[str]
    warnings: Optional[str]
    pc: int
    line: int
    instruction: Optional[str]
    scope: Optional[str]
    output: str
    changed: list
    removed: list


class _JavaInterpreterInterface:
    """
    Starts the JVM once per process and exposes the Java session class.
    A JVM cannot restart inside the same process, so it stays active until the application exits.
    """
    ___JVM_LIBRARIES = (
        ("lib", "server", "libjvm.dylib"),
        ("lib", "server", "libjvm.so"),
        ("bin", "server", "jvm.dll"),
    )
    ___NATIVE_ACCESS_VERSION = 22
    ___MAX_HEAP = "-Xmx256m"
    ___SESSION = None

    @staticmethod
    def ___java_home() -> Optional[str]:
        """ Asks the java executable on PATH for its home directory. """
        try:
            result = subprocess.run(
                ["java", "-XshowSettings:properties", "-version"],
                capture_output=True, text=True, timeout=10,
                # A packaged app has no console, so the command must not open one.
                creationflags=subprocess.CREATE_NO_WINDOW if isWindows() else 0
            )
        except (OSError, subprocess.SubprocessError):
            return None
        for line in result.stderr.splitlines():
            key, _, value = line.partition("=")
            if key.strip() == "java.home":
                return value.strip()
        return None

    @staticmethod
    def ___bundled_java_home() -> Optional[str]:
        """
        Returns the Java runtime shipped with the application, in a folder named runtime.
        A packaged app keeps it next to the executable. A source checkout can keep one in the project folder.
        """
        bases = [app_root()]
        if getattr(sys, "frozen", False):
            bases.insert(0, os.path.dirname(sys.executable))
        for base in bases:
            home = os.path.join(base, "runtime")
            if os.path.isdir(home):
                return home
        return None

    @staticmethod
    def ___find_jvm() -> str:
        """
        Finds the JVM library. The bundled runtime comes first, then JAVA_HOME, then the java command on PATH.
        JPype alone can return a directory on macOS.
        """
        bundled = _JavaInterpreterInterface.___bundled_java_home()
        if bundled and isWindows():
            # jvm.dll loads the other DLLs of the runtime from its bin folder, which Windows searches only on PATH.
            os.environ["PATH"] = os.path.join(bundled, "bin") + os.pathsep + os.environ.get("PATH", "")
        # The java command runs only if the other locations have no JVM.
        homes = (lambda: bundled, lambda: os.environ.get("JAVA_HOME"), _JavaInterpreterInterface.___java_home)
        for find_home in homes:
            home = find_home()
            if not home:
                continue
            for library in _JavaInterpreterInterface.___JVM_LIBRARIES:
                path = os.path.join(home, *library)
                if os.path.isfile(path):
                    return path
        try:
            return jpype.getDefaultJVMPath()
        except jpype.JVMNotFoundException as error:
            raise FileNotFoundError("Java runtime not found. Reinstall the application, install a JDK or set JAVA_HOME.") from error

    @staticmethod
    def ___jvm_arguments(jvm_path: str) -> list[str]:
        """ Builds the JVM options supported by the selected runtime. """
        arguments = [_JavaInterpreterInterface.___MAX_HEAP]
        release = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(jvm_path))), "release")
        try:
            with open(release, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("JAVA_VERSION="):
                        major = int(line.split("=")[1].strip().strip('"').split(".")[0])
                        if major >= _JavaInterpreterInterface.___NATIVE_ACCESS_VERSION:
                            arguments.append("--enable-native-access=ALL-UNNAMED")
                        break
        except (OSError, ValueError):
            pass
        return arguments

    @staticmethod
    def session_class():
        """ Starts the JVM if necessary and returns the DebugSession class. """
        if _JavaInterpreterInterface.___SESSION is not None:
            return _JavaInterpreterInterface.___SESSION

        jar = Settings.get("editor/interpreter", _type=str)
        if not jar or not os.path.isfile(jar):
            # A JAR set in the settings that no longer exists falls back to the bundled one.
            jar = find_path("interpreter.jar")
        if not jar or not os.path.isfile(jar):
            raise FileNotFoundError("Interpreter JAR not found.")

        if not jpype.isJVMStarted():
            jvm_path = _JavaInterpreterInterface.___find_jvm()
            if isWindows() and faulthandler.is_enabled():
                # The JVM raises access violations on purpose and handles them itself (null checks, stack probes,
                # safepoints). On Windows, faulthandler reports each one as a fatal exception, so it must stay off.
                faulthandler.disable()
            jpype.startJVM(
                *_JavaInterpreterInterface.___jvm_arguments(jvm_path),
                jvmpath=jvm_path,
                classpath=[jar],
                convertStrings=False
            )
        _JavaInterpreterInterface.___SESSION = jpype.JClass("xyz.atom7.bridge.DebugSession")
        return _JavaInterpreterInterface.___SESSION


class _Interpreter:
    """ Commands and payload decoding for one Java session. """

    class FeedException(Exception):
        pass

    class RuntimeException(Exception):
        pass

    ___UNSET_VALUE = "unset"
    ___KIND_GROUP = 0
    ___KIND_UNSET = 2

    def __init__(self, session, language: str):
        self.___session = session
        self.___language: str = language
        self.___terminated: bool = False

    @property
    def contexts(self) -> list[str]:
        """ Names of the memory contexts of the language, in display order. """
        return [str(name) for name in self.___session.getContexts()]

    @property
    def language(self) -> str:
        """ Language of the program. """
        return self.___language

    @property
    def terminated(self) -> bool:
        return self.___terminated

    def interpret(self, debug: bool = False) -> None:
        """ Starts the program. In debug mode it pauses before the first instruction. """
        self.___session.start(debug)

    def step(self, count: int = 1) -> bool:
        """ Executes a number of instructions of a paused program. """
        return bool(self.___session.step(count))

    @property
    def max_input_value(self) -> int:
        """ Largest character code that the program can read. """
        return int(self.___session.MAX_INPUT_VALUE)

    def feed(self, line: str) -> bool:
        """
        Sends the characters of a line of input, without a newline. The program reads one character per input
        instruction. Returns False if the session refuses the line, for example if a character code exceeds
        max_input_value.
        """
        return bool(self.___session.feed(line))

    def terminate(self) -> None:
        """ Requests the end of the program. """
        self.___session.stop()

    def read(self, timeout_ms: int = 200) -> Optional[InterpreterUpdate]:
        """ Waits for the next update and decodes it. Returns None if nothing changed. """
        update = self.___session.awaitUpdate(timeout_ms)
        if update is None:
            return None

        terminal = bool(update.isTerminal())
        self.___terminated = self.___terminated or terminal
        delta = update.getDelta()
        return InterpreterUpdate(
            state=str(update.getState()),
            terminal=terminal,
            exit_code=int(update.getExitCode()),
            message=_Interpreter.___text(update.getMessage()),
            warnings=_Interpreter.___text(update.getWarnings()),
            pc=int(update.getProgramCounter()),
            line=int(update.getLine()),
            instruction=_Interpreter.___text(update.getInstruction()),
            scope=_Interpreter.___text(update.getScope()),
            output=str(update.getOutput()),
            changed=_Interpreter.___decode_changed(delta),
            removed=_Interpreter.___decode_removed(delta)
        )

    @staticmethod
    def ___text(value) -> Optional[str]:
        return None if value is None else str(value)

    @staticmethod
    def ___decode_changed(delta) -> list[tuple]:
        """
        Converts the changed nodes to (context, path, value, order) tuples. A group has the value None.
        The order is the position of the node among the current children of its parent.
        """
        keys = str(delta.getChangedKeys())
        if not keys:
            return []
        kinds = memoryview(delta.getChangedKinds()).cast("B").tolist()
        values = memoryview(delta.getChangedValues()).cast("B").cast("i").tolist()
        orders = memoryview(delta.getChangedOrders()).cast("B").cast("i").tolist()
        changed = []
        for key, kind, value, order in zip(keys.split("\n"), kinds, values, orders):
            context, _, path = key.partition(":")
            if kind == _Interpreter.___KIND_GROUP:
                value = None
            elif kind == _Interpreter.___KIND_UNSET:
                value = _Interpreter.___UNSET_VALUE
            changed.append((context, path, value, order))
        return changed

    @staticmethod
    def ___decode_removed(delta) -> list[tuple]:
        """ Converts the removed nodes to (context, path) tuples. """
        keys = str(delta.getRemovedKeys())
        if not keys:
            return []
        return [tuple(key.split(":", 1)) for key in keys.split("\n")]


class Interpreter(_Interpreter):
    """
    Interface for a single interpreter instance.
    Only one program runs at a time: a new handle terminates the previous one.
    """
    ___LANGUAGES = {FT.FIJVM: "ijvm", FT.F8088: "8088"}
    ___RUNNING_INTERPRETER: Optional[tuple] = None

    def __init__(self, session, language: str):
        super().__init__(session, language)

    @staticmethod
    def get_handle(_id: int, doc: Document) -> 'Interpreter':
        """ Returns the active handle of the document or creates a new one. """
        _int = Interpreter.___RUNNING_INTERPRETER
        if not _int or _int[0] != _id or _int[1].terminated:
            return Interpreter.___new(_id, doc)
        return _int[1]

    @staticmethod
    def ___new(_id: int, doc: Document) -> 'Interpreter':
        language = Interpreter.___LANGUAGES.get(FT.findByExt(doc.getExtension()))
        if language is None:
            raise _Interpreter.RuntimeException(f"Unsupported file type: .{doc.getExtension()}")

        session_class = _JavaInterpreterInterface.session_class()
        if Interpreter.___RUNNING_INTERPRETER:
            Interpreter.___RUNNING_INTERPRETER[1].terminate()

        interpreter = object.__new__(Interpreter)
        interpreter.__init__(session_class.create(language, doc.text), language)
        Interpreter.___RUNNING_INTERPRETER = (_id, interpreter)
        return interpreter

    def __new__(cls, *args, **kwargs):
        raise NotImplementedError("Use Interpreter.get_handle() to get an instance.")
