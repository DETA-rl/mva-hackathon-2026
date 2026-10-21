"""sha256 of files, cached in the workdir by (real path, size, mtime) so large inputs are hashed once."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


class HashCache:
    def __init__(self, workdir: Path | None):
        self.path = (workdir / "cache" / "sha256.json") if workdir else None
        self.data = {}
        if self.path and self.path.exists():
            try:
                self.data = json.loads(self.path.read_text())
            except ValueError:
                self.data = {}

    def sha256(self, path: str, progress=None) -> str:
        rp = os.path.realpath(path)
        st = os.stat(rp)
        key = f"{rp}|{st.st_size}|{st.st_mtime_ns}"
        if key in self.data:
            return self.data[key]
        h = hashlib.sha256()
        done = 0
        with open(rp, "rb") as fh:
            while True:
                b = fh.read(8 << 20)
                if not b:
                    break
                h.update(b)
                done += len(b)
                if progress and done % (4 << 30) < (8 << 20):
                    progress(done, st.st_size)
        d = h.hexdigest()
        self.data[key] = d
        self.save()
        return d

    def save(self):
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, indent=0))
        os.replace(tmp, self.path)


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()
