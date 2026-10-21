"""Run one analysis script under a write guard and a network guard (Python audit hooks).

Usage (by the harness only): python -s run.py <script.py> [args...]
Environment: REPL_WORKDIR (the only tree that may be written), REPL_WRITE_GUARD (enforce|warn|off),
REPL_ALLOW_NETWORK (1 to allow sockets).

The guard sees every Python-level file open for writing, delete, rename, mkdir, chmod and socket connect.
Writes that resolve (after following symlinks) outside REPL_WORKDIR raise PermissionError, so an input linked
into a step folder cannot be overwritten through the link. Native code (htslib, CUDA) is not covered; the
harness checks that index files (.fai, .tbi, .bai) exist so htslib never has to create one next to an input.
This folder holds only this file, so nothing here can shadow a module the script imports.
"""
import os
import runpy
import socket
import sys

WORK = os.path.realpath(os.environ["REPL_WORKDIR"])
MODE = os.environ.get("REPL_WRITE_GUARD", "enforce")
ALLOW_NET = os.environ.get("REPL_ALLOW_NETWORK") == "1"
_SPECIAL = {"/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty"}
_WFLAGS = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC
_busy = False


def _inside(p):
    try:
        p = os.fsdecode(p)
    except TypeError:
        return True
    rp = os.path.realpath(p)
    return rp == WORK or rp.startswith(WORK + os.sep) or rp in _SPECIAL or p in _SPECIAL


def _deny(what, path):
    msg = f"[replicate guard] blocked {what} outside the workdir: {path}"
    if MODE == "warn":
        sys.stderr.write(msg + "\n")
        return
    raise PermissionError(msg)


def _hook(event, args):
    global _busy
    if _busy or MODE == "off":
        return
    _busy = True
    try:
        if event == "open":
            path, mode, flags = (list(args) + [None, None, None])[:3]
            if path is None or isinstance(path, int):
                return
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int) and flags & _WFLAGS)
            if writing and not _inside(path):
                _deny("write", path)
        elif event in ("os.remove", "os.rmdir", "os.mkdir", "os.chmod", "os.chown", "os.truncate", "os.utime",
                       "shutil.rmtree"):
            path = args[0] if args else None
            if path is not None and not isinstance(path, int) and not _inside(path):
                _deny(event, path)
        elif event in ("os.rename", "os.link", "os.symlink", "shutil.copyfile", "shutil.copytree", "shutil.move"):
            dst = args[1] if len(args) > 1 else None
            src = args[0] if args else None
            if dst is not None and not _inside(dst):
                _deny(event, dst)
            if event in ("os.rename", "shutil.move") and src is not None and not _inside(src):
                _deny(event, src)
        elif event in ("socket.connect", "socket.connect_ex"):
            sock, addr = args[0], args[1]
            if not ALLOW_NET and getattr(sock, "family", None) != socket.AF_UNIX:
                raise PermissionError(f"[replicate guard] network not allowed for this step: {addr}")
        elif event == "socket.getaddrinfo":
            if not ALLOW_NET:
                raise PermissionError(f"[replicate guard] network not allowed for this step: {args[0]}")
    finally:
        _busy = False


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: run.py <script> [args...]")
    script = os.path.abspath(sys.argv[1])
    sys.argv = [script] + sys.argv[2:]
    sys.path[0] = os.path.dirname(script)
    sys.addaudithook(_hook)
    runpy.run_path(script, run_name="__main__")


if __name__ == "__main__":
    main()
