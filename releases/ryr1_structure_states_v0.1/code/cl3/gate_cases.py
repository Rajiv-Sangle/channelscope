#!/usr/bin/env python3
"""gate_cases.py - CL-3, P0.3: each of S13's 26 entries' gate-numbering case, (a) to (d), derived from CL-2's entries
and segments tables by the rule CL-2's criteria fix, written as a graph table with this run's own method, run and
table records.

The rule is not restated here; it is applied as committed, in what/context/context_channelscope_cl2_numbering_criteria.md
version 2.2, under "The gate residue, and what CL-3 does with it", committed in 125f89f (2026-10-11 16:41:03 IST)
before CL-2's SIFTS files were fetched and before its run. Each RyR1 chain's gate reading falls in one case:
  (c) anything that is not (a) or (b);
  (b) the chain has no SIFTS position at all (path S "none" or another accession), and its gate residue is joined,
      "path A only", at offset 0, inside a run of offset 0 that holds at least 10 modelled residues on each side;
  (a) the gate residue is joined, "agree", at offset 0, the residue is an isoleucine, and it is not identity low.
An entry takes its worst chain's case, (c) worst, then (b), then (a). (d): CL-2's run stopped or is marked unusable,
or the entry has no analysed RyR1 chain.

How each condition is read from CL-2's tables (the tables/ copies, checked against their table records):
  - the chain rows of the entries table (scope "chain") are the analysed RyR1 chains; the gate residue is S13's, and
    the chain row must name the same one;
  - "agree" or "path A only": the chain row's gate_outcome, exactly ("(identity low)" appended means identity low);
  - joined: the gate residue's run in the segments table (the run of the chain whose author numbers hold the gate's)
    has the same status, is not identity low, and is not a short departing run on path A alone; and the chain row's
    gate_note is "-" (CL-2 writes a departure, "not joined", "disputed" or "not modelled" there otherwise);
  - offset 0: the chain row's gate_species_position equals the gate's author number, and the run's offset (offset_s
    for agree, offset_a for path A only) is 0;
  - an isoleucine: the chain row's gate_structure_residue is ILE;
  - no SIFTS position at all: the chain row's path_s begins "none" or "another accession";
  - modelled residues on each side: within the run, the author numbers from its first to the gate (and from the gate
    to its last), less those its unmodelled_gaps name; the run's own count, n_residues, must equal its span less all
    its gaps, or the chain is (c);
  - usable: the committed CL-2 curation file's header holds "# Run: complete" and "# Outcomes: usable".

Planted faults, each run through the same derivation on a corrupted copy, and each must move its entry to the case
named, or nothing is written: CL-2's two (one gate's outcome set to "disputed"; one (b) entry's anchoring run cut to 5
residues), and one per other condition.

    uv run --project how/runtime/channelscope python -I how/runtime/channelscope/cl3/gate_cases.py [--write]

Without --write it derives, runs the planted faults and prints; it writes nothing. With --write it refuses unless this
script and the channelscope package are committed and unchanged, and every input matches its record; then it writes
tables/cl3_gate_cases.tsv and its method, run and table records.
"""
from __future__ import annotations

import copy
import hashlib
import platform
import subprocess
import sys
from pathlib import Path

from channelscope.graph import Graph, tsv_bytes
from channelscope.models import SCHEMA_VERSION
from channelscope.provenance import AGENT_LUMEN, AGENT_SOFTWARE, now

