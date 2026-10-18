# ChannelScope release `ryr1_composition_v0.1`: the evidence for a residue set fixed in advance

This release lays out, for each residue of a set fixed before the build, the evidence ChannelScope gathers about it, side by side, with no verdict of its own. Every value names its source, the logged retrieval it came from and the method that derived it. It is the composition, CL-4 in this project's plan for its first release, built on 12 October 2026 by `code/cl4/compose.py` under criteria committed before the build (`criteria/`). The tables are as the build wrote them, byte for byte.

## The residue set

The set is fixed by a rule committed before the build: the residues of human RyR1 (UniProt P21817, isoform 1) at which ClinVar's expert-panel records place one missense change on the transcript NM_000540.3. Of the 379 records ClinVar's search returned on 29 September 2026, 358 are included and 21 excluded, each with its reason (`cl4_exclusions.tsv`). The included records place a change at 299 residues.

## What each table holds

The tables are in `graph/tables/cl4/51539fd/full_set/`, each with its table record in `graph/records/table.jsonl`, which gives its columns, their meaning and the records it was built from.

| Table | Rows | What a row is |
|---|---|---|
| `cl4_set` | 299 | a residue of the set, with its ClinVar records and whether check C5's sample holds it |
| `cl4_partners` | 897 | the residue's partner in rabbit, mouse or pig, from the mappings release, with the mapping row's reliability flag |
| `cl4_structures` | 31,096 | the partner in one RyR1 chain of one structure of its species: whether the chain's numbering joins it, by which path, or why not; the structure's measured state; its gate's numbering case |
| `cl4_structure_counts` | 897 | for a residue and a species, how many structures join it in each measured state |
| `cl4_gnomad` | 624 | a gnomAD missense variant at a set residue, with its counts and filters |
| `cl4_clinvar` | 358 | an included ClinVar record: its classification, review status and date, as ClinVar gives them |
| `cl4_clinvar_conditions` | 624 | a condition of an included record, with the Mondo identifier ClinVar gives it, if any |
| `cl4_exclusions` | 21 | a record ClinVar's search returned that the set's rule excludes, and why |
| `cl4_vus_counts` | 32 | descriptive counts of the records of uncertain significance by the measured state of the structures that join their residues |

Local model quality is not assessed, and every structure row says so.

## What it found

There are 31,096 structure rows, one for each residue and each RyR1 chain in those of the 26 structures that are of its partner's species:
- 27,228 join the partner: 21,488 on numbering that both of CL-2's paths agree on, and 5,740 on this project's alignment alone (path A), all in the six Woll et al. structures (6W1N, 6X32, 6X33, 6X34, 6X35, 6X36);
- 24 do not, each with its reason;
- 2,344 fall where the chain models no residue at the partner's place;
- 1,496 cannot be decided from the numbering, since an unknown or ambiguous stretch lies between the joined residues on either side;
- 4 were withdrawn by the coordinate test, check C5-S (below).

The criteria read one way in a definition and another in an example, and 20 rows rest on the difference. Step 3 defines as *unplaced* a residue whose only reason for not being joined is path A's short departing run (R11c), whose placement step 2 does not accept; the example given with its rule 3 treats author 2092 in 6X32, 6X33, 6X34, 6X35 and 6X36, which R11c leaves unjoined, as *placed elsewhere*. The build applied the definition. So the rows of human 2060's partner, residue 2061 of UniProt P16960, one for each chain of those entries, read `not determinable`, with the reason "R11c, author 2092"; by the example's reading they would read `not modelled`. They stand as the build wrote them, and the criteria stay as committed (this project's decision of 14 October 2026).

Of the 222 records that ClinVar classifies as of uncertain significance, at 200 residues, 213 are joined in at least one closed structure and 212 in at least one open one, on numbering that both of CL-2's paths agree on; 9 are joined in none. The one record ClinVar classifies as "VUS-high" is counted apart, never with these. These are counts, and nothing is inferred from them (`cl4_vus_counts.tsv`).

gnomAD gives 624 missense variants at 260 of the set's residues, 84 of them with a filter in the exomes or the genomes. Of the 624 conditions the included records name, 365 carry a Mondo identifier that ClinVar gives.

## How it was checked

