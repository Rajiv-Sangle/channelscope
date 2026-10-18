"""M01 objective 2's pre-registered checks, G1-G6, A1 and A2, each run with an injected fault it must catch.

The criteria are the mission's, quoted with the commit that first contained them. Where the mission's words leave a
choice, the execution was fixed in the session file before the check ran. Results are recorded as `check_result`
records, as they came out.
"""

from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path
from typing import Any

import yaml

from . import models as mdl
from .checks import Outcome, check_result_record, run_check
from .clinvar import C_SUB, P_DESC, THREE_TO_ONE, ClinVarVariant, parse_summaries
from .curation import method_record, run_record
from .genome import (STANDARD_CODE, AssemblyRefused, Exon, GenomeWindow, MapRow, TranscriptModel, codon_map, locate,
                     split_codons_from_exon_model, translate)
from .graph import Graph
from .ids import sequence_md5, sha256_hex
from .provenance import AGENT_LUMEN, now
from .query import current
from .residues import IsoformRefused, deletion_between, to_canonical

MISSION = "mission_channelscope_m01_human_rabbit_mapping"
DOC = "how/missions/mission_channelscope_m01_human_rabbit_mapping.md"
CRITERIA = {
    "G1": ("79ff30b", "Any residue differs, or the stop is missing or early"),
    "G2": ("79ff30b", "Any coding boundary differs. The difference is investigated before going on"),
    "G3": ("79ff30b", "A residue has other than three bases; a base is used twice; the split-codon counts disagree; "
                      "or the strand is hard-coded"),
    "G4": ("79ff30b", "Any disagreement"),
    "G5": ("79ff30b", "Any position is used without its assembly"),
    "G6": ("a5b6583", "Any exon's residue range differs, or any anchor lands in a different exon. The difference is "
                      "investigated; either side may be wrong. A difference traced to a different transcript or "
                      "assembly on the archive's side is recorded and dismissed, not tuned away"),
    "A1": ("8e84a8b", "They differ. The mission then records both numberings, and a mapping between them, before "
                      "going on"),
    "A2": ("8e84a8b", "Any such query silently uses P21817-1 numbers"),
}
A1_DESIGN_MD5 = "0566ca43dd75ad82b878f07bc52bf46a"  # the mission's A1, retrieved 2026-09-28
G3_DESIGN_SPLIT = 50                                  # the mission's G3, "50 at design"
G6_ANCHORS = {"R614C": (614, 17), "R530H": (530, 15), "Ser2843": (2843, 54), "I4898T": (4898, 102),
              "A2437V": (2437, 45)}                   # the mission's G6
A2_POSITIONS = {"numbering:P21817-2.sv3": 3500, "numbering:P21817-3.sv3": 3900}


# --- loading ---------------------------------------------------------------------------------------------------------

class Ctx:
    def __init__(self, graph: Graph, inputs_path: Path):
        self.graph = graph
        self.inputs = yaml.safe_load(inputs_path.read_text(encoding="utf-8"))
        if "build_inputs" in self.inputs:  # a check-inputs file names the build's input list, plus its own
            build = yaml.safe_load(graph.path(self.inputs["build_inputs"]).read_text(encoding="utf-8"))
            self.inputs = {**build, **self.inputs}
        self.cur = yaml.safe_load(graph.path(self.inputs["curation"]).read_text(encoding="utf-8"))
        recs = current(graph.records())
        self.by_ident = {getattr(r, "identifier", None): r for r in recs if getattr(r, "identifier", None)}
        self.table = next(r for r in recs if isinstance(r, mdl.Table) and r.name == "codon_map")
        self.rows = list(csv.DictReader(io.StringIO(graph.path(self.table.path).read_text("utf-8")), delimiter="\t"))
        self.exons = {t: sorted((r for r in recs if isinstance(r, mdl.Exon) and r.transcript == t),
                                key=lambda e: e.exon_number) for t in ("refseq:NM_000540.3", "ENSEMBL:ENST00000359596.8")}
        tx = self.by_ident["refseq:NM_000540.3"]
        self.model = TranscriptModel("NM_000540.3", tx.strand, tuple(Exon(e.exon_number, e.genome_start, e.genome_end)
                                     for e in self.exons["refseq:NM_000540.3"]), tx.cds_genome_start, tx.cds_genome_end)
        self.map_rows = [MapRow(int(r["genome_position"]), int(r["exon_number"]), int(r["transcript_position"]),
                                r["c_hgvs"], _int(r["c_position"]), r["region"], _int(r["codon_number"]),
                                _int(r["codon_position"]), _int(r["residue_number"]), r["genome_base"],
                                r["transcript_base"], r["codon"] or None, r["amino_acid"] or None,
                                {"true": True, "false": False}.get(r["split_codon"]), r["data_absent_reason"] or None)
                         for r in self.rows]
        self.seq = {k: v.sequence for k, v in self.by_ident.items() if isinstance(v, mdl.Numbering)}

    def snapshot(self, name: str) -> bytes:
        return self.graph.path(self.inputs["snapshots"][name]).read_bytes()


