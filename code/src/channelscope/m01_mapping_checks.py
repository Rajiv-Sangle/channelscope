"""M01 objective 5's pre-registered checks on the residue mapping, A3-A9 and A11, each run with an injected fault it
must catch.

The criteria are the mission's, quoted with the commit that first contained them. Where a criterion's words leave a
choice, the execution was fixed in the session file before any check ran
(a working record, not public). Results are recorded as `check_result` records, as they
came out, each with what its injected fault produced.
"""

from __future__ import annotations

import csv
import io
import json
import math
import subprocess
import tarfile
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from . import models as mdl
from .align import partners
from .checks import check_result_record, run_check
from .checks import Outcome
from .curation import method_record, run_record
from .graph import Graph, find_vault_root
from .ids import sha256_hex
from .mapping import PATH_OP
from .provenance import AGENT_LUMEN, now
from .query import CQ02_FIELDS, cq02_for_mapping, current

MISSION = "mission_channelscope_m01_human_rabbit_mapping"
DOC = "how/missions/mission_channelscope_m01_human_rabbit_mapping.md"
CRITERIA = {
    "A3": ("8e84a8b", "Any pair differs, unless the difference is a gap that can be placed in more than one position "
                      "with an equal score. Each such residue is listed and flagged *ambiguous* in the mapping"),
    "A4": ("8e84a8b", "A residue in an indel maps to a residue, or either sum fails"),
    "A5": ("8e84a8b", "Any exception"),
    "A6": ("8e84a8b", "A stated correspondence is not reproduced by the mapping. An amino-acid mismatch fails "
                      "**unless** the source itself states the position is not conserved between species, in which "
                      "case the mapping must still give the stated residue number. A mismatch is investigated as a "
                      "possible error on either side"),
    "A7": ("8e84a8b", "The difference exceeds 0.5 percentage points or 10 pairs, and stated parameter differences "
                      "don't explain it"),
    "A8": ("8e84a8b", "Any invalid record, or a checksum mismatch. A new UniProt entry version with an unchanged "
                      "sequence version is explained, not failed"),
    "A9": ("8e84a8b", "Wrong shape, a missing field, or the insertion check fails"),
    "A11": ("258d6d9", "An exact offset differs. The difference is investigated; the archive is a quarry, not a "
                       "source (SO-DOMAIN-10), so either side may be wrong"),
}
NOTES = {
    "A6": "A6's list was amended after 8e84a8b, each amendment dated in the mission (four entries from Xu 2008; "
          "A6-09 and A6-10 on 2026-10-03). A6-02 and A6-03 share one rabbit residue, so at most one can be "
          "reproduced; the list's note says the other is investigated as an error on either side.",
    "A8": "Read against the schema version the records declare, as the operator clarified on 2026-10-03 (01:50 IST); "
          "the count valid under v0.1 is recorded beside it.",
    "A11": "The archive's offset is rabbit minus human (its §2); compared as residue pairs, never signed offsets.",
    "A9": "From 2026-10-06, CQ-02's answers are read for the mapping under test only (query.cq02_for_mapping): CQ-02 "
          "answers once per mapping, and O4 adds mouse and pig mappings beside rabbit's. The criterion is unchanged.",
}


def _i(s: str) -> int | None:
    return int(s) if s else None


def ranges(nums: list[int]) -> list[str]:
    out: list[str] = []
    for n in sorted(nums):
        if out and "-" not in out[-1] and int(out[-1]) == n - 1:
            out[-1] = f"{out[-1]}-{n}"
        elif out and "-" in out[-1] and int(out[-1].split("-")[1]) == n - 1:
            out[-1] = f"{out[-1].split('-')[0]}-{n}"
        else:
            out.append(str(n))
    return out


