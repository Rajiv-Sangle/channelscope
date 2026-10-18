"""O4 of the proof-of-concept sprint: the orthologue numberings (mouse, pig) and the checks on their residue mappings to
human P21817-1, in M01's pattern.

`build_numbering` writes, for each orthologue entry a curation file names (curation/o4_ryr1_orthologues.yaml), a
numbering record and a protein record from its logged UniProt snapshot, as M01's build_genome wrote rabbit's. It
refuses before writing anything if a snapshot disagrees with the file or the numbering already exists. The mappings
themselves are built by M01's builder, unchanged (`channelscope m01 build-mapping`).

`run_mapping_checks` runs what a check file names (curation/check_o4_mapping_*.yaml): M01's A3, A4, A5, A8 and A9, with
injected faults fitted to the alignment under test (M01's own faults name human-rabbit positions); stated
correspondences and controls under A6's rule; and A11 where the file names an archive table. Each check runs with an
injected fault it must catch (checks.run_check). A8 here is offline: validation, the table against its record, and a
re-run of the build in a copy of the graph without this mapping's records; the UniProt replay runs only when asked,
since it calls the network.

A check_result is written only if the check file is committed and unchanged since the commit that first contained it,
which becomes the criterion's `pre_registered_in`. With `trial=True` nothing is written and the results are returned,
for a scratch graph. Written 2026-10-06 from O4's trial (a working record, not public).
"""

from __future__ import annotations

import csv
import io
import json
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from . import models as mdl
from .checks import Outcome, check_result_record, run_check
from .curation import method_record, run_record
from .graph import Graph, find_vault_root
from .ids import sha256_hex
from .m01 import Snapshots, _numbering, _refuse
from .m01_mapping_checks import CRITERIA as M01_CRITERIA
from .m01_mapping_checks import (_a8_fault, _a9_fault, _a11_fault, _jsonable, _plain, a3, a4, a5, a8, a9, a9_queries,
                                 a11, archive_segments)
from .models import SCHEMA_VERSION
from .provenance import AGENT_LUMEN, now
from .query import cq02_for_mapping, current

MISSION = "mission_channelscope_poc_sprint"
FAILS_IF = {"A3": M01_CRITERIA["A3"][1], "A4": M01_CRITERIA["A4"][1], "A5": M01_CRITERIA["A5"][1],
            "A6-stand-in": M01_CRITERIA["A6"][1], "A8": M01_CRITERIA["A8"][1], "A9": M01_CRITERIA["A9"][1],
            "A11": M01_CRITERIA["A11"][1]}


# --- the numberings ---------------------------------------------------------------------------------------------------

def build_numbering(graph: Graph, curation_path: Path) -> dict[str, Any]:
    started = now()
    cur = yaml.safe_load(curation_path.read_text(encoding="utf-8"))
    snaps = Snapshots(graph, {sp: c["snapshot"] for sp, c in cur["proteins"].items()})
    existing = {r.identifier: r.id for r in graph.records() if isinstance(r, mdl.Numbering)}
    plan = []
    for sp, c in cur["proteins"].items():
        d = snaps.json(sp)
        acc = c["uniprot"]
        _refuse(d["primaryAccession"] == acc, f"{sp}: the snapshot is {d['primaryAccession']}, not {acc}")
        _refuse(f"NCBITaxon:{d['organism']['taxonId']}" == c["taxon"], f"{sp}: {acc}'s organism is not {c['taxon']}")
        _refuse(not any(x.get("commentType") == "ALTERNATIVE PRODUCTS" for x in d.get("comments", [])),
                f"{acc} defines isoforms; number them by isoform")
        ident = f"numbering:{acc}.sv{d['entryAudit']['sequenceVersion']}"
        _refuse(ident not in existing, f"{ident} already exists ({existing.get(ident)}); a numbering is written once")
        plan.append((sp, c, d, ident))

    method = graph.append(method_record(
        "channelscope.o4.build_numbering",
        "Write a numbering record and a protein record for each orthologue entry a curation file names, from its "
        "logged UniProt snapshot, as M01's build_genome wrote rabbit's."))
    run = graph.append(run_record(method.id, started, [
        {"path": graph.relative(curation_path), "sha256": "sha256:" + sha256_hex(curation_path.read_bytes())}]))
    out = {}
    for sp, c, d, ident in plan:
        acc, sv, seq = c["uniprot"], d["entryAudit"]["sequenceVersion"], d["sequence"]["value"]
        prov = {"was_generated_by": run.id, "method": method.id, "used": [snaps.digest[sp]],
                "was_attributed_to": AGENT_LUMEN, "primary_knowledge_source": "source:uniprotkb"}
        num = graph.append({"schema_version": SCHEMA_VERSION, "type": "numbering", "synthetic": False,
                            **_numbering(prov, ident, acc, sv, None, f"UniProtKB:{acc}", c["taxon"], seq)})
        names = d["proteinDescription"]
        name = (names.get("recommendedName") or names["submissionNames"][0])["fullName"]["value"]
        prot = graph.append({"schema_version": SCHEMA_VERSION, "type": "protein", "synthetic": False,
                             "provenance": prov, "identifier": f"UniProtKB:{acc}", "name": name,
                             "gene_symbol": d["genes"][0]["geneName"]["value"], "gene": None, "taxon": c["taxon"],
                             "entry_version": d["entryAudit"]["entryVersion"], "canonical_numbering": ident,
                             "isoform_numberings": []})
        out[sp] = {"numbering": ident, "numbering_record": num.id, "protein_record": prot.id,
                   "entry_version": d["entryAudit"]["entryVersion"], "sequence_version": sv, "length": len(seq)}
    return out


