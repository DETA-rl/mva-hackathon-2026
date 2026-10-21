"""Audit of the ported analysis scripts against replicate/analysis/PORTING.json (see PORTING_LOG.md).

Public files (the ported scripts and the as-run copies in this repository) are checked with plain sha256.
Private content (the original files and the original text of each replaced line) is logged as HMAC-SHA256 with a
key the authors keep with the originals; with both (`--key-file` and the origin folders) those are checked too.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os

from replicate.config import REPO_ROOT

PORTING = REPO_ROOT / "replicate" / "analysis" / "PORTING.json"


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _line_diff(orig: bytes, ported: bytes, entry, redacted=(), khash=None):
    """Problems if the two files differ anywhere except the logged lines.
    `redacted`: lines of a public as-run copy that carry [redacted] in place of a private token.
    `khash`: keyed hash function; when given (private audit), each logged original line must match its keyed hash."""
    a, b = orig.decode().split("\n"), ported.decode().split("\n")
    probs = []
    if len(a) != len(b):
        return [f"{entry['ported']}: line count differs from the original"]
    edited = {c["line"]: c for c in entry["changes"]}
    for i, (x, y) in enumerate(zip(a, b), 1):
        if i in redacted:
            if "[redacted]" not in x:
                probs.append(f"{entry['ported']}: as-run copy line {i} is logged as redacted but is not")
            if i in edited and y != edited[i]["new"]:
                probs.append(f"{entry['ported']}: ported line {i} is not the logged replacement")
            continue
        if i in edited:
            if khash and khash(x.encode()) != edited[i]["old_hmac"]:
                probs.append(f"{entry['ported']}: original line {i} is not the logged one")
            if y != edited[i]["new"]:
                probs.append(f"{entry['ported']}: ported line {i} is not the logged replacement")
        elif x != y:
            probs.append(f"{entry['ported']}: unlogged change at line {i}")
    return probs


def _only_redacted(orig: bytes, public: bytes, lines, what):
    a, b = orig.decode().split("\n"), public.decode().split("\n")
    if len(a) != len(b):
        return [f"{what}: line count differs from its original"]
    diff = {k for k, (x, y) in enumerate(zip(a, b), 1) if x != y}
    return [] if diff == set(lines) else [f"{what}: differs from its original on lines {sorted(diff)}, logged {sorted(lines)}"]


def audit(candidates=None, recovered=None, extra=None, key_file=None):
    """Return a list of problems (empty = every ported file and public copy is exactly as logged)."""
    if not PORTING.exists():
        return ["replicate/analysis/PORTING.json missing"]
    log = json.load(open(PORTING))
    roots = {"candidates": candidates, "recovered": recovered, **(extra or {})}
    khash = None
    if key_file:
        key = open(key_file).read().strip().encode()
        khash = lambda b: hmac.new(key, b, hashlib.sha256).hexdigest()   # noqa: E731
    probs = []
    if any(roots.values()) and not khash:
        probs.append("origin folders given without --key-file: the originals' keyed hashes cannot be checked")
    for e in log["files"]:
        p = REPO_ROOT / e["ported"]
        if not p.exists():
            probs.append(f"{e['ported']}: missing")
            continue
        data = p.read_bytes()
        if _sha(data) != e["sha256_after"]:
            probs.append(f"{e['ported']}: sha256 differs from PORTING.json (edited after porting?)")
            continue
        red = {r["line"] for r in e.get("repo_copy_redactions") or []}
        rb = None
        # the as-run copy in this repository, when there is one
        if e.get("repo_copy"):
            rc = REPO_ROOT / e["repo_copy"]
            if not rc.exists():
                probs.append(f"{e['ported']}: repo as-run copy {e['repo_copy']} missing")
            else:
                rb = rc.read_bytes()
                if _sha(rb) != e.get("repo_copy_sha256"):
                    probs.append(f"{e['ported']}: repo as-run copy {e['repo_copy']} changed since porting")
                elif e["mode"] == "lines":
                    probs += _line_diff(rb, data, e, red)
        # the private originals, when given (with the key)
        kind, rel = e["origin"].split(":", 1)
        root = roots.get(kind)
        if root and khash:
            op = os.path.join(root, rel)
            if not os.path.exists(op):
                probs.append(f"{e['ported']}: original not found under {kind}")
                continue
            ob = open(op, "rb").read()
            if khash(ob) != e["hmac_before"]:
                probs.append(f"{e['ported']}: original differs from the logged one (keyed hash)")
                continue
            if e["mode"] == "lines":
                probs += _line_diff(ob, data, e, khash=khash)
            if rb is not None:
                probs += _only_redacted(ob, rb, red, e["repo_copy"])
    for r in log.get("public_copy_redactions", []):
        p = REPO_ROOT / r["file"]
        if not p.exists():
            probs.append(f"{r['file']}: missing")
            continue
        pb = p.read_bytes()
        if _sha(pb) != r["sha256"]:
            probs.append(f"{r['file']}: sha256 differs from PORTING.json")
            continue
        lines = pb.decode().split("\n")
        for x in r["redactions"]:
            if lines[x["line"] - 1] != x["redacted_text"] or "[redacted]" not in lines[x["line"] - 1]:
                probs.append(f"{r['file']}: line {x['line']} is not the logged redacted line")
        if roots.get("asrun") and khash:
            op = os.path.join(roots["asrun"], r["file"])
            if not os.path.exists(op):
                probs.append(f"{r['file']}: original not found under asrun")
                continue
            ob = open(op, "rb").read()
            if khash(ob) != r["hmac_original"]:
                probs.append(f"{r['file']}: original differs from the logged one (keyed hash)")
            else:
                probs += _only_redacted(ob, pb, [x["line"] for x in r["redactions"]], r["file"])
    return probs


def summary():
    log = json.load(open(PORTING))
    n = len(log["files"])
    edited = sum(1 for e in log["files"] if e["changes"] or e["mode"] != "lines")
    in_repo = sum(1 for e in log["files"] if e.get("repo_copy"))
    return n, edited, in_repo
