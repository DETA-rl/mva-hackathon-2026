"""Command line: replicate {check,plan,run,report,audit-port}."""
from __future__ import annotations

import argparse
import json
import sys

from replicate import __version__
from replicate.config import ConfigError, load


def _common(p):
    p.add_argument("--config", help="config file (default: $REPLICATE_CONFIG or ./config.yaml)")
    p.add_argument("--tier", choices=["quick", "full"], default="quick",
                   help="quick = CPU-only local steps; full = everything (GPU, network, long steps)")
    p.add_argument("--steps", help="comma-separated step ids (default: every step of the tier)")
    p.add_argument("--with-deps", action="store_true", help="also select the upstream steps of --steps")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="replicate", description="Replication harness, MVA Hackathon 2026")
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="preflight of machine, inputs and rules")
    _common(c)
    c.add_argument("--no-hash", action="store_true", help="check presence of inputs only (no sha256)")
    c.add_argument("--json", action="store_true")
    p = sub.add_parser("plan", help="show the step graph")
    _common(p)
    p.add_argument("--json", action="store_true")
    p.add_argument("--mermaid", action="store_true")
    r = sub.add_parser("run", help="run the steps and write results/")
    _common(r)
    r.add_argument("--rerun", action="store_true", help="move existing step folders aside and run again")
    r.add_argument("--skip-check", action="store_true", help="do not stop on a FAIL in the preflight")
    sub.add_parser("report", help="print the path of the last report").add_argument("--config")
    a = sub.add_parser("audit-port", help="verify the ported scripts against the porting log")
    a.add_argument("--candidates", help="private copies of the as-run scripts (optional)")
    a.add_argument("--recovered", help="private recovered scripts (optional)")
    a.add_argument("--root", action="append", default=[], help="other private origin root, NAME=DIR (optional)")
    a.add_argument("--key-file", help="HMAC key for the keyed hashes of the private originals (authors only)")
    args = ap.parse_args(argv)

    if args.cmd == "audit-port":
        from replicate.porting import audit, summary
        probs = audit(args.candidates, args.recovered, dict(r.split("=", 1) for r in args.root), args.key_file)
        n, edited, in_repo = summary()
        print(f"{n} ported files ({edited} with logged edits, {in_repo} with an as-run copy in this repository)")
        for x in probs:
            print("PROBLEM", x)
        print("audit: " + ("PASS" if not probs else f"FAIL ({len(probs)} problems)"))
        return 0 if not probs else 1

    try:
        cfg = load(args.config)
    except ConfigError as e:
        print(f"config error: {e}", file=sys.stderr)
        return 2
    only = [s.strip() for s in args.steps.split(",")] if getattr(args, "steps", None) else None

    try:
        if args.cmd == "check":
            from replicate.check import run_check
            rep, res = run_check(cfg, args.tier, only, args.with_deps, hash_inputs=not args.no_hash)
            print(json.dumps(res, indent=1) if args.json else rep.table())
            print(f"\noverall: {res['overall']}")
            return 1 if res["overall"] == "FAIL" else 0
        if args.cmd == "plan":
            from replicate.plan import build_plan, mermaid, render, to_json
            plan = build_plan(cfg, args.tier, only, args.with_deps)
            if cfg.workdir:
                w = cfg.require_workdir(create=True)
                (w / "results").mkdir(exist_ok=True)
                (w / "results" / "plan.json").write_text(to_json(plan))
            print(to_json(plan) if args.json else (mermaid(plan) if args.mermaid else render(plan)))
            return 0
        if args.cmd == "run":
            from replicate.check import run_check
            rep, res = run_check(cfg, args.tier, only, args.with_deps)
            print(rep.table())
            print(f"\npreflight: {res['overall']}\n")
            if res["overall"] == "FAIL" and not args.skip_check:
                print("preflight has FAIL items; fix them or use --skip-check (failing steps are then refused one by one)")
                return 1
            from replicate.runner import Runner
            out = Runner(cfg, args.tier, only, args.with_deps, args.rerun).run()
            print("\nsummary:", json.dumps(out["summary"]))
            print("report:", cfg.workdir / "results" / "REPLICATION_REPORT.md")
            bad = {"FAIL", "ERROR"} & set(out["summary"])
            return 1 if bad else 0
        if args.cmd == "report":
            w = cfg.require_workdir()
            print(w / "results" / "REPLICATION_REPORT.md")
            return 0
    except ConfigError as e:
        print(f"config error: {e}", file=sys.stderr)
        return 2
    return 0
