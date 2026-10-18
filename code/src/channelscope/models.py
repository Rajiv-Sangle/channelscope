"""Schema v0.1 of the ChannelScope evidence graph, as typed models.

The JSON Schema in `what/evidence_graph/schema/v0.1/` is generated from these models and checked byte-equal to
their output (`channelscope schema check`; ADR-001 §7). Names follow the standard that names the thing: W3C PROV-O
for provenance (in snake_case: `was_generated_by`, `used`, `was_attributed_to`, `was_revision_of`,
`was_associated_with`, `acted_on_behalf_of`, `started_at_time`, `ended_at_time`, `generated`); Biolink for
`primary_knowledge_source`; HL7 FHIR DataAbsentReason 2.0.0 for why a value is missing; ECO for evidence classes.

Record kinds, and what each carries:
- plans and activities describe how things were made: `method` (a prov:Plan), `retrieval` and `run` (prov:Activity);
- entities describe things, each under an external or deterministic identifier: `source`, `gene`, `gene_locus`,
  `transcript`, `exon`, `protein`, `numbering`, `residue`;
- derived claims and bulk values: `alignment`, `residue_mapping`, `search_result`, `check_result`, `table`;
- `release` packages records and tables for consumers.

Every record carries `schema_version`, `type`, `id` and `synthetic`. `id` is `cs:<type>.<sha512t24u>` over the
record's own canonical content (channelscope.ids.record_id), so an edited record no longer matches its id and the
validator says so. Every record except plans and activities carries `provenance`.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from .ids import REFERENCE_PATTERN, anchored

SCHEMA_VERSION = "0.2.0"
READABLE_VERSIONS = ("0.1.0", "0.2.0")  # 0.2.0 is additive, so records written under 0.1.0 stay valid


def _pattern(kind: str, description: str) -> Any:
    return Field(pattern=anchored(kind), description=description)


RecordId = Annotated[str, _pattern("record_id", "A record's identifier: `cs:<type>.<sha512t24u of its content>`.")]
RawDigest = Annotated[str, _pattern("raw_digest", "A raw snapshot, named by the SHA-256 of its bytes.")]
SequenceDigest = Annotated[str, _pattern("sequence_digest", "The refget (ga4gh) digest of a sequence: `SQ.<sha512t24u>`.")]
SourceId = Annotated[str, _pattern("source", "A source's identifier in this graph, `source:<name>`.")]
Infores = Annotated[str, _pattern("infores", "A Biolink Information Resource Registry identifier.")]
AgentId = Annotated[str, _pattern("agent", "An agent: a person, an AI agent or a piece of software, `agent:<name>`.")]
GeneId = Annotated[str, _pattern("gene", "An HGNC identifier.")]
TaxonId = Annotated[str, _pattern("taxon", "An NCBI Taxonomy identifier.")]
ProteinId = Annotated[str, _pattern("protein", "A UniProtKB entry.")]
NumberingId = Annotated[str, _pattern("numbering", "A numbering: one exact sequence, with its version.")]
ResidueId = Annotated[str, _pattern("residue", "A residue: a position in a named numbering.")]
TranscriptId = Annotated[str, _pattern("transcript", "A versioned Ensembl or RefSeq transcript.")]
ExonId = Annotated[str, _pattern("exon", "An exon: its number within a named, versioned transcript.")]
GeneLocusId = Annotated[str, _pattern("gene_locus", "A span on a GRCh38 chromosome, with its strand.")]
EcoId = Annotated[str, _pattern("eco", "An Evidence and Conclusion Ontology class.")]
Timestamp = Annotated[str, _pattern("timestamp", "UTC, ISO 8601, millisecond precision.")]
Reference = Annotated[str, Field(pattern=REFERENCE_PATTERN,
                                 description="A record id, a raw snapshot digest, or an entity identifier.")]
PositiveInt = Annotated[int, Field(ge=1)]
NonNegativeInt = Annotated[int, Field(ge=0)]
Number = Annotated[float, Field(strict=False, description="A number; an integral value may be written as an integer.")]
Scalar = Union[str, int, float, bool, None]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class DataAbsentReason(str, Enum):
    """Why a value is missing: HL7 FHIR DataAbsentReason, version 2.0.0 (all 15 codes, checked 2026-09-29).

    A search that found nothing is a value, not an absence; an absence is only ever recorded with its reason."""

    unknown = "unknown"
    asked_unknown = "asked-unknown"
    temp_unknown = "temp-unknown"
    not_asked = "not-asked"
    asked_declined = "asked-declined"
    masked = "masked"
    not_applicable = "not-applicable"
    unsupported = "unsupported"
    as_text = "as-text"
    error = "error"
    not_a_number = "not-a-number"
    negative_infinity = "negative-infinity"
    positive_infinity = "positive-infinity"
    not_performed = "not-performed"
    not_permitted = "not-permitted"


# --- shared parts ---------------------------------------------------------------------------------------------------


class Provenance(Strict):
    """How a record came to be, in W3C PROV-O's terms."""

    was_generated_by: RecordId = Field(description="The retrieval or run that generated this record.")
    method: RecordId = Field(description="The method (prov:Plan) the generating activity followed. Part of the "
                                         "record's content digest, so a new method version gives a new record.")
    used: list[Reference] = Field(min_length=1, description="The inputs: records, raw snapshots or entities.")
    was_attributed_to: AgentId
    primary_knowledge_source: SourceId | None = Field(
        default=None, description="For reported content: the source that asserted it (Biolink).")
    was_revision_of: RecordId | None = Field(default=None, description="The record this one corrects (PROV-O).")