def score_path(path: str, s: str, o: str, matrix, open_gap: float, extend_gap: float) -> float:
    """A path's score under affine gaps, written for A3 apart from both aligners: a pair scores the matrix entry; a
    run of gap columns on one side scores open_gap for its first position and extend_gap for each further one."""
    total, i, j, prev = 0.0, 0, 0, ""
    for n_text, op in PATH_OP.findall(path):
        n = int(n_text)
        if op == "M":
            for _ in range(n):
                total += float(matrix[s[i]][o[j]])
                i, j = i + 1, j + 1
        else:
            total += (extend_gap * n) if op == prev else (open_gap + (n - 1) * extend_gap)
            i, j = (i + n, j) if op == "I" else (i, j + n)
        prev = op
    if i != len(s) or j != len(o):
        raise ValueError("the path does not cover both sequences")
    return total


# --- A3 ---------------------------------------------------------------------------------------------------------------

def a3(inp: dict) -> Outcome:
    s, o, m = inp["s"], inp["o"], inp["matrix"]
    rescored_a = score_path(inp["path_a"], s, o, m, inp["open_gap"], inp["extend_gap"])
    rescored_b = score_path(inp["path_b"], s, o, m, inp["open_gap"], inp["extend_gap"])
    twice = inp["score_b"] == inp["scale"] * inp["score_a"]
    a_opt = math.isclose(rescored_a, inp["score_a"], abs_tol=1e-9)
    b_opt = math.isclose(rescored_b, inp["score_a"], abs_tol=1e-9)
    pa_s, pa_o = partners(inp["path_a"])
    pb_s, pb_o = partners(inp["path_b"])
    diff_s = sorted(k for k in pa_s if pa_s[k] != pb_s.get(k))
    diff_o = sorted(k for k in pa_o if pa_o[k] != pb_o.get(k))
    amb_s = {int(r["subject_position"]) for r in inp["rows"] if r["subject_position"] and r["ambiguous"] == "true"}
    amb_o = {int(r["object_position"]) for r in inp["rows"] if r["object_position"] and r["ambiguous"] == "true"}
    unflagged = [f"subject {k}" for k in diff_s if k not in amb_s] + [f"object {k}" for k in diff_o if k not in amb_o]
    return Outcome(passed=twice and a_opt and b_opt and not unflagged, observed={
        "score_a": inp["score_a"], "score_b": inp["score_b"], "scale": inp["scale"], "b_is_scale_times_a": twice,
        "path_a_rescored": rescored_a, "path_b_rescored": rescored_b, "path_a_optimal": a_opt, "path_b_optimal": b_opt,
        "differing_subject_residues": ranges(diff_s), "differing_object_residues": ranges(diff_o),
        "n_differing_residues": len(diff_s) + len(diff_o), "differing_but_not_flagged": unflagged[:20]})


def _a3_fault(inp: dict) -> dict:
    assert inp["path_b"].startswith("3M1D")
    inp["path_b"] = "1M1D2M" + inp["path_b"][len("3M1D"):]
    return inp


# --- A4 ---------------------------------------------------------------------------------------------------------------

def a4(inp: dict) -> Outcome:
    seen_s: Counter = Counter()
    seen_o: Counter = Counter()
    bad, pairs, s_only, o_only = [], 0, 0, 0
    for r in inp["rows"]:
        sp, op = _i(r["subject_position"]), _i(r["object_position"])
        if sp:
            seen_s[sp] += 1
        if op:
            seen_o[op] += 1
        if r["indel"] == "none":
            pairs += 1
            if not (sp and op and r["correspondence"] == "pair"):
                bad.append(f"column {r['column']}: no indel, but not a pair")
        elif r["indel"] == "subject-only":
            s_only += 1
            if op is not None or r["correspondence"] != "no-correspondence":
                bad.append(f"column {r['column']}: subject {sp} in an indel, mapped to {op}")
        elif r["indel"] == "object-only":
            o_only += 1
            if sp is not None or r["correspondence"] != "no-correspondence":
                bad.append(f"column {r['column']}: object {op} in an indel, mapped to {sp}")
        else:
            bad.append(f"column {r['column']}: indel {r['indel']!r}")
    ns, no = inp["n_subject"], inp["n_object"]
    once_s = sorted(k for k in range(1, ns + 1) if seen_s[k] != 1)
    once_o = sorted(k for k in range(1, no + 1) if seen_o[k] != 1)
    return Outcome(passed=not bad and not once_s and not once_o and pairs + s_only == ns and pairs + o_only == no,
                   observed={"pairs": pairs, "subject_only": s_only, "object_only": o_only,
                             "pairs_plus_subject_only": pairs + s_only, "subject_length": ns,
                             "pairs_plus_object_only": pairs + o_only, "object_length": no,
                             "indel_rows_mapped_to_a_residue": bad[:20],
                             "subject_residues_not_exactly_once": once_s[:20],
                             "object_residues_not_exactly_once": once_o[:20]})


