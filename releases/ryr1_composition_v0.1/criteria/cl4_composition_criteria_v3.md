<!-- context_channelscope_cl4_composition_criteria_v3.md as committed in 2004787a50b87a82bfafd748f9454691bb95986b; working-note references replaced as criteria/replacements.json lists -->
---
type: context
subtype: context_research
status: reviewed
created: 2026-10-11
updated: 2026-10-11
last_edited_by: lumen
owner: agent
tags: [close, cl-4, composition, clinvar, gnomad, mondo, structures, criteria, provenance, version-3]
token_estimate: 28000
---

# CL-4: the composition over a residue set fixed in advance (criteria, version 3)

> **Status: version 3, reviewed: revised after two narrow re-checks (2026-10-11, night; the second "ready after
> fixes", its fixes applied), and committed as reviewed.** Committed earlier as an unreviewed draft (`2039346`).
> Questions Q1 to Q3 go to the operator on the morning of 12 October; Q1's answer may change the VUS subset's rule
> only, and is recorded here with its time. It replaces version 1
> ([a working note, not public]) and version 2
> ([a working note, not public], committed in `77395aa` as an unreviewed draft) as a whole, and
> is written to be read without them. It is committed before the build, and no criterion changes after its commit
> without the operator's word. Part of the close, [a working note, not public], deliverable CL-4 and claim
> PC-4. It depends on CL-1 (the mappings); on CL-2 (criteria version 2.2,
> [a working note, not public], committed in `125f89f`, and its run, usable, committed in
> `c4e8b66`); on CL-3 (the measured states, and each entry's gate case); and on graph records for the upstream tables
> (precondition P0). Every number below was re-derived by a script named in *The scripts behind this version's
> numbers*. The critique of version 2 (verdict "not ready") is answered in the record at the end.

## What it shows, and why

This is the close's demonstration of "composed", one of the motivation's three words. It is also the operator's
condition for the close: "some demonstration of the provenance tracked knowledge assembly". For each residue of a set
fixed in advance, it lays out evidence from separate sources side by side, each value traced to its record:
- the residue's partners in rabbit, mouse and pig (CL-1's mappings);
- the structures that model those partners, chain by chain, on the numbering CL-2 checked, with the class CL-3
  measured and each entry's gate case, and the reason wherever a structure does not join;
- the missense variants gnomAD lists at the residue;
- ClinVar's expert-panel classification, quoted, with each condition and its Mondo identifier where ClinVar gives one.

**It gives no verdict of its own,** and it infers nothing from the counts it reports.

## What has been seen before this commit (so what is not blind)

**CL-2's results are known.** CL-2 ran under its criteria 2.2 (run `e888359`, committed in `c4e8b66`) before these
criteria are committed. Its tables' header lines say: run complete, outcomes usable, every planted fault caught, K9
holding in all 104 chains. What its tables show (scripts v3_01, v3_03, v3_09):
- the 20 entries SIFTS maps are "equal": every compared residue of their 80 RyR1 chains is "agree" (SIFTS and path A
  give the same position) at offset 0;
- 6W1N and 6X32 to 6X35 depart by +1 across author 2736–2939 (species P16960 2737–2940), 180 residues in each of
  their 20 chains, on path A alone. 6X36 does not depart. No other entry has a departing segment;
- 6X32's run at author 2490–2534 is identity low (45 residues, 0.9556) in each of its four chains, so none of its
  180 residues is joined;
- under R11c, author 2092 is not joined in any chain of 6X32 to 6X36 (20 residues, each placed by path A at P16960
  2047);
- 28 residues are undeclared differences, at seven positions in four chains each: 6W1N 2092; 6X32 2516 and 2517; 6X35
  2479; and author 615 in 6X34, 6X35 and 6X36. The 20 declared differences (Y523S in 7T64, 7T65, 9CGP and 9CGQ; R615C
  in 9PWO) are joined;
- the residues CL-2 gives no species position are UNK (5TB0, 5T9V, 9ZO8 and the six Woll et al. entries) and 89
  "neither path" residues in 6X32 to 6X36. No residue is disputed, path S only, a SIFTS anomaly, pairing disagrees,
  microheterogeneity, an insertion code or outside;
- the gate residue sits at S13's author number in all 104 chains: "agree" at offset 0 in the 80 chains SIFTS maps,
  "path A only" at offset 0 in the 24 Woll et al. chains. Read by CL-2's committed gate rule, the 20 SIFTS-mapped
  entries fall in case (a) and the six Woll et al. entries in case (b) (v3_03). That is this drafter's reading of the
  rule, not CL-3's mark, which the rows carry.

**No rule here was fixed by looking at a CL-4 outcome.** L2's rule was written into a file before any set residue's row
was read from CL-2's tables (`v3_rules_L2_fixed_before_614.md`). Only then were residue 614's rows computed, for the
article's worked example (v3_04). The other CL-4-level readings made while drafting are human 163's three planted
joins and their neighbours (v3_04); P16960 950, 940 and 960 in 6X32 chain B (v3_04, v3_05); and C5-S on 1,588 control
positions outside the pig departure, with CL-2's labels, run after version 3's three changes to C5-S were fixed
(v3_05, v3_08). No count of L2 statuses over the set was computed.

**Seen before version 3:**
- **The input's counts:** the set, the exclusions, the VUS subset, the conditions, the gnomAD rows, the partners and
  C7's blind set (s01 to s03, s13, s14, s17). They are properties of the input, stated below.
- **C5's sample of 30** was drawn (s10), and is listed under C5.
- **Path A's outcomes for all 26 entries** were known before CL-2's run, from the emulation CL-2's critic ran (CL-2's
  criteria, lines 492–498).
- **The declarations of all 26 entries** (s04): Y523S in 7T64, 7T65, 9CGP and 9CGQ (`engineered mutation`); R615C in
  9PWO (`variant`); 50 UNK `conflict` rows per chain in 9ZO8, at rabbit 4279–4302 and 4318–4343. None for any Woll et
  al. RyR1 entity.
- **The seven pig structures,** read from the files: the residue at author 615 in every RyR1 chain (s12); their
  modelled residues in author 2650–3000 (s04); 9PWO's author numbers against P16960 (s04); their metadata (s05).
- **Where UNK residues sit.** The critic of version 2 read, by author number, where UNK residues with CA atoms sit in
  the 26 entries, and the stretch around pig 615 (its scripts `c02`, `c03`). Re-run here (v3_06): UNK residues sit at
  the partners' author numbers in 724 of the 31,096 structure rows, at 45 set residues, six of them in C5's 30 (3217,
  3218, 3253, 3290, 3402 and 4283).
- **The coordinate test of C5-S** was judged on control positions outside the pig departure (s06 to s08, s16, s18, s21,
  s22, and now v3_05 and v3_08). Those positions include the pig partners of 92 set residues, and their windows reach
  the partners of 248 of the 288 set residues whose pig partner lies outside 2700–2960, among them 23 of C5's 30 and
  all four worked residues (s22). So C5-S's outcome outside the departure was largely seen. Inside the departure only
  label-free numbers were computed (s07, s16), and there C5-S stays blind.
- **ClinVar's same-version comparison** (s09) was tried on the eight records held both as a summary of 29 September and
  as a summary and full record of 2 October. Seven are outside the set. The eighth, VCV000133055.4
  (c.13994_13995delinsCT, p.Leu4665Pro), is an included record at residue 4665, which is not in C5's sample (v3_02).
  *(Version 2 said all eight were outside the set. That was false.)*

**Not done:** nothing was fetched; no rabbit or mouse structure was compared with another by coordinates; ClinVar's
definition of "VUS-high" was not read (question Q1).

## The inputs, each with its record

Paths are under `what/evidence_graph/` unless they begin with `what/` or `how/`.

| Input | File | Record |
|---|---|---|
| ClinVar search, 2026-09-29 | `raw/clinvar/2026-09-29/esearch_RYR1_expert_panel.json` | `cs:retrieval.LZXj7wr6TidQhydfhP215YfYX94sb-yg` |
| ClinVar summaries, batches 1 and 2 | `raw/clinvar/2026-09-29/esummary_RYR1_expert_panel_1.json`, `_2.json` | `cs:retrieval.PNXvfeq3vV_HZaou_sauo8UQEfmL6M0X`, `cs:retrieval.m3LSpuTeDIuCl6DQZhO0yCz9CU2PxUZR` |
| ClinVar's maintenance and use page (its request for attribution; its link "Classification") | `raw/clinvar/2026-09-30/docs_maintenance_use.html` | `cs:retrieval.DVFq5yeaAE238whGncB4dGFJxDrQVVOD` |
| Human RyR1, P21817 (UniProt 2026_03, sequence version 3) | `raw/uniprot/2026-09-29/P21817.json` | `cs:retrieval.VPdG0C8dOG0RdRCDH3o7hwF0-y22z2qQ`; numbering `numbering:P21817-1.sv3` |
| Rabbit P11716 (sequence version 1) | `raw/uniprot/2026-09-29/P11716.json` | `cs:retrieval.72qWZyUw2nYc8JFq6a01ifDXUgHzhNgc`; `numbering:P11716.sv1` |
| Mouse E9PZQ0 (sequence version 1) | `raw/uniprot/2026-10-06/E9PZQ0.json` | `cs:retrieval.3zXqsU_s_QP4ULOQ6dzkTr2bdaQuY4Uc`; `numbering:E9PZQ0.sv1` |
| Pig P16960 (sequence version 2) | `raw/uniprot/2026-10-06/P16960.json` | `cs:retrieval.RgMUbxHrN4da3VwfkCujOspT9VXLVJoq`; `numbering:P16960.sv2` |
| Mapping, human to rabbit (M01) | `tables/residue_mapping_P21817-1.sv3_P11716.sv1.tsv` | `cs:table.5URsZZtyhn3vUFBvDH0dg0YxVwduVhjo` |
| Mapping, human to mouse (O4) | `tables/residue_mapping_P21817-1.sv3_E9PZQ0.sv1.tsv` | `cs:table.9708f3rPzqExweM8kfbZH1egpdG4nNKI` |
| Mapping, human to pig (O4) | `tables/residue_mapping_P21817-1.sv3_P16960.sv2.tsv` | `cs:table.nt5DASs63Krm6eTtUVxT7Q3GgKRa_nFu` |
| Check A6's outcome (CL-1) | the check-result record | `cs:check_result.R2g8_EbkE2AkRkXlt0hrjWN5bMxBofK1` |
| A6's stated correspondences | `what/references/a6_stated_correspondences.tsv` | no record: a committed file, guarded by its blob at the build's commit (C1) |
| The 26 structures | `cache/rcsb/2026-10-06/<id>.cif.gz` | one retrieval record each (26) |
| SIFTS's 26 files, read by C5-N | `cache/sifts/2026-10-11/<id>.xml.gz` | one retrieval record each (26) |
| CL-2's tables: entries, segments, exceptions | the `tables/` copies of `curation/cl2_run_e888359/cl2_numbering_entries.tsv`, `_segments.tsv`, `_exceptions.tsv` (committed in `c4e8b66`) | their table records: **none yet (P0.2)** |
| CL-3's states: S13's table | the `tables/` copy of `curation/s13_gate_remeasurement.tsv` | its table record: **none yet (P0.3)** |
| CL-3's gate cases | CL-3's table of the 26 entries' cases | its table record: **none yet (P0.3)** |
| S2's gnomAD table | the `tables/` copy of `curation/s2_gnomad_ryr1_missense.tsv`; S2's input, the gnomAD answer of 2026-10-06 | its table record: **none yet (P0.1)**; the answer's retrieval `cs:retrieval.Js-xUiFnFMPG3eB-5PfW6l_HLY-UQ9vQ` |
| gnomAD's dataset label, release post and terms of use | `raw/gnomad/2026-10-06/browser_dataset_metadata_528b499.ts`, `news_2026-09-gnomad-v4-1-2.html`, `browser_terms_528b499.md` | `cs:retrieval.dMNnflVo8QOV-vkgafiAldeVHTWNVVu8`, `cs:retrieval.3B8TFgYeCMaieBwPtQqNwmqspVv8Y791`, `cs:retrieval.grVhkUqc4-d3DYE_XaRfXrbt5goL3uGn` |

CL-2's column names are its committed code's (`ENTRY_COLS`, `SEGMENT_COLS` and `EXC_COLS` in `cl2/numbering.py`), and
this note uses them. CL-3's are those CL-3's notes (version 3) give the derived copy of S13's table: `class_a`,
`class_b_fixed`, `class_at_minus_0_5`, `class_at_plus_0_5`, `radius_a`, `deposited_words`, `deposited_implies`. If
CL-3's release names them otherwise, the build reads them by meaning and its method record states the mapping. CL-4's
own output columns do not depend on them.

## P0. The preconditions: the upstream tables in the graph

Today no table, run or method record covers S2's gnomAD table, CL-2's three tables or S13's table. The graph's four
table records are the codon map and the three mappings (v3_02). CL-2's tables sit in `curation/cl2_run_e888359/`, each
with 54 comment lines above its column line (v3_01). S13's table has comment lines and column names such as `class_A`
and `class_at_minus_0.5A`, which the schema's column-name pattern refuses (`Column.name` in `models.py`) and which
rule V09 would not read as a header. Without records, C1 and C4 would fail on every value of L2 and L3. **Before the
build:**
- **P0.1, S2's gnomAD table:** a method, a run and a table record, written from the committed spec
  (`curation/record_s2_gnomad_ryr1_missense.yaml`). The table's file sits under `tables/` and holds S2's 7,963 data
  rows byte for byte under S2's 37 columns; key `variant_id`, distinct in all 7,963 rows (s02).
- **P0.2, CL-2's three tables:** one method, one run and three table records for run `e888359`. Each file sits under
  `tables/`, and its data rows are byte for byte those of the curation file committed in `c4e8b66`, under the same
  column line. **And CL-2's run is usable,** read from those curation files' header lines as committed: "Run:
  complete", "Outcomes: usable", every planted fault's line "caught", K9's line "pass", and `k9_sum_holds` true in all
  104 chain rows of the entries table. All of this holds today. **The keys:** the entries table is keyed by `entry`,
  `scope`, `entity` and `chain` (distinct in all 260 rows; `entity` is empty on an entry's own row), the segments
  table by `entry`, `chain` and `segment` (distinct in all 610), and the exceptions table by `entry`, `chain`, `kind`
  and `author_first` (distinct and never empty in all 485 rows). The recording tool's rule
  RT06 refuses a key column that is not required (`record_table.py`, `check_rows`), while the validator's V09 allows an
  empty key cell; so P0.4's review brings RT06 into line with V09 before P0.2 is recorded. *(Added after the re-check
  of version 3, finding S-P0: as drafted, no byte-for-byte copy of the entries table could pass RT06.)*
