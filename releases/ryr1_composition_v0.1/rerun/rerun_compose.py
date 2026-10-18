#!/usr/bin/env python3
"""rerun_compose.py - re-run CL-4's composition from this release with the code that built it, and compare every cell of
the nine tables with the release's.

It lays out a working tree in a temporary folder: the release's graph (its records, tables and raw answers), the 26
coordinate files, and the A6 table the build read, with the build's code (`code/cl4/`, as it ran). Each coordinate file
is taken from --cache if a file of its name is there, or else fetched from the address in its retrieval record; either
way the build's own guard (check C1) refuses it unless its SHA-256 and size are its record's. The PDB released revision
1.1 of 9ZO8 and 9ZOE on 14 October 2026, after both were measured at revision 1.0, which it no longer serves: a file of
theirs that is not its record's is first rebuilt from the file served, with the patch in patches/ and
rebuild_revision.py, and the guard then checks the rebuilt file. The rebuild needs zlib's output; a Python whose zlib
is zlib-ng (as CPython 3.14's Windows builds are) gives other bytes, which the guard refuses, and the cause is printed.
The A6 table must have the SHA-256 the build's method record gives. The build read that table from git; here it is
read from the file.

It then runs the build's own steps up to its tables: the residue set and L1 to L4, check C5-S's coordinate test and
the withdrawals it implies, and the counts. It does not repeat the build's checks or planted faults; check C5's
comparisons with fresh retrievals are in the release's check records and raw answers, and are not repeated.

Three kinds of cell hold the identifier of a record the build made in the same run: C5-S's check record (in
`cl4_structures`) and the two tables the count tables cite. An identifier is a digest of its record's content, run
times included, so it cannot recur; the re-run holds a placeholder there, and each placeholder must stand for one
identifier only, the one the release's records give. Every other cell must be equal, character for character, and
every row must hold as many cells as the release's. Each of the release's tables is first checked against the SHA-256
and size its table record gives.

    uv run --project code --with gemmi==0.7.5 python releases/ryr1_composition_v0.1/rerun/rerun_compose.py \
        [--release DIR] [--cache DIR] [--keep DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

sys.dont_write_bytecode = True  # no .pyc is written beside the release's rerun/ scripts

RUN = "cs:run.cM-_PoiSXQoVTsgRu_8U4ar2jE7Xjs1k"
METHOD = "cs:method.Qi6ZhuQgejDjBifo5qEBStIyR9ON4d4f"
A6 = "what/references/a6_stated_correspondences.tsv"
HOLDERS = {"cs:check_result." + "C" * 32: "the build's C5-S check record",
           "cs:check_result." + "S" * 32: "the build's C5-S segment record",
           "cs:table." + "T" * 32: "the build's cl4_structures table record",
           "cs:table." + "U" * 32: "the build's cl4_clinvar table record"}
UA = "ChannelScope-rerun/0.1 (re-run of a published release)"


def sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def records(rel: Path) -> dict:
    out = {}
    for f in sorted((rel / "graph" / "records").glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                out[r["id"]] = r
    return out


def cells(data: bytes) -> list[list[str]]:
    lines = data.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return [ln.split("\t") for ln in lines]


def rebuilt_or_served(data: bytes, rec: dict, entry: str, rel: Path) -> bytes:
    """For a file that is not its record's: the measured file rebuilt with the release's patch for the entry, where
    the rebuild gives the record's bytes; otherwise the file as served, which the build's guard then refuses."""
    patch_file = rel / "rerun" / "patches" / f"{entry}.json"
    if not patch_file.is_file():
        return data
    spec = importlib.util.spec_from_file_location("rebuild_revision", rel / "rerun" / "rebuild_revision.py")
    rb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rb)
    patch = json.loads(patch_file.read_text(encoding="utf-8"))
    try:
        rebuilt = rb.rebuild(data, patch)
    except rb.NotRebuilt as e:
        print(f"{entry}: not rebuilt: {e}", flush=True)
        return data
    if sha(rebuilt) != rec["generated"]:
        print(f"{entry}: {rb.why_refused(patch)}", flush=True)
        return data
    print(f"{entry}: rebuilt from revision {patch['from']['revision']} with rerun/patches/{entry}.json", flush=True)
    return rebuilt


def coordinates(recs: dict, cache: Path | None, dest: Path, rel: Path) -> int:
    """The coordinate files the build read, into dest by their stored paths; bytes are checked later by the guard."""
    run = recs[RUN]
    n = 0
    for f in run["used_files"]:
        if not f["path"].startswith("cache/rcsb/"):
            continue
        target = dest / f["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        local = cache / Path(f["path"]).name if cache else None
        rec = next(r for r in recs.values() if r["type"] == "retrieval" and r.get("stored_at") == f["path"])
        if local and local.is_file():
            data = local.read_bytes()
        else:
            req = urllib.request.Request(rec["request"]["url"], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            time.sleep(0.2)
        if sha(data) != rec["generated"]:
            data = rebuilt_or_served(data, rec, Path(f["path"]).name.split(".")[0], rel)
        target.write_bytes(data)
        n += 1
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--release", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--cache", help="a folder holding the coordinate files (*.cif.gz) by name")
    ap.add_argument("--keep", help="lay the working tree out here and keep it (an empty or new folder)")
    args = ap.parse_args(argv)
    rel = Path(args.release).resolve()
    recs = records(rel)
    method = recs[METHOD]
    tmp = Path(args.keep) if args.keep else Path(tempfile.mkdtemp(prefix="cl4_rerun_"))
    tree = tmp / "tree"
    graph = tree / "what" / "evidence_graph"
    shutil.copytree(rel / "graph", graph)
    got = coordinates(recs, Path(args.cache) if args.cache else None, graph, rel)
    a6 = (rel / "inputs" / Path(A6).name).read_bytes()
    if sha(a6) != method["parameters"]["a6_sha256"]:
        print(f"refused: inputs/{Path(A6).name} is not the A6 table the build read ({method['parameters']['a6_sha256']})")
        return 2
    (tree / A6).parent.mkdir(parents=True, exist_ok=True)
    (tree / A6).write_bytes(a6)
    code = tree / "how" / "runtime" / "channelscope" / "cl4"
    shutil.copytree(rel / "code" / "cl4", code)
    print(f"re-run tree: {got} coordinate files; code from {rel / 'code' / 'cl4'}", flush=True)

    sys.path.insert(0, str(code))
    import common  # noqa: E402

    def git_bytes(*a: str) -> bytes:  # the one git read on the build's path to its tables: the A6 table at HEAD
        if a == ("show", f"HEAD:{common.A6_FILE}"):
            return a6
        raise SystemExit(f"the re-run reads no git history, but was asked for {a}")

    common.git_bytes = git_bytes
    import compose  # noqa: E402
    from columns import TABLES  # noqa: E402
    from channelscope.graph import tsv_bytes  # noqa: E402

    t0 = time.time()
    try:
        w = compose.World(method["parameters"]["scope"])
    except common.Refused as e:
        print(f"refused by the build's guard (check C1): {e}")
        return 2
    b = compose.assemble(w, setup=compose.c5s_setup(w, w.cl2))
    compose.add_counts(w, b, "cs:table." + "T" * 32, "cs:table." + "U" * 32)
    print(f"re-run: built in {time.time() - t0:.0f} s; C5-S tested {len(b['tests'])} joins", flush=True)
    rows_of = {"cl4_set": b["set"], "cl4_partners": b["partners"], "cl4_structures": b["structures"],
               "cl4_gnomad": b["gnomad"], "cl4_clinvar": b["clinvar"], "cl4_clinvar_conditions": b["conditions"],
               "cl4_exclusions": b["exclusions"], "cl4_structure_counts": b["counts"], "cl4_vus_counts": b["vus"]}
    tables = {r["name"]: r for r in recs.values() if r["type"] == "table"
              and r["provenance"]["was_generated_by"] == RUN}
    mine_checks = [r for r in recs.values() if r["type"] == "check_result" and r["provenance"]["was_generated_by"] == RUN]
    c5s = [r["id"] for r in mine_checks if r["check"] == "CL4.C5-S"]
    seg = [r["id"] for r in mine_checks if r["check"] == "CL4.C5-S-segment"]
    expect = {"cs:check_result." + "C" * 32: c5s[0] if len(c5s) == 1 else None,
              "cs:check_result." + "S" * 32: seg[0] if len(seg) == 1 else None,  # none: this build withdrew no segment
              "cs:table." + "T" * 32: tables["cl4_structures"]["id"],
              "cs:table." + "U" * 32: tables["cl4_clinvar"]["id"]}
    stands, diffs, n_cells = {}, [], 0
    for name, rows in rows_of.items():
        cols = TABLES[name]
        mine = cells(tsv_bytes([c[0] for c in cols], [[r.get(c[0]) for c in cols] for r in rows]))
        rec = tables[name]
        data = (rel / "graph" / rec["path"]).read_bytes()
        if sha(data) != rec["sha256"] or len(data) != rec["bytes"]:
            diffs.append(f"{name}: the release's file is not the one its table record {rec['id']} names")
            continue
        theirs = cells(data)
        if mine[0] != theirs[0]:
            diffs.append(f"{name}: the column lines differ")
            continue
        if len(mine) != len(theirs):
            diffs.append(f"{name}: {len(mine) - 1} rows re-run, {len(theirs) - 1} in the release")
        for i, (a, z) in enumerate(zip(mine[1:], theirs[1:]), start=2):
            if len(a) != len(z):
                diffs.append(f"{name}, line {i}: {len(a)} cells re-run, {len(z)} in the release")
                continue
            for col, x, y in zip(mine[0], a, z):
                n_cells += 1
                if x == y:
                    continue
                if x in HOLDERS:
                    stands.setdefault(x, set()).add(y)
                    continue
                diffs.append(f"{name}, line {i}, {col}: re-run {x!r}, release {y!r}")
    for h, ids in sorted(stands.items()):
        if expect.get(h) is None or len(ids) != 1 or next(iter(ids)) != expect.get(h):
            diffs.append(f"{HOLDERS[h]}: stands for {sorted(ids)[:3]}, the release's records give {expect.get(h)}")
        else:
            print(f"  {HOLDERS[h]}: one identifier, {next(iter(ids))}, as the release's records give")
    for d in diffs[:20]:
        print(f"  DIFFERS: {d}")
    print(f"rerun: {len(rows_of)} tables, {n_cells:,} cells compared; {len(diffs)} differences")
    if not args.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0 if not diffs else 1


if __name__ == "__main__":
    raise SystemExit(main())
