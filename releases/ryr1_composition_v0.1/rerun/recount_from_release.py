#!/usr/bin/env python3
"""recount_from_release.py - re-derive, from this release's own files, every structure row's status and both count
tables, by the build's second script (`code/cl4/recount.py`, check C10's), which imports none of the build's code.

It reads the release's copies of CL-2's three numbering tables, CL-3's gate cases, S13's table of measured states and
the three mapping tables, each checked first against the SHA-256, size and row count its table record gives. Three of
its inputs are the build's own outputs: the residue set (`cl4_set`), the ClinVar table (`cl4_clinvar`) and the
coordinate test's verdicts, from check C5-S's record. An error in one of those would pass both the build and this
recount. Each verdict's segment is read from CL-2's segments table by recount.py's own reading. It refuses a table
with a duplicated key, and prints every difference between what it derives and the release's `cl4_structures`,
`cl4_structure_counts` and `cl4_vus_counts`; none means those tables are what CL-2's tables, CL-3's marks, the set, the
ClinVar table and C5-S's verdicts give under the criteria's rules.

It needs only Python 3.10 or later and no package beyond the standard library:

    python rerun/recount_from_release.py [--release DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

RUN = "cs:run.cM-_PoiSXQoVTsgRu_8U4ar2jE7Xjs1k"
SPECIES = {"P11716.sv1": "Oryctolagus cuniculus", "E9PZQ0.sv1": "Mus musculus", "P16960.sv2": "Sus scrofa"}
KEYS = {"cl4_structures": ("human_position", "entry", "chain"),
        "cl4_structure_counts": ("human_position", "species", "class_measure"),
        "cl4_vus_counts": ("subset", "unit", "join_scope", "species", "class_measure"),
        "cl4_set": ("human_position",)}


def read_tsv(data: bytes) -> list[dict]:
    lines = data.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    cols = lines[0].split("\t")
    out = []
    for ln in lines[1:]:
        cells = ln.split("\t")
        if len(cells) != len(cols):
            raise SystemExit(f"a row has {len(cells)} cells, the column line {len(cols)}")
        out.append(dict(zip(cols, cells)))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--release", default=str(Path(__file__).resolve().parents[1]))
    args = ap.parse_args(argv)
    rel = Path(args.release)
    sys.path.insert(0, str(rel / "code" / "cl4"))
    import recount  # noqa: E402  (the release's copy, as it ran)

    records = {}
    for f in sorted((rel / "graph" / "records").glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                records[r["id"]] = r
    by_path = {r["path"]: r for r in records.values() if r["type"] == "table"}

    def table(suffix: str) -> list[dict]:
        hits = [p for p in by_path if p.endswith(suffix)]
        if len(hits) != 1:
            raise SystemExit(f"{len(hits)} table records end with {suffix}; one expected")
        rec = by_path[hits[0]]
        data = (rel / "graph" / rec["path"]).read_bytes()
        if "sha256:" + hashlib.sha256(data).hexdigest() != rec["sha256"] or len(data) != rec["bytes"]:
            raise SystemExit(f"refused: {rec['path']} is not the file its table record {rec['id']} names")
        rows = read_tsv(data)
        if "row_count" in rec and len(rows) != rec["row_count"]:
            raise SystemExit(f"refused: {rec['path']} holds {len(rows)} rows, its record {rec['row_count']}")
        name = rec["path"].rsplit("/", 1)[-1][:-4]
        if name in KEYS:
            keys = [tuple(r[k] for k in KEYS[name]) for r in rows]
            if len(set(keys)) != len(keys):
                raise SystemExit(f"refused: {rec['path']} holds a key twice ({len(keys) - len(set(keys))} repeats)")
        return rows

    entries, segments, exceptions = (table(f"/cl2_numbering_{n}.tsv") for n in ("entries", "segments", "exceptions"))
    mapping = {sp: table(f"_{acc}.tsv") for acc, sp in SPECIES.items()}
    built = {n: table(f"/{n}.tsv") for n in ("cl4_structures", "cl4_structure_counts", "cl4_vus_counts")}
    residues = [int(r["human_position"]) for r in table("/cl4_set.tsv")]
    c5s = [r for r in records.values() if r["type"] == "check_result" and r["check"] == "CL4.C5-S"
           and r["provenance"]["was_generated_by"] == RUN]
    if len(c5s) != 1:
        raise SystemExit(f"{len(c5s)} records of check C5-S from the build's run; one expected")
    chains = recount.Chains(entries, segments, exceptions)
    tests = []
    for e, c, n, p, verdict, offset in c5s[0]["observed"]["joins"]:
        seg = [r[6] for r in chains.res[(e, c)] if r[0] == n]
        if len(seg) != 1:
            raise SystemExit(f"{e} {c} {n}: {len(seg)} residues of that number in CL-2's segments")
        tests.append({"entry": e, "chain": c, "author_number": n, "partner_position": p, "verdict": verdict,
                      "offset": offset, "segment": seg[0]})
    res = recount.run(built, (entries, segments, exceptions), table("/cl3_gate_cases.tsv"),
                      table("/s13_gate_remeasurement.tsv"), mapping, table("/cl4_clinvar.tsv"), residues, tests, True)
    print(f"recount: {res['rows']} structure rows derived; {len(tests)} coordinate-test verdicts read; "
          f"{len(res['withdrawn_segments'])} segments withdrawn by the segment rule")
    for d in res["differences"][:20]:
        print(f"  DIFFERS: {d}")
    print(f"recount: {len(res['differences'])} differences")
    return 0 if not res["differences"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
