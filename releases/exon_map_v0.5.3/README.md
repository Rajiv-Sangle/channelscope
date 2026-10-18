# exon_map_v0.5.3

The files that the exon-map figure of the article *ChannelScope* draws from: the 106 exons of the RYR1 transcript NM_000540.3 on the GRCh38 human genome assembly, with each exon's coding and untranslated parts; the positions the figure highlights; HGVS c. names at a test set of positions; three sequences (the transcript's span on chromosome 19, its exonic sequence, and the protein, UniProt P21817-1); and a header that holds the release's notes, the rules a figure follows to name and class a typed change, ClinVar's classifications as ClinVar gives them, the sources' terms and the provenance of every value.

This release reissues `exon_map_v0.5.2` so that it can be published. Its data are `exon_map_v0.5.2`'s byte for byte; only the header's texts and what the release carries change. `manifest.json` lists every change. It gives no SHA-256 of the texts replaced, and it gives the two entries removed with the comparison by where they were, not by name; its `old_texts` says why.

## Files

| File | What it holds |
|---|---|
| `exon_map_v0.5.3.tsv` | the exon table: 106 rows, one per exon |
| `exon_map_highlights_v0.5.3.tsv` | the positions the figure highlights: 23 rows |
| `exon_map_c_names_v0.5.3.tsv` | ChannelScope's HGVS c. names at the test positions: 587 rows |
| `exon_map_genomic_v0.5.3.fa` | the GRCh38 bases of the transcript's span on chromosome 19 |
| `exon_map_exonic_v0.5.3.fa` | the exonic sequence: the span's bases joined at the exon bounds |
| `exon_map_protein_v0.5.3.fa` | the protein, UniProt P21817-1 |
| `exon_map_header_v0.5.3.json` | the header: the notes, the rules, ClinVar's classifications, the sources' terms and the provenance |
| `manifest.json` | every other file's SHA-256 and size, the changes from `exon_map_v0.5.2`, and the checks the build ran |
| `withheld.tsv` | what this release does not carry, each item with its SHA-256 and the reason |

Check each file's SHA-256 against `manifest.json` before use.

## How it was checked

The build that made this release ran the checks T0 to T11 that `manifest.json` lists, each stated with what would fail it, and each shown to catch faults planted on purpose (`controls`) before anything was written. Among them: the data files are `exon_map_v0.5.2`'s byte for byte (T1); the header differs from `exon_map_v0.5.2`'s only at the declared places, each with its declared value (T2); NHGRI's terms are quoted as its page, as held, gives them (T8); and the leak test that this project runs on everything before it enters its public repository finds nothing in the folder (T10; the test and its patterns are not published).

The checks that the build of `exon_map_v0.5` ran on the data and the typed-variant engine, which this release keeps, are carried in `manifest.json` under `v0_5_checks.checks`: 29 checks, with the SHA-256 of that release's manifest. Two are carried with a declared change: B22, whose statement is reworded and whose outcome is withheld (see *The comparison with an independent implementation*), and B29, one sentence reworded.

## What this release does not carry

`withheld.tsv` lists each item with its SHA-256 and the reason:
- the typed-variant test set, `exon_map_variant_tests_v0.5.2.tsv`, which the header still cites by case (under `typed_variants`: `test_set`, `rules`, `refusals`, `class_order_reading` and `splice_flag`; and the literature's highlight groups);
- `exon_map_v0.5.2`'s header and manifest, and the manifests of `exon_map_v0.5` and `exon_map_v0.5.1`, which this build read;
- the snapshot of Mutalyzer's homepage that the header's note on Mutalyzer describes;
- the four programs that built this release and the releases before it.

### The comparison with an independent implementation

The typed-variant engine's names were compared, case by case, with the answers of an independent implementation, Mutalyzer (https://mutalyzer.nl/). No terms of use for Mutalyzer's service were read: its homepage, as retrieved on 2 October 2026 at 21:11 UTC, needs JavaScript and shows only its title. ChannelScope publishes material from a source only where the source's terms clearly allow the use, so this release carries none of Mutalyzer's answers. The comparison's results, and the test set that holds Mutalyzer's names beside this release's, are withheld; so is the outcome of v0.5's check B22, which made the comparison, whose statement `manifest.json` carries reworded. The header keeps the addresses of the requests sent, under `provenance`, as this project's own record of what was asked, with the sizes and HTTP statuses of the answers withheld. Each answer's SHA-256 is kept too, so anyone can send the same requests to Mutalyzer, under its terms, and check the answers it gives; this release publishes neither the answers nor the comparison's results.

What Mutalyzer's terms would add: if they allow it, a later release can publish the comparison, with the test set.

## Licence, and the sources' terms

ChannelScope's parts of this release are under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), credited as "ChannelScope, release exon_map_v0.5.3"; the header's `licence` says which parts. The sources' parts stay under their own terms, which the header quotes under `terms` from each source's page as retrieved: UniProt, NCBI, HGNC, Ensembl, the UCSC Genome Browser, ClinVar, HGVS Nomenclature, the Sequence Ontology and NHGRI. NHGRI's content is in the public domain unless otherwise indicated, and NHGRI asks for this acknowledgement: Courtesy: National Human Genome Research Institute (https://www.genome.gov/). Quotations from papers remain their authors' and publishers' words, quoted for citation; the papers were read from copies that are not redistributed.

This release's builders are not published; ChannelScope's published code is under the MIT licence.

## Rebuilding it

This release cannot be rebuilt from this repository. A reissue builder made it from `exon_map_v0.5.2`'s files; that release was made from `exon_map_v0.5.1`'s, and that from `exon_map_v0.5`, which was built from ChannelScope's evidence graph. None of those releases, and none of the builders, is published. What is carried instead: every file's SHA-256; every change from `exon_map_v0.5.2`; this build's checks and the faults each caught; and the 29 checks of `exon_map_v0.5`.

## Pointers to records that are not public

- `exon_map_v0.5`, `exon_map_v0.5.1` and `exon_map_v0.5.2`, which the header and the manifest name: earlier releases of these data, not published. The exonic and protein files' title lines name `exon_map_v0.5`, whose build wrote them; their bytes are kept as they were, so their SHA-256 still hold.
- The commits that the header's `provenance.checks` name under `pre_registered_in` (79ff30b, 8e84a8b, a5b6583): each records that a check's criteria were committed before the check ran, in this project's working history, which this repository does not carry.
- The codon map table the header cites (`provenance.codon_map_table`) is published in `releases/ryr1_mappings_v0.1/graph/tables/codon_map_NM_000540.3_GRCh38.tsv`, with the same table record and SHA-256.
- The header also names other working records of this project, none of them published: the records of its evidence graph and its reading record (`what_this_is`, `notes_basis`), the snapshots of the pages and papers it read (`provenance`, `literature`), a brief (`typed_variants.splice_flag`), the earlier release `exon_map_v0.4`, and the view contract that v0.5's check B1 names.

What access to them would add: the earlier releases and the builders would let anyone run this build again and each of its checks; the records and snapshots would let anyone trace each value to the page or paper it was read from; and the working history would show when each criterion was committed.