class Record(Strict):
    schema_version: Literal["0.1.0", "0.2.0"]
    id: RecordId
    synthetic: bool = Field(description="True on every record made from, or touching, invented data. Required, "
                                        "with no default, so that it is never assumed.")


class Entity(Record):
    provenance: Provenance


class FileRef(Strict):
    path: str = Field(min_length=1, description="Relative to the evidence graph's root, with forward slashes.")
    sha256: RawDigest
    bytes: NonNegativeInt | None = None


class Implementation(Strict):
    software: str = Field(min_length=1)
    version: str = Field(min_length=1)
    code_digest: RawDigest | None = Field(
        default=None, description="For ChannelScope's own code: SHA-256 over its source files (see provenance.py).")
    reference: str | None = Field(default=None, description="Where a third-party implementation is documented.")


class Software(Strict):
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    code_digest: RawDigest


class Environment(Strict):
    python: str
    platform: str


# --- plans and activities -------------------------------------------------------------------------------------------


class Method(Record):
    """A method: what was done, by which implementation, with which parameters (prov:Plan)."""

    type: Literal["method"]
    name: str = Field(pattern=r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)*$")
    version: str = Field(min_length=1)
    description: str = Field(min_length=1)
    implementation: Implementation
    parameters: dict[str, Scalar] = Field(default_factory=dict)
    was_attributed_to: AgentId


class Request(Strict):
    http_method: Literal["GET", "POST"]
    url: str = Field(pattern=r"^https://", description="The full URL, query string included.")
    accept: str | None = None
    body_sha256: RawDigest | None = Field(default=None, description="For a POST: the digest of the body sent.")
    body_path: str | None = Field(default=None, description="For a POST: where the body sent is stored.")


class Response(Strict):
    status: int = Field(ge=100, le=599)
    content_type: str | None = None
    bytes: NonNegativeInt


