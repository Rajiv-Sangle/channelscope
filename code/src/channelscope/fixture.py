"""The worked fixture for schema v0.1: a small, wholly invented evidence graph that uses every record type.

ADR-001 §7: each schema version ships a worked fixture that the tests validate. It is generated here, not written
by hand, and the committed copy (`what/evidence_graph/schema/v0.1/fixture/`) is checked byte-equal to this output,
so a change to the schema or the tool shows up as a diff in the fixture.

**Nothing in it is real.** Every record is flagged `synthetic`. Identifiers are chosen to look invented:
UniProtKB Z9ZZZ9ZZZ9 and Z9ZZZ9ZZZ8, HGNC:999999, transcript ENST99999999999.1, symbol FIXTURE1, the taxon NCBI
Taxonomy 32630 ("synthetic construct", checked 2026-09-29), URLs on example.org (reserved for documentation by
RFC 2606), and times on 2026-01-01. The genome positions sit on a real chromosome accession because the schema
accepts only GRCh38 loci; they are invented too.

The two proteins align with one insertion on each side and one mismatch, so CQ-02's tier-1 case (a residue in an
insertion maps to no residue) has something to bite on.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from .checks import Outcome, check_result_record, run_check
from .graph import Graph, tsv_bytes
from .ids import refget_digest, residue_identifier, sequence_md5
from .mapping import MAPPING_COLUMNS, MAPPING_HEADER, columns_from_path, mapping_rows
from .models import SCHEMA_VERSION

T0 = "2026-01-01T00:00:00.000Z"
T1 = "2026-01-01T00:00:01.000Z"
AGENT = "agent:fixture-author"
SOFTWARE = "agent:fixture-software"
FAKE_CODE = "sha256:" + hashlib.sha256(b"channelscope fixture, not real code").hexdigest()

SUBJECT_SEQ = "MKTAYIAKQRQ"  # 11 residues; Y5 is the insertion
OBJECT_SEQ = "MKTAIAKQGRE"   # 11 residues; G9 is the insertion; Q11/E11 is the mismatch
PATH = "4M1I4M1D2M"
WINDOW = 2

CURATION_TEXT = b"# fixture curation file: invented, for schema v0.1's worked fixture\nsources: [source:fixture-db]\n"
FASTA_BYTES = (b">Z9ZZZ9ZZZ9 synthetic fixture protein A\n" + SUBJECT_SEQ.encode() + b"\n"
               b">Z9ZZZ9ZZZ8 synthetic fixture protein B\n" + OBJECT_SEQ.encode() + b"\n")
SEARCH_BYTES = b'{"result_set": []}\n'


def _base(record_type: str) -> dict:
    return {"schema_version": SCHEMA_VERSION, "type": record_type, "synthetic": True}


def _method(name: str, description: str, parameters: dict | None = None) -> dict:
    return {**_base("method"), "name": name, "version": "0.1.0", "description": description,
            "implementation": {"software": "channelscope-fixture", "version": "0.1.0", "code_digest": FAKE_CODE},
            "parameters": parameters or {}, "was_attributed_to": AGENT}


def _run(method_id: str, command: list[str], used_files: list[dict] | None = None) -> dict:
    return {**_base("run"), "method": method_id, "command": command, "started_at_time": T0, "ended_at_time": T1,
            "used_files": used_files or [],
            "software": {"name": "channelscope-fixture", "version": "0.1.0", "code_digest": FAKE_CODE},
            "environment": {"python": "fixture", "platform": "fixture"},
            "was_associated_with": SOFTWARE, "acted_on_behalf_of": AGENT}


def _prov(run_id: str, method_id: str, used: list[str], source: str | None = None) -> dict:
    return {"was_generated_by": run_id, "method": method_id, "used": used, "was_attributed_to": AGENT,
            "primary_knowledge_source": source}


def build(root: Path) -> Graph:
    """Write the fixture graph under `root` (which must be empty or absent) and return it."""
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise FileExistsError(f"{root} is not empty; the fixture is written only into an empty directory")
    g = Graph(root)

    m_seed = g.append(_method("fixture.seed", "Register the fixture's sources from its curation file."))
    m_fetch = g.append(_method("fixture.fetch", "Stand-in for a logged fetch; the fixture's bytes are invented."))
    m_build = g.append(_method("fixture.build", "Parse the fixture's raw snapshots into entity records."))
    m_align = g.append(_method("fixture.align", "A hand-written global alignment, for the fixture only.",
                               {"mode": "global"}))
    m_map = g.append(_method("fixture.map", "Per-column mapping table from an alignment.", {"window": WINDOW}))
    m_check = g.append(_method("fixture.check", "A check with an injected-fault control, for the fixture."))
    m_release = g.append(_method("fixture.release", "Package the fixture's mapping as a release."))

    curation_digest = g.write_bytes("curation/fixture.yaml", CURATION_TEXT)
    seed = g.append(_run(m_seed.id, ["channelscope", "fixture", "seed"],
                         [{"path": "curation/fixture.yaml", "sha256": curation_digest,
                           "bytes": len(CURATION_TEXT)}]))
    source = g.append({**_base("source"), "provenance": _prov(seed.id, m_seed.id, [curation_digest]),
                       "identifier": "source:fixture-db", "name": "Fixture database (invented)",
                       "source_type": "database", "homepage": "https://example.org/fixture",
                       "license": "CC0-1.0"})

    fasta_digest = g.write_bytes("raw/fixture/proteins.fasta", FASTA_BYTES)
    fetched = g.append({**_base("retrieval"), "source": source.identifier, "method": m_fetch.id,
                        "request": {"http_method": "GET", "url": "https://example.org/fixture/proteins.fasta",
                                    "accept": "text/plain"},
                        "started_at_time": T0, "ended_at_time": T1,
                        "response": {"status": 200, "content_type": "text/plain", "bytes": len(FASTA_BYTES)},
                        "source_release": "fixture-1", "source_release_basis": "HTTP response header X-Fixture-Release",
                        "generated": fasta_digest, "stored_at": "raw/fixture/proteins.fasta", "storage": "committed",
                        "was_associated_with": SOFTWARE, "acted_on_behalf_of": AGENT})
    built = g.append(_run(m_build.id, ["channelscope", "fixture", "build"]))
    prov = _prov(built.id, m_build.id, [fasta_digest], source.identifier)

    g.append({**_base("gene"), "provenance": prov, "identifier": "HGNC:999999", "symbol": "FIXTURE1",
              "name": "synthetic fixture gene", "taxon": "NCBITaxon:32630"})
    g.append({**_base("gene_locus"), "provenance": prov, "identifier": "locus:GRCh38:NC_000001.11:1001-1060:+",
              "gene": "HGNC:999999", "assembly": "GRCh38", "sequence_accession": "NC_000001.11", "chromosome": "1",
              "start": 1001, "end": 1060, "strand": "+", "strand_basis": "the fixture transcript's strand field",
              "span_basis": "the span of ENST99999999999.1's exons"})
    g.append({**_base("transcript"), "provenance": prov, "identifier": "ENSEMBL:ENST99999999999.1",
              "gene": "HGNC:999999", "annotation": source.identifier, "annotation_release": "fixture-1",
              "assembly": "GRCh38", "sequence_accession": "NC_000001.11", "strand": "+", "exon_count": 3,
              "cds_genome_start": 1010, "cds_genome_end": 1050, "cds_length_nt": 36,
              "protein_product": "ENSP99999999999.1"})
    subj_num, obj_num = "numbering:Z9ZZZ9ZZZ9.sv1", "numbering:Z9ZZZ9ZZZ8.sv1"
    exons = [
        dict(exon_number=1, genome_start=1001, genome_end=1025, coding_genome_start=1010, coding_genome_end=1025,
             coding_length_nt=16, c_start=1, c_end=16, residue_numbering=subj_num, first_residue=1,
             last_residue=6, start_phase=0, end_phase=1, splits_codon_at_end=True),
        dict(exon_number=2, genome_start=1031, genome_end=1050, coding_genome_start=1031, coding_genome_end=1050,
             coding_length_nt=20, c_start=17, c_end=36, residue_numbering=subj_num, first_residue=6,
             last_residue=11, start_phase=1, end_phase=0, splits_codon_at_end=False),
        dict(exon_number=3, genome_start=1056, genome_end=1060, coding_length_nt=0,
             data_absent_reason="not-applicable"),
    ]
    for e in exons:
        g.append({**_base("exon"), "provenance": prov, "identifier": f"exon:ENST99999999999.1:{e['exon_number']}",
                  "transcript": "ENSEMBL:ENST99999999999.1", **e})
    for acc, seq, name, gene in (("Z9ZZZ9ZZZ9", SUBJECT_SEQ, "synthetic fixture protein A", "HGNC:999999"),
                                 ("Z9ZZZ9ZZZ8", OBJECT_SEQ, "synthetic fixture protein B", None)):
        g.append({**_base("protein"), "provenance": prov, "identifier": f"UniProtKB:{acc}", "name": name,
                  "gene_symbol": "FIXTURE1", "gene": gene, "taxon": "NCBITaxon:32630", "entry_version": 1,
                  "canonical_numbering": f"numbering:{acc}.sv1"})
        g.append({**_base("numbering"), "provenance": prov, "identifier": f"numbering:{acc}.sv1",
                  "accession": acc, "sequence_version": 1, "protein": f"UniProtKB:{acc}",
                  "taxon": "NCBITaxon:32630", "length": len(seq), "sequence": seq,
                  "sequence_digest": refget_digest(seq), "md5": sequence_md5(seq)})
    g.append({**_base("residue"), "provenance": prov, "identifier": residue_identifier(subj_num, 5),
              "numbering": subj_num, "position": 5, "amino_acid": SUBJECT_SEQ[4]})

    aligned = g.append(_run(m_align.id, ["channelscope", "fixture", "align"]))
    cols = columns_from_path(PATH)
    n_ident = sum(1 for c in cols if c.subject_position and c.object_position
                  and SUBJECT_SEQ[c.subject_position - 1] == OBJECT_SEQ[c.object_position - 1])
    n_pairs = sum(1 for c in cols if c.subject_position and c.object_position)
    alignment = g.append({**_base("alignment"), "provenance": _prov(aligned.id, m_align.id, [subj_num, obj_num]),
                          "mode": "global", "subject": subj_num, "object": obj_num,
                          "subject_sequence_digest": refget_digest(SUBJECT_SEQ),
                          "object_sequence_digest": refget_digest(OBJECT_SEQ), "path": PATH, "score": 30.5,
                          "n_columns": len(cols), "n_pairs": n_pairs, "n_identical": n_ident,
                          "n_subject_only": sum(1 for c in cols if c.object_position is None),
                          "n_object_only": sum(1 for c in cols if c.subject_position is None),
                          "identity": n_ident / n_pairs, "equally_optimal_alignments": 1})

    mapped = g.append(_run(m_map.id, ["channelscope", "fixture", "map"]))
    rows = mapping_rows(SUBJECT_SEQ, OBJECT_SEQ, PATH, WINDOW)
    data = tsv_bytes(MAPPING_HEADER, rows)
    table_digest = g.write_bytes("tables/fixture_mapping.tsv", data)
    map_prov = _prov(mapped.id, m_map.id, [alignment.id])
    columns = [c.model_dump(mode="json", exclude_none=True) for c in MAPPING_COLUMNS]
    for c in columns:
        if c["name"] == "subject_position":
            c["numbering"] = subj_num
        if c["name"] == "object_position":
            c["numbering"] = obj_num
    table = g.append({**_base("table"), "provenance": map_prov, "name": "fixture_mapping",
                      "path": "tables/fixture_mapping.tsv", "media_type": "text/tab-separated-values",
                      "sha256": table_digest, "bytes": len(data), "row_count": len(rows), "columns": columns,
                      "primary_key": ["column"], "about": [subj_num, obj_num]})
    mapping = g.append({**_base("residue_mapping"), "provenance": map_prov, "subject": subj_num, "object": obj_num,
                        "alignments": [alignment.id], "table": table.id, "n_pairs": n_pairs, "n_subject_only": 1,
                        "n_object_only": 1, "n_ambiguous": 0, "local_identity_window": WINDOW,
                        "reliability_rules": [f"lowered within {WINDOW} columns of an indel"],
                        "kind": "predicted", "origin": "derived", "evidence_class": "ECO:0007672"})

    search_digest = g.write_bytes("raw/fixture/search.json", SEARCH_BYTES)
    searched = g.append({**_base("retrieval"), "source": source.identifier, "method": m_fetch.id,
                         "request": {"http_method": "GET", "url": "https://example.org/fixture/search?gene=FIXTURE1",
                                     "accept": "application/json"},
                         "started_at_time": T0, "ended_at_time": T1,
                         "response": {"status": 200, "content_type": "application/json", "bytes": len(SEARCH_BYTES)},
                         "source_release_absent": "unknown", "generated": search_digest,
                         "stored_at": "raw/fixture/search.json", "storage": "committed",
                         "was_associated_with": SOFTWARE, "acted_on_behalf_of": AGENT})
    g.append({**_base("search_result"), "provenance": _prov(built.id, m_build.id, [search_digest], source.identifier),
              "route": "fixture: an entity-level search that finds nothing, recorded as a value",
              "source": source.identifier, "retrieval": searched.id, "query": {"gene": "FIXTURE1"}, "hits": [],
              "n_hits": 0})

    def insertion_maps_to_nothing(table_rows: list[list]) -> Outcome:
        row = next(r for r in table_rows if r[1] == 5)
        return Outcome(passed=row[3] is None and row[5] == "no-correspondence",
                       observed={"subject_position": 5, "object_position": row[3], "correspondence": row[5]})

    def shift_onto_neighbour(table_rows: list[list]) -> list[list]:
        for r in table_rows:
            if r[1] == 5:
                r[3], r[5] = 5, "pair"
        return table_rows

    checked = g.append(_run(m_check.id, ["channelscope", "fixture", "check"]))
    run = run_check(insertion_maps_to_nothing, rows, shift_onto_neighbour,
                    "the insertion residue is shifted onto its neighbour's partner")
    g.append(check_result_record(
        run, check="F1", mission="fixture",
        criterion={"document": "how/runtime/channelscope/src/channelscope/fixture.py", "pre_registered_in": "0000000",
                   "fails_if": "the residue in the insertion maps to a residue"},
        provenance=_prov(checked.id, m_check.id, [table.id]), synthetic=True))

    released = g.append(_run(m_release.id, ["channelscope", "fixture", "release"]))
    g.append({**_base("release"), "provenance": _prov(released.id, m_release.id, [mapping.id, table.id]),
              "version": "0.0.1", "record_schema_versions": [SCHEMA_VERSION], "has_part": [mapping.id, table.id],
              "files": [{"path": "tables/fixture_mapping.tsv", "sha256": table_digest, "bytes": len(data)}],
              "crate": "releases/0.0.1/ro-crate-metadata.json", "license": "CC0-1.0"})
    return g


def snapshot(root: Path) -> dict[str, bytes]:
    """Every file under `root`, by relative path: what the byte-equal check compares."""
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}