def _a4_fault(inp: dict) -> dict:
    r = next(r for r in inp["rows"] if r["subject_position"] == "1758")
    r["object_position"], r["correspondence"] = "1758", "pair"
    return inp


# --- A5 ---------------------------------------------------------------------------------------------------------------

def a5(inp: dict) -> Outcome:
    s, o = inp["s"], inp["o"]
    h2r: dict[int, list[int]] = {}
    r2h: dict[int, list[int]] = {}
    letters_bad, identical = [], 0
    for r in inp["rows"]:
        h, q = _i(r["subject_position"]), _i(r["object_position"])
        if h is None or q is None:
            continue
        h2r.setdefault(h, []).append(q)
        r2h.setdefault(q, []).append(h)
        if r["subject_residue"] != s[h - 1] or r["object_residue"] != o[q - 1]:
            letters_bad.append(f"column {r['column']}")
        identical += s[h - 1] == o[q - 1]
    failed = [f"human {h} -> rabbit {q} -> human {r2h.get(q)}" for h, qs in h2r.items() for q in qs if r2h.get(q) != [h]]
    failed += [f"rabbit {q} -> human {h} -> rabbit {h2r.get(h)}" for q, hs in r2h.items() for h in hs
               if h2r.get(h) != [q]]
    return Outcome(passed=not failed and not letters_bad and identical == inp["n_identical"], observed={
        "human_positions_paired": len(h2r), "rabbit_positions_paired": len(r2h), "round_trips_failed": failed[:20],
        "pairs_whose_letters_differ_from_the_sequences": letters_bad[:20], "identical_pairs": identical,
        "alignment_n_identical": inp["n_identical"]})


def _a5_fault(inp: dict) -> dict:
    r = next(r for r in inp["rows"] if r["subject_position"] == "614")
    r["object_position"] = "616"
    return inp


# --- A6 ---------------------------------------------------------------------------------------------------------------

def _expand(text: str) -> list[int]:
    a, _, b = text.partition("-")
    return list(range(int(a), int(b or a) + 1))


def a6(inp: dict) -> Outcome:
    s, o = inp["s"], inp["o"]
    h2r = {int(r["subject_position"]): int(r["object_position"]) for r in inp["rows"]
           if r["subject_position"] and r["object_position"]}
    results = []
    for e in inp["entries"]:
        hs, rs = _expand(e["human"]), _expand(e["rabbit"])
        mapped = [h2r.get(h) for h in hs]
        h_stated = [x.strip() for x in e["human_aa"].split(";")]
        human_letters = [s[h - 1] for h in hs]
        rabbit_stated = None if e["rabbit_aa"].startswith("not stated") else [x.strip() for x in e["rabbit_aa"].split(";")]
        rabbit_letters = [o[q - 1] for q in rs]
        not_conserved = e["conservation"].startswith("NOT conserved")
        letters_ok = human_letters == h_stated and (rabbit_stated is None or rabbit_letters == rabbit_stated)
        if rabbit_stated is not None and not not_conserved:
            letters_ok = letters_ok and human_letters == rabbit_letters
        reproduced = mapped == rs and letters_ok
        results.append({"id": e["id"], "human": hs, "stated_rabbit": rs, "mapped_rabbit": mapped,
                        "human_letters": "".join(human_letters), "stated_human": "".join(h_stated),
                        "rabbit_letters_at_stated": "".join(rabbit_letters),
                        "stated_rabbit_letters": "".join(rabbit_stated) if rabbit_stated else "not stated",
                        "not_conserved_by_source": not_conserved, "reproduced": reproduced})
    n = sum(r["reproduced"] for r in results)
    return Outcome(passed=n == len(results), observed={
        "entries": len(results), "reproduced": n, "not_reproduced": [r["id"] for r in results if not r["reproduced"]],
        "results": results, "list_sha256": inp["list_sha256"],
        "investigation_window": {"human_159_168": s[158:168], "rabbit_160_169": o[159:169]}})