- **P0.3, CL-3's tables:** a table record for S13's table (the derived copy CL-3's notes describe), and a table record
  for the 26 entries' gate cases, one row per entry, with the case as one letter, `a` to `d`, and for `c` and `d` its
  reason, derived
  by CL-3's builder from CL-2's tables (CL-3's check C14), with the builder's own method, run and table records.
  CL-3's notes name it since the night of 2026-10-11 (*What the release holds*, "the gate cases"), after this note's
  version 3 found they named none.
- **P0.4, the recording tool:** `how/runtime/channelscope/record_tables/record_table.py`, committed in `77395aa` as an
  unreviewed draft, is reviewed by a fresh critic and its findings are applied before it writes any of these records.
- **P0.5, the validator:** `channelscope validate` reports no finding.

**What P0 does not require, and why.** S2's checks K0 to K8 and their eight planted faults are not required as
check-result records. S2's run wrote none, and the recording tool records none: its rules RT01 to RT17 cover the table,
the code, the times, the environment and the inputs. The method record's description names the checks, as the
committed spec writes it, and says that the table is written only if every check passes and every control holds. That
is a statement about S2's code, which the run record names by its digest. CL-2's checks stay in its committed tables'
header lines, which P0.2 reads. P0's check row (below) asks for exactly what this section asks.

**What then holds:** CL-4 reads the `tables/` copies, never the curation files, and C1 checks each copy against its
table record. **If P0 is not met, the build does not start** (question Q3).

**P0 depends on CL-3's question 1.** Under its option (a), derived copies, or (b), a schema change, P0.3 can be met.
Under its option (c), no graph records for CL-3, L2's state values would have no table record, C4 could not pass, and
CL-4 could not be built as specified. That combination is the operator's to resolve.

## The residue set, fixed now

- **Input:** the held ClinVar search, `RYR1[gene] AND "reviewed by expert panel"[revstat]`, which returned 379
  records, and its two summary batches. The set is defined on this held retrieval, not on a new one, so it cannot
  move. Every ClinVar value shown is dated 29 September 2026, the day of the retrieval.
- **A record is included** if all three hold:
  1. its `molecular_consequence_list` is exactly `["missense variant"]`;
  2. its `title` names one substitution of one of the twenty amino acids on NM_000540.3, in the form
     `NM_000540.3(RYR1):c.… (p.XaaNYaa)`. A title on another transcript version fails this rule;
  3. `Xaa` equals P21817-1's residue at `N`. NP_000531.2 equals P21817-1 (M01's check A1).
- **Exclusions:** every excluded record is listed with the first rule it fails and what failed (table
  `cl4_exclusions`).
- **The set** is the distinct `N` of the included records. Each included record is placed at the residue its title
  names, and nowhere else.
- **As counted** (s01): 379 records read; 358 included, at 299 residues, 47 of them with more than one record; 21
  excluded, all by rule 1 (splice donor 5, synonymous 4, intron 3, nonsense 2, in-frame deletion 2, frameshift 2,
  in-frame insertion 1, 5′ UTR 1, an empty list 1). Rules 2 and 3 exclude nothing on this input. The one title that
  names NM_000540.2 (VCV000420138.16, c.958_960del) fails rule 1 first: its list is empty. One included record names a
  two-base change (VCV000133055.4, c.13994_13995delinsCT, p.Leu4665Pro): its consequence is missense and its title has
  the form of rule 2. These are properties of the input, and the build must reproduce them (check C2).

## The VUS subset, and the question it raises

- **The rule:** included records whose `germline_classification.description` begins "Uncertain significance". As
  counted (s01): 222 records at 200 residues (219 "Uncertain significance", 3 "Uncertain significance; drug
  response").
- **The record it leaves out:** VCV000133070.12 (c.14471T>C, p.Leu4824Pro, residue 4824) has the description
  "VUS-high". The held summary gives these words and nothing that defines them. ClinVar's own page of classification
  terms, read on 2026-10-11 by a logged retrieval (`raw/clinvar/2026-10-11/docs_clinsig.html`,
  `cs:retrieval.aYuyetCK5FXXreMmP4yNQdSZuIZo0oZr`; the page says "Last updated: 2025-08-15T20:46:46Z"), gives
  "VUS-high", "VUS-mid" and "VUS-low" one row: "These terms are considered consistent with the 2015 guidelines from
  ACMG/AMP for variants classified for Mendelian diseases: "It should be noted that some laboratories may choose to have
  additional tiers (e.g. subclassification of variants of uncertain significance (VUSs), particularly for internal
  use) and this practice is not considered inconsistent with these recommendations." However, those guidelines do not
  provide specific criteria for each sub-tier of VUS so we recommend that submitters who use the sub-tiers describe
  their criteria for each sub-tier in their assertion criteria." So ClinVar presents "VUS-high" as a sub-tier of
  uncertain significance, whose criteria each submitter sets.
- **The options** are put to the operator as question Q1, with their costs, before the commit. The column line does not
  wait for the answer: `cl4_clinvar` and `cl4_vus_counts` have a `subset` column under every option.
- **Decided: option (c)** (the operator, 23:28:41 IST on 2026-10-11, the transcript). The rule stands: 222 records at
  200 residues. VCV000133070.12 is reported apart, as the subset "VUS-high (apart)", never added to the 222, with
  ClinVar's definition above quoted beside it.

## The layers, and the rule for each

**L1. Partners in rabbit, mouse and pig.**
- **Source:** the three mapping tables with their records (above). The row read is the one whose `subject_position` is
  `N`.
- **Per residue and species:** `correspondence` (`pair` or `no-correspondence`); the partner's position and residue
  (`object_position`, `object_residue`); `reliability` (`standard` or `lowered`), `reliability_reasons` and
  `ambiguous`, all as committed. No value is changed.
- **As counted** (s03): all 299 residues are a `pair` in all three species, and none is ambiguous. Reliability is
  `standard` at 268 (rabbit), 269 (mouse) and 269 (pig); the rest are `lowered`, for repeat, disordered, near-indel or
  compositional-bias reasons.
- **Check A6:** an A6 entry (`what/references/a6_stated_correspondences.tsv`) is named on a residue's rabbit row if any
  human position it names is the residue, or any rabbit position it names is the residue's rabbit partner. A range
  counts each position in it: A6-06 names human 4927–4928 and rabbit 4926–4927. Seven entries attach to six residues
  (s14): A6-01 at 522; A6-02 and A6-03 at 163; A6-04 at 156; A6-06 at 4928; A6-08 at 485; A6-09 at 4837. A6-03 is the
  entry that failed: its source names human R164 for rabbit R164, so it attaches to human 163 only through its rabbit
  position. The row cites A6's check-result record.
- **No partner:** a residue with no correspondence in a species has no structure rows for that species. None occurs on
  the held tables.

**L2. The structures that model it.**

*Reading CL-2's tables.* For each RyR1 chain c of an entry that CL-2 analysed (its entries table's chain rows):
- **modelled residues:** every author number from a segment row's `author_first` to `author_last`, less the ranges in
  its `unmodelled_gaps`. Each takes its segment's `status`. A chain's segments cover its modelled residues once each,
  in author order;
- **placed residues:** those whose segment's `status` is `agree` or `path A only`. A placed residue's species position
  is its author number plus `offset_s` (`agree`) or `offset_a` (`path A only`). CL-2 gives no other residue a species
  position (`cl2/numbering.py`, lines 816–819);
- **joined:** a placed residue whose segment has `identity_low` false and `short_departing_run_path_a` false, and for
  which no exceptions row (same `entry` and `chain`, `author_first` equal to its author number and `ins_code` to its
  insertion code, `kind` other than `UNK`) has `joined` false. *(Insertion code added after the re-check: matched on
  the author number alone, a row for 50A would unjoin residue 50. CL-2's run has no insertion code.)*

The reading is guarded (check C11). Per segment, the author numbers counted equal `n_residues`, the species positions
run from `species_first` to `species_last`, and the joined residues number `joined_residues`. Per chain, the joined
residues equal the entries table's `joined`. Every placed residue that is not joined has an exceptions row with
`joined` false. No species position is held by two placed residues of one chain, and joined residues' species
positions rise with their author numbers. Label order follows author order in every chain, and every UNK stretch's
SIFTS range lies between its flanking joined residues' species positions (added after the second re-check, which found
both true in all 104 chains). On CL-2's real tables all of these hold, in all 610 segments and 104 chains (v3_03).

*The status of each row.* For a set residue h, its partner position p in species S, and a RyR1 chain c of an entry E of
species S, the status is decided in this order:
1. **`entry not analysed`:** CL-2 analysed no RyR1 chain of E (refused by R7; excluded by R1a or R1b; path A refused).
   The reason is CL-2's `entity_decision` or the entry's `outcome`, verbatim. None occurs in CL-2's run.
2. **A placed residue of c has species position p:**
   - **`joined`,** if it is joined. `join_path` is its segment's `status`. `agree` means that SIFTS and this project's
     alignment place it there: two methods on the same deposited sequence and the same UniProt release, so not two
     independent checks. `path A only` means that this project's alignment alone places it there, and the row says
     "numbering not checked against SIFTS";
   - **`not determinable`,** if the residue is not joined for one reason only, path A's short departing run (CL-2's
     R11c), since that placement is the one CL-2 does not accept. `not_joined_reason` gives that `kind`. *(Revised after
     the re-check: version 3 called it `not joined`, so the same residue read `not joined` at P16960 2047 and `not
     determinable` at 2092.)*
   - **`not joined`,** otherwise. `not_joined_reason` is the `kind` of every exceptions row for that residue whose
     `joined` is false, in the table's order, joined with `;`. In CL-2's run these are `identity low` and `undeclared
     difference`; eight residues of 6X32 carry both.
