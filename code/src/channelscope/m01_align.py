"""M01 objective 4: align human and rabbit RyR1 two ways, and build the residue mapping.

Reads the two numbering records that objective 2 wrote. Each sequence is checked against its own digests and against
the UniProt snapshot it was parsed from. Then it runs methods A and B (align.py) and writes:
- the two alignment methods, the build's method, and one run;
- an alignment record for each method;
- the mapping table, which follows method A's representative alignment, and its table record;
- the residue_mapping record.

It runs no pre-registered check. A3-A9 and A11 are objective 5's, each with its injected fault. A disagreement
between the methods is recorded in the table (reason `methods-differ`), never resolved here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from . import __version__
from . import models as mdl
from .align import Scoring, counts, library_versions, method_a, method_b, partners
from .curation import method_record, run_record
from .graph import Graph, tsv_bytes
from .ids import refget_digest, sequence_md5, sha256_hex
from .m01 import Snapshots, _refuse
from .mapping import MAPPING_COLUMNS, MAPPING_HEADER, columns_from_path, mapping_rows
from .models import SCHEMA_VERSION
from .provenance import AGENT_LUMEN, now

# UniProt features that lower a residue's reliability (the mission's rule), as reason codes
FEATURE_REASONS = (("Region", "Disordered", "disordered"), ("Compositional bias", None, "compositional-bias"),
                   ("Repeat", None, "repeat"))


def current_numbering(graph: Graph, identifier: str) -> mdl.Numbering:
    found = [r for r in graph.records() if isinstance(r, mdl.Numbering) and r.identifier == identifier]
    _refuse(len(found) == 1, f"{len(found)} numbering records for {identifier}; expected one")
    n = found[0]
    _refuse(len(n.sequence) == n.length and refget_digest(n.sequence) == n.sequence_digest
            and sequence_md5(n.sequence) == n.md5, f"{identifier}'s sequence disagrees with its own digests")
    return n


def feature_ranges(entry: dict) -> list[tuple[int, int, str]]:
    out = []
    for f in entry.get("features", []):
        for ftype, description, reason in FEATURE_REASONS:
            if f["type"] == ftype and (description is None or f.get("description") == description):
                start, end = f["location"]["start"]["value"], f["location"]["end"]["value"]
                _refuse(isinstance(start, int) and isinstance(end, int) and start <= end,
                        f"a {ftype} feature without exact bounds: {f['location']}")
                out.append((start, end, reason))
    return out


def splice_range(entry: dict, feature_id: str) -> tuple[int, int]:
    found = [f for f in entry.get("features", []) if f.get("featureId") == feature_id]
    _refuse(len(found) == 1 and found[0]["type"] == "Alternative sequence",
            f"{feature_id} is not one 'Alternative sequence' feature of the entry")
    loc = found[0]["location"]
    return loc["start"]["value"], loc["end"]["value"]


def method_differences(representative: str, other: str) -> frozenset[int]:
    """The columns of the representative whose subject or object residue has another partner in `other`."""
    s_other, o_other = partners(other)
    out = set()
    for c in columns_from_path(representative):
        if c.subject_position is not None and s_other[c.subject_position] != c.object_position:
            out.add(c.column)
        if c.object_position is not None and o_other[c.object_position] != c.subject_position:
            out.add(c.column)
    return frozenset(out)


def segments(path: str) -> list[dict[str, Any]]:
    """Each run of indel columns: which side has the extra residues, their positions, and the paired residues on
    either side (empty at a sequence's end)."""
    cols = columns_from_path(path)
    out, k = [], 0
    while k < len(cols):
        c = cols[k]
        if c.subject_position is not None and c.object_position is not None:
            k += 1
            continue
        side = "subject-only" if c.object_position is None else "object-only"
        m = k
        while m < len(cols) and (cols[m].object_position is None if side == "subject-only"
                                 else cols[m].subject_position is None):
            m += 1
        run = cols[k:m]
        before = cols[k - 1] if k > 0 else None
        after = cols[m] if m < len(cols) else None
        pos = [x.subject_position if side == "subject-only" else x.object_position for x in run]
        out.append({"side": side, "first": pos[0], "last": pos[-1], "length": len(pos),
                    "pair_before": [before.subject_position, before.object_position] if before else None,
                    "pair_after": [after.subject_position, after.object_position] if after else None})
        k = m
    return out


def build_mapping(graph: Graph, inputs_path: Path) -> dict[str, Any]:
    started = now()
    inputs = yaml.safe_load(inputs_path.read_text(encoding="utf-8"))
    cur_path = graph.path(inputs["curation"])
    snaps = Snapshots(graph, inputs["snapshots"])
    D = snaps.digest
    subj = current_numbering(graph, inputs["subject"])
    obj = current_numbering(graph, inputs["object"])
    human, rabbit = snaps.json("uniprot_human"), snaps.json("uniprot_rabbit")
    _refuse(human["sequence"]["value"] == subj.sequence, f"{subj.identifier} is not the human snapshot's sequence")
    _refuse(rabbit["sequence"]["value"] == obj.sequence, f"{obj.identifier} is not the rabbit snapshot's sequence")

    sc = inputs["scoring"]
    scoring = Scoring(matrix=sc["matrix"], open_gap_score=float(sc["open_gap_score"]),
                      extend_gap_score=float(sc["extend_gap_score"]))
    scale, window = int(inputs["method_b_scale"]), int(inputs["window"])
    versions = library_versions()

    A = method_a(subj.sequence, obj.sequence, scoring)
    path_b, score_b = method_b(subj.sequence, obj.sequence, scoring, scale)
    rep = A.representative

    method_a_rec = graph.append({
        "schema_version": SCHEMA_VERSION, "type": "method", "synthetic": False, "name": "channelscope.m01.align_a",
        "version": __version__,
        "description": "Method A: a global pairwise alignment by Biopython's PairwiseAligner. Every alignment of "
                       "optimal score is enumerated; the representative is the 3'-most of them.",
        "implementation": {"software": "biopython", "version": versions["biopython"],
                           "reference": f"https://pypi.org/project/biopython/{versions['biopython']}/"},
        "parameters": {**scoring.parameters(), "aligner": "Bio.Align.PairwiseAligner",
                       "optimal_alignments": "all enumerated",
                       "representative": "3'-most: the latest first gap column, then the latest second, and so on"},
        "was_attributed_to": AGENT_LUMEN})
    method_b_rec = graph.append({
        "schema_version": SCHEMA_VERSION, "type": "method", "synthetic": False, "name": "channelscope.m01.align_b",
        "version": __version__,
        "description": "Method B: a global pairwise alignment by parasail's nw_trace, a separately written C "
                       "library. It scores in integers, so BLOSUM62 and both gap scores are doubled: the same "
                       "scoring scaled by two, with its score in those units. One optimal alignment, by parasail's "
                       "own tie-breaking.",
        "implementation": {"software": "parasail", "version": f"{versions['parasail_python']} "
                                                              f"(C library {versions['parasail_c']})",
                           "reference": f"https://pypi.org/project/parasail/{versions['parasail_python']}/"},
        "parameters": {"mode": "global", "function": "parasail.nw_trace",
                       "substitution_matrix": f"BLOSUM62 x {scale}, parasail's own, checked equal to Biopython's "
                                              "on the 400 pairs of standard amino acids",
                       "open_gap": int(-scoring.open_gap_score * scale),
                       "extend_gap": int(-scoring.extend_gap_score * scale),
                       "scale": scale, "end_gaps": scoring.end_gaps},
        "was_attributed_to": AGENT_LUMEN})
    build = graph.append(method_record(
        "channelscope.m01.build_mapping",
        "Run methods A and B on two numberings, and build the per-column residue mapping from method A's "
        "representative alignment: identity in a window, the indel and ambiguity flags, and reliability by the "
        "mission's rules.",
        {"window": window, "follows": "method A's representative alignment",
         "ambiguous": "another partner in an alignment of equal score, or in method B's alignment",
         "splice_feature": inputs["splice_feature"]}))
    run = graph.append(run_record(build.id, started, [
        {"path": graph.relative(inputs_path), "sha256": "sha256:" + sha256_hex(inputs_path.read_bytes())},
        {"path": graph.relative(cur_path), "sha256": "sha256:" + sha256_hex(cur_path.read_bytes())}]))

    def prov(method_id: str, used: list[str]) -> dict:
        return {"was_generated_by": run.id, "method": method_id, "used": used, "was_attributed_to": AGENT_LUMEN}

    def rec(rtype: str, body: dict) -> mdl.Record:
        return graph.append({"schema_version": SCHEMA_VERSION, "type": rtype, "synthetic": False, **body})

    def alignment(method_id: str, path: str, score: float, n_optimal: int | None) -> mdl.Record:
        c = counts(subj.sequence, obj.sequence, path)
        body = {"provenance": prov(method_id, [subj.id, obj.id]), "mode": "global", "subject": subj.identifier,
                "object": obj.identifier, "subject_sequence_digest": subj.sequence_digest,
                "object_sequence_digest": obj.sequence_digest, "path": path, "score": score, **c,
                "identity": c["n_identical"] / c["n_pairs"]}
        if n_optimal is not None:
            body["equally_optimal_alignments"] = n_optimal
        return rec("alignment", body)

    aln_a = alignment(method_a_rec.id, rep, A.score, A.count)
    aln_b = alignment(method_b_rec.id, path_b, score_b, None)

    co_optimal = A.ambiguous_columns(rep)
    differ = method_differences(rep, path_b)
    lowered: dict[int, list[str]] = {}
    ranges = [(a, b, r, "subject") for a, b, r in feature_ranges(human)] + \
             [(a, b, r, "object") for a, b, r in feature_ranges(rabbit)]
    asi = splice_range(human, inputs["splice_feature"])
    for c in columns_from_path(rep):
        reasons = []
        for a, b, reason, side in ranges:
            pos = c.subject_position if side == "subject" else c.object_position
            if pos is not None and a <= pos <= b:
                reasons.append(reason)
        if c.subject_position is not None and asi[0] <= c.subject_position <= asi[1]:
            reasons.append("asi-splice-region")
        if c.column in co_optimal:
            reasons.append("equally-optimal")
        if c.column in differ:
            reasons.append("methods-differ")
        if reasons:
            lowered[c.column] = reasons
    rows = mapping_rows(subj.sequence, obj.sequence, rep, window, co_optimal | differ, lowered)
    data = tsv_bytes(MAPPING_HEADER, rows)
    path = f"tables/residue_mapping_{subj.identifier.split(':', 1)[1]}_{obj.identifier.split(':', 1)[1]}.tsv"
    digest = graph.write_bytes(path, data)
    numbering_of = {"subject_position": subj.identifier, "object_position": obj.identifier}
    columns = [col.model_copy(update={"numbering": numbering_of.get(col.name)}).model_dump(mode="json",
                                                                                           exclude_none=True)
               for col in MAPPING_COLUMNS]
    table = rec("table", {"provenance": prov(build.id, [aln_a.id, aln_b.id, D["uniprot_human"],
                                                        D["uniprot_rabbit"]]),
                          "name": "residue_mapping", "path": path, "media_type": "text/tab-separated-values",
                          "sha256": digest, "bytes": len(data), "row_count": len(rows), "columns": columns,
                          "primary_key": ["column"], "about": [subj.identifier, obj.identifier]})
    c_rep = counts(subj.sequence, obj.sequence, rep)
    rules = [
        f"near-indel: within {window} columns of an insertion or deletion column",
        "ambiguous: the column's residue has another partner in an alignment of equal score (equally-optimal), or "
        "in method B's alignment (methods-differ)",
        "disordered: a residue in a UniProt Region feature 'Disordered', in either entry",
        "compositional-bias: a residue in a UniProt 'Compositional bias' feature, in either entry",
        "repeat: a residue in a UniProt 'Repeat' feature, in either entry",
        f"asi-splice-region: subject residues {asi[0]}-{asi[1]}, UniProt {inputs['splice_feature']}",
    ]
    mapping = rec("residue_mapping", {
        "provenance": prov(build.id, [aln_a.id, aln_b.id, table.id, D["uniprot_human"], D["uniprot_rabbit"]]),
        "subject": subj.identifier, "object": obj.identifier, "alignments": [aln_a.id, aln_b.id], "table": table.id,
        "n_pairs": c_rep["n_pairs"], "n_subject_only": c_rep["n_subject_only"],
        "n_object_only": c_rep["n_object_only"], "n_ambiguous": len(co_optimal | differ),
        "local_identity_window": window, "reliability_rules": rules, "kind": "predicted", "origin": "derived",
        "evidence_class": "ECO:0007672"})
    return {"alignment_a": aln_a.id, "alignment_b": aln_b.id, "table": table.id, "residue_mapping": mapping.id,
            "score_a": A.score, "score_b": score_b, "scale": scale, "equally_optimal_alignments": A.count,
            "b_among_a_optimal": path_b in A.paths, "counts": c_rep,
            "identity": c_rep["n_identical"] / c_rep["n_pairs"],
            "ambiguous_subject_positions": sorted(A.ambiguous_subject),
            "ambiguous_object_positions": sorted(A.ambiguous_object),
            "ambiguous_columns": len(co_optimal), "methods_differ_columns": len(differ),
            "lowered_columns": sum(1 for r in rows if r[MAPPING_HEADER.index("reliability")] == "lowered"),
            "segments": segments(rep), "versions": versions}