SCRIPT = Path(__file__).resolve()
RUNTIME = SCRIPT.parents[1]
VAULT = SCRIPT.parents[4]
GRAPH_ROOT = VAULT / "what" / "evidence_graph"
PACKAGE = RUNTIME / "src" / "channelscope"
CRITERIA = "what/context/context_channelscope_cl2_numbering_criteria.md"
CRITERIA_COMMIT = "125f89f"
CL2_CURATION = "curation/cl2_run_e888359/cl2_numbering_entries.tsv"
CL2_CURATION_COMMIT = "c4e8b66"
INPUTS = {  # table record, its file under the graph root
    "entries": ("cs:table.M297DUgTR3XktfSgcAekIpqsa2hkNz58", "tables/cl2_numbering_entries.tsv"),
    "segments": ("cs:table.txYgUtvq3af8irDMd4I7NEE8-IqG315J", "tables/cl2_numbering_segments.tsv"),
    "s13": ("cs:table.lVP1WAqwY-tpBjgn7zQrADn2rHj-4G1X", "tables/s13_gate_remeasurement.tsv"),
}
ANCHOR = 10  # modelled residues on each side of the gate, in its run, for case (b)
OUT = "tables/cl3_gate_cases.tsv"
COLUMNS = [
    ("entry", "string", True, "The PDB entry, one of the 26 of S13's table."),
    ("species", "string", True, "The entry's species, as S13's table gives it."),
    ("gate_residue", "string", True, "The gate residue S13 measured, as S13's table gives it: I and its author number."),
    ("gate_case", "string", True, "The entry's case under CL-2's rule (criteria 2.2, committed in 125f89f): a, its gate "
                                  "numbering checked against SIFTS; b, checked by this project's alignment alone, not "
                                  "against SIFTS; c, not checked, or not as expected; d, no usable reading. An entry "
                                  "takes its worst chain's case, c worst, then b, then a."),
    ("gate_case_reason", "string", False, "For cases c and d, why: each chain that is not a or b, with the condition "
                                          "it fails, or why no case can be read; empty for a and b."),
    ("chain_cases", "string", True, "Each analysed RyR1 chain's case, as chain:case, semicolon-separated in CL-2's "
                                    "order; - where the entry has none."),
]
WORST = {"a": 0, "b": 1, "c": 2}


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.run(["git", "-C", str(VAULT), *args], capture_output=True, check=True).stdout


def read_tsv(data: bytes) -> list[dict[str, str]]:
    lines = data.decode("utf-8").split("\n")
    assert lines[-1] == "", "a table ends with a newline"
    head = lines[0].split("\t")
    rows = [dict(zip(head, ln.split("\t"))) for ln in lines[1:-1]]
    assert all(len(r) == len(head) for r in rows)
    return rows


def gaps(text: str) -> list[tuple[int, int]]:
    if text == "-":
        return []
    return [(int(a), int(b)) for a, b in (g.split("-") for g in text.split(","))]


def missing_between(gs: list[tuple[int, int]], lo: int, hi: int) -> int:
    """Author numbers in [lo, hi] that the run's gaps name."""
    return sum(max(0, min(b, hi) - max(a, lo) + 1) for a, b in gs)


def chain_case(row: dict[str, str], runs: list[dict[str, str]], gate: int) -> tuple[str, str]:
    """(case, why) for one chain: why is empty for a and b, else the first condition that fails."""
    outcome, note = row["gate_outcome"], row["gate_note"]
    if outcome not in ("agree", "path A only"):
        return "c", f"gate outcome {outcome!r}"
    if note != "-":
        return "c", f"gate note {note!r}"
    if row["gate_species_position"] != str(gate):
        return "c", f"species position {row['gate_species_position'] or 'none'}, not the author number {gate}"
    held = [s for s in runs if s["author_first"].isdigit() and s["author_last"].isdigit()
            and int(s["author_first"]) <= gate <= int(s["author_last"])]
    if len(held) != 1:
        return "c", f"{len(held)} runs hold author number {gate}"
    run = held[0]
    if run["status"] != outcome:
        return "c", f"its run's status {run['status']!r} is not the gate's outcome {outcome!r}"
    if run["identity_low"] != "false":
        return "c", "its run is identity low"
    if run["short_departing_run_path_a"] != "false":
        return "c", "its run is a short departing run on path A alone"
    offset = run["offset_s"] if outcome == "agree" else run["offset_a"]
    if offset != "0":
        return "c", f"its run's offset is {offset or 'none'}"
    if outcome == "agree":
        if row["gate_structure_residue"] != "ILE":
            return "c", f"the residue is {row['gate_structure_residue']}, not an isoleucine"
        return "a", ""
    if not (row["path_s"].startswith("none") or row["path_s"].startswith("another accession")):
        return "c", f"path A only in a chain SIFTS maps (path S {row['path_s']!r})"
    first, last, gs = int(run["author_first"]), int(run["author_last"]), gaps(run["unmodelled_gaps"])
    if (last - first + 1) - missing_between(gs, first, last) != int(run["n_residues"]):
        return "c", "its run's modelled residues cannot be counted on each side"
    before = (gate - first) - missing_between(gs, first, gate - 1)
    after = (last - gate) - missing_between(gs, gate + 1, last)
    if min(before, after) < ANCHOR:
        return "c", f"its run of offset 0 holds {before} modelled residues before the gate and {after} after it"
    return "b", ""