def _int(s: str) -> int | None:
    return int(s) if s not in ("", None) else None


# --- G1 ---------------------------------------------------------------------------------------------------------------

def g1(inp: dict) -> Outcome:
    cds = "".join(r["transcript_base"] for r in inp["rows"] if r["region"] == "cds")
    protein = translate(cds)
    body, stop = protein[:-1], protein[-1:]
    internal = [i + 1 for i, a in enumerate(body) if a == "*"]
    firsts = {k: next((i + 1 for i, (a, b) in enumerate(zip(body, s)) if a != b), None) for k, s in inp["refs"].items()}
    identical = {k: body == s for k, s in inp["refs"].items()}
    return Outcome(passed=stop == "*" and not internal and all(identical.values()),
                   observed={"cds_bases": len(cds), "codons": len(cds) // 3, "residues_before_stop": len(body),
                             "stop_codon": cds[-3:], "internal_stops": internal[:10], "identical_to": identical,
                             "first_difference": firsts})


def _g1_fault(inp: dict) -> dict:
    for r in inp["rows"]:
        if r["c_position"] == "1840":  # c.1840C>T, p.Arg614Cys
            r["transcript_base"] = "T" if r["transcript_base"] != "T" else "C"
    return inp


# --- G2 ---------------------------------------------------------------------------------------------------------------

def g2(inp: dict) -> Outcome:
    ref, ens = inp["refseq"], inp["ensembl"]
    diffs = [(a, b) for a, b in zip(ref, ens) if a != b]
    return Outcome(passed=len(ref) == len(ens) and not diffs,
                   observed={"coding_exons_refseq": len(ref), "coding_exons_ensembl": len(ens),
                             "differences": [list(map(list, d)) for d in diffs[:10]],
                             "all_exon_bounds_identical_utr_included": inp["all_bounds_equal"]})


def _g2_fault(inp: dict) -> dict:
    n, s, e = inp["ensembl"][40]
    inp["ensembl"][40] = (n, s + 1, e)
    return inp


# --- G3 ---------------------------------------------------------------------------------------------------------------

def g3(inp: dict) -> Outcome:
    rows = inp["rows"]
    coding = [r for r in rows if r.region == "cds"]
    per_codon: dict[int, list[int]] = {}
    for r in coding:
        per_codon.setdefault(r.codon_number, []).append(r.codon_position)
    bad_codons = [c for c, ps in per_codon.items() if sorted(ps) != [1, 2, 3]]
    positions = [r.genome_position for r in rows]
    reused = len(positions) - len(set(positions))
    split_map = len({r.codon_number for r in coding if r.split_codon})
    split_model = split_codons_from_exon_model(inp["model"])
    expected_bases = 3 * (inp["residues"] + 1)
    flipped = TranscriptModel(inp["model"].accession, "-" if inp["model"].strand == "+" else "+",
                              tuple(Exon(i, e.start, e.end) for i, e in enumerate(reversed(inp["model"].exons), 1)),
                              inp["model"].cds_start, inp["model"].cds_end)
    try:
        flipped_protein = translate("".join(r.transcript_base for r in codon_map(flipped, inp["window"])
                                            if r.region == "cds"))
    except ValueError as e:
        flipped_protein = f"refused: {e}"
    strand_load_bearing = not flipped_protein.startswith(inp["canonical"][:20])
    strand_read = inp["strand_record"] == inp["strand_annotation"]
    passed = (len(coding) == expected_bases and len(per_codon) == inp["residues"] + 1 and not bad_codons
              and reused == 0 and split_map == split_model and strand_read and strand_load_bearing)
    return Outcome(passed=passed, observed={
        "coding_bases": len(coding), "expected_coding_bases": expected_bases, "codons": len(per_codon),
        "codons_without_three_bases": bad_codons[:10], "bases_used_twice": reused,
        "split_codons_in_map": split_map, "split_codons_from_exon_model": split_model,
        "split_codons_at_design": G3_DESIGN_SPLIT, "strand_in_record": inp["strand_record"],
        "strand_in_annotation": inp["strand_annotation"], "flipped_strand_changes_the_protein": strand_load_bearing})


