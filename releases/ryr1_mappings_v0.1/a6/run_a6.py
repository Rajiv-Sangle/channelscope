#!/usr/bin/env python3
"""run_a6.py - run check A6 alone, from this release's public files, and read the result.

Check A6 compares the human-rabbit mapping with ten published statements of which human residue corresponds to which
rabbit residue (the list `a6_stated_correspondences.tsv`, beside this script). Its first run failed on one entry,
A6-03, whose source states a pair the human sequence cannot hold; the release's README explains it.

This script needs only the release and the project's code:
- the mapping table, through its table record (its SHA-256 is checked);
- the two protein sequences, from their numbering records;
- A6's list, byte for byte, and A6's own record from the first run;
- check A6's functions, read from the code's `m01_mapping_checks.py` and `checks.py` by their names, so nothing is
  retyped.

It runs A6 on those inputs, and runs A6's planted fault (every human residue from 4540 on mapped one rabbit residue
further) on the same inputs. It then reads the result by the four conditions in `how_a_rerun_of_a6_is_read.md`: the
list's SHA-256, all ten rows, the window around A6-03, and the fault's count of reproduced entries below the real
run's. It prints each condition and the reading, "known" or "news". It exits 0 only if the run reproduces the first
run's record exactly, real run and fault; otherwise 1. A6's own outcome is "fail" either way: the known case is the
failure the README explains.

    python run_a6.py [--code DIR] [--mapping TSV]

`--code` is the folder that holds the package's modules (default: `code/src/channelscope` at the repository's root).
`--mapping` replaces the mapping table with another file, for testing; its checksum is then not checked, and a run on
any other mapping is expected to read "news".
"""
from __future__ import annotations

import argparse
import ast
import copy
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RELEASE = HERE.parent
GRAPH = RELEASE / "graph"
LIST = HERE / "a6_stated_correspondences.tsv"
A6_RECORD = "cs:check_result.R2g8_EbkE2AkRkXlt0hrjWN5bMxBofK1"


def grab(path: Path, names: set[str]) -> str:
    """The named top-level functions and classes of a module, as stored (decorators included)."""
    text = path.read_text("utf-8")
    out = []
    for node in ast.parse(text).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            seg = ast.get_source_segment(text, node)
            if node.decorator_list:
                seg = "\n".join("@" + ast.get_source_segment(text, d) for d in node.decorator_list) + "\n" + seg
            out.append(seg)
    if len(out) != len(names):
        sys.exit(f"could not find {sorted(names)} in {path}")
    return "\n\n".join(out)


def record(name: str, rid: str) -> dict:
    for raw in (GRAPH / "records" / name).read_bytes().split(b"\n"):
        if raw.strip():
            rec = json.loads(raw)
            if rec.get("id") == rid:
                return rec
    sys.exit(f"{rid} is not in records/{name}")


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run check A6 alone and read the result.")
    ap.add_argument("--code", type=Path, default=RELEASE.parents[1] / "code" / "src" / "channelscope")
    ap.add_argument("--mapping", type=Path, default=None)
    args = ap.parse_args(argv)

    ns: dict = {}
    exec("from __future__ import annotations\nfrom dataclasses import dataclass\nfrom typing import Any\n"
         + grab(args.code / "checks.py", {"Outcome"}), ns)
    exec(grab(args.code / "m01_mapping_checks.py", {"_expand", "a6", "_a6_fault"}), ns)
    a6, a6_fault = ns["a6"], ns["_a6_fault"]

    first = record("check_result.jsonl", A6_RECORD)
    obs = first["observed"]
    table_id = next(u for u in first["provenance"]["used"] if u.startswith("cs:table."))
    table = record("table.jsonl", table_id)
    if args.mapping is None:
        data = (GRAPH / table["path"]).read_bytes()
        if sha256(data) != table["sha256"]:
            sys.exit("the mapping table does not match its record")
        print(f"mapping: {table['path']} (SHA-256 matches its table record)")
    else:
        data = args.mapping.read_bytes()
        print(f"mapping: {args.mapping} (a replacement, not checked against the record)")
    rows = list(csv.DictReader(io.StringIO(data.decode("utf-8")), delimiter="\t"))
    seqs = {}
    for raw in (GRAPH / "records" / "numbering.jsonl").read_bytes().split(b"\n"):
        if raw.strip():
            r = json.loads(raw)
            seqs[r.get("identifier")] = r.get("sequence")
    list_bytes = LIST.read_bytes()
    entries = list(csv.DictReader(io.StringIO(list_bytes.decode("utf-8")), delimiter="\t", quoting=csv.QUOTE_NONE))
    inp = {"rows": rows, "s": seqs["numbering:P21817-1.sv3"], "o": seqs["numbering:P11716.sv1"], "entries": entries,
           "list_sha256": sha256(list_bytes)}

    real = json.loads(json.dumps(a6(copy.deepcopy(inp)).observed))
    fault = a6(a6_fault(copy.deepcopy(inp))).observed
    print(f"A6: {real['reproduced']} of {real['entries']} entries reproduced; not reproduced: "
          f"{', '.join(real['not_reproduced']) or 'none'}; under the planted fault: {fault['reproduced']}")

    conditions = {
        "1. the list's SHA-256 equals the first run's": real["list_sha256"] == obs["list_sha256"],
        "2. all ten rows equal the first run's, field for field": real["results"] == obs["results"],
        "3. the window around A6-03 equals the first run's": real["investigation_window"] == obs["investigation_window"],
        "4. the planted fault lowers the count of reproduced entries": fault["reproduced"] < real["reproduced"],
    }
    for text, held in conditions.items():
        print(f"  {'holds' if held else 'FAILS'}: {text}")
    known = all(conditions.values())
    print(f"reading: {'known' if known else 'news'}"
          + (" (the source error the README explains; A6's outcome is still 'fail')" if known else
             " (investigate on both sides, the source's and ours, with neither presumed right)"))

    same_record = ({k: v for k, v in obs.items() if k != "control_observed"} == real
                   and {"reproduced": fault["reproduced"], "not_reproduced": fault["not_reproduced"][:5]}
                   == obs["control_observed"])
    print(f"the first run's record reproduced exactly (real run and fault): {'yes' if same_record else 'no'}")
    return 0 if known and same_record else 1


if __name__ == "__main__":
    raise SystemExit(main())
