import os
import shutil

from donetools import info

def norm(path: str) -> str:
    return os.path.normcase(os.path.normpath(path))

def isabs(path: str) -> bool:
    return os.path.isabs(norm(path))

def isdir(path: str) -> bool:
    return os.path.isdir(norm(path))

def isfile(path: str) -> bool:
    return os.path.isfile(norm(path))

def join(*paths: str) -> str:
    return norm(os.path.join(*map(norm, paths)))

def abspath(path: str) -> str:
    return os.path.abspath(norm(path))

def relpath(path: str, start: str = os.curdir) -> str:
    return os.path.relpath(norm(path), norm(start))

def dirname(path: str) -> str:
    path = norm(path)
    return os.path.dirname(path) if isabs(path) else relpath(os.path.dirname(abspath(path)))

def basename(path: str) -> str:
    return os.path.splitext(os.path.basename(norm(path)))[0]

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

def secure(*dirs: str, override: bool = False) -> None:
    reconcile(*dirs, override=override)
    for path in dirs:
        os.makedirs(path, exist_ok=True)