def _g3_fault(inp: dict) -> dict:
    i = next(k for k, r in enumerate(inp["rows"]) if r.c_position == 3000)
    del inp["rows"][i]  # codon 1000 left with two bases
    return inp


# --- G4 ---------------------------------------------------------------------------------------------------------------

def g4_sample(variants: list[ClinVarVariant], model: TranscriptModel, rows: list[MapRow]) -> tuple[list, dict]:
    ok, excluded = [], {}
    for v in variants:
        reason = (v.problems[0] if v.problems else
                  "not on NM_000540.3" if v.transcript != "NM_000540.3" else
                  "no GRCh38 location on chromosome 19" if v.grch38_chr != "19" or v.grch38_start is None else None)
        if reason:
            excluded.setdefault(reason, []).append(v.accession)
        else:
            ok.append(v)
    anchor = [v for v in ok if v.accession.startswith("VCV000012964")]
    pool = sorted((v for v in ok if v not in anchor), key=lambda v: (v.grch38_start, int(v.uid)))
    lo, hi = pool[0].grch38_start, pool[-1].grch38_start
    chosen: list[ClinVarVariant] = []
    for k in range(20):
        t = lo + k * (hi - lo) / 19
        best = min((v for v in pool if v not in chosen), key=lambda v: (abs(v.grch38_start - t), v.grch38_start,
                                                                           int(v.uid)))
        chosen.append(best)
    sample = anchor + chosen
    split_codons = {r.codon_number for r in rows if r.split_codon}
    by_c = {r.c_position: r for r in rows if r.c_position}

    def in_split(v: ClinVarVariant) -> bool:
        m = C_SUB.match(v.c or "")
        return bool(m and m.group("pos").isdigit() and by_c.get(int(m.group("pos")))
                    and by_c[int(m.group("pos"))].codon_number in split_codons)

    added = []
    if not any(v.is_intronic for v in sample):
        first = next((v for v in pool if v.is_intronic), None)
        if first:
            sample.append(first)
            added.append(("first intronic", first.accession))
    if not any(in_split(v) for v in sample):
        first = next((v for v in pool if in_split(v)), None)
        if first:
            sample.append(first)
            added.append(("first in a split codon", first.accession))
    return sample, {"candidates": len(ok), "excluded": {k: len(v) for k, v in excluded.items()},
                    "excluded_examples": {k: v[:3] for k, v in excluded.items()}, "added_by_rule": added,
                    "anchor_found": bool(anchor)}


def g4_compare(v: ClinVarVariant, model: TranscriptModel, rows: list[MapRow], window: GenomeWindow) -> list[str]:
    problems = []
    positions = v.c_positions
    ends = [v.grch38_start] if len(positions) == 1 else [v.grch38_start, v.grch38_stop]
    for pos, want in zip(ends, positions):
        got = locate(model, rows, pos, "GRCh38")["c_hgvs"]
        if got != f"c.{want}":
            problems.append(f"GRCh38 {pos} is {got} in the map; ClinVar says c.{want}")
    sub = C_SUB.match(v.c or "")
    by_c = {r.c_position: r for r in rows if r.c_position}
    if sub:
        genome_base = window.base(v.grch38_start)
        spdi = (v.spdi or "").split(":")
        if len(spdi) != 4 or spdi[2] != genome_base or spdi[2] != sub.group("ref") or spdi[3] != sub.group("alt"):
            problems.append(f"bases: SPDI {v.spdi}, GRCh38 {genome_base}, c. {sub.group('ref')}>{sub.group('alt')}")
    hit = locate(model, rows, v.grch38_start, "GRCh38")
    if hit["residue_number"] is None:
        if v.p not in (None, "p.?"):
            problems.append(f"the map gives no residue, but ClinVar gives {v.p}")
        return problems
    pm = P_DESC.match(v.p or "")
    if not pm:
        problems.append(f"the map gives residue {hit['residue_number']}, but ClinVar gives no parsable p. ({v.p})")
        return problems
    if int(pm.group("pos")) != hit["residue_number"]:
        problems.append(f"residue {hit['residue_number']} in the map; ClinVar {v.p}")
    row = hit["row"]
    if THREE_TO_ONE.get(pm.group("ref")) != row.amino_acid:
        problems.append(f"reference amino acid {row.amino_acid} in the map; ClinVar {v.p}")
    if sub and sub.group("pos").isdigit():
        c = int(sub.group("pos"))
        codon = list(by_c[c].codon or "")
        codon[by_c[c].codon_position - 1] = sub.group("alt")
        alt = STANDARD_CODE["".join(codon)]
        rest = pm.group("rest")
        want = "=" if alt == row.amino_acid else ("Ter" if alt == "*" else
                                                  next(k for k, a in THREE_TO_ONE.items() if a == alt))
        if rest != want:
            problems.append(f"the alternate codon translates to {want}; ClinVar {v.p}")
    return problems