class Retrieval(Record):
    """One logged call to a public source (a prov:Activity). The raw bytes it returned are an entity named by their
    SHA-256 (`generated`); records parsed from them name that digest in `used`."""

    type: Literal["retrieval"]
    source: SourceId
    method: RecordId = Field(description="The fetch method followed.")
    request: Request
    started_at_time: Timestamp
    ended_at_time: Timestamp
    response: Response
    source_release: str | None = Field(default=None, description="The source's release, as the source states it.")
    source_release_basis: str | None = Field(default=None, description="Where the release was read.")
    source_release_absent: DataAbsentReason | None = Field(
        default=None, description="Why no release is recorded; the retrieval date then stands as the version.")
    generated: RawDigest
    stored_at: str = Field(min_length=1, description="Where the raw bytes are, relative to the graph's root.")
    storage: Literal["committed", "cache"] = Field(
        description="`committed`: under raw/, in git. `cache`: git-ignored; re-fetched by replaying the request.")
    was_associated_with: AgentId
    acted_on_behalf_of: AgentId


class Run(Record):
    """One run of ChannelScope's own code (a prov:Activity; a CreateAction in RO-Crate's Process Run Crate)."""

    type: Literal["run"]
    method: RecordId
    command: list[str] = Field(min_length=1)
    started_at_time: Timestamp
    ended_at_time: Timestamp
    used_files: list[FileRef] = Field(default_factory=list,
                                      description="Local files the run read, such as a curation file.")
    software: Software
    environment: Environment
    was_associated_with: AgentId
    acted_on_behalf_of: AgentId


# --- entities -------------------------------------------------------------------------------------------------------


class Source(Entity):
    """A database, paper, dataset or standard that content comes from."""

    type: Literal["source"]
    identifier: SourceId
    name: str = Field(min_length=1)
    source_type: Literal["database", "paper", "dataset", "standard", "software"]
    homepage: str | None = Field(default=None, pattern=r"^https?://")
    infores: Infores | None = Field(default=None, description="Its Biolink infores identifier, where one exists. "
                                    "Never invented: absent when the registry has none.")
    license: str | None = None
    citation: str | None = Field(default=None, description="A DOI or PMID, for a paper.")


class Gene(Entity):
    type: Literal["gene"]
    identifier: GeneId
    symbol: str = Field(min_length=1)
    name: str = Field(min_length=1)
    taxon: TaxonId
    xrefs: list[str] = Field(default_factory=list, description="Other identifiers for the gene, as CURIEs.")


class GeneLocus(Entity):
    """Where a gene's declared transcript lies on the genome. The strand is read from the annotation, never assumed;
    only GRCh38 is accepted (M01's G5)."""

    type: Literal["gene_locus"]
    identifier: GeneLocusId
    gene: GeneId
    assembly: Literal["GRCh38"]
    sequence_accession: str = Field(pattern=r"^NC_[0-9]{6}\.[1-9][0-9]*$")
    chromosome: str = Field(pattern=r"^([1-9]|1[0-9]|2[0-2]|X|Y|MT)$")
    start: PositiveInt = Field(description="1-based, inclusive.")
    end: PositiveInt = Field(description="1-based, inclusive.")
    strand: Literal["+", "-"]
    strand_basis: str = Field(min_length=1, description="The record and field the strand was read from.")
    span_basis: str = Field(min_length=1, description="What the span is, e.g. the span of a named transcript's exons.")


class Transcript(Entity):
    type: Literal["transcript"]
    identifier: TranscriptId
    gene: GeneId
    annotation: SourceId
    annotation_release: str | None = None
    assembly: Literal["GRCh38"]
    sequence_accession: str = Field(pattern=r"^NC_[0-9]{6}\.[1-9][0-9]*$")
    strand: Literal["+", "-"]
    exon_count: PositiveInt
    cds_genome_start: PositiveInt = Field(description="First base of the start codon, 1-based.")
    cds_genome_end: PositiveInt = Field(description="Last base of the stop codon, 1-based.")
    cds_length_nt: PositiveInt = Field(description="Coding bases, the stop codon included.")
    protein_product: str = Field(min_length=1, description="The accession of the translation product.")
    mane_status: Literal["MANE Select", "MANE Plus Clinical"] | None = None
    mane_counterpart: TranscriptId | None = None


