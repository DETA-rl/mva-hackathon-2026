"""Create the ported analysis scripts (replicate/analysis/) from the as-run originals, and log every edit.

Usage:
  python tools/port_scripts.py --candidates <dir> --recovered <dir> --root t2tests=<dir> --root asrun=<dir> \
      --key-file <file>

<dir> are the authors' private copies of the as-run scripts (not shipped: some contain the organiser
sample ID, candidate coordinates or the authors' local paths); asrun=<dir> holds the verbatim copies of the public
files whose local paths were redacted. The edits come from tools/porting_spec.json. Each edit replaces exactly one
line, so line numbers stay aligned and every other line is byte-identical.

Hashes of private content (the original files and the original text of each replaced line) are keyed:
HMAC-SHA256 with the key in --key-file, which the authors keep with the originals. A plain sha256 of a short
line (a path with a user name, a coordinate, a protein change) could be reversed by trying candidates.
Hashes of public files (the ported scripts, the as-run copies in this repository) are plain sha256.

Writes:
  replicate/analysis/<ported path>   the ported scripts
  replicate/analysis/PORTING.json    machine-readable log
  PORTING_LOG.md                     the same log for humans

`python -m replicate audit-port` re-checks the ported files and the public as-run copies against PORTING.json;
with the originals and the key it also checks them, so the claim "only these lines changed" is testable.
"""
import argparse
import hashlib
import hmac
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "tools", "porting_spec.json")
DEST = os.path.join(ROOT, "replicate", "analysis")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def differing_lines(a: bytes, b: bytes, what):
    x, y = a.decode().split("\n"), b.decode().split("\n")
    if len(x) != len(y):
        sys.exit(f"{what}: line count differs from its original")
    return [k + 1 for k, (p, q) in enumerate(zip(x, y)) if p != q], y