3. **No placed residue of c has species position p.** The joined residues that flank p decide. Here a joined residue is
   one C5-S has not withdrawn: a withdrawn join never flanks, as a residue CL-2 does not trust never does. L is the
   last joined residue of c, in author order, whose species position is below p. R is the first joined residue after
   L, or, when L is absent, the first joined residue of c. Either may be absent at a chain's end. M is the set of
   modelled residues strictly between L and R in author order (every one before R if L is absent, every one after L if
   R is absent). Its residues are of two kinds. *Unplaced:* those CL-2 gives no species position (in CL-2's run, `UNK`
   and `neither path`); a join C5-S withdrew; and a residue whose only reason for not being joined is path A's short
   departing run (R11c), whose placement step 2 does not accept. *Placed elsewhere:* every other residue of M, which
   CL-2 places at a position other than p and does not join. Each flank has an offset, d, its species position less its
   author number; the offsets the flanks allow are every integer between the smaller and the larger of d(L) and d(R),
   both included, when both flanks exist, or the one flank's offset when only one does. The rules are applied in this
   order, and the first that applies decides the row and its `not_joined_reason`. Where a rule could name several
   residues, it names the first in author order:
   1. **`not determinable`,** "the chain has no joined residue", if c has none.
   2. **`not modelled`,** if M is empty.
   3. **`not determinable`,** "CL-2 places the residue at author n at species position q", if a placed-elsewhere
      residue n of M could stand at p, that is, if p − n is one of the offsets the flanks allow (as for author 2092 in
      6X32 to 6X36, placed at 2047 under R11c, at p = 2092).
   4. **`not modelled`,** if M holds no unplaced residue.
   5. **`not determinable`,** "the residue at author n is ambiguous on path A (partners q1 q2)", if an unplaced residue
      of M lists p among its exceptions row's `path_a_partners`.
   6. **`modelled, not placed`,** if both flanks exist, no residue of M is placed elsewhere, and M fills the gap between
      the flanks exactly: it holds as many residues as there are species positions between them (the species position
      of R less that of L, less one). The residue that stands at p is then the one at that place in M's author order,
      counted from L, and the row shows it. `not_joined_reason` is its segment `status`, verbatim, then ", placed by
      its order between the flanks".
   7. **`modelled, not placed`,** if p lies in an unplaced stretch of M whose two readings agree: its author numbers,
      and the range SIFTS gives it, as CL-2's exceptions row records it in its `note` ("SIFTS gives a position for N
      (first-last)", N being the note's count). They agree when the stretch is contiguous (its `n_residues` fill its
      author range, `author_first` to `author_last`, and equal N) and the two ranges are equal. The residue at author
      number p is then shown. `not_joined_reason` is its segment `status`, then ", author number and SIFTS agree".
   8. **`not modelled`,** if every unplaced residue of M is placed by rule 6 or 7 at a position other than p.
   9. **`not determinable`** in every other case. `not_joined_reason` names each reading of M's unplaced residues, in
      author order, separated by " | ": a stretch as its kind, its author range and SIFTS's range ("UNK, author
      4320-4345, SIFTS 4254-4279"), or "SIFTS none" where CL-2's note gives no position; an ambiguous residue as its
      kind, its author number and its partners ("neither path, author 240, partners 237 240"), or "partners not listed";
      a withdrawn join as "withdrawn join, author n"; a residue left by R11c as "R11c, author n".

   **What the rules reach in CL-2's run** (the second re-check, from CL-2's tables only): rule 7 places nothing, since
   the stretches whose two ranges agree (9ZO8's, author 4279-4343) are not contiguous (50 residues over 65 numbers),
   and the contiguous ones (5TB0's and 5T9V's) disagree; so rule 8 never fires either, and 9ZO8 reads `not
   determinable` between its flanks. Rule 1 never fires, and rule 6 fires at one gap. Rule 5 reaches 6X35 only: 76 of
   the 88 ambiguous residues list no partners, and rule 9 decides them. So the synthetic chains of check C11-S carry
   most of the test of rules 1 to 9.

   No residue is placed by its author number alone. *(Revised after the re-check of version 3, finding B1′: version 3
   called a position `not modelled` when no residue of M could stand there by the flanks' offsets, and `modelled, not
   placed` when the residue at author number p − d was unplaced. In 5TB0 and 5T9V an UNK stretch's author numbers and
   SIFTS's positions disagree, by up to 66, in all four of their stretches per chain (for example chain B: author
   4320-4345, SIFTS 4254-4279; CL-2's exceptions table), and 88 of the 89 `neither path` residues are ambiguous on
   path A (for example 6X35 chain B, author 240: partners 237 or 240). So that rule placed residues by author number
   and called possibly modelled positions "not modelled". The rules now keep the two conditions the critic of version 2
   proposed, "not modelled" only where no unplaced residue lies between the flanks and "modelled, not placed" only
   where the stretch fills the gap, and depart from that proposal in three ways, each stated: the flanks are joined
   residues, not every placed one; a placed-elsewhere residue that cannot stand at p does not block "not modelled"
   (rules 3 and 4); and an UNK stretch whose author numbers and SIFTS's range agree is placed by them (rule 7, which
   places none in CL-2's run).)*
4. **`withdrawn (C5-S)`:** a joined row whose join C5-S withdraws (*C5-S*, below), alone or under its segment rule. Its
   `join_path` stays. `not_joined_reason` is `coordinates disagree with 9PWO (C5-S)` for a join C5-S tested, and
   `withdrawn with its segment (C5-S's segment rule)` for one it did not; `c5s_check_result` names the record of the
   test or of the segment rule. Withdrawals are decided before step 3, which then reads the flanks without them.

*What would count against this rule's use:* a `joined` row whose residue in the file is neither the partner's nor a
declared difference (C7); a status or reason that C10's second script, deriving every row by its own code, does not
reproduce; any guard of C11 that fails, or a known case of C11-U that the build decides otherwise. The rule takes
offsets only from joined residues, not from every placed one, so that a residue CL-2 itself does not trust (identity
low, R11c, an undeclared difference) never sets an offset. At P16960 2092 in 6X32 to 6X36, for example, flanks taken
from placed residues would include author 2092, which R11c places at 2047, and would call the position `not
modelled`; joined flanks find author 2092 between them and call it `not determinable` (v3_10, chain B).

*Per row it also shows:*
- `author_number` and `structure_residue`: for `joined`, `not joined`, `withdrawn (C5-S)` and `modelled, not placed`
  rows, the residue's `_atom_site.auth_seq_id` and its `label_comp_id`, read from the mmCIF's atom records; empty
  otherwise. So a residue that differs from the partner's is shown even where it is not joined, as at pig 615 in 6X34,
  6X35 and 6X36;
- for a joined residue that differs from the reference: `differs_from_reference` true, and `declaration`, the
  `declared` value of its exceptions row (the mmCIF's `_struct_ref_seq_dif.details`, as CL-2 read it). Under CL-2's R10
  only a declared difference is joined;
- `cl2_segment`, the CL-2 segment that holds the residue, so that the row can be traced to CL-2's segment row;
- **the entry's gate case,** `gate_case`, from CL-3's table: (a) checked against SIFTS; (b) checked by this project's
  alignment alone, not against SIFTS; (c) not checked, or not as expected; (d) no usable reading (CL-2's criteria,
  lines 446–485). **An entry in case (c) or (d) is never counted under closed or open.** Its rows keep their classes,
  marked by the case, and it is counted apart;
- CL-3's measured classes, verbatim from the derived copy of S13's table: by measure A (`class_a`) and by measure B at
  the gate's height (`class_b_fixed`); both, written `A/B`, with the two class lines moved down by 0.5 Å and up by 0.5 Å; the gate's
  radius by A; and the deposited words and the state they imply;
- local model quality: "not assessed", in every row;
- C5-S's verdict where C5-S tested the join, and its check-result record.

*Per residue and species,* the count of entries in each status, with joined entries split by gate case, class
(measure A) and join path (table `cl4_structure_counts`). An entry's status is the first that any of its chains
reaches, in this order: joined on `agree`; joined on `path A only`; `withdrawn (C5-S)`; `not joined`; `modelled, not
placed`; `not determinable`; `not modelled`; `entry not analysed`.

*Size:* the 26 entries have 104 RyR1 chains: mouse 24, rabbit 52, pig 28 (s04). Each chain gets one row for each
residue that has a partner in its species: 31,096 rows for the full set, 416 for the four residues (s13).

**L3. Population variation (gnomAD).**
- **Source:** S2's table, through its records (P0.1). Its dataset is `gnomad_r4`, which the browser's source labels
  "gnomAD v4.1.2" at commit 528b499 (`dataset-metadata/metadata.ts`, line 21). gnomAD's post of 28 September 2026
  calls v4.1.2 "a constraint-only update", and says "All variant frequency data and filtering status are unchanged from
  v4.1.1" (s11). The table holds 7,963 single-base missense variants on ENST00000359596.8 (NM_000540.3), at 3,865
  residues (s02). S2 selected single-base changes only, so missense changes of more than one base are not in its table,
  and L3 does not show them (VCV000133055.4's change at 4665 is one).
- **What is listed:** every row whose `residue` is `N`: exome and genome allele counts and numbers with their filters,
  the joint count and number, `observed_pass` and gnomAD's flags. As counted: 624 rows at 260 of the 299 residues; 39
  residues have none (s02). (The 624 rows and the 624 condition entries of L4 are unrelated counts.)
- **No row is dropped for its filters.** Each filter is shown as gnomAD gives it.
- **Presence, made explicit:** in S2's table an empty filter cell means either "this data type is absent" or "it passes
  with no filter". 6,223 cells are empty because the data type is absent (s02). So CL-4 adds, per data type, whether it
  is present: present where S2's AC cell is not empty. AC and AN are empty together in every row, and a present data
  type with no alleles has AC 0 (1,456 cells) (s17).
- **`observed_pass` is S2's own rule, not a gnomAD field** (`gnomad_ryr1_missense.py`, line 177): true where the exomes
  or the genomes have an allele count above 0 and no filter. It reproduces from the table's own cells in all 7,963 rows
  (s02).
- **Attribution:** gnomAD's terms of use, in the browser's source at commit 528b499 (line 7), ask: "we request that you
  actively acknowledge and give attribution to the gnomAD project, and link back to the relevant page, wherever
  possible" (v3_02). Every gnomAD row carries an attribution.
- **Not re-derived here:** C5-G re-queries a sample, and C9 checks the copy.

**L4. ClinVar's classification.** For each included record at `N`, from the held summaries:
- the variation's `accession_version` and `title`;
- `germline_classification.description`, `review_status` and `last_evaluated`, verbatim;
- **the conditions, one row each:** every entry of `germline_classification.trait_set`, in the held order, with its
  `trait_name` and its Mondo identifier (from `trait_xrefs` with `db_source` MONDO), or an empty Mondo cell where
  ClinVar gives none.
- **As counted, per condition** (s01): the 358 included records carry 624 condition entries; 365 carry a Mondo
  identifier and 259 do not. The 259 are seven drug-response conditions ("desflurane response - Toxicity" and six
  others) in each of 37 records. 356 of the 358 records carry at least one Mondo identifier. The other two
  (VCV000012984.69 and VCV000012972.25, both "drug response") carry only those seven conditions. Over all 379 records
  read: 652 entries, 266 without a Mondo identifier, and 377 records with at least one. No entry carries more than
  one, and no condition name holds `;`, a tab or a newline (v3_02).
- **Attribution:** ClinVar's page asks: "If you distribute or copy data from ClinVar, we ask that you provide
  attribution to ClinVar as a data source in publications and websites" (held 2026-09-30; s15). Every ClinVar row
  carries it.

**Absent, and said so:** conservation (no source chosen); EMHG's list, AlphaMissense's values and des Georges et al.'s
domain division. These three are left out because their terms do not clearly allow this use, and no permission was
sought in the close (the operator's rule, 2026-10-11, 21:41:53 IST); each could be added with the source's permission. A graph table carries no comment lines, so the build's method record
names each absent layer with its reason, in its parameters.

## The confidence columns

Each says what its source says, with the basis named. None is ChannelScope's judgement.

| Layer | Column | Basis |
|---|---|---|
| L1 | `reliability`, `reliability_reasons`, `ambiguous` | M01's and O4's definitions, cited from their method records |
| L1 | `c7_blind_plus1`, `c7_blind_minus1` | The species' sequence: whether a neighbour of the partner is the same amino acid |
| L2 | `status`, `join_path`, `checked_against_sifts`, `not_joined_reason`, `differs_from_reference` | CL-2's rules R10 to R12 and R11c (criteria 2.2), through its tables, by L2's rule |
| L2 | `gate_case` | CL-3's mark, by CL-2's gate rule (criteria 2.2, lines 446–485) |
| L2 | `state_class_a`, `state_class_b`, `state_class_minus_0_5`, `state_class_plus_0_5`, `gate_radius_a` | S13's table, in CL-3's release |
| L2 | `c5s_verdict` | C5-S, as fixed here |
| L2 | `local_model_quality` = "not assessed" | Fixed text |
| L3 | the filters, `flags` | gnomAD's own fields |
| L3 | `observed_pass` | S2's rule (`gnomad_ryr1_missense.py`, line 177) |
| L4 | `review_status`, `last_evaluated` | ClinVar's own fields |

## Provenance

- **Every row names, in its record columns, the record behind each group of its values:** a retrieval, for a value
  read from a raw snapshot; a table record, for a value read from a derived table. One row may name several. An L2 row
  names the mapping table for the partner, CL-2's tables for the join, the mmCIF's retrieval for the residue in the
  file, S13's table for the state, CL-3's gate-case table for the case, and C5-S's check-result record for its
  verdict. The column line says which record column backs which column.
- **A value's date is in its record:** a retrieval's `started_at_time` (UTC) and its `source_release` or the reason it
  has none, or a run's `started_at_time`. The vault's snapshot folders are named by the IST date, so a folder's date
  and a record's UTC date can differ by a day (9PWO's file sits in `2026-10-06/`; its retrieval began at
  2026-10-05T23:03:39.928Z; v3_09). The rows carry no date columns of their own, apart from ClinVar's
  `last_evaluated` and the fixed attribution texts.
- **The build's own records:** one method and one run (two runs under question Q3's option (c)), a table record for each
  output, and a check-result record for each check and planted fault. Each table record's `provenance.used` names its
  direct inputs: the retrievals of the raw snapshots it read and the table records of the derived tables it read. The
  path to a source runs through those records (for example, `cl4_structures` → CL-2's table record → CL-2's run → its
  retrievals → the sources). The method's parameters name the scope, the sample, C5-S's thresholds, question Q1's
  decision, each absent layer with its reason, and the input table records.
- **The validator must report no finding after the records are written** (claim PC-1).

## The outputs and their column line

**Rules for every output table.** Each is a graph table:
- **Path:** `tables/cl4/<commit>/<scope>/<name>.tsv`, where `<commit>` is the first seven characters of the build's
  commit and `<scope>` is `full_set` or `four_residues`. The table record's `name` is `<name>`.
- **Writing:** nothing is written until every check that stops the build has passed and every planted fault is caught,
  or not run where its row allows. A table is never edited. A build repeated at a new commit writes new files.
- **Form:** UTF-8; LF only; the first line is the column line below, in this order; no comment lines (rule V09 reads
  the first line as the header).
- **Cells:** integers in decimal; numbers as their source writes them (S13's radii, two decimals); booleans `true` or
  `false`; strings verbatim from their source. If a source value holds a tab or a newline, the build stops rather than
  alter it. An empty cell means no value, and is allowed only where "Req" is "no".
- **Lists inside a cell** are joined with `;`, with no space, in the order each column states. gnomAD's filters keep
  S2's commas, verbatim.
- **Record columns** hold record identifiers (`cs:<type>.<digest>`), never paths. Several in one cell are joined with
  `;`.
- **Species** are named as CL-2 and S13 name them: `Oryctolagus cuniculus`, `Mus musculus`, `Sus scrofa`.
- **Positions:** a human position indexes `numbering:P21817-1.sv3`, and its column record names that numbering. A
  partner's position indexes the numbering its row's `partner_numbering` names; its column record names none, since
  one column holds positions in three numberings.

**1. `cl4_set`**: one row per set residue. Key: `human_position`.

| Column | Type | Req | Description | Source; record column |
|---|---|---|---|---|
| `human_position` | integer | yes | A residue of P21817-1 named by at least one included record | ClinVar titles (rule 2), checked on P21817 (rule 3); `clinvar_records`, `uniprot_record` |
| `human_residue` | string | yes | P21817-1's amino acid there, one letter | P21817.json; `uniprot_record` |
| `n_records` | integer | yes | Included ClinVar records at this residue | The held summaries; `clinvar_records` |
| `in_c5_sample` | boolean | yes | True if C5 re-derives this residue | This note's sample |
| `clinvar_records` | string | yes | The retrievals of the held search and of the summary batch or batches holding this residue's records | Retrieval records |
| `uniprot_record` | string | yes | The retrieval of P21817.json | `cs:retrieval.VPdG0C8dOG0RdRCDH3o7hwF0-y22z2qQ` |

**2. `cl4_partners`** (L1): one row per set residue and species. Key: `human_position`, `species`.

| Column | Type | Req | Description | Source; record column |
|---|---|---|---|---|
| `human_position` | integer | yes | The set residue | Mapping table `subject_position`; `mapping_table` |
| `species` | string | yes | The partner's species | The mapping table's object numbering |
| `partner_numbering` | string | yes | `numbering:P11716.sv1`, `numbering:E9PZQ0.sv1` or `numbering:P16960.sv2` | The mapping table record's `about` |
| `correspondence` | string | yes | `pair` or `no-correspondence`, as committed | Mapping table; `mapping_table` |
| `partner_position` | integer | no | The partner's position in `partner_numbering`; empty with no correspondence | `object_position`; `mapping_table` |
| `partner_residue` | string | no | The partner's amino acid, one letter | `object_residue`; `mapping_table` |
| `reliability` | string | yes | `standard` or `lowered`, as committed | `reliability`; `mapping_table` |
| `reliability_reasons` | string | no | As committed: `;`-separated reason codes | `reliability_reasons`; `mapping_table` |
| `ambiguous` | boolean | yes | As committed | `ambiguous`; `mapping_table` |
| `mapping_column` | integer | yes | The mapping table's `column` (its key) for this row | `mapping_table` |
| `mapping_table` | string | yes | The mapping table's record | Table record |
| `c7_blind_plus1` | boolean | no | True if the partner's next residue is the same amino acid, so C7 cannot see a slip of +1 in CL-4's reading; empty with no partner | The species' sequence; `partner_numbering_record` |
| `c7_blind_minus1` | boolean | no | The same for the previous residue (a slip of −1) | The same |
| `partner_numbering_record` | string | yes | The numbering record of `partner_numbering` | Numbering record |
| `a6_entries` | string | no | The A6 entries that attach to this residue (rabbit rows only), `;`-separated, by L1's rule | `what/references/a6_stated_correspondences.tsv`; `a6_record` |
| `a6_record` | string | no | A6's check-result record, where `a6_entries` is filled | `cs:check_result.R2g8_EbkE2AkRkXlt0hrjWN5bMxBofK1` |

**3. `cl4_structures`** (L2): one row per set residue and RyR1 chain of each entry of the partner's species. Key:
`human_position`, `entry`, `chain`.

| Column | Type | Req | Description | Source; record column |
|---|---|---|---|---|
| `human_position` | integer | yes | The set residue | `cl4_partners`; `mapping_table` |
| `species` | string | yes | The entry's species, as CL-2's entries table writes it | CL-2's entries table; `numbering_tables` |
| `partner_numbering` | string | yes | As in `cl4_partners` | Mapping table record; `mapping_table` |
| `partner_position` | integer | yes | The partner's position in `partner_numbering` | Mapping table; `mapping_table` |
| `partner_residue` | string | yes | The partner's amino acid, one letter | Mapping table; `mapping_table` |
| `entry` | string | yes | The PDB entry | CL-2's entries table; `numbering_tables` |
| `chain` | string | yes | A RyR1 chain, `auth_asym_id` | CL-2's entries table (chain rows); `numbering_tables` |
| `status` | string | yes | `joined`, `not joined`, `modelled, not placed`, `not determinable`, `not modelled`, `entry not analysed` or `withdrawn (C5-S)`, by L2's rule | CL-2's segments, exceptions and entries tables; `numbering_tables`; for `withdrawn (C5-S)`, `c5s_check_result` too |
| `join_path` | string | no | For `joined` and `withdrawn (C5-S)` rows: `agree` or `path A only`, the CL-2 segment's `status`; empty otherwise | CL-2's segments table; `numbering_tables` |
| `checked_against_sifts` | boolean | no | For the same rows: true for `agree`, false for `path A only` (the segment's `checked_against_sifts`); empty otherwise | CL-2's segments table; `numbering_tables` |
| `not_joined_reason` | string | no | `not joined`: CL-2's `kind`s, `;`-joined, in the exceptions table's order; `modelled, not placed`: CL-2's segment `status`; `not determinable`: the reason of step 2 (R11c) or of rule 1, 3, 5 or 9 of step 3, in the forms step 3 gives; `modelled, not placed`: as above, then ", placed by its order between the flanks" or ", author number and SIFTS agree"; `entry not analysed`: CL-2's decision; `withdrawn (C5-S)`: `coordinates disagree with 9PWO (C5-S)` or `withdrawn with its segment (C5-S's segment rule)`; empty for `joined` and `not modelled` | CL-2's tables; `numbering_tables`; for C5-S, `c5s_check_result` |
| `author_number` | integer | no | The residue's `_atom_site.auth_seq_id`, for `joined`, `not joined`, `withdrawn (C5-S)` and `modelled, not placed` rows, and for a `not determinable` row of step 2 (R11c), whose residue CL-2 places there; empty otherwise | CL-2's segments table and the mmCIF; `numbering_tables`, `structure_record` |
| `structure_residue` | string | no | That residue's `label_comp_id`, three letters, from the atom records; empty where `author_number` is | The mmCIF; `structure_record` |
| `differs_from_reference` | boolean | no | For `joined` rows: true where CL-2's exceptions table lists the residue as a declared difference, false otherwise; empty for other rows | CL-2's exceptions table; `numbering_tables` |
| `declaration` | string | no | Where `differs_from_reference` is true: that exceptions row's `declared` value (`_struct_ref_seq_dif.details`, as CL-2 read it) | CL-2's exceptions table; `numbering_tables` |
| `cl2_segment` | integer | no | CL-2's `segment` holding the residue at `author_number` (with `entry` and `chain`, the key of its CL-2 segment row); empty where `author_number` is | CL-2's segments table; `numbering_tables` |
| `gate_case` | string | yes | The entry's gate case, CL-3's mark: `a`, `b`, `c` or `d` | CL-3's gate-case table; `gate_case_table` |
| `gate_case_reason` | string | no | CL-3's reason for case `c` or `d`; empty for `a` and `b` | CL-3's gate-case table; `gate_case_table` |
| `state_class_a` | string | yes | `closed`, `open` or `indeterminate` by measure A (`class_a` in the derived copy of S13's table; `class_A` in S13's own file) | S13's table; `state_table` |
| `state_class_b` | string | yes | The same by measure B at the gate's height (`class_b_fixed`; S13's own `class_B_fixed`) | S13's table; `state_table` |
| `state_class_minus_0_5` | string | yes | The classes by A and by B, written `A/B`, with both class lines moved down by 0.5 Å (`class_at_minus_0_5`; S13's own `class_at_minus_0.5A`) | S13's table; `state_table` |
| `state_class_plus_0_5` | string | yes | The same, with both lines moved up by 0.5 Å (`class_at_plus_0_5`; S13's own `class_at_plus_0.5A`) | S13's table; `state_table` |
| `gate_radius_a` | number | yes | The pore's radius at the gate by measure A, in Å (the column record's unit), as S13 writes it (`radius_a`; S13's own `radius_A`) | S13's table; `state_table` |
| `deposited_words` | string | yes | The words that name the state, verbatim from S13's table, with their source where S13 names it | S13's table; `state_table` |
| `deposited_implies` | string | yes | The state those words imply, verbatim from S13's table: `closed`, `open`, or `-` where they imply none | S13's table; `state_table` |
| `local_model_quality` | string | yes | Fixed text: `not assessed` | This note |
| `c5s_verdict` | string | no | For a join C5-S tested: `consistent`, `counts against` or `not determinable`; empty otherwise | `c5s_check_result` |
| `c5s_check_result` | string | no | C5-S's check-result record, where `c5s_verdict` is filled; for a join withdrawn with its segment, the record of C5-S's segment rule, `CL4.C5-S-segment` | Check-result record |
| `structure_record` | string | yes | The mmCIF's retrieval record | Retrieval record |
| `numbering_tables` | string | yes | CL-2's table records read for the row: the entries and segments tables always, the exceptions table where a `kind` or a declaration was read | Table records |
| `state_table` | string | yes | S13's table record | Table record |
| `gate_case_table` | string | yes | CL-3's gate-case table record | Table record |
| `mapping_table` | string | yes | The mapping table's record | Table record |

**4. `cl4_structure_counts`**: one row per set residue, species and class measure. Key: `human_position`, `species`,
`class_measure`. An entry is counted once, under the status its chains reach first (L2).

| Column | Type | Req | Description | Source; record column |
|---|---|---|---|---|
| `human_position` | integer | yes | The set residue | `structures_table` |
| `species` | string | yes | The species | `structures_table` |
| `class_measure` | string | yes | `A`; and also `B` if S13's table gives any entry different classes by A and by B | This note |
| `entries` | integer | yes | Entries of this species among the 26 | `structures_table` |
| `entries_joined_closed_agree` | integer | yes | Entries joined on `agree`, gate case `a` or `b`, class `closed` by the measure | `structures_table` |
| `entries_joined_open_agree` | integer | yes | The same, class `open` | `structures_table` |
| `entries_joined_closed_path_a_only` | integer | yes | Entries joined on `path A only` (none on `agree`), gate case `a` or `b`, class `closed` | `structures_table` |
| `entries_joined_open_path_a_only` | integer | yes | The same, class `open` | `structures_table` |
| `entries_joined_indeterminate` | integer | yes | Entries joined either way, gate case `a` or `b`, class `indeterminate` | `structures_table` |
| `entries_joined_gate_case_c_or_d` | integer | yes | Entries joined either way whose gate case is `c` or `d`, whatever their class | `structures_table` |
| `entries_withdrawn_c5s` | integer | yes | Entries whose joins C5-S withdrew in every chain | `structures_table` |
| `entries_not_joined` | integer | yes | Entries whose status is `not joined` | `structures_table` |
| `entries_modelled_not_placed` | integer | yes | Entries whose status is `modelled, not placed` | `structures_table` |
| `entries_not_determinable` | integer | yes | Entries whose status is `not determinable` | `structures_table` |
| `entries_not_modelled` | integer | yes | Entries whose status is `not modelled` | `structures_table` |
| `entries_not_analysed` | integer | yes | Entries CL-2 did not analyse | `structures_table` |
| `structures_table` | string | yes | The record of `cl4_structures` these counts come from | Table record |

`entries` equals the sum of the twelve columns from `entries_joined_closed_agree` to `entries_not_analysed` (C10 checks
this).

**5. `cl4_gnomad`** (L3): one row per gnomAD variant at a set residue. Key: `variant_id`.

| Column | Type | Req | Description | Source; record column |
|---|---|---|---|---|
| `human_position` | integer | yes | S2's `residue` | S2's table; `gnomad_table` |
| `variant_id` | string | yes | gnomAD's identifier: GRCh38 chromosome, position, reference and alternate base | S2; `gnomad_table` |
| `hgvsc` | string | yes | gnomAD's c. name on ENST00000359596.8 | S2; `gnomad_table` |
| `hgvsp` | string | yes | gnomAD's p. name | S2; `gnomad_table` |
| `ref_aa` | string | yes | S2's reference amino acid, one letter | S2; `gnomad_table` |
| `alt_aa` | string | yes | S2's new amino acid, one letter | S2; `gnomad_table` |
| `exome_present` | boolean | yes | True where gnomAD returned exome data (S2's `exome_ac` not empty) | Derived here from S2; `gnomad_table` |
| `exome_ac` | integer | no | Exome allele count | S2; `gnomad_table` |
| `exome_an` | integer | no | Exome allele number | S2; `gnomad_table` |
| `exome_filters` | string | no | gnomAD's exome filters, `,`-separated with no space, verbatim (for example `AC0,AS_VQSR`); empty with `exome_present` true means none | S2; `gnomad_table` |
| `genome_present` | boolean | yes | As `exome_present`, for genomes | Derived here from S2; `gnomad_table` |
| `genome_ac` | integer | no | Genome allele count | S2; `gnomad_table` |
| `genome_an` | integer | no | Genome allele number | S2; `gnomad_table` |
| `genome_filters` | string | no | As `exome_filters`, for genomes | S2; `gnomad_table` |
| `joint_ac` | integer | no | Joint allele count | S2; `gnomad_table` |
| `joint_an` | integer | no | Joint allele number | S2; `gnomad_table` |
| `observed_pass` | boolean | yes | S2's rule: an allele count above 0 with no filter, in the exomes or the genomes | S2; `gnomad_table` |
| `flags` | string | no | gnomAD's variant flags, verbatim | S2; `gnomad_table` |
| `gnomad_dataset` | string | yes | Fixed: `gnomad_r4` | S2's request |
| `gnomad_label` | string | yes | Fixed: `gnomAD v4.1.2`, the browser's label at commit 528b499 | `gnomad_label_record` |
| `gnomad_label_record` | string | yes | The retrieval of the browser's dataset metadata | `cs:retrieval.dMNnflVo8QOV-vkgafiAldeVHTWNVVu8` |
| `gnomad_table` | string | yes | S2's table record (P0.1) | Table record |
| `attribution` | string | yes | Fixed: `gnomAD (Genome Aggregation Database), dataset gnomad_r4, retrieved 2026-10-06` | `attribution_record` |
| `attribution_record` | string | yes | The retrieval of gnomAD's terms of use | `cs:retrieval.grVhkUqc4-d3DYE_XaRfXrbt5goL3uGn` |

**6. `cl4_clinvar`** (L4): one row per included record. Key: `accession_version`.

| Column | Type | Req | Description | Source; record column |
|---|---|---|---|---|
| `human_position` | integer | yes | `N` from the title | `title`; `clinvar_retrieval` |
| `uid` | integer | yes | ClinVar's variation identifier (the summary's `uid`) | `clinvar_retrieval` |
| `accession_version` | string | yes | For example `VCV000012964.91` | `clinvar_retrieval` |
| `title` | string | yes | Verbatim | `clinvar_retrieval` |
| `protein_change` | string | yes | `p.XaaNYaa`, from the title | `clinvar_retrieval` |
| `ref_residue` | string | yes | `Xaa`, one letter | `clinvar_retrieval` |
| `alt_residue` | string | yes | `Yaa`, one letter | `clinvar_retrieval` |
| `description` | string | yes | `germline_classification.description`, verbatim | `clinvar_retrieval` |
| `review_status` | string | yes | Verbatim | `clinvar_retrieval` |
| `last_evaluated` | string | yes | Verbatim, as held (`YYYY/MM/DD 00:00`) | `clinvar_retrieval` |
| `subset` | string | yes | `VUS` or `not VUS`, and `VUS-high (apart)` under question Q1's option (c) | This note's rule |
| `n_conditions` | integer | yes | Entries of `trait_set` | `clinvar_retrieval` |
| `n_conditions_with_mondo` | integer | yes | Of them, entries with a Mondo identifier | `clinvar_retrieval` |
| `clinvar_retrieval` | string | yes | The retrieval of the summary batch holding the record | Retrieval record |
| `attribution` | string | yes | Fixed: `ClinVar (NCBI), retrieved 2026-09-29` | `attribution_record` |
| `attribution_record` | string | yes | The retrieval of ClinVar's maintenance and use page | `cs:retrieval.DVFq5yeaAE238whGncB4dGFJxDrQVVOD` |

**7. `cl4_clinvar_conditions`** (L4): one row per condition entry of an included record. Key: `accession_version`,
`condition_index`.

| Column | Type | Req | Description | Source; record column |
|---|---|---|---|---|
| `human_position` | integer | yes | The record's residue | `cl4_clinvar` |
| `accession_version` | string | yes | The record | `clinvar_retrieval` |
| `condition_index` | integer | yes | The entry's place in the held `trait_set`, from 1 | `clinvar_retrieval` |
| `condition_name` | string | yes | `trait_name`, verbatim | `clinvar_retrieval` |
| `mondo_id` | string | no | `MONDO:` and seven digits, from `trait_xrefs` with `db_source` MONDO; empty where ClinVar gives none | `clinvar_retrieval` |
| `mondo_given` | boolean | yes | True where ClinVar's record gives a Mondo identifier for this condition | `clinvar_retrieval` |
| `clinvar_retrieval` | string | yes | The retrieval of the summary batch | Retrieval record |

**8. `cl4_exclusions`**: one row per excluded record. Key: `accession_version`.

| Column | Type | Req | Description | Source; record column |
|---|---|---|---|---|
| `uid` | integer | yes | ClinVar's variation identifier | `clinvar_retrieval` |
| `accession_version` | string | yes | The record | `clinvar_retrieval` |
| `title` | string | yes | Verbatim | `clinvar_retrieval` |
| `rule` | integer | yes | The first rule it fails: 1, 2 or 3 | This note's rules |
| `reason` | string | yes | What failed, for example `molecular_consequence_list is ["nonsense"]` | `clinvar_retrieval` |
| `clinvar_retrieval` | string | yes | The retrieval of the summary batch | Retrieval record |

**9. `cl4_vus_counts`**: the descriptive counts. Key: `subset`, `unit`, `join_scope`, `species`, `class_measure`.

| Column | Type | Req | Description | Source; record column |
|---|---|---|---|---|
| `subset` | string | yes | `VUS`, and under question Q1's option (c) also `VUS-high (apart)` | `clinvar_table` |
| `unit` | string | yes | `records` or `residues` | This note |
| `join_scope` | string | yes | `agree`, or `agree or path A only` | This note |
| `species` | string | yes | A species, or `any` | This note |
| `class_measure` | string | yes | `A`; and also `B` if S13's table gives any entry different classes by A and by B | This note |
| `n_total` | integer | yes | Records or residues in the subset | `clinvar_table` |
| `n_closed` | integer | yes | Joined, within the scope, in at least one entry of class `closed` and gate case `a` or `b` | `structures_table` |
| `n_open` | integer | yes | The same, class `open` | `structures_table` |
| `n_both` | integer | yes | Both of the above | `structures_table` |
| `n_joined_other_only` | integer | yes | Joined in at least one entry, but in none of class `closed` or `open` with gate case `a` or `b` (only in `indeterminate` entries, or in entries of case `c` or `d`) | `structures_table` |
| `n_not_joined` | integer | yes | Joined in no entry | `structures_table` |
| `clinvar_table` | string | yes | The record of `cl4_clinvar` | Table record |
| `structures_table` | string | yes | The record of `cl4_structures` | Table record |

`n_total` equals `n_closed + n_open − n_both + n_joined_other_only + n_not_joined` (C10 checks this). A withdrawn join is
not a join.

## Residue 614, the article's worked example ([a peer's project])

- **The residue:** human R614 (P21817-1). Partners: rabbit R615 (P11716), mouse R616 (E9PZQ0) and pig R615 (P16960).
  All three are a `pair`, `standard`, not ambiguous, with valine before and serine after (s03, v3_04).
- **ClinVar** (s01, v3_07): two included records. VCV000012964.91 (c.1840C>T, p.Arg614Cys) and VCV000133108.25
  (c.1841G>T, p.Arg614Leu), both "Pathogenic; drug response", reviewed by expert panel, last evaluated 2021/03/24.
  Each has eight condition entries: "Malignant hyperthermia, susceptibility to, 1" (MONDO:0007783) and seven
  drug-response conditions with no Mondo identifier. Neither is in the VUS subset.
- **gnomAD** (s02): four rows, none filtered, all with `observed_pass` true: 19-38457545-C-T (p.Arg614Cys; exome
  101/1,461,868, genome 17/152,186, joint 118/1,614,054), 19-38457545-C-A (p.Arg614Ser), 19-38457546-G-T (p.Arg614Leu)
  and 19-38457546-G-A (p.Arg614His).
- **The structures, from CL-2's real tables by L2's rule** (v3_04, computed after the rule was written). These are the
  104 rows the build is expected to give before C5-S. The build re-derives them, and C5-S may withdraw joins that rest
  on path A alone. The gate cases are this drafter's reading of CL-2's rule; the rows will carry CL-3's mark.

| Species, partner | Entries, four RyR1 chains each | Status | Join path | Residue in the file at the partner's author number | Gate case | Class A |
|---|---|---|---|---|---|---|
| Rabbit R615 | 8X4A, 8X4C, 7M6A, 5TB0, 7T64, 9CGP, 9ZO8 | joined | `agree` | Arg | (a) | closed |
| Rabbit R615 | 8X4B, 7M6L, 5T9V, 7T65, 9CGQ, 9ZOE | joined | `agree` | Arg | (a) | open |
| Mouse R616 | 9NMO, 9NMQ, 8VJJ, 8VJK | joined | `agree` | Arg | (a) | closed |
| Mouse R616 | 9NMN, 9NMP | joined | `agree` | Arg | (a) | open |
| Pig R615 | 9PWO | joined, a declared difference (`variant`) | `agree` | Cys | (a) | open |
| Pig R615 | 6W1N, 6X32 | joined | `path A only`: not checked against SIFTS | Arg | (b) | closed |
| Pig R615 | 6X33 | joined | `path A only` | Arg | (b) | open |
| Pig R615 | 6X34, 6X35 | not joined: `undeclared difference` | — | Cys | (b) | open |
| Pig R615 | 6X36 | not joined: `undeclared difference` | — | Cys | (b) | closed |

- **What the table says.** At residue 614, 23 of the 26 entries join the partner (20 on `agree`, 3 on `path A only`),
  and 3 do not. Those three are the Woll et al. R615C structures, 6X34, 6X35 and 6X36: their files carry Cys at author
  615 and declare no difference for the RyR1 entity, so CL-2's R10 leaves them unjoined. Four of the seven pig
  structures carry R615C (9PWO, 6X34, 6X35 and 6X36), as the article's brief says (S.8); in CL-4's rows three of them
  are not joined, each with its reason, for the figure to show. The expected counts (measure A) are: rabbit, 13
  entries, 7 joined closed and 6 joined open, all on `agree`; mouse, 6 entries, 4 closed and 2 open, on `agree`; pig, 7
  entries, 1 open on `agree` (9PWO), 2 closed and 1 open on `path A only`, and 3 not joined.
- **What goes to [a peer's project], and when:**
  - **By 13:00 IST on 12 October:** the column line of every table, as this note fixes it once committed (these names
    replace any provisional names given earlier), and residue 614's L2 statuses above, marked as read from CL-2's
    tables before the build.
  - **After the build:** residue 614's rows of each table that has them (`cl4_set` 1, `cl4_partners` 3,
    `cl4_structures` 104, `cl4_structure_counts` 3, `cl4_gnomad` 4, `cl4_clinvar` 2, `cl4_clinvar_conditions` 16), each
    file beginning with its table's column line, the rows byte for byte. With them, a manifest naming, for each file,
    its table record, the full table's path and SHA-256, and the line numbers of the rows taken; and one records file
    in JSON Lines, each record exactly as its line in the graph, holding every record the rows name and every record
    reachable from them through provenance, down to the sources, the build's own method, run, table and check-result
    records included. Every record carries `synthetic: false`.
  - **Conditions on publication:** values derived from SIFTS (every `agree` join, and the rows and counts that rest on
    one) carry SIFTS's attribution. SIFTS's terms were read and quoted on 2026-10-11
    (`[a working note, not public]`): its files' rights line leads to EMBL-EBI's terms of use,
    which allow use and redistribution and expect attribution, which SIFTS's page gives as two papers (Dana, Gutmanas
    et al. 2019; Velankar et al. 2013). That reading goes through the critique before publication. ClinVar's and gnomAD's requests for attribution travel in their tables' `attribution` columns. Claim
    PC-4's wording follows questions Q2 and Q3.

## Checks and planted faults, each with what fails it

**Live** means the outcome depends on real data, or on corrupted input, in a way the code does not fix in advance.
**Labelled guard** means it can fail only if the code is not what this note describes. **Report** means it has no pass
or fail. Every planted fault is applied in memory after C1's guard, never to a file, since a changed file would be
refused by C1 and so test nothing. C1-P corrupts the bytes the guard is given. Each planted fault is run against the
check it targets, which must report it; another check reporting it too does not count in its place.

| # | Check or planted fault | Kind | Passes when | Fails when, and then |
|---|---|---|---|---|
| P0 | Exactly what P0.1 to P0.5 ask: S2's table recorded, its 7,963 data rows byte for byte under S2's 37 columns, `variant_id` distinct; CL-2's three tables recorded, each copy's data rows byte for byte those of its curation file at `c4e8b66` under the same column line, with the keys stated in P0.2; CL-2's run usable, read from those files' header lines; S2's records written from the committed spec; S13's table recorded as CL-3's derived copy; CL-3's gate cases recorded, with the builder's own method, run and table records, one row per entry, its case one letter `a` to `d`, with a reason for `c` and `d`; the recording tool reviewed by a fresh critic and its findings applied before it wrote any of these records; the validator reporting no finding | precondition | All hold | Any does not: the build does not start (Q3) |
| P0-P | One cell of one data row of the `tables/` copy of CL-2's segments table changed in memory | live, on corrupted input | P0's comparison reports the row | It does not |
| C1 | Every input matches its record: the SHA-256 and size of the ClinVar, UniProt, mmCIF and SIFTS snapshots and of gnomAD's label, post and terms of use against their retrievals; of the mapping, CL-2, CL-3 and S2 tables against their table records; the A6 table against its blob at the build's commit | labelled guard | All match | Any differs: the build refuses that input and stops |
| C1-P | One byte of 9PWO's mmCIF changed in memory, in the bytes the guard compares | live, on corrupted input | Refused | Read |
| C2 | The set reproduces from the whole held input, in either build | live | 379 read; 358 included at 299 residues; 47 with more than one record; 21 excluded, all by rule 1, in the categories above; the VUS subset as Q1 decides (222 records at 200 residues under (a) or (c), with the VUS-high record apart under (c); 223 at 201 under (b)) | Any count differs: the build stops until the difference is explained |
| C2-P | VCV000012964.91's consequence list changed in memory to `["nonsense"]` | live, on corrupted input | C2 reports 357 included and 22 excluded | C2 passes |
| C3 | Rule 3, applied | labelled guard (it excludes nothing on the held input) | — | — |
| C3-P | VCV000012964.91's title changed in memory from p.Arg614Cys to p.Gly614Cys | live, on corrupted input | Excluded, by rule 3 | Included |
| C4 | Every record cell names a record of the stated type, in the graph or among this run's pending records (its method, run, table and check-result records, built before anything is written); no value cell has an empty record cell. After writing, the validator resolves every reference (V07) | live | All resolve | Any does not: stop |
| C4-P | In memory: (i) residue 163's first ClinVar row's `clinvar_retrieval` set to `cs:retrieval.` followed by 32 `A`, a well-formed identifier of no record; (ii) a gnomAD row added at residue 163 with an empty `gnomad_table` | live, on corrupted input | Both caught by C4 | Either passes |
| C5-C | ClinVar re-derived, per included record at a sampled residue, against L4's rows (*C5-C*, below) | live | At the same version, the five fields equal L4's row; at a higher version, the title equals it. The number of records at a higher version is reported | At the same version, any field differs; a lower version; no record returned; a different title at a higher version. Then no output is used until the cause is found: a fault in the build is fixed and the build repeated; a difference at the source goes to the operator, since these criteria give no rule for it |
| C5-C-P | In the build's L4 rows, before C5-C compares: one character appended to the `description` of the first sampled record (by `uid`, ascending) that came back at the same version | live, on corrupted input | Caught by C5-C | Passed. Not run if no sampled record came back at the same version, and its record says so |
| C5-G | gnomAD re-derived, per variant at a sampled residue, against L3's rows (*C5-G*, below) | live | No later release is recorded, or the later release's post says that variant data are unchanged, and every compared value equals L3's row | Any value differs, unless a later release's post says that variant data changed (then each difference is reported as that change, with both values, and L3 keeps S2's values under their label). Then no output is used until the cause is found, as for C5-C |
| C5-G-P | In the build's L3 rows: `exome_ac` increased by 1 for the first sampled variant (by `variant_id`, ascending) whose exome data are present | live, on corrupted input | Caught by C5-G | Passed. Not run if no sampled variant has exome data, or if a later release with changed variant data was recorded |
| C5-S | The joins that rest on path A alone, at sampled residues, tested by coordinates against 9PWO (*C5-S*, below) | live | No tested join counts against | Any join counts against: it, and its segment under the segment rule, is withdrawn from every count and shown as `withdrawn (C5-S)`. The build goes on |
| C5-S-P | Every label of 6X32 chain B moved +1 in memory, and the join at P16960 950 tested; 940 if 950 is not joined (both are, v3_04) | live, on corrupted input | "counts against", offset −1 | Any other outcome |
| C5-S-W-P | After C5-S has run, in memory: every sampled join of the segment of 6X32 chain B that holds P16960 950 given "counts against" | live, on corrupted input | Every joined row of that segment in 6X32 chain B becomes `withdrawn (C5-S)`, the counts move with them, and C10's recount equals the build's | Any row of that segment stays joined, or C10 differs |
| C5-N | The joins where CL-2's paths agree, at sampled residues, re-derived by a second script that does not import CL-2's code: SIFTS's UniProt position for the chain and author number equals the row's partner position, and the mmCIF has a CA there | live; a second code path on the same inputs, not a second source | Every sampled join equal | Any differs: no output is used until the cause is found |
| C5-N-P | In the build's copy of CL-2's segments table: the segment holding the first sampled `agree` join (by entry, chain and residue) given `offset_s`, `offset_a`, `species_first` and `species_last` one higher | live, on corrupted input | Caught by C5-N | Passed |
| C6-P | A join moved by one: human 163's joins to rabbit 164 in 7M6A chain A, mouse 165 in 9NMO chain A and pig 164 in 9PWO chain A, each moved in memory to the partner's next position (165, 166 and 165: valine in all three) | live, on corrupted input | All three caught by C7 | Any passes |
| C7 | Every joined row's identity: the mmCIF's residue at `author_number` is the partner's residue, or a declared difference listed as such | labelled guard: CL-2 joins only identical or declared residues, so C7 can fail only if CL-4's reading of CL-2's tables is wrong | Holds | An unlisted difference: stop |
| C7-R | C7's blind set: the joined rows where C7 could not see a slip of one position (below) | report | — | — |
| C8 | Species: a partner is joined only to entries of its own species, as CL-2's entries table names them (`species`, which R7 compared with the source organism; K2: R7 refused no entry) | labelled guard | Holds | Any cross-species join: stop |
| C8-P | Human 163's pig partner (P16960 164) joined in memory to 7M6A chain A (rabbit) | live, on corrupted input | Caught by C8 | Passed |
| C9 | gnomAD's copy: each L3 row's AC, AN, filters, presence and flags equal S2's row with the same `variant_id`; per residue, the rows with any filter equal S2's; `observed_pass` equals S2's rule recomputed from the cells | labelled guard | Holds | Not: stop |
| C9-P | In the build's L3 rows: full set, residue 35's row 19-38440803-G-T given an empty exome filter (S2: `AC0`); four residues, residue 614's row 19-38457545-C-T given the exome filter `AC0` (S2: none) | live, on corrupted input | Caught by C9 | Passed |
| C10 | The structure counts and the VUS counts recounted by a second script that does not import the build's code. The build hands it, in memory, the inputs it used, any planted change included: the ClinVar rows, the mapping tables, CL-2's, CL-3's and S2's tables, CL-3's marks, C5-S's verdict for each tested join, and the mmCIF residue types. It applies C5-S's segment rule itself, from those verdicts; derives every row's status and `not_joined_reason` by its own code and compares each with the build's row; derives each entry's gate case from CL-2's entries and segments tables by CL-2's rule and compares it with CL-3's mark; and recounts both count tables and checks their sums | live; a second code path on the same inputs, not a second source | Every row's status and reason equal; every mark equals the derivation; the counts equal; the sums hold | Any difference: stop until explained |
| C10-P | In memory: (i) one cell of the build's VUS counts increased by 1; (ii) the row of 6X34 chain B at human 614 (`not joined`, an undeclared difference, in both builds) given `joined` before counting | live, on corrupted input | Both caught by C10 | Either passed |
| C11-U | The status rule at two positions the re-check of version 3 read, before this note's commit: 5TB0 chain B at P11716 4260, between joined E4253 and F4540, where the 26 UNK residues' author numbers (4320-4345) and SIFTS's range (4254-4279) disagree; and 6X35 chain B at P16960 237, an ambiguous `neither path` residue's other partner (author 240: 237 or 240). Each is computed by the build's status function and by C10's, whether or not it is a set residue's partner | live, on real data | Both functions give `not determinable` at both, by rule 9 at 4260 and rule 5 at 237, with the same reason | Anything else: stop |
| C11-U-P | The build's status function replaced in memory by version 3's first rule (a residue placed at author number p − d when both flanks share an offset) | live, on corrupted input | C11-U reports both positions | It does not |
| C11-S | Synthetic chains with known answers, committed with the build's code before the build: one for each of rules 1 to 9 of step 3, one for step 2's R11c, one with a withdrawn join inside M, and one with flank offsets falling (d(L) > d(R)). Each gives a status, the deciding rule and the reason. Both the build's status function and C10's are run on each | live, on constructed input | Both give every expected answer exactly | Any differs: stop |
| C10-G-P | In the build's copy of CL-3's gate cases: 7M6L given case `c` | live, on corrupted input | 7M6L leaves the closed and open columns and enters `entries_joined_gate_case_c_or_d` wherever it is joined, and C10 reports that its mark differs from CL-2's rule | Either does not happen |
| C10-W-P | In memory, after C5-S: "counts against" for all four chains of 6X33 at human 614, or, if 614 is not sampled, at the first sampled residue joined in all four | live, on corrupted input | 6X33 moves to `entries_withdrawn_c5s` at that residue, and C10's recount equals the build's | The count does not move, or C10 differs |
| C11 | L2's reading of CL-2's tables: the guards under *L2* | labelled guard | All hold | Any fails: stop |
| C11-P | In the build's copy of CL-2's exceptions table: the row of 6X34 chain B, author 615 (`undeclared difference`) given `joined` true | live, on corrupted input | Caught by C11: that segment's joined residues exceed its `joined_residues` | Passed |

**If a planted fault is missed,** no output of the build is used. The code is fixed and the build repeated. The criteria
stay as committed unless the operator decides otherwise. C5-S's withdrawals, C5-C's records at a higher version and
C7-R are reported, not stops.

**The records.** Each check and each planted fault is a check-result record, with `check` written `CL4.<label>` (the
schema's pattern), `criterion.document` this file, `pre_registered_in` its commit, and `fails_if` quoted from the
table above. A check with one planted fault holds it as its `control` (detected or missed). A check with more holds the
first, and each further fault is a record of its own, with `outcome` "pass" if it was caught and "fail" if missed, and
`control` "not-run", "none: this record reports a planted fault itself", as CL-3's notes do. A guard with no planted
fault holds `control` "not-run", "none: a labelled guard". `observed` holds the values. C5-S's segment rule, wherever
it withdraws a join, has a check-result record of its own, `CL4.C5-S-segment`, naming each segment and the verdicts
that moved it; each join it withdraws names that record in `c5s_check_result`.

## C5: the re-derivation, in detail

**The sample.**
- **Full set: the departure's residues.** CL-2's run reports one departure, in 6W1N and 6X32 to 6X35, across author
  2736–2939 (P16960 2737–2940), and no other departing segment in any entry (v3_01). Its set residues are the nine whose
  pig partner lies there: human 2764, 2776, 2787, 2840, 2843, 2867, 2880, 2885 and 2910 (s03). Seven are modelled in
  the departing entries. Human 2840 and 2843 have their partners at P16960 2841 and 2844, which no pig structure
  models: the six Woll et al. entries leave out author 2831–2854, and 9PWO leaves out 2832–2851 (s04).
- **Plus 30 others, drawn** (s10): `random.Random(20261011).sample(others, 30)`, where `others` is the list of the
  other 290 set residues, as integers in ascending order, in CPython 3.12.14 (the project's environment). In ascending
  order: 33, 64, 71, 156, 177, 178, 248, 1075, 1342, 1583, 2130, 2224, 2321, 2346, 2363, 2435, 2458, 3118, 3217, 3218,
  3253, 3290, 3402, 3985, 4283, 4638, 4664, 4725, 4733, 4856. Two of them, 64 and 248, are in C7's blind set in all
  three species.
- **Plus the four worked residues** (human 163, 522, 614 and 2060), if question Q2 is answered as recommended. None of
  them is a departure residue or among the 30 (v3_07).
- **Workload** (v3_07; two ClinVar calls per record, one gnomAD call per variant, three calls for the release check):
  the nine and the thirty, 39 residues, 45 included ClinVar records, 90 gnomAD rows, about 183 logged calls; with the
  four added, 43 residues, 53 records, 97 rows, about 206 calls; the four alone, 8 records, 7 rows, about 26 calls.
- **Four-residue build:** all four, in full.

**The fetches.** Every re-query runs from a fetch plan committed before it runs, by `channelscope fetch`, which writes
one retrieval record per call: `what/evidence_graph/curation/fetch_close_cl4_c5_clinvar.yaml` and
`fetch_close_cl4_c5_gnomad.yaml`, storing under `raw/clinvar/<fetch date>/` and `raw/gnomad/<fetch date>/`. NCBI calls
carry `tool=channelscope` and no e-mail address, as the vault's earlier ClinVar plans do. Nothing is fetched before
these criteria and the plans are committed.

**C5-C, ClinVar.** For each included record at a sampled residue:
- **The calls:** its summary (`esummary.fcgi?db=clinvar&id=<uid>&retmode=json`; the plan reads
  `result.<uid>.accession_version` as the release), then its full record
  (`efetch.fcgi?db=clinvar&rettype=vcv&is_variationid&id=<uid>`, release read from the summary call), as
  `fetch_exon_map_v0_4_clinvar_indels.yaml` did.
- **The normalisation, fixed now:** L4's `last_evaluated` (`YYYY/MM/DD 00:00`) is read as `YYYY-MM-DD` and compared with
  the full record's `GermlineClassification/@DateLastEvaluated`. The full record's conditions are the preferred names
  and MONDO cross-references of the trait sets of its germline classification whose
  `ContributesToAggregateClassification` is `true`, compared with L4's conditions as a set of (name, Mondo identifiers).
  The title (the full record's `VariationName`), description and review status are compared verbatim.
- **Same version** (the full record's `Accession` and `Version` equal L4's `accession_version`): the title,
  description, review status, date and conditions must equal L4's values exactly. **Any difference fails.**
- **Higher version:** the title must still equal L4's (the variation is the same). The classification and conditions
  are reported as an update, with both versions, and do not fail. L4 keeps the held values, dated 29 September 2026.
  The check record states how many sampled records came back at a higher version, so a reader sees how much of C5-C was
  a full comparison.
- **Also fails:** a lower version, no record returned, or a different title at a higher version.
- **Tried before this commit** (s09): on the eight records held both as a summary of 29 September and as a summary and
  full record of 2 October (seven outside the set; VCV000133055.4 at residue 4665; all at the same version on both
  days), the five fields agree in 40 of 40 comparisons under this normalisation. Without the trait-set filter, the
  conditions differ in seven of the eight, since the full record lists every submitter's conditions.

**C5-G, gnomAD.**
- **First, the release check,** logged in the plan before any variant is asked for: the browser's head commit on main
  (GitHub's API), its `dataset-metadata/metadata.ts` at that commit, and gnomAD's news page, as S2's plans did. **A later
  release is recorded** if the label of `gnomad_r4` is no longer "gnomAD v4.1.2", or the news page lists a release after
  v4.1.2. Its post is read for whether it says that variant frequency data or filtering status changed.
- **Then, per gnomAD variant at a sampled residue** (every S2 row there): the API's `variant(variantId, dataset:
  gnomad_r4)` query, asking `exome`, `genome` and `joint` for `ac`, `an` and `filters`. The held schema introspection
  (`raw/gnomad/2026-10-06/api_schema_introspection.json`) declares each of these fields. Compared with L3's row:
  whether each data type is present; AC and AN as integers; exome and genome filters as sets of strings. S2 holds no
  joint filters, so the joint data are compared on AC and AN alone.
- **A difference is excused only by a later release whose post says that variant data changed.** Then each difference is
  reported as that change, with both values, and L3 keeps S2's values under their label. A later release whose post says
  variant data are unchanged, as v4.1.2's says of v4.1.1, excuses nothing. With no later release recorded, any
  difference fails.
- **The per-variant query is not the gene query S2 used.** A difference that comes from the query alone still fails,
  and is explained before L3 is used.

**C5-S, the joins that rest on path A alone, by coordinates.**
- **Where it matters:** path A stands alone in every join to the six Woll et al. 2021 entries, since SIFTS maps none of
  their RyR1 entities (CL-2's run: `path_s` "none: chain not mapped to UniProt" in all 24 chains; PDBe's answers logged
  on 2026-10-11, s19). Re-reading SIFTS has nothing to read there. The independent input is a second structure: 9PWO, a
  pig structure that SIFTS maps to P16960, whose author numbers equal P16960's at 4,102 of the 4,103 modelled residues
  of each chain (the other is its declared R615C; s04), and which CL-2's run found "equal" on both paths.
- **The test, for one join:** a Woll entry E, chain c, a sampled residue whose pig partner p is joined there.
  1. **Labels:** each joined residue of E chain c is labelled with its CL-2 species position; so is each joined residue
     of 9PWO chain A.
  2. **A fit that does not use the labels under test.** Three fits, with r = 40, 60 and 80. Each takes E chain c's
     labelled residues from p − r to p + r (at least 20) against 9PWO's labelled p − r − 30 to p + r + 30 (at least
     20). Each starts from a least-squares fit of CA atoms on anchors: joined residues of E chain c outside the region
     and outside every departing segment of that chain, whose label and residue type equal a 9PWO residue's, and whose
     9PWO CA lies within 20 Å of a CA of 9PWO's region; at least 10 of them. Then iterative closest point on CA atoms
     alone, with cut-offs of 12, 9, 6, 4 and 3 Å, at most 50 rounds each, a cut-off's rounds ending when fewer than 10
     pairs remain or when the fit stops changing (every element of the rotation within 1e-6 and of the translation
     within 1e-4 Å of the round before). No label inside the region is used. Each residue's CA is the first one gemmi
     finds, whatever its alternate location; residues with an insertion code are skipped.
  3. **The window:** the residues of E chain c labelled p − 15 to p + 15 whose nearest 9PWO CA of the region, after the
     fit, lies closer than 2.0 Å. Each gives an offset: the 9PWO label of that CA less its own label.
  4. **Each fit's verdict:** "consistent" if at least 10 residues give an offset, the commonest offset is 0 and no
     other is as common, and at least 75% are 0; "counts against" if at least 10 give one and the commonest offset is
     not 0 and no other is as common; otherwise "not determinable". **A tie for the commonest offset is "not
     determinable".**
  5. **The join's outcome:** the fits that decide (those that say "consistent" or "counts against") must number at
     least two and agree, in verdict and, for "counts against", in offset. The join takes their verdict. Otherwise it is
     "not determinable".
- **The implementation:** the drafter's `kabsch`, `icp`, `Pair.fit`, `Pair.decide` and `rule_b` (script s21), with
  three changes fixed in this version before they were run: labels and anchors from CL-2's joined residues only;
  departing segments left out of the anchors by residue, not by label range; a tie made "not determinable". Script v3_05
  runs them as fixed. They are committed as the build's C5-S code before the build.
- **What counts against the join:** "counts against". Such a join is withdrawn: shown as `withdrawn (C5-S)`, with its
  `c5s_verdict`, and left out of every count. **The segment rule:** if at least two sampled joins of one CL-2 segment in
  one chain count against, and they are at least half of that segment's sampled joins there, every join of that segment
  in that chain is withdrawn the same way (planted fault C5-S-W-P). A "not determinable" join keeps its place and its
  "numbering not checked against SIFTS" mark, and is listed. It is not a pass.
- **The rule is asymmetric.** "Consistent" needs 75% of the window at offset 0; "counts against" needs only a commonest
  offset, not 0 and not tied. So it errs towards withdrawing correct joins, losing coverage: the three withdrawals of
  correct joins below were pluralities of 0.56 to 0.69 of their windows (v3_08). A window whose commonest offset is
  0 but under 75% of it, or whose commonest offset is tied, is "not determinable", and such a join keeps its place
  unverified, with its mark; a window whose commonest offset is not 0, untied, counts against however narrow its
  plurality ({−1: 8, 0: 7}, for example). *(Version 3 said the rule never keeps
  a wrong join on a split window; the re-check showed windows {0: 7, −1: 7}, {0: 8, −1: 7} and {0: 9, −1: 6} each keep
  the join, by version 3's own code.)*
- **What a "counts against" can mean:** a wrong join; a local difference between the two models' coordinates, one
  placing residues a position along from the other; or a fit locked onto a repeating structure. The test does not tell
  these apart, and the build does not choose among them.
- **Why this form, from what was tried on the pig structures before this commit:**
  - **The nearest CA, residue by residue, is not reliable.** After one fit on a control domain (P16960 842 to 1069,
    UniProt's repeats 1 and 2), 5 to 10% of correctly labelled residues have their nearest 9PWO CA at another number
    (s06). Hence a window and a majority.
  - **A fit made on the labels under test absorbs a shift.** With every label moved by one, 28 to 33% of residues still
    lie within 2.0 Å of their labelled partner after a fit on those labels (±10 residues; s06). Hence the label-free
    fit. A superposition on 9PWO with a stated distance fails in this way if it is made on the labels it tests.
  - **One fit region, on 3,185 control positions** (s08): correct labels gave 3,042 "consistent", 125 "not
    determinable" and 18 "counts against" (0.6%). Since C5-S tests several hundred joins, a spurious rate of 0.6% would
    withdraw some by chance. Three fits were added for that reason. They guard against one fit that goes astray, not
    against a difference between the two models: at the three false withdrawals under the fixed rule, the window was
    the same at r = 40, 60 and 80 (v3_08).
- **The rule as fixed, on control positions** (v3_05): 1,588 positions, every tenth joined residue of chain B of 6W1N
  and 6X32 to 6X35 outside P16960 2700–2960 whose label is a joined residue of 9PWO chain A of the same type (315 to 320
  per entry). Correct labels gave 1,528 "consistent", 57 "not determinable" and 3 "counts against" (0.19%): 6W1N at
  2530 (offset +1) and 3418 (+4), and 6X33 at 2528 (−1). Labels moved +1 gave 1,532 "counts against", 56 "not
  determinable" and none "consistent"; labels moved −1 gave 1,537, 51 and none. Around P16960 2524–2530 the Woll et al.
  models and 9PWO seem to place residues one position apart (s16, s21, v3_05); which model, if either, is out of
  register is not settled here. In 6X32 that stretch lies inside CL-2's identity-low run (2490–2534), which is not
  joined, so no control position falls there. These cases show the rate at which C5-S withdraws a join whose numbering
  is right by sequence.
- **The planted fault's position** (v3_04, v3_05): P16960 950 is joined in 6X32 chain B (`path A only`) and in 9PWO
  chain A (`agree`). With correct labels all three fits say "consistent"; with labels moved +1 all three say "counts
  against" with offset −1; with labels moved −1, "counts against" with offset +1. The fallback, P16960 940, behaves
  the same.
- **Inside the departure, label-free** (s07, s16): after a fit on UniProt's repeats 5 and 6 (P16960 2727 to 2960), the
  five departing entries' traces lie within 2.0 Å of 9PWO's at 175 to 178 of their 180 residues (median distance 0.53
  to 0.73 Å; s07). In the test's own fits, window by window (the seven modelled residues, five entries, three fits;
  s16), 9 of the 105 fits put fewer than 10 of the window's residues within 2.0 Å, each in a different window (around
  human 2764, 2776, 2787 and 2880, in 6W1N, 6X32 and 6X33). Every window keeps at least two fits that put 10 or more
  there, the minimum the rule needs. Whether those fits decide, and which way, is not known. s16 used version 2's
  anchors (author numbers, unjoined residues admitted), and it was not re-run under version 3's, so that the
  departure's labels stay unread.
- **What it shows:** that in the 31-residue window around p, most of the residues path A labels there sit where 9PWO's
  residues of the same labels sit. It is a statement about the window's register, not about residue p alone. The join
  then agrees with a structure whose numbering SIFTS and its own sequence check.
- **What it cannot show:**
  - a fault confined to fewer residues than the window's majority detects;
  - that 9PWO's coordinates are independent of the Woll et al. models. 9PWO was refined from 9OL4, its record's initial
    model (`_pdbx_initial_refinement_model`; s05), and whether 9OL4 descends from those models is not known from the
    held files. The traces coincide more closely in repeats 5 and 6 (median 0.53 to 0.73 Å) than in repeats 1 and 2
    (1.10 to 1.46 Å; s06, s07), which shared descent would explain but does not show. If they share descent, the test
    checks path A's labels against 9PWO's, not the models against their maps;
  - whether either model fits its map: local model quality stays "not assessed";
  - 9PWO's own joins: no other pig structure has a SIFTS-checked numbering. 9PWO's check is CL-2's two paths. Its chains
    A and G gave identical results in every trial (s06), so a second 9PWO chain is not a second comparator;
  - the joins where CL-2's two paths agree (every rabbit and mouse entry, and 9PWO). C5 adds no independent input for
    them: their checks are CL-2's two methods on shared inputs, C5-N's second code path, and C7, which tests CL-4's
    reading. Testing them by coordinates would need same-species comparators whose feasibility was not judged before
    this commit.

**C5-N, the joins where CL-2's paths agree.** For every `agree` row at a sampled residue, a second script that does not
import CL-2's code reads the entry's SIFTS file and mmCIF: SIFTS's UniProt position for the chain and the row's author
number must equal the row's partner position, on the species' accession, and the mmCIF must have a CA there. It is a
second code path on CL-2's inputs, not a second source.

## C7's blind set, and C6-P's residue

C7 compares residue types. CL-2 joins only residues identical to the reference or declared, so C7 tests CL-4's reading
of CL-2's tables, not CL-2's joins. It cannot see a slip of one position in that reading where the partner's neighbour
on that side is the same amino acid. Computed from the held reference sequences and the mapping tables (s03):
- **A slip of +1** (the partner's next residue the same): rabbit 23, mouse 21 and pig 21 of the 299 residues. Mouse and
  pig: human 64, 166, 209, 248, 708, 1393, 1773, 2102, 2283, 2669, 2963, 3284, 3292, 3418, 3583, 3806, 4050, 4587,
  4808, 4847 and 4880. Rabbit: these, and 207 and 2060.
- **A slip of −1** (the previous residue the same): 13 in each species, the same 13 residues: 1577, 1592, 1678, 1711,
  2348, 2354, 2428, 3584, 3916, 4650, 4849, 4897 and 4938.
- No residue is blind both ways.

Each row of `cl4_partners` carries both flags. C7-R lists every joined row C7 could not test this way. For CL-2's joins
themselves, the checks are CL-2's two paths (`agree` joins), path A under CL-2's identity floor (`path A only` joins),
C5-N at sampled residues (a second code path) and C5-S at sampled residues.

**C6-P's residue, fixed now:** human 163 (R). Its partners, rabbit 164, mouse 165 and pig 164, each stand between two
valines (V-R-V), `standard` and not ambiguous in all three (s03). The planted joins are 7M6A chain A, 9NMO chain A and
9PWO chain A. All three are joined in CL-2's tables, on `agree`, and so is the next position in each, valine (v3_04).
No fallback is needed: P0.2 fixes CL-2's tables to run `e888359`'s.

## The descriptive counts for the VUS

- **What is counted:** for the VUS subset as Q1 decides, how many are joined, through L1 and L2, in at least one closed
  entry, in at least one open entry, in both, only in other entries, and in none. A closed or open entry here is one of
  that class whose gate case is (a) or (b); entries of case (c) or (d), and indeterminate ones, count only under "only in
  other entries". By species and over all three; in two units, records and residues (the 222 records sit at 200
  residues); for join path `agree` alone, and for `agree or path A only`. A withdrawn join is not a join.
- **The class is CL-3's measure A.** In S13's table, measures A and B give the same class for all 26 entries: 14 closed
  (mouse 4, rabbit 7, pig 3) and 12 open (mouse 2, rabbit 6, pig 4) (s12). If CL-3's table shows any difference, the
  counts are given for each measure, keyed by `class_measure`.
- **Reported as counts, with no inference:** never "most VUS can be assessed structurally", never a rate set against
  other classes.
- **Four residues:** the counts cover the one VUS record among them (VCV000635269.31, p.Arg163His; s13, v3_07),
  labelled as such, and say nothing about the set.

## Size: the full set or the four residues

Which build runs was put to the operator as question Q2, planned for 10:00 IST on 12 October and answered at 23:28:41
IST on 11 October: the full set, with the four worked residues added to C5's sample (option (c)). Both use these criteria, the same
rules and the same column line. They differ in the residues composed and in C5's sample, and the table paths say which
(`.../full_set/` or `.../four_residues/`). A later build writes new tables. Nothing is edited.

| | Full set | Four residues (human 163, 522, 614, 2060) |
|---|---|---|
| Residues | 299 | 4 |
| Rows: partners; structures; gnomAD; ClinVar; conditions; exclusions | 897; 31,096; 624; 358; 624; 21 | 12; 416; 7; 8; 43; 21 (s13) |
| C2 | On the whole input | The same: the set's rule is checked on the whole input |
| C5's sample | The departure's nine and the 30 others, with the four worked residues if Q2 is answered as recommended | All four, in full |
| C5-S | Includes the seven modelled departure residues | No residue in the departure: its joins are not re-derived until a full build. It tests the Woll et al. joins at human 163, 522 and 614 (at most 60); human 2060's pig partner, P16960 2061, is modelled in none of the seven pig entries (s20) |
| C6-P | 163 | 163 |
| C9-P | A filter dropped (residue 35's row) | A filter added (residue 614's row) |
| C10-W-P | 6X33 at 614 if sampled, else the first sampled residue joined in all four chains | 6X33 at 614 |
| VUS counts | As Q1 decides (222 records at 200 residues under (a) or (c)) | The one VUS record, labelled |
| C7-R | As listed above | 2060 is blind to a +1 slip in rabbit; reported |

Every other check is the same in both.

## What the composition may and may not say

| May | May not |
|---|---|
| The layers side by side, each with its source, record and date | A verdict, an effect or a direction for any residue or variant |
| "Not assessed" for local model quality | That a residue is buried, exposed or at an interface, unless measured by a method with its own criteria |
| A row `modelled, not placed` or `not determinable`, with CL-2's words | That such a residue is joined, or that the structure does not model it |
| Gate case (b) as "gate numbering checked by this project's alignment alone, not against SIFTS" | That a case (b) entry's numbering was compared with SIFTS |
| Entries of gate case (c) or (d), named and counted apart | Such an entry counted under closed or open |
| "Coordinates consistent with 9PWO" for a join C5-S found consistent | That such a join is right; or that a "not determinable" join was checked |
| The descriptive counts | Any inference from the counts |
| ClinVar's classification and conditions, quoted | Any classification of this project's |

## The build's record

- **Code:** `how/runtime/channelscope/cl4/compose.py`, its checks, the second script for C10, the C5 scripts (C5-S's from
  s21 with version 3's three changes; C5-N's) and the two fetch plans, all committed before the build. Their SHA-256 go
  in the method record (its implementation's code digest) and the run record, not in the tables.
- **Libraries:** CPython 3.12.14; gemmi 0.7.5 for mmCIF; numpy and Biopython as pinned in `uv.lock`.
- **Outputs,** written by the build and never edited: the nine tables under `tables/cl4/<commit>/<scope>/`, each with its
  table record; one method and one run record (two runs under Q3's option (c)); one check-result record for each check
  and planted fault. The method's parameters name the scope, the sample, C5-S's thresholds, Q1's decision, the input
  table records and each absent layer with its reason. The validator reports no finding.
- **For the article:** residue 614's rows and records, as above.

## Questions for the operator

Each says what it decides, what each option costs, what waiting delays, and a recommendation. None asks the operator to
judge a variant.

**Q1. The "VUS-high" record** (needed before the build; its answer is recorded here, with its time, in a commit
before the build).
- **What it decides.** 222 of the included records carry a classification that begins "Uncertain significance" (a
  variant of uncertain significance, a VUS). The composition counts them, with no inference, to show how many sit on
  residues that structures model. One more included record, VCV000133070.12 (p.Leu4824Pro, residue 4824), carries a
  different label, "VUS-high", and the held record does not say what it means. The question is whether that record is
  counted with the 222.
- **The options:**
  - **(a) Keep the rule.** 222 records at 200 residues. "VUS-high" is shown, as written, in its own row, outside the
    counts. *Cost:* a reader may see a record whose label names a VUS missing from the VUS counts, and take it for an
    omission.
  - **(b) Widen the rule** to labels beginning "Uncertain significance" or "VUS". 223 records at 201 residues. *Cost:*
    this project would read "VUS-high" as a kind of uncertain significance without ClinVar's own definition in hand,
    which SO-DOMAIN-02 and SO-DOMAIN-05 forbid.
  - **(c) Keep the rule, and report the record apart.** The counts gain a second subset, "VUS-high (apart)", holding that
    record alone, never added to the 222. *Cost:* one more line in each count; a reader who wants the sum adds it.
  - **(d) Read ClinVar's definition first.** Done on 2026-10-11 (above): ClinVar calls the term a sub-tier of
    uncertain significance whose criteria each submitter sets. So (b)'s cost as first stated, reading the label
    without ClinVar's definition, no longer holds; its remaining cost is that the count then mixes ClinVar's own
    category with one submitter's sub-tier, whose criteria the held record does not give.
- **What waiting delays:** the final commit of these criteria, since the counts' rule must be fixed before the build, and so
  the build.
- **Recommended: (c),** with ClinVar's definition quoted beside the record. It is right whatever the definition says:
  the subset stays defined by ClinVar's words alone, and the record still appears where a reader looks for VUS. The
  column line is the same under every option.
- **Answered: (c),** with ClinVar's definition quoted beside the record, by the operator at 23:28:41 IST on 2026-10-11
  (the transcript: "Accept all nine now (Recommended)", the three questions here with CL-3's six).

**Q2. The size of the build** (put at 10:00 IST on 12 October).
- **What it decides.** Whether CL-4 composes all 299 residues of the set, or only the four the article works through
  (human 163, 522, 614 and 2060), and which residues its re-derivation (C5) checks against fresh retrievals. Both
  builds use the same code, criteria and column line. The build itself is quick; the cost lies mostly in C5's logged
  calls and in reviewing its outcomes.
- **The options:**
  - **(a) The full set, with the sample as drawn** (the nine departure residues and 30 others): 39 residues, 45 ClinVar
    records and 90 gnomAD rows re-derived, about 183 logged calls. *Cost:* none of the four worked residues is in the
    sample, so the article's rows for residue 614 would rest on rows that no C5 check touched.
  - **(b) The four residues only:** all four re-derived, 8 records and 7 rows, about 26 calls. *Cost:* claim PC-4's
    wording changes to "four worked-example residues"; the VUS counts cover one record (p.Arg163His); no join in the
    pig departure is re-derived; and C5-S's windows at these four were largely seen before this commit.
  - **(c) The full set, with the four worked residues added to C5's sample** (the critique's suggestion): 43 residues,
    53 records and 97 rows, about 206 calls. *Cost:* about 23 more calls than (a), and the review of the four's
    outcomes.
  - **(d) The four first, then the full set, under one commit of the code** (the option the critique found missing): a
    four-residue build for the article, then a full build writing new tables. *Cost:* two builds, two sets of records
    and two reviews. The article cites the first build's records, and the full build's rows at the four must equal them;
    a difference is reported, and the article's rows are checked again.
- **What waiting delays:** the build cannot start before this answer and P0. Each hour after 10:00 IST shortens the
  margin before 23:00 IST, when the article needs CL-4's table.
- **Recommended: (c).** It gives the article checked rows for residue 614, keeps claim PC-4 as worded, re-derives the
  pig departure, and costs about 23 calls more than (a). If the full build is not checked in time, the four-residue
  build (b) is the cut-down set the article's brief already allows ("or the cut-down set if the full one slips", line
  341).
- **Answered: (c),** by the operator at 23:28:41 IST on 2026-10-11, the night before the planned 10:00 IST. The
  operator's credit reading that night: 63% of the week remaining, against a reserve of 30%; at the reserve, the
  smaller close (b) stands as plan v2 sets it.

**Q3. If P0 is not met in time.**
- **What it decides.** What CL-4 does if the upstream tables are not yet graph records when the build should start. The
  deadline is fixed by the article: its brief needs CL-4's table by 23:00 IST on 12 October (line 341). Allowing about
  five hours for the build, its checks and their review (an allowance, not a measurement), P0 should hold by 18:00 IST.
- **The options:**
  - **(a) Wait for P0 in full, then build once.** *Cost:* if P0 is late, CL-4 misses 23:00 IST, and the article's S.7
    and S.8 wait or go out marked pending.
  - **(b) Build without L3** (L1, L2 and L4) and reword claim PC-4 without gnomAD. *Cost:* PC-4 changes, and the close
    shows no population variation.
  - **(c) Build L1, L2 and L4 as soon as P0's CL-2 and CL-3 parts hold, and L3 as a later run under these same
    criteria once S2's records exist,** with claim PC-4 claimed only once all four layers exist (the critique's third
    option). *Cost:* two runs, each with its own records and checks (C1, C4, C5-G, C9 and C9-P for L3's run); the
    article shows L1, L2 and L4 by 23:00 IST and adds gnomAD when L3 lands, with PC-4 held until then. The counts do
    not depend on L3, so nothing in the first run changes.
- **A limit on (c):** it helps only when the late part is S2's. If CL-2's or CL-3's records are late, L2 cannot be traced
  and only (a) remains. Under CL-3's question 1 option (c), P0.3 cannot be met at all (P0, above).
- **What waiting delays:** nothing until P0 slips. Deciding at 10:00 IST, with Q2, avoids a decision under pressure at
  18:00 IST.
- **Recommended: (c).** It keeps claim PC-4 unchanged, since PC-4 waits for all four layers, and it keeps the article on
  time.
- **Answered: (c),** by the operator at 23:28:41 IST on 2026-10-11.

## Corrections owed in other files

Not edited here.
- **`how/campaigns/proposal_campaign_close_20261011.md`, line 94** (claim PC-4): "on numbering checked against SIFTS".
  False for the six Woll et al. entries, whose numbering CL-2 checks by this project's alignment alone (CL-2's run). A
  wording that holds: "on numbering checked by CL-2: against SIFTS where SIFTS maps the entity, and by this project's own
  alignment alone for the six Woll et al. entries, which it does not".
- **The same file, line 143** (deliverable CL-4): "Each ClinVar condition carries the Mondo identifier from ClinVar's
  own record" is overstated: 259 of the 624 condition entries of the 358 included records carry none (s01). A wording
  that holds: "each condition carries the Mondo identifier ClinVar gives it, where it gives one (365 of 624 entries)".
  And "through independent paths (gnomAD's browser API, ClinVar's record pages, SIFTS)" is overstated: C5-N reads
  SIFTS, CL-2's own input, by a second code path; ClinVar's and gnomAD's re-queries are fresh retrievals from the same
  sources, not other sources.
- **The same file, line 164** (the roadmap, "Composed with community graphs"): "Each ClinVar condition carries the
  Mondo identifier ClinVar gives it (377 of 379 expert-panel records do)". The record count holds; the claim per
  condition does not: 266 of the 652 entries of all 379 records carry none (s01).
- **The same file, lines 197–198** (the fallback): "each re-derived in full through the independent paths". The
  four-residue build adds no independent check for rabbit or mouse joins (C5-N is a second code path on the same
  inputs), and its C5-S windows were largely seen before this commit.
- **The same file, line 95** (a note, not a correction): "gnomAD v4.1.1" matches v4.1.2's post (variant data unchanged
  from v4.1.1), but the dataset's label is "gnomAD v4.1.2", and public text should give both, with the basis.
- **Versions 1 and 2 of these criteria** are superseded by this one, and should be marked so when it is committed.
  Version 1's lines 81, 92 and 108 and version 2's lines 51–52 and 544–545 (the "outside the set" claim) are false or
  stale.

## Found while drafting version 3, beyond the critique

- **CL-2's tables carry the join rule exactly.** Read by L2's rule, they reproduce every segment's `joined_residues`
  and every chain's `joined` (610 segments, 104 chains), and in no chain is a species position held twice or joined
  positions out of order (v3_03).
- **CL-3's notes named no table for the gate cases,** which CL-4 must read (P0.3). They name one since the night of
  2026-10-11.
- **CL-4 cannot be built as specified under CL-3's question 1 option (c)** (P0).
- **One included record is a two-base change** (VCV000133055.4 at residue 4665, a VUS); S2's table holds single-base
  changes only, so L3 cannot show it.
- **The recording tool places each table at `tables/<name>.tsv`** (`record_table.py`, line 1005); CL-4's own tables
  carry the build's commit in their path instead.
- **At residue 614 three of the four R615C pig structures are not joined** (6X34, 6X35, 6X36: undeclared Cys); the
  article's figure, which shows four structures carrying R615C, must show them with that reason.
- **C5-S under version 3's rule** withdraws 3 of 1,588 correct joins (0.19%) and judges none of 3,176 moved labels
  consistent (v3_05).

## The scripts behind this version's numbers

Written and run while drafting, each reading the held files only (no network). They and their outputs travel with this
draft in its drafting folder, and should be committed beside it for these citations to resolve. *(Copied byte for byte
at the close of session `[a working record, not public]` into `[a working file, not public]`, not yet reviewed:
`v2/` holds s01 to s22 and their outputs, `v3/` the rest, `v3/rerun_drafter/` the re-runs.)* Python scripts run
with the project's interpreter and `-I`; mmCIF scripts with gemmi 0.7.5 (`uv run --with gemmi==0.7.5`). Version 2's
scripts s01 to s04, s09 to s15, s17 and s20 were re-run for version 3 and gave outputs identical, byte for byte, to
those version 2 cited; s05 to s08, s16, s18, s19, s21 and s22 were not re-run.

| Script | What it re-derives |
|---|---|
| s01_clinvar_set.py | The set: 379, 358, 299, 47, 21; the descriptions; the VUS subset and the VUS-high record; Mondo per record and per condition; the four residues' records |
| s02_gnomad_table.py | S2's table: 7,963 rows, 37 columns, keys; `observed_pass`; the filters; the empty cells; rows at the set; the missing graph records |
| s03_partners_blind.py | Partners; reliability; C7's blind set; C6-P's candidates; the nine departure residues |
| s04_structures.py | The 26 entries' RyR1 chains and declarations; the pig entries' modelled residues in 2650 to 3000; 9PWO against P16960 |
| s05_meta.py | The pig entries' titles, citations, related entries and 9PWO's initial model |
| s06_superposition_feasibility.py | The first coordinate trials: residue by residue, and the label-based fit |
| s07_register_window.py | The window test on repeats 1 and 2; the departure's label-free coincidence |
| s08_register_general.py | The window test with one fit region, across the chain |
| s09_clinvar_vcv_vs_summary.py | ClinVar's same-version comparison on eight records |
| s10_c5_sample.py | C5's 30 others; C9-P's rows |
| s11_quotes.py | gnomAD's label and post; the proposal's lines; S2's `observed_pass` line |
| s12_states_and_615.py | S13's classes by species; the pig residue at author 615 |
| s13_misc_counts.py | Exclusion categories; the four residues' rows; chains by species |
| s14_a6_attach.py | A6's attachments |
| s15_clinvar_terms.py | ClinVar's request for attribution |
| s16_register_consensus.py | The three fits; the departure's label-free windows; the tie at 6X34 chain B, 3409 |
| s17_sample_sizes.py | C5's workload as drawn; S2's presence rule |
| s18_planted_position.py | C5-S-P's position under version 2's rule |
| s19_pdbe_snapshots.py | PDBe's logged mappings for the seven pig entries |
| s20_four_presence.py | Whether the seven pig entries model the four residues' pig partners |
| s21_rule_compare.py | The two ways of combining the three fits, under version 2's rule; the source of C5-S's functions |
| s22_control_overlap.py | How far the control positions overlap the set residues' pig partners |
| v3_01_cl2_tables_summary.py | CL-2's real tables: columns, statuses, offsets, identity-low and R11c runs, departures, exception kinds, gate readings |
| v3_02_records_and_quotes.py | Record identifiers; gnomAD's terms (line 7); ClinVar's attribution; the proposal's and CL-2's lines; the brief's line 341; VCV000133055.4; condition names |
| v3_03_cl2_properties.py | L2's reading guards on CL-2's real tables; the gate case of each entry by CL-2's rule |
| v3_rules_L2_fixed_before_614.md | L2's rule, written before any set residue's row was computed |
| cl4v3_lib.py | The readers and L2's rule, as v3_04 to v3_08 use them |
| v3_04_residue_614_and_fault_targets.py | Residue 614's 104 rows; human 163's planted joins; P16960 950, 940, 960 in 6X32 chain B |
| v3_05_c5s_controls.py | C5-S under version 3's rule on 1,588 control positions; C5-S-P's position and fallbacks |
| v3_06_sum_c02.py | The critic's count of UNK residues at partners' author numbers (its `c02`, re-run): 724 rows, 45 residues |
| v3_07_q2_workload.py | Q2's workloads; residue 614's condition entries; the four's VUS record |
| v3_08_c5s_false_withdrawals.py | The window offsets behind C5-S's three withdrawals of correct joins |
| v3_09_spot_checks.py | The pig partners of 2496, 2508 and 2510; C9-P's two rows; CL-2's undeclared differences and neither-path residues; the tie in s16; residue 614's conditions in order; retrieval times (the 26 mmCIFs: 24 on 2026-10-05 and 2 on 2026-10-06, UTC); S13's four entries with no state word; A6-06's ranges |
| v3_10_flank_example.py | P16960 2092 in 6X32 chain B under joined flanks and under placed flanks (run after the rule was fixed) |

Not verified here: anything that needs a fetch (C5's re-queries; ClinVar's definition of "VUS-high"; whether gnomAD's
per-variant query reproduces the gene query); CL-3's gate-case table, which does not exist yet; the graph records that
P0 requires.

## See Also
- [a working note, not public]: version 1, which this replaces
- [a working note, not public]: version 2, which this replaces
- [a working note, not public]: CL-2, version 2.2, whose tables L2 reads
- [a working note, not public]: CL-4, claim PC-4 and the smaller close
- [a working note, not public]: the article's brief, S.7 and S.8, and the deadline (line 341)

## The re-check of version 3, and what changed (2026-10-11, night)

A fresh, read-only critic re-checked the rules version 3 rewrote (session `[a working record, not public]`;
about 333,000 tokens). Verdict: **"not ready"**: S1 and S2 answered, B1 only in part, and P0.2 unmeetable with the
recording tool as drafted. Its key claims were checked at source before any change: the UNK stretches of 5TB0 and 5T9V
(all eight chains: author 1276-1564, 2487-2703, 2942-3613 and 4320-4345; SIFTS 1276-1572, 2480-2733, 2940-3638 and
4254-4279, from CL-2's exceptions table); 88 of the 89 `neither path` rows ambiguous on path A, with 6X35 chain B's
alternatives as quoted; RT06 in `record_table.py` (`check_rows`); the entries table distinct on `entry`, `scope`,
`entity` and `chain` (260 rows) and the segments table on `entry`, `chain` and `segment` (610 rows); the C5-S code's
convergence test, its strict "< 2.0" and its insertion-code skip (`v3_05_c5s_controls.py`).

| Finding | Disposition |
|---|---|
| **B1′ (blocking):** step 3 still placed residues by author number and called possibly modelled positions "not modelled" (5TB0, 5T9V; ambiguous `neither path` residues) | **Accepted.** Step 3 rewritten as nine ordered rules: "not modelled" only when M is empty or holds no unplaced residue that could stand at p; "modelled, not placed" only when M fills the flanks' gap exactly, or an UNK stretch's author numbers and SIFTS's range agree; a position among an ambiguous residue's partners is "not determinable"; every other case "not determinable", with the readings named. The three departures from the version 2 critic's proposal are recorded in the step's note. New guard C11-U at 5TB0 chain B, P11716 4260, and 6X35 chain B, P16960 237 |
| **S-P0 (serious):** P0.2 cannot be met: RT06 refuses a key column that is not required | **Accepted.** P0.2 states the three tables' keys; P0.4's review brings RT06 into line with V09 |
| **M-a:** C10 cannot see planted faults applied in memory | **Accepted.** The build hands C10 its in-memory inputs, any planted change included; C10 applies the segment rule itself |
| **M-b:** C10 had no live control on its status derivation | **Accepted.** C10 compares every row's status and reason; C10-P (ii) moved to 6X34 chain B at 614, a row in both builds |
| **M-c:** whether withdrawn joins flank | **Accepted.** They never do; withdrawals are decided before step 3 |
| **M-d:** "never by keeping a wrong one on a split window" is false | **Accepted.** Deleted; a split window's join keeps its place unverified, as stated |
| **M-e:** P0's check row weaker than its text; the stale "CL-3 names no table" | **Accepted.** The row lists exactly what P0.1 to P0.5 ask; CL-3's notes name the gate-case table since that night, and both lines say so |
| Minor: insertion codes | **Accepted.** Exceptions rows matched on author number and insertion code |
| Minor: R undefined when L absent; the reason for a chain with no join; which reason when two apply | **Accepted.** All three defined (rules 1 to 9 apply in order) |
| Minor: R11c read `not joined` at 2047 and `not determinable` at 2092 | **Accepted.** Step 2 gives R11c alone `not determinable` |
| Minor: segment-rule withdrawals had no check record and a wrong reason | **Accepted.** Their own reason, and `c5s_check_result` names the segment rule's record |
| Minor: C5-S-W-P's segment not fixed | **Accepted.** Every sampled join of the segment of 6X32 chain B that holds P16960 950 |
| Minor: C5-S's text omitted the code's tolerances, its strict "<", the alternate-location CA and the insertion-code skip; "hence three fits" unsupported | **Accepted.** All four stated; the three fits' purpose restated with v3_08's finding |
| Minor: S13's raw column names cited where CL-4 reads the derived copy's | **Accepted.** Both names given |

**Not changed:** nothing the critic found was rejected. Its finding that the set residues B1′ touches were not counted
stands: they stay unread, to keep the build blind. A second short re-check followed (below).

**Also changed in this revision, beyond the critique:** question Q1, with ClinVar's definition of "VUS-high" read
(option (d) done) and (c) recommended; the absent layers, under the operator's rule of 2026-10-11 (21:41:53 IST: no
permission sought in the close); the conditions on publication, with SIFTS's terms read.

## The second re-check, and what changed (2026-10-11, night)

A second fresh, read-only critic re-checked the revised rules (about 271,000 tokens). Verdict: **"ready after
fixes"**. It implemented rules 1 to 9 from the text alone and found every position it was given decided as the text
says: 5TB0 and 5T9V chain B, 4254-4345, by rule 9; 9ZO8 chain A, 4279-4343, by rule 9; 6X35 chain B, 237, 240, 1502,
1510, 2263 and 2270 by rule 5, and 238, 1505 and 2266 by rule 9; 6X32 to 6X36 chain B, 2047 by step 2 and 2092 by rule
3. Its key claims were checked at source: 9ZO8's UNK row holds 50 residues over author 4279-4343, as SIFTS's range does;
76 of the 88 ambiguous `neither path` rows list no partners; the exceptions table is distinct and never empty on
`entry`, `chain`, `kind` and `author_first` (485 rows). It also found that this file's working copy had CRLF line
endings on every line, written by a Windows text-mode patch; restored to LF.

| Finding | Disposition |
|---|---|
| **S1:** a withdrawn join inside M was neither of M's kinds, so rules 3, 4 and 6 had no reading for it, and two readings gave `not modelled` where C5-S might place it | **Accepted.** A withdrawn join counts as unplaced |
| **S2:** no test of rules 1 to 9 could fail on a wrong rule: C11-U checked the status only, through the build's function only | **Accepted.** C11-U compares status, deciding rule and reason through both functions; C11-U-P runs version 3's rule, which must fail it; C11-S, synthetic chains with known answers, one per rule, run through both functions |
| **M1:** rule 7 places nothing in CL-2's run, though the record said such a stretch "is placed" | **Accepted.** Stated, with what the rules reach in this run; rule 7 is kept for other inputs. Comparing residue by residue (9ZO8's own declarations, or SIFTS's file) was not taken: it adds an input for one entry, whose rows stay `not determinable`, which is safe |
| **M2:** at the R11c gaps, rule 4 rested on author 2092's number | **Accepted.** A residue left by R11c alone counts as unplaced in step 3 |
| **M3:** points where C10 and the build could read the text differently | **Accepted.** The offsets "between the smaller and the larger"; N is the note's count, and must equal `n_residues`; the first residue in author order is named; each reason's form fixed, rule 9's readings separated by " \| " |
| **M4:** the column line behind the rules | **Accepted.** `not_joined_reason`'s forms; `author_number` for step 2's rows; `c5s_check_result` naming the segment rule's own record, `CL4.C5-S-segment`, added to *The records* |
| Minor: P0.2 stated two keys of three | **Accepted.** The exceptions table's key stated |
| Minor: P0's row left out three conditions; P0.3's reason against `gate_case_reason` | **Accepted.** All three added; a reason for `c` and `d` only |
| Minor: not every split window is "not determinable" | **Accepted.** Restated: an untied commonest offset other than 0 counts against |
| Minor: rule 5 reaches 6X35 only | **Accepted.** Stated |
| Minor: author order and the UNK stretches' SIFTS ranges | **Accepted.** Both made C11 guards |
| Minor: CRLF line endings | **Accepted.** Restored to LF |

**Not changed:** nothing rejected. Left unread, to keep the build blind: how many sampled joins C5-S-W-P's segment
holds.

## Critique record: the critique of version 2

A fresh, read-only critic judged version 2 "not ready", with one blocking finding, four serious, nine moderate, eleven
minor, and remarks on the three questions. Lumen checked the mechanisms of B1, S1 and S2 against CL-2's code (species
positions are set only for `agree` and `path A only`; UNK residues appear only as author ranges in the exceptions
table; the identity-low and R11c reasons sit in `kind`, not `category`). This drafter checked every finding again at
source before its disposition.

| Finding | Checked at source | Disposition | What changed, or why not |
|---|---|---|---|
| B1 (blocking). L2 cannot place the residues CL-2 leaves without a species position; the build would call them "not modelled" (about 724 rows) | Yes: `cl2/numbering.py`, lines 816–819 (species positions for `agree` and `path A only` only), 1243 (segment ranges from placed residues) and 1274–1287 (UNK as author ranges); the critic's `c02` re-run: 724 rows at 45 residues, six in C5's 30 (v3_06); in CL-2's run the unplaced residues are UNK and 89 "neither path" (v3_01) | Accepted | L2's rule: a placed residue decides `joined` or `not joined`; otherwise the flanking joined residues decide `modelled, not placed`, `not determinable` or `not modelled`, each defined, with `entry not analysed` apart; each counted in its own column; C10 derives every status by its own code; C11 guards the reading. The rule was written before any set residue's row was computed. One change from the critic's proposal: the flanks are joined residues, not every placed one, so that residues CL-2 does not trust never set an offset (*L2*, the example at P16960 2092) |
| S1. Written against CL-2 2.1; the not-joined reason read from the wrong column | Yes: lines 1296–1301 and 1307 put R11c and identity low in `kind` and keep `category`; the real tables carry identity low (180), R11c (20), undeclared difference (28), neither path (89), declared difference (20), and 8 residues with two kinds (v3_01); 6X32's run is 2490–2534 and holds pig 2497, 2509 and 2511, the partners of 2496, 2508 and 2510 (v3_09) | Accepted | The join is stated in CL-2's committed columns (segment `status`, `identity_low`, `short_departing_run_path_a`, the exceptions rows' `joined`); `not_joined_reason` holds every `kind`, `;`-joined; CL-2 2.2 cited throughout, with "SIFTS anomaly" and R11c; the rule reproduces every segment's `joined_residues` (v3_03) |
| S2. CL-2 2.2's gate rule not carried | Yes: CL-2's criteria, lines 446–485; by that rule the 20 SIFTS-mapped entries are (a) and the six Woll et al. entries (b) (v3_03) | Accepted | `gate_case` (CL-3's mark) and `gate_case_reason` on every row; entries of case (c) or (d) counted apart (`entries_joined_gate_case_c_or_d`, `n_joined_other_only`), never under closed or open; C10 derives the case from CL-2's tables and compares; C10-G-P moves 7M6L to (c) |
| S3. P0 covers S2's table only; nothing gates L2's tables | Yes: CL-2's tables in `curation/cl2_run_e888359/` with 54 comment lines each (v3_01); S13's columns `class_A`, `class_at_minus_0.5A` (s12); no table record names CL-2, S13 or S2 (v3_02); the recording tool unreviewed ([a working record, not public]) | Accepted | P0.1 to P0.5: records for S2's, CL-2's and CL-3's tables (S13's and the gate cases), CL-2's run usable, the tool reviewed, the validator clean; CL-4 reads the `tables/` copies; P0-P |
| S4. C10 does not know about C5-S's withdrawals | Yes: version 2, lines 489–493 and 589–593 | Accepted | C10 takes C5-S's check record as an input; a C5-N failure now stops the build, so no rows are withheld; C10-W-P and C5-S-W-P must move counts that C10 reproduces |
| M1. C9-P corrupts C9's own comparator | Yes: S2's rows (v3_09): 19-38440803-G-T, exome 0/1,456,722 with `AC0`, no genome data, `observed_pass` false; 19-38457545-C-T passing in both | Accepted | C9-P corrupts the build's L3 rows |
| M2. C5's update branches cannot fail; two planted faults can miss by design; "As below" | Yes: version 2, lines 485–487, 540–542 and 559–560 | Accepted | A gnomAD difference is excused only by a later release whose post says variant data changed; the number of ClinVar records at a higher version is reported; C5-C-P and C5-G-P targets chosen by a stated rule, "not run" if there is none; every failure condition and its consequence written in the table |
| M3. C5-S as written does not match the code behind its control rates | Yes: s16, line 27 (6X34 chain B at 3409, r = 40: {+1: 7, 0: 7}; v3_09); s21's `Pair.fit` (20 residues in each region; 20 Å to 9PWO's region; ICP ends below 10 pairs); its anchors admitted unjoined residues | Accepted, with one part kept | C5-S's implementation is s21's functions with three changes (CL-2's joined labels and anchors, departing segments left out by residue, ties "not determinable"), committed before the build; every parameter stated; the control rates recomputed (v3_05). The asymmetry is kept and stated: it errs only by withdrawing correct joins; the three such withdrawals were pluralities of 0.56 to 0.69 (v3_08) |
| M4. C7, C8 and C9 labelled live but cannot fail on real data | Yes: lines 820–826 and 894 | Accepted | All three labelled guards on CL-4's reading; their planted faults kept; C7's section says what it tests and lists CL-2's own checks apart |
| M5. A false "not seen" claim | Yes: s01's records: VCV000133055.4 included at 4665, "Uncertain significance" (v3_02) | Accepted | Corrected under *What has been seen* and in C5-C; listed under corrections owed for version 2 |
| M6. Gaps in provenance | Yes: version 2, lines 307, 367, 482–483 and 713 | Accepted | `gnomad_label_record`, `c5s_verdict` and `c5s_check_result`; a withdrawal credited to `c5s_check_result`; C4 resolves against this run's pending records; the validator runs after writing |
| M7. Table form: key without `class_measure`; no run identifier in paths | Yes: version 2, lines 415, 428, 502–503 and 678–679 | Accepted | `class_measure` in the keys of both count tables; the build's commit in every path; nothing written until the checks pass |
| M8. Corrections owed incomplete | Yes: the proposal's lines 94, 143 and 197–198 (v3_02) | Accepted | All three added, with wordings |
| M9. P0's check row weaker than its text | Yes: the recording tool's rules RT01 to RT17 record no check outcome; S2's run wrote none | Accepted, by cutting the text | P0 asks for what can be recorded, and says why S2's K0 to K8 are not required as records; P0's row asks for exactly that |
| Minor: `entries_not_modelled` lumps "entry not analysed" | Yes: version 2, line 339 | Accepted | `entries_not_analysed`, apart |
| Minor: `deposited_implies` is "-" in S13's table; CL-3's three word columns | Yes: S13's table writes "-" for four entries, 8VJJ, 8VJK, 8X4C and 6W1N (v3_09); CL-3's notes describe three word columns | Accepted in part | Both columns carried verbatim from S13's table, "-" defined; CL-3's per-source words are not carried, since they belong to CL-3's release, not to a graph table CL-4 reads |
| Minor: C8 relies on an organism no CL-2 column holds | Yes: CL-2's entries table holds `species`, not the taxon | Accepted | C8 uses CL-2's `species`, which R7 compared with the organism, and K2's report that R7 refused no entry |
| Minor: "each window can be decided" overstated; a window read as a statement about p | Yes: version 2, lines 631–634 | Accepted | Reworded: the minimum the rule needs, not a decision; a statement about the window's register |
| Minor: 6X32's run is 2490–2534 | Yes: CL-2's run (v3_01) | Accepted | Corrected |
| Minor: C5-S-P has no fallback; the segment rule has no planted fault | Yes | Accepted | Fallback 940 (v3_05); C5-S-W-P |
| Minor: the hand-off to [a peer's project] lacks SIFTS's licence condition and gnomAD's attribution | Yes: CL-2's criteria, lines 87–89; gnomAD's terms, line 7 (v3_02) | Accepted | Both in the hand-off; `attribution` and `attribution_record` in `cl4_gnomad` |
| Minor: "What was seen" omits path A's outcomes and the declarations | Yes: CL-2's criteria, lines 492–498; s04 | Accepted | Both listed |
| Minor: the A6 rule does not say how a range attaches | Yes: A6-06 names human 4927–4928 and rabbit 4926–4927 (v3_09) | Accepted | Each position of a range counts; the attachments are unchanged (s14) |
| Minor: `n_neither` absorbs residues joined only in indeterminate entries | Yes | Accepted | `n_joined_other_only`, which also takes entries of case (c) or (d); `n_not_joined` |
| Minor: C1 does not guard SIFTS, the A6 table, or the label and attribution snapshots | Yes | Accepted | All in C1 |
| Q1: the missing option of reading ClinVar's definition first | Yes: no held file defines "VUS-high"; the held maintenance page links "Classification" to ClinVar's `clinsig` page | Accepted | Option (d); recommended (d), then (c) |
| Q2: not fairly costed; the full set never re-derives the four; the missing option | Yes: 39, 45, 90, about 183 calls; with the four 43, 53, 97, about 206; the four alone 26 (v3_07); none of the four in the sample (s10) | Accepted | Options (c) and (d); costs restated; recommended (c), with (b) as the cut-down set |
| Q3: no deadline; the wait is longer than it looks; a third option | Yes: the brief's line 341 (v3_02); P0 now covers four tables and a review of the tool | Accepted | The deadline and a latest time for P0; option (c); its limit stated; recommended (c) |

**The critic's own confirmations of critic A's findings** (finding 3 answered by P0; finding 8's control figures
reproducing; findings 9, 17, 18 and 19 answered) are taken as recorded; what remained of them is answered in the rows
above (S3, M9, M3, S4, M2, M4).

## Critique record carried: critic A on version 1

Critic A (fresh, read-only; report of 2026-10-11) judged version 1 "not ready". Version 2 answered each finding, and
version 3 keeps those answers, with the changes shown.

| Finding | Version 2's answer | In version 3 |
|---|---|---|
| 3 (blocking). L3's table has no graph record | P0 for S2's table | P0 covers CL-2's and CL-3's tables too (S3) |
| 8. C5 cannot re-derive the joins where path A stands alone | C5-S by coordinates against 9PWO; C5-N named a second code path | C5-S's code and parameters fixed, its control rates recomputed (M3) |
| 9. C5's ClinVar and gnomAD parts cannot fail | Same version must match; a release check first | Only a release whose notes say variant data changed excuses a difference; targets by rule (M2) |
| 17. C6-P and C7 blind where neighbours match | Blind sets listed; C6-P fixed at human 163 | C6-P's joins confirmed in CL-2's tables; C7 labelled a guard (M4) |
| 18. Mondo counted per record only | A conditions table, counted per condition | Unchanged |
| 19. The VUS-high record left out | Options (a) to (c), (c) recommended | Option (d) added (Q1) |
| Minors: 7,964 rows; `observed_pass`; C3; "CR3"; the not-joined list; the counts' unit and measure; C5's draw; C10's inputs; C2's script | Each accepted | Unchanged, except the not-joined list, now CL-2 2.2's `kind`s (S1), and C10's inputs (S4) |