def g4(inp: dict) -> Outcome:
    results = []
    for v in inp["sample"]:
        probs = g4_compare(v, inp["model"], inp["rows"], inp["window"])
        results.append({"vcv": v.accession, "grch38": [v.grch38_start, v.grch38_stop], "c": v.c, "p": v.p,
                        "agrees": not probs, "problems": probs})
    return Outcome(passed=bool(results) and all(r["agrees"] for r in results),
                   observed={"sample_size": len(results), "disagreements": sum(not r["agrees"] for r in results),
                             "variants": results, **inp["selection"]})


def _g4_fault(inp: dict) -> dict:
    m = inp["model"]
    inp["model"] = TranscriptModel(m.accession, m.strand, m.exons, m.cds_start + 1, m.cds_end + 1)
    inp["rows"] = codon_map(inp["model"], inp["window"])  # every c. label now one base off
    return inp


# --- G5 ---------------------------------------------------------------------------------------------------------------

def g5(inp: dict) -> Outcome:
    refused = {}
    for assembly in (None, "GRCh37", "hg19"):
        try:
            inp["locate"](assembly)
            refused[str(assembly)] = False
        except AssemblyRefused:
            refused[str(assembly)] = True
    answered = inp["locate"]("GRCh38") is not None
    grch37_in_records = inp["records_text"].count("GRCh37")
    return Outcome(passed=all(refused.values()) and answered and grch37_in_records == 0,
                   observed={"refused": refused, "grch38_answered": answered,
                             "records_mentioning_grch37": grch37_in_records})


def _g5_fault(inp: dict) -> dict:
    real = inp["locate"]
    inp["locate"] = lambda assembly: real("GRCh38")  # a permissive locate that ignores the assembly
    return inp


# --- G6 ---------------------------------------------------------------------------------------------------------------

def g6(inp: dict) -> Outcome:
    ours, arch = inp["ours"], inp["archive"]
    diffs = [{"exon": n, "ours": list(ours.get(n, ())), "archive": list(arch.get(n, ()))}
             for n in sorted(set(ours) | set(arch)) if ours.get(n) != arch.get(n)]
    anchors = {}
    for name, (residue, exon) in G6_ANCHORS.items():
        exons = sorted({r.exon_number for r in inp["rows"] if r.residue_number == residue})
        anchors[name] = {"residue": residue, "stated_exon": exon, "exons_holding_the_codon": exons,
                         "lands": exon in exons}
    return Outcome(passed=not diffs and all(a["lands"] for a in anchors.values()),
                   observed={"exons_compared": len(set(ours) | set(arch)), "differences": diffs[:10],
                             "anchors": anchors, "archive_file": inp["archive_file"]})


def _g6_fault(inp: dict) -> dict:
    a, b = inp["ours"][17]
    inp["ours"][17] = (a + 1, b)
    return inp


# --- A1 and A2 --------------------------------------------------------------------------------------------------------

def a1(inp: dict) -> Outcome:
    s1, s2 = inp["P21817-1"], inp["NP_000531.2"]
    first = next((i + 1 for i, (a, b) in enumerate(zip(s1, s2)) if a != b), None)
    md5 = sequence_md5(s1)
    return Outcome(passed=s1 == s2 and md5 == A1_DESIGN_MD5,
                   observed={"lengths": [len(s1), len(s2)], "identical": s1 == s2, "first_difference": first,
                             "md5": md5, "md5_at_design": A1_DESIGN_MD5})