# --- faults fitted to the alignment under test ------------------------------------------------------------------------

def a3_fault(inp: dict) -> dict:
    """Method B's first gap moved two columns 5' (M01's fault, at this alignment's first gap after a run of pairs)."""
    ops = [(int(n), op) for n, op in re.findall(r"([1-9][0-9]*)([MID])", inp["path_b"])]
    k = next(i for i, (n, op) in enumerate(ops) if op in "ID" and i > 0 and ops[i - 1][1] == "M" and ops[i - 1][0] >= 3)
    new = ops[:k - 1] + [(ops[k - 1][0] - 2, "M"), ops[k], (2, "M")] + ops[k + 1:]
    merged: list[tuple[int, str]] = []
    for n, op in new:
        if merged and merged[-1][1] == op:
            merged[-1] = (merged[-1][0] + n, op)
        else:
            merged.append((n, op))
    inp["path_b"] = "".join(f"{n}{op}" for n, op in merged)
    return inp


def a4_fault(inp: dict) -> dict:
    """The first subject-only residue given an object residue of its own number (M01's fault used human 1758)."""
    r = next(r for r in inp["rows"] if r["indel"] == "subject-only")
    r["object_position"], r["correspondence"] = r["subject_position"], "pair"
    return inp


def a5_fault(inp: dict) -> dict:
    """Human 614's row given the object residue two past its partner, which then has two partners."""
    r = next(r for r in inp["rows"] if r["subject_position"] == "614")
    r["object_position"] = str(int(r["object_position"]) + 2)
    return inp


# --- stated correspondences and controls, under A6's rule --------------------------------------------------------------

def a6_stated(inp: dict) -> Outcome:
    """Each entry: the mapping gives the stated object residue, and both sides carry the stated amino acid."""
    h2o = {int(r["subject_position"]): (int(r["object_position"]) if r["object_position"] else None)
           for r in inp["rows"] if r["subject_position"]}
    res = []
    for e in inp["entries"]:
        h, q = int(e["human"]), int(e["object"])
        got = h2o.get(h)
        ok = got == q and inp["s"][h - 1] == e["residue"] and inp["o"][q - 1] == e["residue"]
        res.append({"id": e["id"], "human": h, "stated_object": q, "mapped_object": got,
                    "human_aa": inp["s"][h - 1], "object_aa_at_stated": inp["o"][q - 1], "ok": ok})
    return Outcome(passed=bool(res) and all(x["ok"] for x in res), observed={"entries": res})


def a6_stated_fault(inp: dict) -> dict:
    """Every human residue from 500 to 700 and from 4540 on mapped one object residue further (M01's A6 fault, and
    the region of human 614)."""
    for r in inp["rows"]:
        if r["subject_position"] and r["object_position"]:
            h = int(r["subject_position"])
            if h >= 4540 or 500 <= h <= 700:
                r["object_position"] = str(int(r["object_position"]) + 1)
    return inp