def redaction_log(orig: bytes, public: bytes, declared, what):
    """Check that `public` differs from `orig` exactly on the declared lines, each carrying [redacted]."""
    diff, lines = differing_lines(orig, public, what)
    want = sorted(r["line"] for r in declared)
    if diff != want:
        sys.exit(f"{what} differs from its original on lines {diff}, not exactly on the logged redactions {want}")
    out = []
    for r in sorted(declared, key=lambda r: r["line"]):
        if "[redacted]" not in lines[r["line"] - 1]:
            sys.exit(f"{what} line {r['line']} does not carry [redacted]")
        out.append({"line": r["line"], "redacted_text": lines[r["line"] - 1], "reason": r["reason"]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--recovered", required=True)
    ap.add_argument("--root", action="append", default=[], help="extra origin root, NAME=DIR (t2tests, asrun)")
    ap.add_argument("--key-file", required=True, help="HMAC key for hashes of private content (kept by the authors)")
    a = ap.parse_args()
    key = open(a.key_file).read().strip().encode()
    khash = lambda b: hmac.new(key, b, hashlib.sha256).hexdigest()   # noqa: E731
    roots = {"candidates": a.candidates, "recovered": a.recovered}
    roots.update(dict(r.split("=", 1) for r in a.root))
    spec = json.load(open(SPEC))
    log = []
    for s in spec["scripts"]:
        kind, rel = s["origin"].split(":", 1)
        src = os.path.join(roots[kind], rel)
        raw = open(src, "rb").read()
        mode = s.get("mode", "lines")
        changes = []
        if mode == "lines":
            lines = raw.decode().split("\n")
            for e in s["edits"]:
                i = e["line"] - 1
                old = lines[i]
                changes.append({"line": e["line"], "old_hmac": khash(old.encode()), "new": e["new"], "reason": e["reason"]})
                lines[i] = e["new"]
            out = "\n".join(lines).encode()
            if len(out.decode().split("\n")) != len(raw.decode().split("\n")):
                sys.exit(f"line count changed for {s['ported']}")
        elif mode == "extract":
            out = s["content"].encode()
        else:
            sys.exit(f"unknown mode {mode}")
        dst = os.path.join(DEST, s["ported"])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as fh:
            fh.write(out)
        if dst.endswith(".sh"):
            os.chmod(dst, 0o755)
        repo_copy_sha = None
        redactions = []
        if s.get("repo_copy"):
            p = os.path.join(ROOT, s["repo_copy"])
            if not os.path.exists(p):
                sys.exit(f"repo as-run copy {s['repo_copy']} missing")
            rb = open(p, "rb").read()
            repo_copy_sha = sha(rb)
            # the public as-run copy is the original except on the lines where a private token became [redacted]
            redactions = redaction_log(raw, rb, s.get("repo_copy_redactions", []), s["repo_copy"])
        log.append({
            "ported": "replicate/analysis/" + s["ported"],
            "origin": s["origin"],
            "repo_copy": s.get("repo_copy"),
            "repo_copy_sha256": repo_copy_sha,
            "repo_copy_redactions": redactions,
            "register": s["register"],
            "mode": mode,
            "hmac_before": khash(raw),
            "sha256_after": sha(out),
            "lines_before": raw.decode().count("\n"),
            "changes": changes,
            "extract_note": s.get("extract_note"),
            "origin_note": s.get("origin_note"),
        })
    public = []
    for r in spec.get("public_copy_redactions", []):
        p = os.path.join(ROOT, r["file"])
        pb = open(p, "rb").read()
        orig = open(os.path.join(roots["asrun"], r["file"]), "rb").read()
        reds = redaction_log(orig, pb, [{"line": n, "reason": r["reason"]} for n in r["lines"]], r["file"])
        public.append({"file": r["file"], "sha256": sha(pb), "hmac_original": khash(orig), "redactions": reds})
    json.dump({"about": spec["about"], "files": log, "public_copy_redactions": public},
              open(os.path.join(DEST, "PORTING.json"), "w"), indent=1)
    write_md(log, public, spec["about"], spec.get("reuse", []))
    print(f"ported {len(log)} files; edited {sum(1 for x in log if x['changes'] or x['mode'] != 'lines')}; "
          f"{len(public)} other public copies with redacted lines")


def write_md(log, public, about, reuse=()):
    L = ["# Porting log", "",
         "Every analysis script the harness runs is a copy of the script that produced the register result, with",
         "only path constants, hard-coded candidate coordinates and the candidate's protein-change labels replaced.",
         "This file lists every replaced line.",
         "", about, "",
         "How to check it: `./replicate.sh audit-port` verifies that each ported file still has the hash below and,",
         "where the as-run copy is in this repository (column 'repo as-run copy', under `as_run/`), that the two files",
         "differ only on the listed lines (lines marked `[redacted]` in a public as-run copy are skipped there). With the",
         "private originals and the key: `./replicate.sh audit-port --candidates DIR --recovered DIR --root t2tests=DIR",
         "--root asrun=DIR --key-file FILE`.",
         "", "| ported file | origin | repo as-run copy | keyed hash before | sha256 after | edited lines |",
         "|---|---|---|---|---|---|"]
    for x in log:
        if x["mode"] == "extract":
            edited = "extracted (see note)"
        else:
            edited = ", ".join(str(c["line"]) for c in x["changes"]) or "none (copied unchanged)"
        L.append(f"| `{x['ported']}` | {x['origin']} | {('`' + x['repo_copy'] + '`') if x['repo_copy'] else 'held back or recovered'} | "
                 f"`{x['hmac_before'][:16]}` | `{x['sha256_after'][:16]}` | {edited} |")
    L += ["", "## Edits, line by line", ""]
    for x in log:
        if x["mode"] == "extract":
            L += [f"### `{x['ported']}`", "", x["extract_note"], ""]
            continue
        if not x["changes"] and not x.get("repo_copy_redactions"):
            continue
        L += [f"### `{x['ported']}`", ""]
        if x.get("origin_note"):
            L += [f"Origin: {x['origin_note']}", ""]
        for c in x["changes"]:
            L.append(f"- line {c['line']} (old line keyed hash `{c['old_hmac'][:16]}`): {c['reason']}")
            L.append(f"  new: `{c['new']}`")
        for r in x.get("repo_copy_redactions") or []:
            L.append(f"- public as-run copy `{x['repo_copy']}`, line {r['line']}: `[redacted]` in place of {r['reason']}")
        L.append("")
    if public:
        L += ["## Other public copies with redacted lines", "",
              "Files in `as_run/` and `citations/` that the harness does not run. Each differs from the file that ran only on",
              "the listed lines, where a local user name, a disk identifier or a session folder became `[redacted]`.", "",
              "| file | lines | sha256 of the public copy |", "|---|---|---|"]
        for p in public:
            L.append(f"| `{p['file']}` | {', '.join(str(r['line']) for r in p['redactions'])} | `{p['sha256'][:16]}` |")
        L.append("")
    if reuse:
        L += ["## Scripts the harness runs on another input (no line changed)", ""]
        for r in reuse:
            L += [f"- `{r['script']}` in step {r['step']}: {r['how']}. Why: {r['why']}", ""]
    L += ["Full hashes are in `replicate/analysis/PORTING.json`.", ""]
    open(os.path.join(ROOT, "PORTING_LOG.md"), "w").write("\n".join(L))


if __name__ == "__main__":
    main()