The criteria fixed every rule, every check and each check's planted fault before the build: drafted in commit 2039346, reviewed in e05184e and completed with the answers to their three questions in 2004787, the text the build ran by (`ledger.md`). `checks.tsv` lists each of the build's 20 check records with its outcome, its planted fault and that fault's outcome; the records themselves are in `graph/records/check_result.jsonl`. Each record names, as `pre_registered_in`, the first commit that held its fails-if sentence; `checks.tsv` adds the commits from which the check's row, and its planted fault's row, had the text the build ran by. For P0, C5-S-W-P and C10 and its planted fault, that was the review, which also added C11-U and C11-S, so theirs came from it too.
- Of the 20 check records, 18 passed. Check C5-S failed as its criteria define failure, and as they fix, the build went on: a join that counts against is withdrawn from every count and shown as withdrawn. C7-R is a report, with no pass or fail.
- The criteria list 18 planted faults, and 18 were caught by their own checks: 15 are the planted faults of check records (`checks.tsv`, column `planted_fault`), and 3 have records of their own (C5-S-W-P, C10-G-P and C10-W-P). The records of C7-R and C11-S list none.
- **Check C5** re-derived a sample of 43 residues. ClinVar's and gnomAD's answers were fetched afresh on 12 October 2026, by two fetch plans committed before any call. ClinVar, 53 records: 44 at the same version, equal in every field compared, and 9 at a higher version with the same title, reported as updates. gnomAD, 97 variants: all equal, and the dataset's label unchanged. SIFTS's files, those CL-2 read on 11 October, were read again by a second code path: 2,804 joins, all equal; this checks the code, not the source. 204 of the 206 fresh answers are in `graph/raw/`; the other 2 are among the raw answers not carried (below). C5's comparison code was committed with the build's code, 14 minutes after those answers were; the rules it applies were fixed in the criteria the night before (`ledger.md`).
- **Check C5-S** tested by coordinates, against a second pig structure, 9PWO, whose numbering SIFTS checks, the joins at the sampled residues that rest on this project's alignment alone: 744 of the 5,744 such rows. The other 5,000 were not tested. Of the 744, 660 were consistent, 80 could not be decided, and 4 counted against: human 3985 in 6X36 (chains B, E, H and K). There, the best fit puts 9PWO's residues of the same number 4 positions along: 12 or 13 residues of each 27- or 28-residue window sit at that offset, against 10 at offset 0. The criteria withdraw a join that counts against, and a whole segment only when at least two of its tested joins count against. In each of those 4 chains, the segment holding it (human 3696 to 4081) had that one tested join, so its other 21 joins stand, untested, in every count: 84 rows, at 15 of whose 21 residues ClinVar places a record of uncertain significance. The test compares the numbering's register with 9PWO's; it does not test either model against its map, and 9PWO's coordinates may not be independent of the models it is compared with.

## Re-running it

Two scripts in `rerun/` re-derive the tables from this release:
- `rerun/recount_from_release.py` needs only Python 3.10 or later, with no package: `uv run --project code python releases/ryr1_composition_v0.1/rerun/recount_from_release.py`, or any such Python. It reads the release's copies of CL-2's tables, CL-3's gate cases, the measured states and the mapping tables, each checked against its record's SHA-256, size and row count, and three of the build's own outputs: the set, the ClinVar table and check C5-S's verdicts. From them it re-derives every structure row's status and both count tables with the build's second script, `code/cl4/recount.py`, which imports none of the build's code, and refuses a table that holds a key twice. It prints "recount: 0 differences" when the release's tables are what those inputs give; an error in the three outputs it reads would pass both the build and the recount.
- `rerun/rerun_compose.py` re-runs the build's own code (`code/cl4/`, as it ran) on the release's records, tables and raw answers and on the 26 structures' coordinate files, which it fetches from the PDB by their retrieval records; the build's guard refuses any file whose SHA-256 is not its record's. It checks the release's nine tables against their records, then compares every cell, row by row, with what the build's code gives. It prints "0 differences" when they agree. Cells that hold the identifier of a record the build made in the same run (its C5-S check record; the two tables the count tables cite) cannot recur, since an identifier is a digest of its record's content, run times included; there the re-run must find one identifier for each, the one the release's records give. It needs the repository's code environment (`code/`) with gemmi 0.7.5: `uv run --project code --with gemmi==0.7.5 python releases/ryr1_composition_v0.1/rerun/rerun_compose.py`.