class Exon(Entity):
    """One exon of one transcript, and how it codes. Phases are defined by formula (the exon figure's contract):
    start_phase = (c_start - 1) mod 3; end_phase = c_end mod 3. A wholly untranslated exon has coding_length_nt 0,
    empty coding fields, and data_absent_reason `not-applicable`."""

    type: Literal["exon"]
    identifier: ExonId
    transcript: TranscriptId
    exon_number: PositiveInt
    genome_start: PositiveInt
    genome_end: PositiveInt
    coding_genome_start: PositiveInt | None = None
    coding_genome_end: PositiveInt | None = None
    coding_length_nt: NonNegativeInt
    c_start: PositiveInt | None = Field(default=None, description="HGVS c. position of the first coding base.")
    c_end: PositiveInt | None = Field(default=None, description="HGVS c. position of the last coding base.")
    residue_numbering: NumberingId | None = None
    first_residue: PositiveInt | None = None
    last_residue: PositiveInt | None = None
    start_phase: Annotated[int, Field(ge=0, le=2)] | None = None
    end_phase: Annotated[int, Field(ge=0, le=2)] | None = None
    splits_codon_at_end: bool | None = None
    data_absent_reason: DataAbsentReason | None = None
    external_id: str | None = Field(default=None, description="The annotation's own exon identifier, if any.")


class Protein(Entity):
    type: Literal["protein"]
    identifier: ProteinId
    name: str = Field(min_length=1)
    gene_symbol: str = Field(min_length=1)
    gene: GeneId | None = Field(default=None, description="HGNC, for a human protein.")
    taxon: TaxonId
    entry_version: PositiveInt = Field(description="The UniProtKB entry version when retrieved.")
    canonical_numbering: NumberingId
    isoform_numberings: list[NumberingId] = Field(default_factory=list)


class Numbering(Entity):
    """The residue numbers of one exact sequence. The sequence travels with its numbering."""

    type: Literal["numbering"]
    identifier: NumberingId
    accession: str = Field(min_length=1)
    sequence_version: PositiveInt
    isoform: str | None = None
    protein: ProteinId | None = None
    taxon: TaxonId
    length: PositiveInt
    sequence: str = Field(pattern=r"^[ACDEFGHIKLMNPQRSTVWYUO]+$")
    sequence_digest: SequenceDigest
    md5: str = Field(pattern=r"^[0-9a-f]{32}$")


class Residue(Entity):
    type: Literal["residue"]
    identifier: ResidueId
    numbering: NumberingId
    position: PositiveInt
    amino_acid: str = Field(pattern=r"^[ACDEFGHIKLMNPQRSTVWYUO]$")


# --- derived claims and bulk values -------------------------------------------------------------------------------


class Alignment(Record):
    """A recorded global pairwise alignment. `path` is a run-length string over the alignment's columns: `M` pairs a
    subject residue with an object residue, `I` is a subject residue against a gap, `D` an object residue against a
    gap (so `I` residues are insertions in the subject)."""

    type: Literal["alignment"]
    provenance: Provenance
    mode: Literal["global"]
    subject: NumberingId
    object: NumberingId
    subject_sequence_digest: SequenceDigest
    object_sequence_digest: SequenceDigest
    path: str = Field(pattern=r"^([1-9][0-9]*[MID])+$")
    score: Number
    n_columns: PositiveInt
    n_pairs: NonNegativeInt
    n_identical: NonNegativeInt
    n_subject_only: NonNegativeInt
    n_object_only: NonNegativeInt
    identity: Number = Field(description="n_identical / n_pairs.")
    equally_optimal_alignments: PositiveInt | None = Field(
        default=None, description="How many alignments share the optimal score, where the method reports it.")


