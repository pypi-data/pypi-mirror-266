import os
import shutil

from donetools import info

def norm(path: str) -> str:
    return os.path.normcase(os.path.normpath(path))

def abs(path: str) -> str:
    return os.path.abspath(norm(path))

def join(*paths: str) -> str:
    return norm(os.path.join(*map(norm, paths)))

def dirname(path: str) -> str:
    return os.path.dirname(norm(path))

def basename(path: str) -> str:
    return os.path.splitext(os.path.basename(norm(path)))[0]

def isdir(path: str) -> bool:
    return os.path.isdir(norm(path))

def isfile(path: str) -> bool:
    return os.path.isfile(norm(path))

def collide(path: str) -> bool:
    path = norm(path)
    return isfile(path) or (isdir(path) and len(os.listdir(path)) > 0)

def remove(path: str) -> None:
    path = norm(path)
    shutil.rmtree(path) if os.path.isdir(path) else os.unlink(path)

def removeall(*paths: str) -> None:
    for path in paths:
        remove(path)

def reconcile(*paths: str, override: bool = False) -> None:
    conflicts = list(filter(collide, paths))
    if len(conflicts) > 0:
        prompt = f"Agree to {info.warn('remove')} conflicts?" + 2*os.linesep
        if override or info.dilemma(prompt + info.indent(os.linesep.join(conflicts))):
            removeall(*conflicts)
        else: exit()

def secure(*paths: str, override: bool = False) -> None:
    reconcile(*paths, override=override)
    for path in paths:
        os.makedirs(path if isdir(path) else dirname(abs(path)), exist_ok=True)
