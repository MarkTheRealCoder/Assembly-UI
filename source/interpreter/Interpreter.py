import os
import socket
import threading
from typing import Literal

import jpype

from source.filesystem.documents import Document
from source.interface.shared import Settings


class SocketInterface:
    def __init__(self):
        self.___socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.___socket.bind(("localhost", 0))
        self.___socket.listen(1)

        self.___port = self.___socket.getsockname()[1]

        self.___conn: socket = None

    def accept(self):
        conn, _ = self.___socket.accept()
        self.___conn = conn

    def close(self):
        if self.___conn:
            self.___conn.close()
        if self.___socket:
            self.___socket.close()

    def get_port(self):
        return self.___port

    def read(self):
        if not self.___conn:
            return None
        data = ""
        while True:
            tmp = self.___conn.recv(4096)
            if not tmp:
                break
            data += tmp.decode()
        return data if data else None

    def send(self, message: str) -> bool:
        if not self.___conn:
            return False
        try:
            self.___conn.sendall(message.encode())
            return True
        except Exception:
            return False


class _JavaInterpreterInterface:
    """
    Internal interpreter configuration and path management.
    """
    def __init__(self, socket: int):
        ipath = Settings.get("editor/interpreter", _type=str)
        if not ipath:
            raise FileNotFoundError("Interpreter path not set in settings.")
        self.___interpreter = ipath
        self.___thread = threading.Thread(target=self.___run, args=(socket,), daemon=True)
        self.___thread.start()

    def ___run(self, socket: int):
        if not jpype.isJVMStarted():
            jpype.startJVM(classpath=[self.___interpreter])
        MainClass = jpype.JClass('xyz.atom7.Main')
        args = jpype.JArray(jpype.JString)(["-net", str(socket)])
        MainClass.main(args)
        jpype.shutdownJVM()

    def close(self):
        self.___thread.join()


class _Interpreter:
    class FeedException(Exception):
        pass

    class RuntimeException(Exception):
        pass

    def __init__(self, communication_handle: callable):
        self.___comm = communication_handle
        self.___status: Literal["running", "waiting", "terminated"] = "running"

    def interpret(self) -> bool:
        result = self.___comm("INTERPRET <UUID> <PATH>")
        self.___status = "running"
        return result

    def parse(self) -> bool:
        return self.___comm("PARSE <UUID> <PATH>")

    def feed(self, input: str) -> bool:
        if len(input) != 1:
            raise _Interpreter.FeedException("Input must be a single character.")
        result = self.___comm(f"FEED <UUID> {input}")
        self.___status = "running"
        return result

    def terminate(self) -> bool:
        result = self.___comm("INTERRUPT <UUID>")
        self.___status = "terminated"
        return result

    def read(self):
        while self.___status != "terminated":
            value = self.___comm("READ")
            if value is None:
                raise _Interpreter.RuntimeException("Interpreter not ready.")
            if not value:
                self.___status = "waiting"
                raise _Interpreter.FeedException("Waiting for input.")
            for line in value.split(os.linesep):
                yield line

    def __del__(self):
        self.terminate()


class Interpreter(_Interpreter):
    """
    Interface for a single interpreter instance.
    Manages the lifecycle and communication with the interpreter process.
    """

    ___SOCKET = SocketInterface()
    ___INTERPRETER = _JavaInterpreterInterface(___SOCKET.get_port())
    ___RUNNING_INTERPRETER: tuple[int, 'Interpreter'] | None = None
    ___SOCKET.accept()

    def __init__(self, communication_handle: callable):
        super().__init__(communication_handle)

    @staticmethod
    def get_handle(_id: int, doc: Document) -> 'Interpreter | None':
        _int = Interpreter.___RUNNING_INTERPRETER
        if not _int or _int[0] != _id:
            return Interpreter.___new(_id, doc)
        else:
            return _int[1]

    @staticmethod
    def ___new(_id: int, doc: Document) -> 'Interpreter | None':
        if Interpreter.___RUNNING_INTERPRETER:
            Interpreter.___RUNNING_INTERPRETER[1].terminate()

        def communication_handle(command: str) -> bool | str | None:
            cmd = command.replace("<UUID>", str(_id)).replace("<PATH>", doc.getPath())
            if cmd == "READ":
                content = Interpreter.___SOCKET.read()
                return content
            else:
                return Interpreter.___SOCKET.send(cmd)

        # Bypass __new__ restriction by using object.__new__
        interpreter = object.__new__(Interpreter)
        interpreter.__init__(communication_handle)
        Interpreter.___RUNNING_INTERPRETER = (_id, interpreter)
        return interpreter

    def __new__(cls, *args, **kwargs):
        raise NotImplementedError("Use Interpreter.get_handle() to get an instance.")





# import socket
# import sys
# import tempfile
# import os
#
#
# class LocalSocket:
#     def __init__(self, name):
#         self.name = name
#         self.socket = None
#         self.socket_path = None
#
#     def create_server(self):
#         if sys.platform == 'win32':
#             # Use localhost on Windows
#             self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             self.socket.bind(('127.0.0.1', 0))  # Let OS choose port
#             port = self.socket.getsockname()[1]
#             self.address = ('127.0.0.1', port)
#         else:
#             # Use Unix socket on Unix-like systems
#             self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#             self.socket_path = os.path.join(tempfile.gettempdir(), f"{self.name}.sock")
#
#             # Remove existing socket
#             try:
#                 os.unlink(self.socket_path)
#             except OSError:
#                 pass
#
#             self.socket.bind(self.socket_path)
#             self.address = self.socket_path
#
#         self.socket.listen(5)
#         return self.address
#
#     def connect_client(self, address):
#         if sys.platform == 'win32':
#             client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         else:
#             client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#
#         client.connect(address)
#         return client
#
#     def cleanup(self):
#         if self.socket:
#             self.socket.close()
#         if self.socket_path and os.path.exists(self.socket_path):
#             os.unlink(self.socket_path)
#
#
# # Usage
# local_comm = LocalSocket("myapp")
# server_address = local_comm.create_server()
# print(f"Local server created at: {server_address}")