class ResidueMapping(Record):
    """Which residue of one numbering corresponds to which of another, position by position. The per-position
    values are in `table`; this record says how they were made."""

    type: Literal["residue_mapping"]
    provenance: Provenance
    subject: NumberingId
    object: NumberingId
    alignments: list[RecordId] = Field(min_length=1)
    table: RecordId
    n_pairs: NonNegativeInt
    n_subject_only: NonNegativeInt
    n_object_only: NonNegativeInt
    n_ambiguous: NonNegativeInt
    local_identity_window: PositiveInt = Field(description="Residues on each side of a position.")
    reliability_rules: list[str] = Field(min_length=1)
    kind: Literal["measured", "predicted", "interpreted"]
    origin: Literal["derived", "reported"]
    evidence_class: EcoId


class Column(Strict):
    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    datatype: Literal["integer", "number", "string", "boolean"]
    description: str = Field(min_length=1)
    unit: str | None = None
    numbering: NumberingId | None = Field(default=None, description="The numbering a position column indexes.")
    required: bool = Field(description="If false, an empty cell is allowed and means no value.")


class Table(Record):
    """A TSV of bulk values from one method run. Tables are never edited; a correction is a new table."""

    type: Literal["table"]
    provenance: Provenance
    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    path: str = Field(pattern=r"^tables/[A-Za-z0-9._/-]+\.tsv$")
    media_type: Literal["text/tab-separated-values"]
    sha256: RawDigest
    bytes: PositiveInt
    row_count: NonNegativeInt
    columns: list[Column] = Field(min_length=1)
    primary_key: list[str] = Field(min_length=1)
    about: list[Reference] = Field(default_factory=list, description="The entities the table describes.")


class SearchResult(Record):
    """A query put to a source, and everything it returned. An empty result is a value, not an absence."""

    type: Literal["search_result"]
    provenance: Provenance
    route: str = Field(min_length=1, description="What was searched, and how, in words.")
    source: SourceId
    retrieval: RecordId
    query: dict[str, Any]
    hits: list[dict[str, Scalar | list[Scalar]]]
    n_hits: NonNegativeInt


class Criterion(Strict):
    document: str = Field(min_length=1, description="The file that states the criterion.")
    pre_registered_in: str = Field(pattern=r"^[0-9a-f]{7,40}$", description="The commit that first contained it.")
    fails_if: str = Field(min_length=1, description="The failure condition, quoted.")


class Control(Strict):
    fault: str = Field(min_length=1, description="The fault injected to show that the check can fail.")
    outcome: Literal["detected", "missed", "not-run"]


class CheckResult(Record):
    """A pre-registered check, as it came out, with the injected fault that shows it could have failed."""

    type: Literal["check_result"]
    provenance: Provenance
    check: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    mission: str = Field(min_length=1)
    criterion: Criterion
    outcome: Literal["pass", "fail", "not-run"]
    control: Control
    observed: dict[str, Any]
    note: str | None = None


class Release(Record):
    """A versioned, checksummed package of records and tables for consumers (an RO-Crate)."""

    type: Literal["release"]
    provenance: Provenance
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    record_schema_versions: list[str] = Field(min_length=1)
    has_part: list[RecordId] = Field(min_length=1)
    files: list[FileRef] = Field(min_length=1)
    crate: str = Field(min_length=1, description="Path of the release's ro-crate-metadata.json.")
    license: str = Field(min_length=1)


RECORD_TYPES: tuple[type[Record], ...] = (
    Method, Retrieval, Run,
    Source, Gene, GeneLocus, Transcript, Exon, Protein, Numbering, Residue,
    Alignment, ResidueMapping, Table, SearchResult, CheckResult, Release,
)

TYPE_NAMES: dict[str, type[Record]] = {m.model_fields["type"].annotation.__args__[0]: m for m in RECORD_TYPES}

AnyRecord = Annotated[
    Union[Method, Retrieval, Run, Source, Gene, GeneLocus, Transcript, Exon, Protein, Numbering, Residue,
          Alignment, ResidueMapping, Table, SearchResult, CheckResult, Release],
    Field(discriminator="type"),
]
