import hashlib
import os
import random


def isWindows():
    return os.name == "nt"

def isMac():
    return os.name == "posix" and os.uname().sysname == "Darwin"

def isLinux():
    return os.name == "posix" and os.uname().sysname == "Linux"


def randomColor():
        return "#"+''.join([random.choice('0123456789ABCDEF') for _ in range(6)])


def getColorFromStr(s: str):
    hash_object = hashlib.md5(s.encode())
    hex_hash = hash_object.hexdigest()
    return f"#{hex_hash[:6]}"


def roundColors(scope: str, scopes: dict[str: int] = {}):
    colors = ["#5790fc", "#f89c20", "#e42536", "#964a8b", "#9c9ca1", "#7a21dd"]
    num_colors = 6
    if scope not in scopes:
        scopes[scope] = 0
    color = colors[scopes[scope] % num_colors]
    scopes[scope] += 1
    return color