def derive(entries, segments, s13, usable: bool) -> list[dict[str, str]]:
    out = []
    for srow in s13:
        entry, gate_res = srow["entry"], srow["gate_residue"]
        gate = int(gate_res[1:])
        chains = [r for r in entries if r["entry"] == entry and r["scope"] == "chain"]
        base = {"entry": entry, "species": srow["species"], "gate_residue": gate_res}
        if not usable:
            out.append({**base, "gate_case": "d", "gate_case_reason": "CL-2's run is not usable", "chain_cases": "-"})
            continue
        if not chains:
            out.append({**base, "gate_case": "d", "gate_case_reason": "no analysed RyR1 chain", "chain_cases": "-"})
            continue
        cases, whys = [], []
        for r in chains:
            if r["gate_residue"] != gate_res:
                case, why = "c", f"CL-2 read {r['gate_residue']!r}, S13 measured {gate_res!r}"
            else:
                runs = [s for s in segments if s["entry"] == entry and s["chain"] == r["chain"]]
                case, why = chain_case(r, runs, gate)
            cases.append(f"{r['chain']}:{case}")
            if why:
                whys.append(f"chain {r['chain']}: {why}")
        worst = max((c.split(":")[1] for c in cases), key=WORST.get)
        out.append({**base, "gate_case": worst, "gate_case_reason": "; ".join(whys) if worst == "c" else "",
                    "chain_cases": ";".join(cases)})
    return out


def usable_of(curation: bytes) -> bool:
    head = [ln for ln in curation.decode("utf-8").split("\n") if ln.startswith("#")]
    return "# Run: complete" in head and "# Outcomes: usable" in head


def planted(entries, segments, s13, real: list[dict[str, str]]) -> list[tuple[str, bool, str]]:
    """Each fault runs the real derivation on a corrupted copy; caught when its entry lands in the case named."""
    case = {r["entry"]: r["gate_case"] for r in real}
    a = next(e for e, c in case.items() if c == "a")
    b = next(e for e, c in case.items() if c == "b")
    gate = {r["entry"]: int(r["gate_residue"][1:]) for r in s13}

    def first_chain(rows, entry):
        return next(r for r in rows if r["entry"] == entry and r["scope"] == "chain")

    def gate_run(segs, entry, chain):
        return next(s for s in segs if s["entry"] == entry and s["chain"] == chain and s["author_first"].isdigit()
                    and int(s["author_first"]) <= gate[entry] <= int(s["author_last"]))

    out = []

    def run(name, entry, want, ents=entries, segs=segments, usable=True):
        got = {r["entry"]: r for r in derive(ents, segs, s13, usable)}[entry]
        out.append((name, got["gate_case"] == want, f"{entry}: {got['gate_case']} ({got['gate_case_reason'] or '-'})"))

    e = copy.deepcopy(entries)
    first_chain(e, a)["gate_outcome"] = "disputed"
    run(f"CL-2's first: one gate's outcome set to 'disputed' ({a})", a, "c", ents=e)
    s = copy.deepcopy(segments)
    ch = first_chain(entries, b)["chain"]
    g = gate_run(s, b, ch)
    g.update(author_first=str(gate[b] - 2), author_last=str(gate[b] + 2), n_residues="5", unmodelled_gaps="-")
    run(f"CL-2's second: a (b) entry's anchoring run cut to 5 residues ({b})", b, "c", segs=s)
    e = copy.deepcopy(entries)
    first_chain(e, b)["path_s"] = "mapped"
    run(f"a (b) chain whose path S is mapped ({b})", b, "c", ents=e)
    e = copy.deepcopy(entries)
    first_chain(e, a)["gate_structure_residue"] = "VAL"
    run(f"an (a) chain's gate residue not an isoleucine ({a})", a, "c", ents=e)
    e = copy.deepcopy(entries)
    first_chain(e, a)["gate_species_position"] = str(gate[a] + 1)
    run(f"an (a) chain's gate one position off ({a})", a, "c", ents=e)
    s = copy.deepcopy(segments)
    gate_run(s, a, first_chain(entries, a)["chain"])["identity_low"] = "true"
    run(f"an (a) chain's run identity low ({a})", a, "c", segs=s)
    s = copy.deepcopy(segments)
    gate_run(s, b, ch)["offset_a"] = "1"
    run(f"a (b) chain's run off by one ({b})", b, "c", segs=s)
    e = copy.deepcopy(entries)
    first_chain(e, a)["gate_note"] = "departs by 1"
    run(f"an (a) chain's gate note not '-' ({a})", a, "c", ents=e)
    s = copy.deepcopy(segments)
    gate_run(s, b, ch)["short_departing_run_path_a"] = "true"
    run(f"a (b) chain's run a short departing run ({b})", b, "c", segs=s)
    s = copy.deepcopy(segments)
    gate_run(s, b, ch)["status"] = "agree"
    run(f"a (b) chain's run of another status than its gate ({b})", b, "c", segs=s)
    s = copy.deepcopy(segments)
    gr = gate_run(s, b, ch)
    gr["n_residues"] = str(int(gr["n_residues"]) + 1)
    run(f"a (b) chain's run whose count does not match its span ({b})", b, "c", segs=s)
    e, s = copy.deepcopy(entries), copy.deepcopy(segments)
    first_chain(e, b)["gate_outcome"] = "UNK"
    gate_run(s, b, ch)["status"] = "UNK"
    run(f"a (b) chain whose gate and its run are of another category at offset 0 ({b})", b, "c", ents=e, segs=s)
    s = copy.deepcopy(segments)
    s.append(dict(gate_run(s, b, ch)))
    run(f"a (b) chain with two runs holding its gate ({b})", b, "c", segs=s)
    e = copy.deepcopy(entries)
    first_chain(e, a)["gate_residue"] = "I4936"
    run(f"a chain whose gate residue is not S13's ({a})", a, "c", ents=e)
    e = [r for r in entries if not (r["entry"] == a and r["scope"] == "chain")]
    run(f"an entry with no analysed chain ({a})", a, "d", ents=e)
    run(f"CL-2's run not usable ({a})", a, "d", usable=False)
    return out