def _a1_fault(inp: dict) -> dict:
    s = inp["NP_000531.2"]
    inp["NP_000531.2"] = s[:613] + ("C" if s[613] != "C" else "R") + s[614:]
    return inp


def a2(inp: dict) -> Outcome:
    out, ok = {}, True
    canon = inp["canonical"]
    for iso, pos in A2_POSITIONS.items():
        seq = inp["isoforms"][iso]
        try:
            inp["resolve"](iso, pos, seq, explicit=False)
            refused = False
        except IsoformRefused:
            refused = True
        _, cpos, how = inp["resolve"](iso, pos, seq, explicit=True)
        window_ok = seq[pos - 6:pos + 5] == canon[cpos - 6:cpos + 5]
        d = deletion_between(canon, seq)
        vsp_ok = [d.start, d.end] == inp["vsp"][iso]
        ok &= refused and window_ok and vsp_ok and cpos != pos
        out[iso] = {"position": pos, "refused_without_explicit": refused, "canonical_position": cpos,
                    "translation": how, "window_of_11_agrees": window_ok, "deletion_from_sequences": [d.start, d.end],
                    "deletion_in_uniprot_vsp": inp["vsp"][iso], "vsp_agrees": vsp_ok}
    return Outcome(passed=ok, observed=out)


def _a2_fault(inp: dict) -> dict:
    inp["resolve"] = lambda iso, pos, seq, explicit=False: ("numbering:P21817-1.sv3", pos, "silently the same number")
    return inp


# --- running them ------------------------------------------------------------------------------------------------------