def _a6_fault(inp: dict) -> dict:
    for r in inp["rows"]:
        if r["subject_position"] and r["object_position"] and int(r["subject_position"]) >= 4540:
            r["object_position"] = str(int(r["object_position"]) + 1)
    return inp


# --- A7 ---------------------------------------------------------------------------------------------------------------

def a7(inp: dict) -> Outcome:
    pts = 100 * inp["n_identical"] / inp["n_pairs"]
    d_pairs, d_pts = abs(inp["n_pairs"] - inp["their_pairs"]), abs(pts - inp["their_percent"])
    return Outcome(passed=d_pairs <= inp["tolerance_pairs"] and d_pts <= inp["tolerance_points"], observed={
        "ours": {"pairs": inp["n_pairs"], "identical": inp["n_identical"], "percent": round(pts, 4)},
        "comparator": {"pairs": inp["their_pairs"], "percent": inp["their_percent"], "method": inp["their_method"]},
        "difference": {"pairs": d_pairs, "percentage_points": round(d_pts, 4)},
        "tolerance": {"pairs": inp["tolerance_pairs"], "percentage_points": inp["tolerance_points"]}})


def _a7_fault(inp: dict) -> dict:
    inp["n_pairs"] -= 11
    return inp


# --- A8 ---------------------------------------------------------------------------------------------------------------

def a8(inp: dict) -> Outcome:
    table_sha = "sha256:" + sha256_hex(inp["table_bytes"])
    replays_ok = all(r["sequence_equal"] and r["sequence_version_equal"] for r in inp["replays"])
    passed = (not inp["findings"] and not inp["without_provenance"] and table_sha == inp["table_sha_recorded"]
              and inp["rerun_table_sha"] == inp["table_sha_recorded"] and replays_ok)
    return Outcome(passed=passed, observed={
        "validate_findings": inp["findings"][:20], "records": inp["records"],
        "declared_schema_versions": inp["declared_versions"], "valid_under_v0_1": inp["v0_1_valid"],
        "mapping_records_without_provenance": inp["without_provenance"],
        "table_sha256_file": table_sha, "table_sha256_record": inp["table_sha_recorded"],
        "rerun": {"base_commit": inp["rerun_base"], "table_sha256": inp["rerun_table_sha"]},
        "replays": inp["replays"]})


def _a8_fault(inp: dict) -> dict:
    b = bytearray(inp["table_bytes"])
    b[-2] = ord("1") if b[-2] != ord("1") else ord("2")
    inp["table_bytes"] = bytes(b)
    return inp


# --- A9 ---------------------------------------------------------------------------------------------------------------

def a9(inp: dict) -> Outcome:
    problems, answered = [], 0
    for residue, inside_indel in inp["queries"]:
        try:
            answers = inp["cq02"](residue)
        except Exception as e:  # a query that cannot answer is a wrong shape
            problems.append(f"{residue}: {type(e).__name__}: {e}")
            continue
        if len(answers) != 1:
            problems.append(f"{residue}: {len(answers)} answers")
            continue
        a = answers[0]
        answered += 1
        missing = [f for f in CQ02_FIELDS if f not in a]
        if missing:
            problems.append(f"{residue}: missing {missing}")
            continue
        pair = a["correspondence"] == "pair"
        if pair != (a["other_residue"] is not None):
            problems.append(f"{residue}: correspondence {a['correspondence']} with other_residue {a['other_residue']}")
        if not a["methods"]:
            problems.append(f"{residue}: no method")
        if not (a["local_identity"] is None or isinstance(a["local_identity"], float)) \
                or not isinstance(a["local_pairs"], int):
            problems.append(f"{residue}: local identity {a['local_identity']!r} over {a['local_pairs']!r}")
        if a["indel"] not in ("none", "subject-only", "object-only"):
            problems.append(f"{residue}: indel {a['indel']!r}")
        if inside_indel and a["correspondence"] != "no-correspondence":
            problems.append(f"{residue}: inside an indel, but mapped to {a['other_residue']}")
    return Outcome(passed=not problems and answered == len(inp["queries"]), observed={
        "queries": len(inp["queries"]), "answered": answered,
        "inside_an_indel": [r for r, inside in inp["queries"] if inside], "problems": problems[:30]})


