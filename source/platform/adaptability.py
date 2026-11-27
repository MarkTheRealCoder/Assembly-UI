import os


def isWindows():
    return os.name == "nt"

def isMac():
    return os.name == "posix" and os.uname().sysname == "Darwin"

def isLinux():
    return os.name == "posix" and os.uname().sysname == "Linux"


def roundColors(scope: str, scopes: dict[str: int] = {}):
    colors = ["#5790fc", "#f89c20", "#e42536", "#964a8b", "#9c9ca1", "#7a21dd"]
    num_colors = 6
    if scope not in scopes:
        scopes[scope] = 0
    color = colors[scopes[scope] % num_colors]
    scopes[scope] += 1
    return color

