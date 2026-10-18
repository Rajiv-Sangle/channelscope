"""M01 objective 2: build the genome leg's records and the codon map from the logged snapshots.

Reads the snapshots named in `curation/build_m01_genome.yaml`, checks each against its retrieval's digest, parses
them, and refuses any response that disagrees with the curation file. It writes records; it runs no pre-registered
check (those are in m01_checks.py, each with its injected fault).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from . import models as mdl
from .curation import method_record, run_record
from .genome import Exon, GenomeWindow, MapRow, TranscriptModel, codon_map, split_codons_from_exon_model, \
    split_codons_in_map
from .graph import Graph, tsv_bytes
from .ids import refget_digest, sequence_md5
from .models import SCHEMA_VERSION, Column
from .provenance import AGENT_LUMEN, now


class BuildRefused(RuntimeError):
    pass


def _refuse(ok: bool, message: str) -> None:
    if not ok:
        raise BuildRefused(message)


@dataclass
class Snapshots:
    graph: Graph
    paths: dict[str, str]
    digest: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        retrievals = {r.stored_at: r for r in self.graph.records() if isinstance(r, mdl.Retrieval)}
        for name, rel in self.paths.items():
            _refuse(rel in retrievals, f"{rel} is not the snapshot of any retrieval record")
            _refuse(self.graph.file_digest(rel) == retrievals[rel].generated, f"{rel} does not match its retrieval")
            self.digest[name] = retrievals[rel].generated

    def bytes(self, name: str) -> bytes:
        return self.graph.path(self.paths[name]).read_bytes()

    def json(self, name: str) -> Any:
        return json.loads(self.bytes(name))


def parse_fasta(data: bytes) -> list[tuple[str, str]]:
    out, header, seq = [], None, []
    for line in data.decode("ascii").splitlines():
        if line.startswith(">"):
            if header is not None:
                out.append((header, "".join(seq)))
            header, seq = line[1:], []
        elif line.strip():
            seq.append(line.strip())
    if header is not None:
        out.append((header, "".join(seq)))
    return out


def ensembl_model(d: dict, cur: dict) -> tuple[TranscriptModel, dict]:
    acc = f"{d['id']}.{d['version']}"
    _refuse(acc == cur["mane_select"]["ensembl_transcript"], f"Ensembl returned {acc}")
    _refuse(d["assembly_name"] == "GRCh38" and d["seq_region_name"] == cur["assembly"]["chromosome"],
            "Ensembl's transcript is not on GRCh38 chromosome 19")
    _refuse(d["strand"] in (1, -1), f"Ensembl strand {d['strand']!r}")
    strand = "+" if d["strand"] == 1 else "-"
    exons = sorted(d["Exon"], key=lambda e: e["start"], reverse=strand == "-")
    model_exons = tuple(Exon(i, e["start"], e["end"]) for i, e in enumerate(exons, start=1))
    tl = d["Translation"]
    coding = sum(max(0, min(e.end, tl["end"]) - max(e.start, tl["start"]) + 1) for e in model_exons)
    # Whether Ensembl's translation span includes the stop codon is read from the data, not assumed.
    if coding == 3 * tl["length"] + 3:
        convention, cds_start, cds_end = "includes the stop codon", tl["start"], tl["end"]
    elif coding == 3 * tl["length"]:
        convention = "excludes the stop codon; extended by three bases here"
        model_tmp = TranscriptModel(acc, strand, model_exons, tl["start"], tl["end"])
        walk = [p for e in model_tmp.exons for p in (range(e.start, e.end + 1) if strand == "+"
                                                     else range(e.end, e.start - 1, -1))]
        last = tl["end"] if strand == "+" else tl["start"]
        stop_end = walk[walk.index(last) + 3]
        cds_start, cds_end = (tl["start"], stop_end) if strand == "+" else (stop_end, tl["end"])
    else:
        raise BuildRefused(f"Ensembl's translation spans {coding} coding bases for {tl['length']} residues")
    meta = {"protein_product": f"{tl['id']}.{tl['version']}", "stop_convention": convention}
    return TranscriptModel(acc, strand, model_exons, cds_start, cds_end), meta


def refseq_model(report: dict, cur: dict) -> tuple[TranscriptModel, dict]:
    acc = cur["mane_select"]["refseq_transcript"]
    [t] = [t for p in report["reports"] for t in p["product"]["transcripts"] if t["accession_version"] == acc]
    _refuse(t.get("select_category") == "MANE_SELECT", f"{acc} is not MANE Select in NCBI's report")
    _refuse(t.get("ensembl_transcript") == cur["mane_select"]["ensembl_transcript"], "NCBI pairs another ENST")
    _refuse(t["protein"]["accession_version"] == cur["mane_select"]["refseq_protein"], "NCBI names another protein")
    [loc] = [g for g in t["genomic_locations"]
             if g["genomic_accession_version"] == cur["assembly"]["sequence_accession"]]
    orient = loc["genomic_range"]["orientation"]
    _refuse(orient in ("plus", "minus"), f"orientation {orient!r}")
    strand = "+" if orient == "plus" else "-"
    exons = tuple(Exon(int(e["order"]), int(e["begin"]), int(e["end"])) for e in
                  sorted(loc["exons"], key=lambda e: int(e["order"])))
    [cds] = t["cds"]["range"]
    walk = [p for e in exons for p in (range(e.start, e.end + 1) if strand == "+" else range(e.end, e.start - 1, -1))]
    first, last = walk[int(cds["begin"]) - 1], walk[int(cds["end"]) - 1]
    meta = {"protein_product": t["protein"]["accession_version"], "protein_length": t["protein"].get("length"),
            "cds_transcript_range": [int(cds["begin"]), int(cds["end"])], "transcript_length": t.get("length")}
    return TranscriptModel(acc, strand, exons, min(first, last), max(first, last)), meta


MAP_COLUMNS = [
    ("genome_position", "integer", True, "GRCh38 position on the chromosome sequence named in the table record"),
    ("exon_number", "integer", True, "The exon of NM_000540.3 holding this base"),
    ("transcript_position", "integer", True, "Position along the transcript's exons, 1-based"),
    ("c_hgvs", "string", True, "HGVS c. position on NM_000540.3: c.-N, c.N or c.*N"),
    ("c_position", "integer", False, "The coding position, for a coding base"),
    ("region", "string", True, "`5utr`, `cds` or `3utr`"),
    ("codon_number", "integer", False, "The codon this base belongs to, counted from the start codon"),
    ("codon_position", "integer", False, "1, 2 or 3 within the codon"),
    ("residue_number", "integer", False, "The residue in numbering P21817-1.sv3 (G1 tests that this holds); empty "
                                         "for untranslated bases and the stop codon"),
    ("genome_base", "string", True, "The GRCh38 base, plus strand"),
    ("transcript_base", "string", True, "The base on the transcript's strand"),
    ("codon", "string", False, "The codon's three bases, read from the assembled coding sequence"),
    ("amino_acid", "string", False, "The codon's translation, standard code; `*` for the stop codon"),
    ("split_codon", "boolean", False, "True where the codon's bases lie in two exons"),
    ("data_absent_reason", "string", False, "`not-applicable` where there is no residue (FHIR DataAbsentReason)"),
]


def build_genome(graph: Graph, inputs_path: Path) -> dict[str, Any]:
    started = now()
    inputs = yaml.safe_load(inputs_path.read_text(encoding="utf-8"))
    cur_path = graph.path(inputs["curation"])
    cur = yaml.safe_load(cur_path.read_text(encoding="utf-8"))
    snaps = Snapshots(graph, inputs["snapshots"])
    D = snaps.digest

    ens, ens_meta = ensembl_model(snaps.json("ensembl_transcript"), cur)
    ref, ref_meta = refseq_model(snaps.json("ncbi_products"), cur)
    hgnc = snaps.json("hgnc")["response"]["docs"][0]
    _refuse(hgnc["hgnc_id"] == cur["gene"]["identifier"] and hgnc["symbol"] == cur["gene"]["symbol"], "HGNC differs")
    _refuse(set(hgnc["mane_select"]) == {cur["mane_select"]["ensembl_transcript"],
                                         cur["mane_select"]["refseq_transcript"]}, "HGNC's MANE pair differs")

    [(ncbi_header, ncbi_seq)] = parse_fasta(snaps.bytes("ncbi_locus"))
    region = ncbi_header.split()[0]
    _refuse(region.startswith(cur["assembly"]["sequence_accession"] + ":"), f"NCBI returned {region}")
    lo, hi = (int(x) for x in region.split(":")[1].split("-"))
    ucsc = snaps.json("ucsc_locus")
    _refuse(ucsc["genome"] == "hg38" and ucsc["chrom"] == "chr" + cur["assembly"]["chromosome"]
            and ucsc["start"] == lo - 1 and ucsc["end"] == hi, "UCSC's window is not NCBI's")
    _refuse(ucsc["dna"].upper() == ncbi_seq.upper(), "NCBI's and UCSC's copies of the locus differ")
    window = GenomeWindow(cur["assembly"]["sequence_accession"], lo, ncbi_seq.upper())
    rows = codon_map(ref, window)

    uni = snaps.json("uniprot_human")
    rab = snaps.json("uniprot_rabbit")
    fasta = dict(parse_fasta(snaps.bytes("uniprot_isoforms_fasta")))
    iso_audit = {n: snaps.json(f"uniprot_isoform_{n}")["entryAudit"] for n in (2, 3)}
    [(np_header, np_seq)] = parse_fasta(snaps.bytes("refseq_protein"))
    _refuse(np_header.split()[0] == cur["mane_select"]["refseq_protein"], f"NCBI returned {np_header.split()[0]}")
    human_acc, rabbit_acc = cur["proteins"]["human"]["uniprot"], cur["proteins"]["rabbit"]["uniprot"]
    _refuse(uni["primaryAccession"] == human_acc and rab["primaryAccession"] == rabbit_acc, "UniProt accessions")
    _refuse(fasta[next(h for h in fasta if h.startswith(f"sp|{human_acc}|"))] == uni["sequence"]["value"],
            "the canonical FASTA and the JSON entry differ")
    _refuse(not [c for c in rab.get("comments", []) if c["commentType"] == "ALTERNATIVE PRODUCTS"],
            f"{rabbit_acc} defines isoforms; number them by isoform")

    method = graph.append(method_record(
        "channelscope.m01.build_genome", "Parse the genome leg's snapshots into records and build the codon map of "
        "the MANE Select transcript from RefSeq's exon model and NCBI's copy of the locus.",
        {"codon_map_transcript": ref.accession, "genome_copy": "ncbi", "second_genome_copy": "ucsc"}))
    run = graph.append(run_record(method.id, started, [
        {"path": graph.relative(inputs_path), "sha256": "sha256:" + _sha(inputs_path)},
        {"path": graph.relative(cur_path), "sha256": "sha256:" + _sha(cur_path)}]))

    def prov(used: list[str], source: str | None) -> dict:
        return {"was_generated_by": run.id, "method": method.id, "used": used, "was_attributed_to": AGENT_LUMEN,
                "primary_knowledge_source": source}

    def rec(rtype: str, body: dict) -> mdl.Record:
        return graph.append({"schema_version": SCHEMA_VERSION, "type": rtype, "synthetic": False, **body})

    gene_id = cur["gene"]["identifier"]
    rec("gene", {"provenance": prov([D["hgnc"]], "source:hgnc"), "identifier": gene_id, "symbol": hgnc["symbol"],
                 "name": hgnc["name"], "taxon": cur["gene"]["taxon"],
                 "xrefs": [f"NCBIGene:{hgnc['entrez_id']}", f"ENSEMBL:{hgnc['ensembl_gene_id']}"]})
    seq_acc = cur["assembly"]["sequence_accession"]
    span = (min(e.start for e in ref.exons), max(e.end for e in ref.exons))
    rec("gene_locus", {"provenance": prov([D["ncbi_products"]], "source:ncbi-refseq"),
                       "identifier": f"locus:GRCh38:{seq_acc}:{span[0]}-{span[1]}:{ref.strand}", "gene": gene_id,
                       "assembly": "GRCh38", "sequence_accession": seq_acc, "chromosome": cur["assembly"]["chromosome"],
                       "start": span[0], "end": span[1], "strand": ref.strand,
                       "strand_basis": f"NCBI Datasets product report, genomic_range.orientation of {ref.accession} "
                                       f"on {seq_acc}",
                       "span_basis": f"the span of {ref.accession}'s exons"})
    canonical = f"numbering:{human_acc}-{cur['proteins']['human']['canonical_isoform']}" \
                f".sv{uni['entryAudit']['sequenceVersion']}"
    for model, meta, ident, source, used in (
            (ref, ref_meta, f"refseq:{ref.accession}", "source:ncbi-refseq", [D["ncbi_products"]]),
            (ens, ens_meta, f"ENSEMBL:{ens.accession}", "source:ensembl", [D["ensembl_transcript"]])):
        counterpart = f"ENSEMBL:{ens.accession}" if model is ref else f"refseq:{ref.accession}"
        cds_len = sum(max(0, min(e.end, model.cds_end) - max(e.start, model.cds_start) + 1) for e in model.exons)
        rec("transcript", {"provenance": prov(used + [D["hgnc"], D["ncbi_products"]], source), "identifier": ident,
                           "gene": gene_id, "annotation": source,
                           "annotation_release": _release(graph, used[0]), "assembly": "GRCh38",
                           "sequence_accession": seq_acc, "strand": model.strand, "exon_count": len(model.exons),
                           "cds_genome_start": model.cds_start, "cds_genome_end": model.cds_end,
                           "cds_length_nt": cds_len, "protein_product": meta["protein_product"],
                           "mane_status": "MANE Select", "mane_counterpart": counterpart})
        for e, body in exon_bodies(model, canonical):
            rec("exon", {"provenance": prov(used, source), "identifier": f"exon:{model.accession}:{e.number}",
                         "transcript": ident, **body})

    iso_nums = []
    for n in cur["proteins"]["human"]["other_isoforms"]:
        header = next(h for h in fasta if h.startswith(f"sp|{human_acc}-{n}|"))
        seq = fasta[header]
        ident = f"numbering:{human_acc}-{n}.sv{iso_audit[int(n)]['sequenceVersion']}"
        iso_nums.append(ident)
        rec("numbering", _numbering(prov([D["uniprot_isoforms_fasta"], D[f"uniprot_isoform_{n}"]], "source:uniprotkb"),
                                    ident, f"{human_acc}-{n}", iso_audit[int(n)]["sequenceVersion"], n,
                                    f"UniProtKB:{human_acc}", cur["proteins"]["human"]["taxon"], seq))
    rec("numbering", _numbering(prov([D["uniprot_human"]], "source:uniprotkb"), canonical,
                                f"{human_acc}-{cur['proteins']['human']['canonical_isoform']}",
                                uni["entryAudit"]["sequenceVersion"], cur["proteins"]["human"]["canonical_isoform"],
                                f"UniProtKB:{human_acc}", cur["proteins"]["human"]["taxon"], uni["sequence"]["value"]))
    rabbit_num = f"numbering:{rabbit_acc}.sv{rab['entryAudit']['sequenceVersion']}"
    rec("numbering", _numbering(prov([D["uniprot_rabbit"]], "source:uniprotkb"), rabbit_num, rabbit_acc,
                                rab["entryAudit"]["sequenceVersion"], None, f"UniProtKB:{rabbit_acc}",
                                cur["proteins"]["rabbit"]["taxon"], rab["sequence"]["value"]))
    np_acc = cur["mane_select"]["refseq_protein"]
    rec("numbering", _numbering(prov([D["refseq_protein"]], "source:ncbi-refseq"), f"numbering:{np_acc}", np_acc,
                                int(np_acc.rsplit(".", 1)[1]), None, None, cur["proteins"]["human"]["taxon"], np_seq))
    for data, acc, taxon, gene, canon, isos, snap in (
            (uni, human_acc, cur["proteins"]["human"]["taxon"], gene_id, canonical, iso_nums, "uniprot_human"),
            (rab, rabbit_acc, cur["proteins"]["rabbit"]["taxon"], None, rabbit_num, [], "uniprot_rabbit")):
        _refuse(f"NCBITaxon:{data['organism']['taxonId']}" == taxon, f"{acc}'s organism is not {taxon}")
        rec("protein", {"provenance": prov([D[snap]], "source:uniprotkb"), "identifier": f"UniProtKB:{acc}",
                        "name": data["proteinDescription"]["recommendedName"]["fullName"]["value"],
                        "gene_symbol": data["genes"][0]["geneName"]["value"], "gene": gene, "taxon": taxon,
                        "entry_version": data["entryAudit"]["entryVersion"], "canonical_numbering": canon,
                        "isoform_numberings": isos})

    table = write_codon_map(graph, rows, prov([D["ncbi_products"], D["ncbi_locus"], D["ucsc_locus"]], None),
                            ref, seq_acc, canonical, rec)
    pdb = [x for x in uni.get("uniProtKBCrossReferences", []) if x["database"] == "PDB"]
    rec("search_result", {"provenance": prov([D["uniprot_human"]], "source:uniprotkb"),
                          "route": f"UniProtKB {human_acc}'s PDB cross-references, read from the fetched entry",
                          "source": "source:uniprotkb", "retrieval": _retrieval_id(graph, D["uniprot_human"]),
                          "query": {"entry": human_acc, "cross_reference_database": "PDB"},
                          "hits": [{"pdb_id": x["id"], **{p["key"]: p["value"] for p in x.get("properties", [])}}
                                   for x in pdb], "n_hits": len(pdb)})
    rcsb = snaps.json("rcsb_search")
    body = json.loads(graph.path(inputs["snapshots"]["rcsb_search"] + ".request").read_bytes())
    hits = [{"entity": h["identifier"], "score": h.get("score")} for h in rcsb.get("result_set", [])]
    rec("search_result", {"provenance": prov([D["rcsb_search"]], "source:rcsb-pdb"),
                          "route": "RCSB entity-level search: source organism Homo sapiens (NCBI Taxonomy 9606, "
                                   "in the lineage) and gene name RYR1, required on the same polymer entity",
                          "source": "source:rcsb-pdb", "retrieval": _retrieval_id(graph, D["rcsb_search"]),
                          "query": body, "hits": hits, "n_hits": len(hits)})
    return {"codon_map": table.id, "cds_bases": sum(1 for r in rows if r.region == "cds"),
            "split_codons_map": split_codons_in_map(rows), "split_codons_model": split_codons_from_exon_model(ref),
            "ensembl_stop_convention": ens_meta["stop_convention"], "strand": ref.strand,
            "exons": len(ref.exons), "genome_copies_identical": True}


def _sha(p: Path) -> str:
    from .ids import sha256_hex
    return sha256_hex(p.read_bytes())


def _retrieval(graph: Graph, digest: str) -> mdl.Retrieval:
    [r] = [r for r in graph.records() if isinstance(r, mdl.Retrieval) and r.generated == digest]
    return r


def _retrieval_id(graph: Graph, digest: str) -> str:
    return _retrieval(graph, digest).id


def _release(graph: Graph, digest: str) -> str | None:
    """The release the source stated for this snapshot, as its retrieval record holds it (None if none stated)."""
    return _retrieval(graph, digest).source_release


def _numbering(prov: dict, ident: str, accession: str, version: int, isoform: str | None, protein: str | None,
               taxon: str, seq: str) -> dict:
    return {"provenance": prov, "identifier": ident, "accession": accession, "sequence_version": version,
            "isoform": isoform, "protein": protein, "taxon": taxon, "length": len(seq), "sequence": seq,
            "sequence_digest": refget_digest(seq), "md5": sequence_md5(seq)}


def exon_bodies(model: TranscriptModel, numbering: str) -> list[tuple[Exon, dict]]:
    walk_c: dict[int, int] = {}
    t = 0
    first = model.cds_start if model.strand == "+" else model.cds_end
    for e in model.exons:
        for p in (range(e.start, e.end + 1) if model.strand == "+" else range(e.end, e.start - 1, -1)):
            walk_c[p] = t
            t += 1
    i0 = walk_c[first]
    n_codons = sum(max(0, min(e.end, model.cds_end) - max(e.start, model.cds_start) + 1) for e in model.exons) // 3
    out = []
    for e in model.exons:
        lo, hi = max(e.start, model.cds_start), min(e.end, model.cds_end)
        body: dict[str, Any] = {"exon_number": e.number, "genome_start": e.start, "genome_end": e.end,
                                "coding_length_nt": max(0, hi - lo + 1)}
        if hi >= lo:
            c_a, c_b = walk_c[lo] - i0 + 1, walk_c[hi] - i0 + 1
            c_start, c_end = min(c_a, c_b), max(c_a, c_b)
            body.update({"coding_genome_start": lo, "coding_genome_end": hi, "c_start": c_start, "c_end": c_end,
                         "residue_numbering": numbering, "first_residue": (c_start + 2) // 3,
                         "last_residue": min((c_end + 2) // 3, n_codons - 1), "start_phase": (c_start - 1) % 3,
                         "end_phase": c_end % 3, "splits_codon_at_end": c_end % 3 != 0})
        else:
            body["data_absent_reason"] = "not-applicable"
        out.append((e, body))
    return out


def write_codon_map(graph: Graph, rows: list[MapRow], prov: dict, model: TranscriptModel, seq_acc: str,
                    numbering: str, rec) -> mdl.Record:
    names = [c[0] for c in MAP_COLUMNS]
    data = tsv_bytes(names, ([getattr(r, n) for n in names] for r in rows))
    path = f"tables/codon_map_{model.accession}_GRCh38.tsv"
    digest = graph.write_bytes(path, data)
    columns = [Column(name=n, datatype=t, required=req, description=desc,
                      numbering=numbering if n == "residue_number" else None).model_dump(mode="json", exclude_none=True)
               for n, t, req, desc in MAP_COLUMNS]
    return rec("table", {"provenance": prov, "name": "codon_map", "path": path,
                         "media_type": "text/tab-separated-values", "sha256": digest, "bytes": len(data),
                         "row_count": len(rows), "columns": columns, "primary_key": ["genome_position"],
                         "about": [f"refseq:{model.accession}", numbering]})