def _a9_fault(inp: dict) -> dict:
    real = inp["cq02"]
    inp["cq02"] = lambda residue: [{k: v for k, v in a.items() if k != "methods"} for a in real(residue)]
    return inp


def a9_queries(build: dict, path_a: str, human_positions: list[int]) -> list[tuple[str, bool]]:
    """A9's queries for one mapping: the named human residues; each indel segment's flanking pair, from both sides;
    and every residue inside a segment, which must map to nothing."""
    from .m01_align import segments

    subj_id, obj_id = build["subject"].split(":", 1)[1], build["object"].split(":", 1)[1]
    queries: list[tuple[str, bool]] = [(f"residue:{subj_id}:{p}", False) for p in human_positions]
    for seg in segments(path_a):
        for pair in (seg["pair_before"], seg["pair_after"]):
            if pair:
                queries += [(f"residue:{subj_id}:{pair[0]}", False), (f"residue:{obj_id}:{pair[1]}", False)]
        side = subj_id if seg["side"] == "subject-only" else obj_id
        queries += [(f"residue:{side}:{p}", True) for p in range(seg["first"], seg["last"] + 1)]
    return list(dict.fromkeys(queries))


# --- A11 --------------------------------------------------------------------------------------------------------------

def archive_segments(text: str, header: str = "**Human → rabbit (P11716):**") -> list[tuple[int, int, int]]:
    """A table of the archive's grounding note, §2, by its header line (human-to-rabbit unless another is named):
    (first human residue, last, other - human)."""
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.strip().startswith(header))
    out = []
    for ln in lines[start + 1:]:
        if out and not ln.strip().startswith("|"):
            break
        cells = [c.strip().strip("*").strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) >= 2 and "–" in cells[0] and cells[0].replace("–", "").isdigit():
            a, b = cells[0].split("–")
            out.append((int(a), int(b), int(cells[1].replace("−", "-").replace("+", ""))))
    return out


def a11(inp: dict) -> Outcome:
    h2r = {int(r["subject_position"]): _i(r["object_position"]) for r in inp["rows"] if r["subject_position"]}
    flagged = {int(r["subject_position"]) for r in inp["rows"] if r["subject_position"] and r["ambiguous"] == "true"}
    covered: set[int] = set()
    per_segment, boundary, differ = [], [], []
    for a, b, off in inp["segments"]:
        agree = 0
        for h in range(a, b + 1):
            covered.add(h)
            if h2r.get(h) == h + off:
                agree += 1
            elif h in flagged:
                boundary.append(h)
            else:
                differ.append(f"human {h}: archive rabbit {h + off}, ours {h2r.get(h)}")
        per_segment.append({"human": f"{a}-{b}", "offset_rabbit_minus_human": off, "residues": b - a + 1,
                            "agree": agree})
    outside = sorted(h for h in h2r if h not in covered)
    return Outcome(passed=bool(inp["segments"]) and not differ, observed={
        "segments": per_segment, "not_compared_ambiguous": ranges(boundary),
        "not_in_any_archive_segment": ranges(outside), "differ": differ[:30], "archive_file": inp["archive_file"]})


def _a11_fault(inp: dict) -> dict:
    a, b, off = inp["segments"][-1]
    inp["segments"][-1] = (a, b, off - 1)
    return inp


# --- the parts of A8 that run once ------------------------------------------------------------------------------------

