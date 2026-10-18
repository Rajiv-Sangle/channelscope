"""`channelscope` — fill, validate and query the evidence graph.

    channelscope schema write|check      generate the JSON Schema from the models / check it byte-equal
    channelscope fixture write|check     generate the worked fixture / check it byte-equal and valid
    channelscope validate                validate every record, reference and file (rules V01-V17)
    channelscope fetch PLAN.yaml         run a fetch plan: logged calls, raw snapshots, retrieval records
    channelscope query cq02 RESIDUE      CQ-02 for one residue, e.g. residue:P21817-1.sv3:614
    channelscope query sql "SELECT ..."  ad hoc SQL; each record type is a view named after it
    channelscope o4 build-numbering CUR  O4: numbering and protein records for the orthologue entries a curation names
    channelscope o4 check-mapping CHECK  O4: the checks a check file names, on its orthologue mapping (--trial writes
                                         nothing; --replay also replays the UniProt calls, over the network)

Every command takes --graph (default: what/evidence_graph/ of the vault found above the working directory).
Exit codes: 0 clean; 1 findings or differences; 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from . import fixture as fixture_mod
from . import schema as schema_mod
from .graph import Graph, default_graph_root
from .validate import validate


def _graph(args: argparse.Namespace) -> Graph:
    return Graph(Path(args.graph) if args.graph else default_graph_root())


def _fixture_dir(g: Graph) -> Path:
    return schema_mod.schema_dir(g.root) / "fixture"


def cmd_schema(args: argparse.Namespace) -> int:
    d = schema_mod.schema_dir(_graph(args).root)
    if args.action == "write":
        for name in schema_mod.write(d):
            print(f"wrote {d / name}")
        return 0
    problems = schema_mod.check(d)
    for p in problems:
        print(p)
    print("schema: byte-equal to the models" if not problems else f"schema: {len(problems)} difference(s)")
    return 1 if problems else 0


def cmd_fixture(args: argparse.Namespace) -> int:
    target = _fixture_dir(_graph(args))
    with tempfile.TemporaryDirectory() as tmp:
        built = fixture_mod.build(Path(tmp) / "fixture")
        if args.action == "write":
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(built.root, target)
            print(f"wrote {target}")
            return 0
        want, have = fixture_mod.snapshot(built.root), fixture_mod.snapshot(target) if target.exists() else {}
    problems = [f"missing: {k}" for k in want if k not in have]
    problems += [f"differs: {k}" for k in want if k in have and have[k] != want[k]]
    problems += [f"not generated: {k}" for k in have if k not in want]
    findings = validate(Graph(target)) if target.exists() else []
    for p in problems:
        print(p)
    for f in findings:
        print(f)
    ok = not problems and not findings
    print("fixture: byte-equal to its generator and valid" if ok
          else f"fixture: {len(problems)} difference(s), {len(findings)} finding(s)")
    return 0 if ok else 1


def cmd_validate(args: argparse.Namespace) -> int:
    g = _graph(args)
    findings = validate(g)
    for f in findings:
        print(f)
    n = sum(1 for _ in g.lines())
    print(f"validate: {n} record(s) in {g.root}; {len(findings)} finding(s)")
    return 1 if findings else 0


def cmd_fetch(args: argparse.Namespace) -> int:
    from .fetch import fetch, load_plan  # the network layer is imported only when fetching
    from .net import http

    g = _graph(args)
    for r in fetch(g, load_plan(Path(args.plan)), http):
        print(f"{r.id}  {r.response.status}  {r.response.bytes:>9} B  {r.stored_at}  release={r.source_release}")
    return 0


def cmd_seed_sources(args: argparse.Namespace) -> int:
    from .curation import seed_sources

    for s in seed_sources(_graph(args), Path(args.curation)):
        print(f"{s.id}  {s.identifier}")
    return 0


def cmd_plan_clinvar(args: argparse.Namespace) -> int:
    from .clinvar import summary_plan

    g = _graph(args)
    text = summary_plan(g.path(args.esearch).read_bytes(), args.batch, args.stored_prefix)
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


def cmd_m01(args: argparse.Namespace) -> int:
    g = _graph(args)
    if args.action == "build-genome":
        from .m01 import build_genome
        print(json.dumps(build_genome(g, Path(args.inputs)), indent=2))
        return 0
    if args.action == "build-mapping":
        from .m01_align import build_mapping
        print(json.dumps(build_mapping(g, Path(args.inputs)), indent=2))
        return 0
    if args.action == "check-mapping":
        from .m01_mapping_checks import run_mapping_checks
        results = run_mapping_checks(g, Path(args.inputs))
        for r in results:
            print(f"{r.check:4s} {r.outcome:8s} control={r.control.outcome:9s} {r.id}")
        return 0 if all(r.outcome == "pass" and r.control.outcome == "detected" for r in results) else 1
    from .m01_checks import run_genome_checks
    results = run_genome_checks(g, Path(args.inputs))
    for r in results:
        print(f"{r.check:4s} {r.outcome:8s} control={r.control.outcome:9s} {r.id}")
    return 0 if all(r.outcome == "pass" and r.control.outcome == "detected" for r in results) else 1


def cmd_o4(args: argparse.Namespace) -> int:
    g = _graph(args)
    if args.action == "build-numbering":
        from .o4 import build_numbering
        print(json.dumps(build_numbering(g, Path(args.inputs)), indent=2))
        return 0
    from .o4 import run_mapping_checks
    results = run_mapping_checks(g, Path(args.inputs), trial=args.trial, replay=args.replay)
    for r in results:
        print(f"{r['check']:12s} {r['outcome']:5s} control={r['control']:9s} {r.get('id', '(trial: not recorded)')}")
    return 0 if all(r["outcome"] == "pass" and r["control"] == "detected" for r in results) else 1


def cmd_query(args: argparse.Namespace) -> int:
    from .query import connect, cq02

    g = _graph(args)
    if args.kind == "cq02":
        print(json.dumps(cq02(g, args.text), indent=2))
        return 0
    rel = connect(g).sql(args.text)
    if rel is not None:
        print(rel)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="channelscope", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--graph", help="the evidence graph's root (default: what/evidence_graph/ of this vault)")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("schema")
    s.add_argument("action", choices=["write", "check"])
    s.set_defaults(func=cmd_schema)
    s = sub.add_parser("fixture")
    s.add_argument("action", choices=["write", "check"])
    s.set_defaults(func=cmd_fixture)
    s = sub.add_parser("validate")
    s.set_defaults(func=cmd_validate)
    s = sub.add_parser("fetch")
    s.add_argument("plan")
    s.set_defaults(func=cmd_fetch)
    s = sub.add_parser("seed-sources")
    s.add_argument("curation")
    s.set_defaults(func=cmd_seed_sources)
    s = sub.add_parser("m01", help="M01: build the genome leg's records, run checks G1-G6, A1 and A2, or align the "
                                   "two numberings two ways and build the residue mapping")
    s.add_argument("action", choices=["build-genome", "check-genome", "build-mapping", "check-mapping"])
    s.add_argument("inputs", help="the build's input list, e.g. what/evidence_graph/curation/build_m01_genome.yaml")
    s.set_defaults(func=cmd_m01)
    s = sub.add_parser("o4", help="O4: write the orthologue numberings, or run an O4 check file on its mapping")
    s.add_argument("action", choices=["build-numbering", "check-mapping"])
    s.add_argument("inputs", help="the curation file (build-numbering) or the check file (check-mapping)")
    s.add_argument("--trial", action="store_true", help="check-mapping: run on a scratch graph and write nothing")
    s.add_argument("--replay", action="store_true", help="check-mapping: also replay the UniProt calls (network)")
    s.set_defaults(func=cmd_o4)
    s = sub.add_parser("plan-clinvar-summaries")
    s.add_argument("esearch", help="the esearch snapshot, relative to the graph root")
    s.add_argument("out", help="where to write the plan")
    s.add_argument("--batch", type=int, default=200)
    s.add_argument("--stored-prefix", required=True, help="snapshot path prefix, relative to the graph root")
    s.set_defaults(func=cmd_plan_clinvar)
    s = sub.add_parser("query")
    s.add_argument("kind", choices=["cq02", "sql"])
    s.add_argument("text")
    s.set_defaults(func=cmd_query)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