def run_genome_checks(graph: Graph, inputs_path: Path) -> list[mdl.CheckResult]:
    started = now()
    ctx = Ctx(graph, inputs_path)
    tx = ctx.by_ident["refseq:NM_000540.3"]
    window_bytes = ctx.snapshot("ncbi_locus").decode("ascii").splitlines()
    lo = int(window_bytes[0].split()[0].split(":")[1].split("-")[0])
    window = GenomeWindow("NC_000019.10", lo, "".join(window_bytes[1:]).upper())
    uni_iso = {f"numbering:P21817-{n}.sv3": json.loads(ctx.snapshot(f"uniprot_isoform_{n}")) for n in (2, 3)}
    human = json.loads(ctx.snapshot("uniprot_human"))
    vsp = {}
    for f in human.get("features", []):
        if f["type"] == "Alternative sequence":
            n = re.search(r"isoform (\d+)", f.get("description", "")).group(1)  # type: ignore[union-attr]
            vsp[f"numbering:P21817-{n}.sv3"] = [f["location"]["start"]["value"], f["location"]["end"]["value"]]
    report = json.loads(ctx.snapshot("ncbi_products"))
    [t] = [t for p in report["reports"] for t in p["product"]["transcripts"] if t["accession_version"] == "NM_000540.3"]
    orient = t["genomic_locations"][0]["genomic_range"]["orientation"]
    clinvar_paths = sorted(p for p in (graph.root / "raw" / "clinvar" / "2026-09-29").glob("esummary_*.json"))
    variants = [v for p in clinvar_paths for v in parse_summaries(p.read_bytes())]
    sample, selection = g4_sample(variants, ctx.model, ctx.map_rows)
    archive = Path(ctx.inputs["g6_archive_exon_map"])
    arch_rows = [r for r in csv.DictReader(line for line in archive.read_text("utf-8").splitlines()
                                           if not line.startswith("#"))]
    coding = lambda exs: [(e.exon_number, e.coding_genome_start, e.coding_genome_end) for e in exs  # noqa: E731
                          if e.coding_length_nt]
    ref_ex, ens_ex = ctx.exons["refseq:NM_000540.3"], ctx.exons["ENSEMBL:ENST00000359596.8"]
    # Check results are left out: they name assemblies by design, and must not count against the rule they record.
    records_text = "".join(p.read_text("utf-8") for p in sorted(graph.records_dir.glob("*.jsonl"))
                           if p.name != "check_result.jsonl")

    def resolve(iso, pos, seq, explicit=False):
        return to_canonical(iso, "numbering:P21817-1.sv3", pos, ctx.seq["numbering:P21817-1.sv3"], seq,
                            explicit=explicit)

    plans = {
        "G1": (g1, {"rows": ctx.rows, "refs": {"P21817-1.sv3": ctx.seq["numbering:P21817-1.sv3"],
                                                "NP_000531.2": ctx.seq["numbering:NP_000531.2"]}},
               _g1_fault, "c.1840 changed from C to T in the assembled coding sequence (p.Arg614Cys)"),
        "G2": (g2, {"refseq": coding(ref_ex), "ensembl": coding(ens_ex),
                    "all_bounds_equal": [(e.genome_start, e.genome_end) for e in ref_ex]
                    == [(e.genome_start, e.genome_end) for e in ens_ex]},
               _g2_fault, "one Ensembl coding boundary moved by one base"),
        "G3": (g3, {"rows": ctx.map_rows, "model": ctx.model, "window": window, "residues": len(ctx.seq[
                    "numbering:P21817-1.sv3"]), "canonical": ctx.seq["numbering:P21817-1.sv3"],
                    "strand_record": tx.strand, "strand_annotation": {"plus": "+", "minus": "-"}.get(orient)},
               _g3_fault, "one coding base (c.3000) removed from the map"),
        "G4": (g4, {"sample": sample, "selection": selection, "model": ctx.model, "rows": ctx.map_rows,
                    "window": window}, _g4_fault, "the coding start moved by one base, so every c. label is off by one"),
        "G5": (g5, {"locate": lambda assembly: locate(ctx.model, ctx.map_rows, 38457545, assembly),
                    "records_text": records_text}, _g5_fault, "a locate that ignores the assembly it is given"),
        "G6": (g6, {"ours": {e.exon_number: (e.first_residue, e.last_residue) for e in ref_ex if e.coding_length_nt},
                    "archive": {int(r["exon_number"]): (int(r["residue_start"]), int(r["residue_end"]))
                                for r in arch_rows},
                    "rows": ctx.map_rows, "archive_file": {"path": str(archive),
                                                           "sha256": sha256_hex(archive.read_bytes())}},
               _g6_fault, "exon 17's first residue moved by one"),
        "A1": (a1, {"P21817-1": ctx.seq["numbering:P21817-1.sv3"], "NP_000531.2": ctx.seq["numbering:NP_000531.2"]},
               _a1_fault, "residue 614 of NP_000531.2 changed"),
        "A2": (a2, {"canonical": ctx.seq["numbering:P21817-1.sv3"],
                    "isoforms": {k: ctx.seq[k] for k in A2_POSITIONS}, "vsp": vsp, "resolve": resolve},
               _a2_fault, "a resolver that silently keeps the isoform's residue number"),
    }
    method = graph.append(method_record("channelscope.m01.check_genome", "Run M01's pre-registered checks G1-G6, "
                                        "A1 and A2, each with an injected fault it must catch."))
    run = graph.append(run_record(method.id, started, [{"path": graph.relative(inputs_path),
                                                        "sha256": "sha256:" + sha256_hex(inputs_path.read_bytes())}]))
    used = [ctx.table.id, "refseq:NM_000540.3", "ENSEMBL:ENST00000359596.8", "numbering:P21817-1.sv3",
            "numbering:NP_000531.2"]
    raw_used = {"G4": [r.generated for r in graph.records() if isinstance(r, mdl.Retrieval)
                       and "/clinvar/" in r.stored_at],
                "A2": [r.generated for r in graph.records() if isinstance(r, mdl.Retrieval)
                       and r.stored_at.split("/")[-1] in ("P21817.json", "P21817-2.json", "P21817-3.json")]}
    out = []
    for check, (fn, inputs, fault, fault_text) in plans.items():
        result = run_check(fn, inputs, fault, fault_text)
        commit, fails_if = CRITERIA[check]
        rec = check_result_record(
            result, check=check, mission=MISSION, criterion={"document": DOC, "pre_registered_in": commit,
                                                             "fails_if": fails_if},
            provenance={"was_generated_by": run.id, "method": method.id, "used": used + raw_used.get(check, []),
                        "was_attributed_to": AGENT_LUMEN}, synthetic=False,
            note="Execution fixed in the session file before the run." if check in ("G4", "G6", "A2") else None)
        out.append(graph.append(json.loads(json.dumps(rec, default=_jsonable))))
    return out  # type: ignore[return-value]


def _jsonable(o: Any) -> Any:
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(f"not JSON: {type(o)}")