def _rerun_table_sha(graph: Graph, base: str, build_inputs: Path, table_path: str) -> str:
    """Extract the graph as committed at `base`, run the build there, and return its table's sha256."""
    from .m01_align import build_mapping

    vault = find_vault_root(Path(__file__).parent)  # the code's own vault, so a copy of the graph can be checked
    with tempfile.TemporaryDirectory() as tmp:
        data = subprocess.run(["git", "-C", str(vault), "archive", base, "what/evidence_graph"], check=True,
                              capture_output=True).stdout
        with tarfile.open(fileobj=io.BytesIO(data)) as tar:
            tar.extractall(tmp, filter="data")
        g = Graph(Path(tmp) / "what" / "evidence_graph")
        inputs = g.path("curation/" + build_inputs.name)
        inputs.write_bytes(build_inputs.read_bytes())
        build_mapping(g, inputs)
        return "sha256:" + sha256_hex(g.path(table_path).read_bytes())


def _replays(graph: Graph, snapshot_paths: list[str]) -> list[dict]:
    from .net import http

    out = []
    for rel in snapshot_paths:
        [ret] = [r for r in graph.records() if isinstance(r, mdl.Retrieval) and r.stored_at == rel]
        stored = json.loads(graph.path(rel).read_bytes())
        res = http(ret.request.http_method, ret.request.url, accept=ret.request.accept)
        now_ = json.loads(res.content) if res.status == 200 else {}
        out.append({"url": ret.request.url, "logged_retrieval": ret.id, "status": res.status,
                    "started_at_time": res.started_at_time, "sha256": "sha256:" + sha256_hex(res.content),
                    "entry_version_then": stored["entryAudit"]["entryVersion"],
                    "entry_version_now": now_.get("entryAudit", {}).get("entryVersion"),
                    "sequence_version_then": stored["entryAudit"]["sequenceVersion"],
                    "sequence_version_now": now_.get("entryAudit", {}).get("sequenceVersion"),
                    "sequence_equal": now_.get("sequence", {}).get("value") == stored["sequence"]["value"],
                    "sequence_version_equal": now_.get("entryAudit", {}).get("sequenceVersion")
                    == stored["entryAudit"]["sequenceVersion"]})
    return out