Neither repeats the build's checks or planted faults, check C5's comparisons with fresh retrievals, or check C5-N's reading of SIFTS. The PDB released revision 1.1 of 9ZO8 and 9ZOE on 14 October 2026, after both were measured at revision 1.0, which it no longer serves; for these two, `rerun/rerun_compose.py` rebuilds the measured file from the file the PDB serves now, with the patch in `rerun/patches/` (applied by `rerun/rebuild_revision.py`), and the build's guard then checks the rebuilt file like any other. The rebuild depends on the deflate library of the Python that runs it: it gave the measured bytes with zlib 1.3.2 on Windows and with zlib 1.3 on Linux (the logs of 14 October 2026, UTC, in the states release's `rerun/logs/`), and, in a separate test that day whose log neither release carries, with zlib 1.3.2 on Linux; while a Python whose zlib is zlib-ng, as CPython 3.14's Windows builds are, gives other bytes, which the guard refuses, the cause printed; so the repository's commands pin CPython 3.12. The pin fixes the interpreter, not the zlib a Python links. The states release's README says how the patches were made. If the PDB revises another structure, its file's SHA-256 differs and the re-run refuses it.

## What is in this release

- `graph/`: the records (`records/`), the tables (`tables/`) and the raw answers (`raw/`) of the reference closure: 382 records, of which 18 are tables and 284 are retrievals;
- `checks.tsv`: the build's check records, one line each;
- `criteria/`: the criteria as the build ran by, with working-note references replaced, as `criteria/replacements.json` lists;
- `code/cl4/`: the build's code as it ran, and `code/digests.tsv`, which gives each file's SHA-256 beside the one the build's method record gives;
- `inputs/a6_stated_correspondences.tsv`: the table of published statements the build read for the partners' `a6_entries` column, with the SHA-256 the method record gives;
- `ledger.md`: the order of the criteria's commits, check C5's retrievals and the build's run;
- `rerun/`: the two re-run scripts;
- `licences/gnomad_browser_LICENSE.txt`: the licence of the gnomAD browser's source files this release carries;
- `withheld.tsv` and `withheld_records.json`: what is not carried, and why;
- `manifest.json` and `ro-crate-metadata.json`: every file with its SHA-256.

## What is withheld, and why

- 3 method records that cite this project's working records by identifier, inside their content digests. They are summarised, less those parameters, in `withheld_records.json`.
- 5 raw answers whose bytes are not carried: gnomAD's page https://gnomad.broadinstitute.org/news/, which check C5 read, since decision S6 does not carry gnomAD's website pages; ClinVar's page on maintenance and use, which holds a session token as NCBI served it; EMBL-EBI's terms-of-use page; GitHub's answer on the gnomAD browser's latest commit, which names its author by a personal email address; SIFTS's documentation page. Their retrieval records are carried, each with its address and SHA-256.
- 26 coordinate files and 26 SIFTS files, fetched, not stored, and the other files the upstream runs read, each with its SHA-256 (`withheld.tsv`).

So a plain `channelscope validate` on `graph/` reports 13 findings: 8 references to the withheld records (rule V07) and 5 raw answers whose bytes are not carried (rule V08). The release's builder checks the graph in an export mode that excuses a finding only if `withheld.tsv` names its item, and checks that a plain run reports nothing else.

## The release's own checks

Before this release was written, its builder ran 13 checks on it, and each passed:
- **R1:** every file is in the manifest and the RO-Crate as it is; each copied table, raw answer and request body is the bytes its record names; the A6 table is the one the build's method record gives
- **R2:** the validator, in an export mode that excuses a finding only if `withheld.tsv` names its item, finds nothing on `graph/`; a plain run reports nothing but such items
- **R3:** the leak test (no machine path, working record, personal address, credential or session identifier), its own control first
- **R4:** the code is the code that ran: each file's SHA-256, and the code digest over all of them, as the build's method record gives them; the re-run scripts are as committed
- **R5:** the criteria's copy is the committed text with the listed replacements; each check record's fails-if sentence is in its row; each row, and its planted fault's row, had the text the build ran by from the commit `checks.tsv` names, before the run
- **R6:** `checks.tsv` is the check records, line for line, and the criteria's 18 planted faults were caught
- **R7:** the recount from the release's own files finds no difference
- **R8:** the full re-run of the build's code from the release finds every cell equal
- **R9:** this note regenerates from its sources
- **R10:** a clean rebuild is the same, file for file
- **R11:** each quotation of a source's terms is on the page it cites, word for word, and each page is the one its retrieval record holds
- **R12:** the ledger is in time order, and each time is its commit's or its record's
- **R13:** the gnomAD browser's licence notice is the file GitHub names for commit 528b499

Each check also ran on a copy of the release with a fault planted in it, 24 faults in all, and each fault was reported by its own check. R6, R9 and R10 regenerate a file with the builder's own code, so they catch an edit made after the build, not an error in that code; R8 re-runs the build's own code, so it reproduces any error the code makes every time.

## Licence and sources' terms

What ChannelScope made in this release is under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/); the code is under the MIT licence. Each source's part is under its own terms, quoted here from the pages this project read. A page marked "carried" is in `graph/raw/`; the others are named by their address and the day they were read. Each has its retrieval record in `graph/records/`.
- ClinVar's records, its search and summary answers of 29 September 2026 and check C5's answers of 12 October 2026: ClinVar, at NCBI, is their data source, as ClinVar asks of those who copy its data ("attribution to ClinVar as a data source"). ClinVar's page also says that its information is "not intended for direct diagnostic use or medical decision-making without review by a genetics professional" (its page on maintenance and use, https://www.ncbi.nlm.nih.gov/clinvar/docs/maintenance_use/, as read on 30 September 2026; the page is not carried, as above, but its retrieval record is);
- gnomAD's variant data: "The primary data from the gnomAD exomes and genomes are available free of restrictions under the [Creative Commons Zero Public Domain Dedication]". gnomAD also writes, "we request that you actively acknowledge and give attribution to the gnomAD project", and "All users of gnomAD data agree to not attempt to reidentify participants" (its terms page, from the gnomAD browser's source at commit 528b499, carried: `graph/raw/gnomad/2026-10-06/browser_terms_528b499.md`);
- the gnomAD browser's source files this release carries (`browser_dataset_metadata_528b499.ts` and `browser_terms_528b499.md`, from commit 528b499, and `c5_browser_dataset_metadata_main.ts`, from its main branch on 12 October 2026): the MIT licence, whose notice, as at commit 528b499, is in `licences/gnomad_browser_LICENSE.txt`. The licence at the main branch on 12 October was not read separately;
- UniProt's entries: UniProt applies the "Creative Commons Attribution 4.0 International (CC BY 4.0) License" "to all copyrightable parts of our databases", and adds: "We make no warranties regarding the correctness of the data, and disclaim liability for damages resulting from its use. We cannot provide unrestricted permission regarding the use of the data, as some data may be covered by patents or other rights." (its licence page, read on 11 October 2026, carried: `graph/raw/uniprot/2026-10-11/help_license.json`);
- NCBI's gene record: "NCBI itself places no restrictions on the use or distribution of the data contained therein", though some submitters "may claim patent, copyright, or other intellectual property rights in all or a portion of the data" (its policies page, read on 29 September 2026, carried: `graph/raw/ncbi/2026-09-29/about_policies.html`);
- Ensembl's transcript record: "Ensembl imposes no restrictions on access to, or use of, the data provided and the software used to analyse and present it", and "Some of the data and software included in the distribution may be subject to third-party constraints" (its disclaimer, read on 30 September 2026, carried: `graph/raw/ensembl/2026-09-30/archive_jun2026_legal_disclaimer.html`);
- HGNC's gene record: "all data is released under the Creative Commons Public Domain (CC0) License" (its licence page, read on 30 September 2026, carried: `graph/raw/hgnc/2026-09-30/about_license.html`);
- the structures' coordinates, which are not carried: the PDB's CC0 1.0 dedication, as the states release quotes it from held copies of the PDB's policies (`releases/ryr1_structure_states_v0.1/README.md`); the patches in `rerun/patches/`, which hold lines of the PDB's own files for 9ZO8 and 9ZOE, are under the same terms;
- SIFTS's mapping, which is not carried: SIFTS asks, "If you use SIFTS, please cite: Dana, Gutmanas et al., Nucleic Acids Research 47, D482 (2019) Velankar et al., Nucleic Acids Research 41, D483 (2013)" (https://www.ebi.ac.uk/pdbe/docs/sifts/, read on 11 October 2026), and EMBL-EBI's terms of use say: "EMBL-EBI itself places no additional restrictions on the use or redistribution of the data available via its Data Resources and Tools other than those provided by the original data owners" (https://www.ebi.ac.uk/about/terms-of-use/, read on 11 October 2026). Neither page is carried: they are EMBL-EBI's own pages, and the terms they hold speak to its data, not to the pages' text.