# --- the criteria's commit, and A8's re-run ---------------------------------------------------------------------------

def criteria_commit(check_path: Path) -> str:
    """The commit that first contained the check file, refusing a file in no commit or changed since that commit."""
    vault = find_vault_root(Path(__file__).parent)
    try:
        rel = check_path.resolve().relative_to(vault.resolve()).as_posix()
    except ValueError:
        _refuse(False, f"{check_path} is not in the vault, so no commit can hold its criteria")
    added = subprocess.run(["git", "-C", str(vault), "log", "--diff-filter=A", "--format=%h", "--", rel],
                           capture_output=True, text=True, check=True).stdout.split()
    _refuse(bool(added), f"{rel} is in no commit: commit the criteria before the run they judge")
    first = added[-1]
    then = subprocess.run(["git", "-C", str(vault), "show", f"{first}:{rel}"], capture_output=True, check=True).stdout
    _refuse(then == check_path.read_bytes(),
            f"{rel} differs from its version in {first}: a criterion changed after its commit needs the operator's word")
    return first


def rerun_without_mapping(graph: Graph, build_path: Path, drop: set[str], table_path: str) -> str:
    """Build the mapping again in a copy of the graph that holds neither this mapping's records nor its table, and
    return the new table's sha256. The copy keeps the records, the curation files and the build's snapshots."""
    from .m01_align import build_mapping

    build = yaml.safe_load(build_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "graph"
        (root / "records").mkdir(parents=True)
        for f in graph.records_dir.glob("*.jsonl"):
            kept = [ln for ln in f.read_bytes().splitlines(keepends=True)
                    if ln.strip() and json.loads(ln).get("id") not in drop]
            (root / "records" / f.name).write_bytes(b"".join(kept))
        shutil.copytree(graph.path("curation"), root / "curation")
        for rel in build["snapshots"].values():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(graph.path(rel), root / rel)
        g = Graph(root)
        build_mapping(g, g.path(graph.relative(build_path)))
        return "sha256:" + sha256_hex(g.path(table_path).read_bytes())


# --- running them ------------------------------------------------------------------------------------------------------

def run_mapping_checks(graph: Graph, check_path: Path, trial: bool = False, replay: bool = False) -> list[dict]:
    from Bio.Align import substitution_matrices

    from .validate import validate

    started = now()
    chk = yaml.safe_load(check_path.read_text(encoding="utf-8"))
    commit = None if trial else criteria_commit(check_path)
    build_path = graph.path(chk["build_inputs"])
    build = yaml.safe_load(build_path.read_text(encoding="utf-8"))
    recs = current(graph.records())
    by_id = {r.id: r for r in recs}
    [mapping] = [r for r in recs if isinstance(r, mdl.ResidueMapping) and r.subject == build["subject"]
                 and r.object == build["object"]]
    aln_a, aln_b = (by_id[x] for x in mapping.alignments)
    method_b = by_id[aln_b.provenance.method]
    table = by_id[mapping.table]
    rows = list(csv.DictReader(io.StringIO(graph.path(table.path).read_text("utf-8")), delimiter="\t"))
    nums = {r.identifier: r for r in recs if isinstance(r, mdl.Numbering)}
    s, o = nums[build["subject"]].sequence, nums[build["object"]].sequence
    sc = build["scoring"]

    lines = list(graph.lines())
    replays = []
    if replay:
        from .m01_mapping_checks import _replays
        replays = _replays(graph, [build["snapshots"]["uniprot_human"], build["snapshots"]["uniprot_rabbit"]])
    a8_inputs = {"findings": [f"{f.rule} {f.where}: {f.message}" for f in validate(graph)], "records": len(lines),
                 "declared_versions": dict(Counter(json.loads(ln.raw)["schema_version"] for ln in lines)),
                 "v0_1_valid": None,
                 "without_provenance": [r.id for r in (aln_a, aln_b, table, mapping)
                                        if getattr(r, "provenance", None) is None],
                 "table_bytes": graph.path(table.path).read_bytes(), "table_sha_recorded": table.sha256,
                 "rerun_base": "this graph without the mapping's own records and table",
                 "rerun_table_sha": rerun_without_mapping(graph, build_path, {mapping.id, aln_a.id, aln_b.id, table.id},
                                                          table.path),
                 "replays": replays}
    entries = list(chk.get("controls", [])) + list(chk.get("a6_stand_in", []))
    plans = {
        "A3": (a3, {"s": s, "o": o, "matrix": _plain(substitution_matrices.load(sc["matrix"])),
                    "open_gap": float(sc["open_gap_score"]), "extend_gap": float(sc["extend_gap_score"]),
                    "path_a": aln_a.path, "path_b": aln_b.path, "score_a": aln_a.score, "score_b": aln_b.score,
                    "scale": method_b.parameters["scale"], "rows": rows},
               a3_fault, "method B's first gap moved two columns 5'"),
        "A4": (a4, {"rows": rows, "n_subject": len(s), "n_object": len(o)}, a4_fault,
               "the first subject-only residue given an object residue of its own number"),
        "A5": (a5, {"rows": rows, "s": s, "o": o, "n_identical": aln_a.n_identical}, a5_fault,
               "human 614's row given the object residue two past its partner"),
        "A6-stand-in": (a6_stated, {"rows": rows, "s": s, "o": o, "entries": entries}, a6_stated_fault,
                        "human 500-700 and from 4540 on mapped one object residue further"),
        "A8": (a8, a8_inputs, _a8_fault, "one byte of a copy of the mapping table changed"),
        "A9": (a9, {"queries": a9_queries(build, aln_a.path, chk["a9_human_positions"]),
                    "cq02": cq02_for_mapping(graph, mapping.id)}, _a9_fault, "a cq02 that drops the field `methods`"),
    }
    if chk.get("a11_archive_note"):
        note = Path(chk["a11_archive_note"])
        plans["A11"] = (a11, {"rows": rows, "segments": archive_segments(note.read_text("utf-8"),
                                                                          chk["a11_table_header"]),
                              "archive_file": {"path": str(note), "sha256": "sha256:" + sha256_hex(note.read_bytes())}},
                        _a11_fault, "the archive's last segment offset lowered by one")
    results = {name: run_check(fn, inp, fault, text) for name, (fn, inp, fault, text) in plans.items()}
    notes = {"A8": "Offline: validation, the table against its record, and a re-run in a copy of the graph without "
                   "this mapping's records" + ("; with the UniProt replay." if replay else
                                                "; the UniProt replay was not run (it calls the network)."),
             "A9": "CQ-02's answers read for this mapping only (query.cq02_for_mapping).",
             "A6-stand-in": "A6's rule on the stand-ins and controls the check file lists."}
    if trial:
        return [{"check": n, "outcome": r.outcome, "control": r.control, "fault": r.fault,
                 "observed": json.loads(json.dumps(r.observed, default=_jsonable))} for n, r in results.items()]

    method = graph.append(method_record("channelscope.o4.check_mapping", "Run the checks an O4 check file names on an "
                                        "orthologue residue mapping, each with an injected fault it must catch."))
    run = graph.append(run_record(method.id, started, [
        {"path": graph.relative(check_path), "sha256": "sha256:" + sha256_hex(check_path.read_bytes())},
        {"path": graph.relative(build_path), "sha256": "sha256:" + sha256_hex(build_path.read_bytes())}]))
    used = [mapping.id, aln_a.id, aln_b.id, table.id, build["subject"], build["object"]]
    vault = find_vault_root(Path(__file__).parent)
    document = check_path.resolve().relative_to(vault.resolve()).as_posix()
    out = []
    for name, r in results.items():
        rec = check_result_record(
            r, check=name, mission=MISSION,
            criterion={"document": document, "pre_registered_in": commit, "fails_if": FAILS_IF[name]},
            provenance={"was_generated_by": run.id, "method": method.id, "used": used, "was_attributed_to": AGENT_LUMEN},
            synthetic=False, note=notes.get(name))
        brief = {k: (v[:5] if isinstance(v, list) else v) for k, v in r.control_observed.items()
                 if not isinstance(v, (bytes, bytearray))}
        rec["observed"] = {**rec["observed"], "control_observed": brief}
        stored = graph.append(json.loads(json.dumps(rec, default=_jsonable)))
        out.append({"check": name, "outcome": r.outcome, "control": r.control, "id": stored.id})
    return out