def _v0_1_valid(graph: Graph) -> int:
    import jsonschema

    schema = json.loads((graph.root / "schema" / "v0.1" / "record.schema.json").read_text("utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return sum(1 for line in graph.lines() if validator.is_valid(json.loads(line.raw)))


# --- running them ------------------------------------------------------------------------------------------------------

def run_mapping_checks(graph: Graph, inputs_path: Path) -> list[mdl.CheckResult]:
    from Bio.Align import substitution_matrices

    from .validate import validate

    started = now()
    inputs = yaml.safe_load(inputs_path.read_text(encoding="utf-8"))
    build_path = graph.path(inputs["build_inputs"])
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
    vault = find_vault_root(Path(__file__).parent)
    a6_path = vault / inputs["a6_list"]
    a6_text = a6_path.read_text("utf-8")
    a6_entries = list(csv.DictReader(io.StringIO(a6_text), delimiter="\t", quoting=csv.QUOTE_NONE))
    archive = Path(inputs["a11_archive_note"])
    a11_text = archive.read_text("utf-8")
    sc = build["scoring"]

    findings = [f"{f.rule} {f.where}: {f.message}" for f in validate(graph)]
    lines = list(graph.lines())
    mapping_records = [aln_a, aln_b, table, mapping]
    a8_inputs = {"findings": findings, "records": len(lines),
                 "declared_versions": dict(Counter(json.loads(ln.raw)["schema_version"] for ln in lines)),
                 "v0_1_valid": _v0_1_valid(graph),
                 "without_provenance": [r.id for r in mapping_records if getattr(r, "provenance", None) is None],
                 "table_bytes": graph.path(table.path).read_bytes(), "table_sha_recorded": table.sha256,
                 "rerun_base": inputs["a8_rerun_base"],
                 "rerun_table_sha": _rerun_table_sha(graph, inputs["a8_rerun_base"], build_path, table.path),
                 "replays": _replays(graph, [build["snapshots"]["uniprot_human"], build["snapshots"]["uniprot_rabbit"]])}

    queries = a9_queries(build, aln_a.path, inputs["a9_human_positions"])

    plans = {
        "A3": (a3, {"s": s, "o": o, "matrix": _plain(substitution_matrices.load(sc["matrix"])),
                    "open_gap": float(sc["open_gap_score"]), "extend_gap": float(sc["extend_gap_score"]),
                    "path_a": aln_a.path, "path_b": aln_b.path, "score_a": aln_a.score, "score_b": aln_b.score,
                    "scale": method_b.parameters["scale"], "rows": rows},
               _a3_fault, "method B's first gap moved two columns 5' (3M1D... to 1M1D2M...), a lower score"),
        "A4": (a4, {"rows": rows, "n_subject": len(s), "n_object": len(o)}, _a4_fault,
               "human 1758's row (a human-only residue) given rabbit 1758"),
        "A5": (a5, {"rows": rows, "s": s, "o": o, "n_identical": aln_a.n_identical}, _a5_fault,
               "human 614's row given rabbit 616, so rabbit 616 has two partners"),
        "A6": (a6, {"rows": rows, "s": s, "o": o, "entries": a6_entries,
                    "list_sha256": "sha256:" + sha256_hex(a6_path.read_bytes())}, _a6_fault,
               "every human residue from 4540 on mapped one rabbit residue further"),
        "A7": (a7, {"n_pairs": aln_a.n_pairs, "n_identical": aln_a.n_identical, **inputs["a7"]}, _a7_fault,
               "alignment A's n_pairs reduced by 11"),
        "A8": (a8, a8_inputs, _a8_fault, "one byte of a copy of the mapping table changed"),
        "A9": (a9, {"queries": queries, "cq02": cq02_for_mapping(graph, mapping.id)}, _a9_fault,
               "a cq02 that drops the field `methods`"),
        "A11": (a11, {"rows": rows, "segments": archive_segments(a11_text),
                      "archive_file": {"path": str(archive), "sha256": "sha256:" + sha256_hex(archive.read_bytes())}},
                _a11_fault, "the archive's last segment offset changed from -1 to -2"),
    }
    method = graph.append(method_record("channelscope.m01.check_mapping", "Run M01's pre-registered checks A3-A9 "
                                        "and A11 on the residue mapping, each with an injected fault it must catch."))
    run = graph.append(run_record(method.id, started, [
        {"path": graph.relative(inputs_path), "sha256": "sha256:" + sha256_hex(inputs_path.read_bytes())},
        {"path": graph.relative(build_path), "sha256": "sha256:" + sha256_hex(build_path.read_bytes())}]))
    used = [mapping.id, aln_a.id, aln_b.id, table.id, build["subject"], build["object"]]
    out = []
    for check, (fn, check_inputs, fault, fault_text) in plans.items():
        result = run_check(fn, check_inputs, fault, fault_text)
        commit, fails_if = CRITERIA[check]
        rec = check_result_record(
            result, check=check, mission=MISSION,
            criterion={"document": DOC, "pre_registered_in": commit, "fails_if": fails_if},
            provenance={"was_generated_by": run.id, "method": method.id, "used": used, "was_attributed_to": AGENT_LUMEN},
            synthetic=False, note=" ".join(x for x in ("Execution fixed in the session file before the run.",
                                                        NOTES.get(check)) if x))
        rec["observed"] = {**rec["observed"], "control_observed": _brief(check, result.control_observed)}
        out.append(graph.append(json.loads(json.dumps(rec, default=_jsonable))))
    return out  # type: ignore[return-value]


def _plain(matrix) -> dict[str, dict[str, float]]:
    """A substitution matrix as plain nested dicts, so a check's inputs compare by value."""
    return {a: {b: float(matrix[a][b]) for b in matrix.alphabet} for a in matrix.alphabet}


def _brief(check: str, observed: dict) -> dict:
    """What the injected fault produced, in short: enough to see that the check caught it for the right reason."""
    keep = {"A3": ("path_b_optimal", "differing_but_not_flagged"), "A4": ("indel_rows_mapped_to_a_residue",
            "object_residues_not_exactly_once"), "A5": ("round_trips_failed",), "A6": ("reproduced", "not_reproduced"),
            "A7": ("difference",), "A8": ("table_sha256_file",), "A9": ("problems",), "A11": ("differ",)}[check]
    return {k: (v[:5] if isinstance(v, list) else v) for k, v in observed.items() if k in keep}


def _jsonable(o: Any) -> Any:
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(f"not JSON: {type(o)}")