def code_files() -> list[tuple[str, bytes]]:
    files = [(SCRIPT.relative_to(RUNTIME).as_posix(), SCRIPT.read_bytes())]
    files += [(p.relative_to(RUNTIME).as_posix(), p.read_bytes()) for p in sorted(PACKAGE.rglob("*.py"))]
    return files


def files_digest(files: list[tuple[str, bytes]]) -> str:
    h = hashlib.sha256()
    for rel, data in sorted(files):
        h.update(rel.encode("utf-8") + b"\0")
        h.update(data.replace(b"\r\n", b"\n") + b"\0")
    return "sha256:" + h.hexdigest()


def main(argv: list[str]) -> int:
    write = "--write" in argv
    started = now()
    graph = Graph(GRAPH_ROOT)
    by_id = graph.by_id()
    data, used_files, used = {}, [], []
    for key, (rid, path) in INPUTS.items():
        raw = graph.path(path).read_bytes()
        rec = by_id.get(rid)
        if rec is None or rec.path != path or rec.sha256 != sha256(raw):
            sys.exit(f"refused: {path} does not match its table record {rid}")
        data[key] = read_tsv(raw)
        used_files.append({"path": path, "sha256": sha256(raw), "bytes": len(raw)})
        used.append(rid)
    curation = graph.path(CL2_CURATION).read_bytes()
    if curation != git("show", f"{CL2_CURATION_COMMIT}:what/evidence_graph/{CL2_CURATION}"):
        sys.exit(f"refused: {CL2_CURATION} differs from its blob at {CL2_CURATION_COMMIT}")
    used_files.append({"path": CL2_CURATION, "sha256": sha256(curation), "bytes": len(curation)})
    usable = usable_of(curation)
    rows = derive(data["entries"], data["segments"], data["s13"], usable)
    faults = planted(data["entries"], data["segments"], data["s13"], rows)
    for r in rows:
        print(f"{r['entry']}  {r['gate_case']}  {r['chain_cases']}  {r['gate_case_reason']}")
    for name, caught, detail in faults:
        print(f"{'caught' if caught else 'NOT CAUGHT'}: {name}: {detail}")
    counts = {c: sum(1 for r in rows if r["gate_case"] == c) for c in "abcd"}
    print(f"CL-2's run usable: {usable}; cases: " + ", ".join(f"{c} {n}" for c, n in counts.items()))
    if not all(c for _, c, _ in faults):
        sys.exit("refused: a planted fault was not caught; nothing written")
    if not write:
        print("nothing written (add --write)")
        return 0
    rel_paths = [SCRIPT.relative_to(VAULT).as_posix(), PACKAGE.relative_to(VAULT).as_posix()]
    if git("status", "--porcelain", "--", *rel_paths).strip():
        sys.exit("refused: this script or the channelscope package is not committed as it is")
    commit = git("rev-parse", "HEAD").decode().strip()
    criteria = git("show", f"{CRITERIA_COMMIT}:{CRITERIA}")
    digest = files_digest(code_files())
    script_rel = SCRIPT.relative_to(VAULT).as_posix()
    method = graph.append({
        "schema_version": SCHEMA_VERSION, "type": "method", "synthetic": False, "name": "channelscope.cl3.gate_cases",
        "version": commit[:7],
        "description": "CL-3's gate cases: for each of S13's 26 entries, the case (a to d) of its gate residue's "
                       "numbering under the rule CL-2's criteria fix (version 2.2, under 'The gate residue, and what "
                       "CL-3 does with it', committed in 125f89f before CL-2's fetch and run), derived from CL-2's "
                       "entries and segments tables by this script's own code. (a) checked against SIFTS: the gate "
                       "residue joined, agree, at offset 0, an isoleucine, not identity low; (b) checked by this "
                       "project's alignment alone: no SIFTS position for the chain, the gate residue joined, path A "
                       "only, at offset 0, inside a run of offset 0 holding at least 10 modelled residues on each side; "
                       "(c) anything else; an entry takes its worst chain's case; (d) CL-2's run stopped or unusable, or "
                       "no analysed RyR1 chain. How each condition is read from the tables is in the script's "
                       "docstring. Sixteen planted faults, CL-2's two among them and one for each other condition, "
                       "each run through the same derivation on a corrupted copy, must each move their entry to the "
                       "case named, or nothing is written.",
        "implementation": {"software": script_rel, "version": commit, "code_digest": digest},
        "parameters": {"criteria": CRITERIA, "criteria_commit": git("rev-parse", CRITERIA_COMMIT).decode().strip(),
                       "criteria_sha256": sha256(criteria), "anchor_residues_each_side": ANCHOR,
                       "cl2_usability_from": f"{CL2_CURATION} at {CL2_CURATION_COMMIT}: '# Run: complete' and "
                                             f"'# Outcomes: usable'",
                       "planted_faults": "; ".join(f"{n}: {'caught' if c else 'NOT CAUGHT'} ({d})" for n, c, d in faults),
                       "code_digest_form": "SHA-256 over this script and the channelscope package's source files, "
                                           "each as its path from how/runtime/channelscope, a NUL, its bytes with "
                                           "CRLF as LF, a NUL, in path order"},
        "was_attributed_to": AGENT_LUMEN})
    table = tsv_bytes([c[0] for c in COLUMNS], ([r[c[0]] for c in COLUMNS] for r in rows))
    graph.write_bytes(OUT, table)
    command = ["python", *(["-I"] if sys.flags.isolated else []), script_rel, *argv]
    run = graph.append({
        "schema_version": SCHEMA_VERSION, "type": "run", "synthetic": False, "method": method.id, "command": command,
        "started_at_time": started, "ended_at_time": now(), "used_files": used_files,
        "software": {"name": script_rel, "version": commit, "code_digest": digest},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "was_associated_with": AGENT_SOFTWARE, "acted_on_behalf_of": AGENT_LUMEN})
    rec = graph.append({
        "schema_version": SCHEMA_VERSION, "type": "table", "synthetic": False,
        "provenance": {"was_generated_by": run.id, "method": method.id, "used": used, "was_attributed_to": AGENT_LUMEN},
        "name": "cl3_gate_cases", "path": OUT, "media_type": "text/tab-separated-values", "sha256": sha256(table),
        "bytes": len(table), "row_count": len(rows),
        "columns": [{"name": n, "datatype": t, "required": req, "description": d} for n, t, req, d in COLUMNS],
        "primary_key": ["entry"], "about": []})
    print(f"written: {OUT} {sha256(table)} ({len(rows)} rows); method {method.id}; run {run.id}; table {rec.id}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
