# ChannelScope release ryr1_structure_states_v0.1: the pore at the gate of 26 RyR1 structures

**What this release is.** For 26 deposited cryo-EM structures of the four-subunit RyR1 channel, from rabbit, mouse
and pig, the radius of the pore at the gate, measured by two implementations, with the words that name each
structure's state, quoted with their source. With them comes a survey of the 188 PDB entries holding RyR1
that the project's searches found, saying where each came from, what bound it and what its title calls it. The
searches' answers are listed in `rcsb_answers.tsv`, each with its retrieval record: the PDB's, retrieved on
3 October and 6 October 2026 (IST), are in `graph/raw/rcsb/`, and UniProt's, retrieved on 29 September and 6 October 2026,
in `graph/raw/uniprot/`. Entries released after those searches are not in it.

**Which 26.** Twenty-four were named before any was measured, on 6 October 2026: six pairs, each a
closed and an open structure sorted from one dataset; ten other structures; and two structures that a review calls
closed and open, used as positive controls. Two more, a closed and open pair released on 30 September 2026 (9ZO8 and
9ZOE, by the survey's own column), were measured later the same day under the same criteria and code (`selection.tsv`). Of the survey's
155 electron-microscopy entries whose deposited RyR1 sequence has 3,000 residues or more, the other
129 were not measured. Forty-two of their titles carry a state word the survey
records ("primed" 21 times, a form of "open" 12 times and of "closed" 9 times), and
nine more name a state its word list misses (`word_list.md`, `survey_unmeasured.tsv`). What
follows describes these 26 structures, not RyR1's structures in general.

**How the pore was measured.** The gate is a ring of four isoleucines, one in each subunit (rabbit I4937; mouse and pig
I4935; human I4938). Two implementations, written in one script, read the files with different libraries (Biopython for
A, gemmi for B) and share only the list of structures and the gate's number in each species.
- **Implementation A** takes as the pore's axis the line through the centre of the four gate residues' Cα atoms,
  perpendicular to the plane that best fits them. Its radius is the least distance from that axis to any heavy atom of
  the four gate residues, less that atom's radius.
- **Implementation B** takes as its axis the main axis of a block of all four chains, from 117 residues before the gate
  to 100 after it. Its radius is a probe's: the distance from a point on that axis to the nearest heavy atom, less that
  atom's radius. In the first measurement, B took the least such value within 3 Å of O2's height, the height along the
  axis of the centroid of the gate residues' heavy atoms, sampling every 0.25 Å ("O2's window"). Whether each of the
  two samples at exactly 3 Å is kept is decided by rounding, so in 11 of the 26 structures O2's window has another possible value, by up to 0.16 Å (`rerun/window_readings.tsv` gives every
  reading). In the re-measurement, B was read at the gate's own height (the mean, over the four chains, of the height
  of each chain's gate heavy atom whose surface lies nearest the axis), from atoms within a slab 2.5 Å deep ("the
  fixed B").

The radius quoted here, and the class, are A's. A structure is classed closed if A's radius is below 2.0 Å, open
if above 3.0 Å, and indeterminate between. "Closed" and "open" mean narrow or wide at the gate's ring, not
whether ions flow.

**Where the lines come from.** The lines are this project's own rule, committed before any structure was measured (in
O2's criteria, commit b9323291dd69625d6b498139cb3b669fdbec3196 of this project's private working history, an order `ledger.md` attests
but this release cannot show; `criteria/o2_criteria.md`), so they could
not be tuned to the results. A search of the papers this project holds, recorded on 6 October 2026, found
no published value that sets them. The values it found are on other measures (each a checked quotation row,
`quotations.tsv`):

| Source | Words | Where |
|---|---|---|
| Yan et al. 2015 | "The pore radius at the constriction point is less than 1 Å, impermeable to a completely dehydrated Ca 2+ ion." | Results, "A closed channel" |
| Zalk et al. 2015 | "and the diameter of hydrated Ca 2+ (8.2 Å 27 ) we conclude that the pore is in a non-conducting state." | Results, "RyR1 is a 6TM ion channel" |
| des Georges et al. 2016 | "The pore remains constricted at I4937 to an aperture insufficient to allow passage of a hydrated monovalent or divalent cation." | Results |
| Nayak and Samsó 2022 | "indicated a closed pore with a radius constricting to 1 Å at the known hydrophobic gate Ile4937" | Results, "Classification of the high Ca2+ dataset reveals an open conformation and a closed-inactivated conformation" |
| Nayak and Samsó 2022 | "displayed a pore diameter at the Ile4937 gate of ~2 Å when considering the side chains" | Results, "Classification of the high Ca2+ dataset reveals an open conformation and a closed-inactivated conformation" |
| Iyer et al. 2020 | "an increased radius from 0.8 Å (PDB: 5TB0) to ~1.2 Å at the gating residue, I4937" | Results, "Mutant RyR1 exhibits a closed-dilated pore under closed-state conditions" |
| Iyer et al. 2022 | "remained closed, with a radius of 1.0 Å at the gating residue Ile4937" | Results, "The Pore Is Marginally Affected by the Mutation." |
| Weninger et al. 2026 | "(calculated using HOLE) confirmed the closed and open conformations (minimum pore radius: ~0.8 versus ~3.0 Å, respectively)" | Results, "Structure of RyR1 in complex with rosuvastatin" |
| Melville et al. 2022 | "the radius of the pore residue could not be measured at I4937 ( Smart et al., 1993 ), though by estimation it remains at approximately 4 Å" | Results, the text after Figure 4's caption (its nearest heading) |
| Wei et al. 2025 | "The pore diameter expands from 6.2 to 13.8 Å, which indicates the channel is in the open state" | Results, "S0 facilitates the RyR1 channel gating in response to Ca2+ and ATP" |
| Wei et al. 2025 | "However, the gate remains the same size (6.2 Å)" | Results, "S0 facilitates the RyR1 channel gating in response to Ca2+ and ATP" |

One is close to the lines: for 9ZOE, its authors report a minimum radius of about 3.0 Å by a method (HOLE) that finds
the narrowest point of the whole pathway; these lines would class that value as indeterminate, while A reads 9ZOE's
gate at 5.28 Å. For these 26 structures the exact values matter little: A's radii fall into two
groups with nothing between them, closed from 0.83 to 1.52 Å (14 structures)
and open from 3.20 to 5.55 Å (12), so any pair of lines inside that gap gives the
same classes. The two positive controls sit well inside their groups (5TB0, 1.01 Å; 5T9V,
4.16 Å). Two structures sit near the gap's edges: 7M6A (1.52
Å) becomes indeterminate if both lines move down by 0.5 Å, and 6X34
(3.20 Å) if they move up by 0.5 Å. Read by O2's window, 9NMP and 6X35 would
also become indeterminate if the lines moved up by 0.5 Å.

**The words.** Each structure's words and measured class are set side by side, with no summary count. The words come
from its title, its depositors' paper, a partner entry's record or, for the two controls, a review. Which words imply a
pore state was not committed before the measurement: the first measurement's reading of them was written into its code
before it ran and committed with its results, and it was applied unevenly (8X4C's paper calls its condition primed,
`wei2025_condition4_primed`, a state the same paper defines as closed, `wei2025_resting_primed`, but the reading records
no state word for it). The table gives that reading, and beside it a reading written afterwards, on 11 October 2026:
a word implies a class only if it says closed or open, or if the same paper defines it by the pore. Both are
descriptions, not tests: a match counted under a reading written after the measurement would describe the data, not
test it. Titles can be checked against the
PDB's answers this release carries (`rcsb_answers.tsv` lists them). For a paper's words, `quotations.tsv` gives the passage and its locator, and a reader with
the paper can check it.

| Entry | Words, as the first measurement's code holds them | Their source | That code's reading | A reading written afterwards | Class by A (radius) |
|---|---|---|---|---|---|
| 9NMO | closed pore | the entry's title (rcsb_answers.tsv) | closed | closed | closed (0.92 Å) |
| 9NMN | open pore | the entry's title (rcsb_answers.tsv) | open | open | open (4.84 Å) |
| 9NMQ | closed pore | the entry's title (rcsb_answers.tsv) | closed | closed | closed (0.94 Å) |
| 9NMP | open pore | the entry's title (rcsb_answers.tsv) | open | open | open (4.38 Å) |
| 8VJJ | EGTA-only dataset (no state word) | none recorded | - | not read: the paper is read before any count under this reading is stated | closed (0.86 Å) |
| 8VJK | high-Ca2+/CFF/ATP dataset (no state word) | none recorded | - | not read: the paper is read before any count under this reading is stated | closed (0.85 Å) |
| 8X4A | closed state | the entry's title (rcsb_answers.tsv) | closed | closed | closed (1.30 Å) |
| 8X4B | open state | the entry's title (rcsb_answers.tsv) | open | open | open (5.23 Å) |
| 8X4C | 20 uM Ca2+, 2 mM ATP (no state word) | none recorded | - | closed: its paper's primed (`wei2025_condition4_primed`), which the paper defines as closed | closed (1.40 Å) |
| 7M6A | primed model (paper); Closed state model (7M6L's record) | Melville et al. 2022, row `melville2022_primed`; the RCSB PDB's record of 7M6L, row `rcsb7m6l_closed_model` | closed | closed: 7M6L's record; the paper's primed is not defined by the pore in the rows held | closed (1.52 Å) |
| 7M6L | open model (paper) | Melville et al. 2022, row `melville2022_open` | open | open | open (4.96 Å) |
| 5TB0 | a closed RyR1 pore (Woll and Van Petegem 2022): positive control | Woll and Van Petegem 2022, row `woll2022_5tb0_closed` | closed | closed | closed (1.01 Å) |
| 5T9V | an open RyR1 (Woll and Van Petegem 2022): positive control | Woll and Van Petegem 2022, row `woll2022_5tb0_5t9v` | open | open | open (4.16 Å) |
| 7T64 | closed state | the entry's title (rcsb_answers.tsv) | closed | closed | closed (1.24 Å) |
| 7T65 | open state | the entry's title (rcsb_answers.tsv) | open | open | open (5.55 Å) |
| 9CGP | the closed state without Ca (paper) | Iyer et al. 2025, row `iyer2025_states`; Iyer et al. 2025, row `iyer2025_pdb_ids` | closed | closed | closed (0.83 Å) |
| 9CGQ | the open state with Ca (paper) | Iyer et al. 2025, row `iyer2025_open_with_ca`; Iyer et al. 2025, row `iyer2025_pdb_ids` | open | open | open (5.01 Å) |
| 6W1N | WT, 5 mM EGTA (no state word) | none recorded | - | not read: the paper is read before any count under this reading is stated | closed (0.90 Å) |
| 6X32 | closed | the entry's title (rcsb_answers.tsv) | closed | closed | closed (0.86 Å) |
| 6X33 | open | the entry's title (rcsb_answers.tsv) | open | open | open (4.71 Å) |
| 6X34 | open (title); intermediate (paper) | the entry's title; Woll et al. 2021, row `woll2021_intermediate_open` | open | open: the title, and the paper's intermediate, which it says corresponds to an open channel | open (3.20 Å) |
| 6X35 | open | the entry's title (rcsb_answers.tsv) | open | open | open (4.24 Å) |
| 6X36 | closed | the entry's title (rcsb_answers.tsv) | closed | closed | closed (0.92 Å) |
| 9PWO | Open Conformation | the entry's title (rcsb_answers.tsv) | open | open | open (5.27 Å) |
| 9ZO8 | closed pore | the entry's title (rcsb_answers.tsv) | closed | closed | closed (0.93 Å) |
| 9ZOE | open pore | the entry's title (rcsb_answers.tsv) | open | open | open (5.28 Å) |

**How the checks went** (`checks.tsv`; S13's from its check records, the others from their tables' headers):

| Run | Check | Kind | The line's word | Row | Outcome |
|---|---|---|---|---|---|
| S13's run | S | check |  |  | pass |
| S13's run | R0 | check |  |  | pass |
| S13's run | G1-prime | check |  |  | pass |
| S13's run | G2-prime | check |  |  | pass |
| S13's run | P1-A | arithmetic | caught |  | pass |
| S13's run | P1-B | seen in O2's diagnosis | caught |  | pass |
| S13's run | P2-A | live | caught | P2 | pass |
| S13's run | P2-B | live | caught | P2 | pass |
| S13's run | P3-A | live | caught | P3 | pass |
| S13's run | P3-B | live | caught | P3 | pass |
| S13's run | P4 | by construction | caught |  | pass |
| S13's run | P5-plus-2A | live | caught | P5 | fail |
| S13's run | P5-minus-2A | live | NOT CAUGHT | P5 | fail |
| S13's run | P6-A | arithmetic | caught |  | pass |
| S13's run | P6-B | by construction | caught |  | pass |
| S13's run | L1 | live | caught |  | pass |
| S13's run | L2-7M6L | live | caught |  | pass |
| S13's run | L2-7T65 | live | caught |  | pass |
| S13's run | L2-6X35 | live | caught |  | pass |
| O2's run | G1 | check |  |  | fail |
| O2's run | G2 | check |  |  | pass |
| O2's run | planted faults: 5 of 6 caught | faults |  |  | fail |
| the 9ZO8/9ZOE run | G1 | check |  |  | fail |
| the 9ZO8/9ZOE run | G2 | check |  |  | pass |
| the 9ZO8/9ZOE run | planted faults: 9 of 10 caught | faults |  |  | fail |

- **The first measurement (24 structures)** compared the two implementations (check G1: the same class, and
  radii within 1.0 Å). Its criteria were committed before it ran. The code was then written, run in full once without
  writing its table, and run again, unchanged, to write it; between the two, the first run's outcomes were read and a
  short diagnosis was run (`ledger.md`). The classes agreed for all, but the radii of three open
  structures (7M6L, 7T65 and 6X35) differed by more than 1.0 Å, so check G1 failed. Both positive controls were
  classed correctly by both implementations (check G2).
- **The same code, run that evening on 9ZO8 and 9ZOE,** also ran in full once without writing before the run that wrote
  its table. Check G1 failed for 9ZOE in the same way. Over the two runs, check G1 failed for: 7M6L (A 4.96 Å, B 3.80 Å); 7T65 (A 5.55 Å, B 4.06 Å); 6X35 (A 4.24 Å, B 3.22 Å); 9ZOE (A 5.28 Å, B 4.07 Å) (B here is O2's
  window). Read each way at O2's window's 3 Å edge (`rerun/window_readings.tsv`): 7M6L, B 3.80 Å as measured, 1.16 Å from A against G1's 1.0 Å, or 3.69 Å by another reading, 1.27 Å; 7T65, B 4.06 Å as measured, 1.49 Å from A against G1's 1.0 Å, or 4.22 Å by another reading, 1.33 Å; 6X35, B 3.22 Å as measured, 1.02 Å from A against G1's 1.0 Å, or 3.38 Å by another reading, 0.86 Å; 9ZOE, B 4.07 Å as measured, 1.21 Å from A against G1's 1.0 Å, or 4.19 Å by another reading, 1.09 Å. So G1's failure for 6X35 rests on one sample at the window's edge: read the other way, it would pass; the others fail by every reading.
- **The cause,** found by the diagnosis: in all four failures, B's window reached a glutamine four
  residues before the gate on the same helix, about one turn away, where the pore is narrower.
- **Planted faults in the first measurement.** Six were planted, and its table's header
  records 5 of 6 caught. Three could not have failed as written: A's move of the
  gate's atoms is added to every distance (`code/o2/gate.py`, line 115), and both "renamings" raise the refusal by a
  switch (lines 101 and 144). Of the three that could have failed, two were caught. B did not read 5TB0 as open after
  its gate atoms were moved 4 Å outward, because the same glutamine held the reading. The evening run planted
  ten faults, and its table's header records 9 of 10 caught:
  the first run's six again, and four on the new entries (`code/s2/gate_9zo8_9zoe.py`). Four of the ten could not fail
  (the first run's three, and 9ZO8's gate atoms moved through A); of the six that could, five were caught, and the miss
  was the same one.
- **The re-measurement, with B read at the gate's own height,** its criteria and code committed first, agreed with A for
  all 26 structures: the same class, and radii within 0.02 Å. Check S (16 tests, 16 pass; 16 controls caught), R0, G1′ and
  G2′ passed. For the open structures the class half of that agreement was known in advance (S13's criteria,
  `criteria/s13_criteria.md`). Of its
  15 planted faults, its criteria labelled 10 live. By each line's word, 9
  of the live ones were caught, and P5-minus-2A was not, a limit of the check stated before the run
  (a reading taken 2 Å from the gate's own height in a closed pore (5TB0), toward O2's height, 1.3 Å beyond it, still passes G1′. Its records call it "minus" by the sign of B's axis as that run's LAPACK returned it, which another platform may reverse). The criteria judge rows
  P2, P3 and P5 whole, each over its lines, so by its row 13 of the
  15 fault records pass and two fail
  (P5-plus-2A and P5-minus-2A, of row P5); `checks.tsv` gives each line's word and
  its row. As the criteria require of any agreement claimed while row P5 is missed: "G1′ cannot detect a reading 2 Å off the gate's height in a closed pore".
- **What the agreement now tests:** both implementations read the same ring, so their agreement checks the code that
  reads the structures, picks the chains and finds the axis, not the pore by an independent route.

**Numbering.** The gate is found by its author number in each deposited model, and both implementations check that the
residue there is an isoleucine. The residue before the gate is also an isoleucine in all four species, and the one
after it an aspartate, so a model numbered one higher than UniProt at the gate would pass that check while the wrong
ring was measured. Each entry's case under the rule this project fixed before checking its numbering is in
`graph/tables/cl3_gate_cases.tsv`: 20 entries in case a, 6 in case b,
0 in case c and 0 in case d.
- For the entries in case a, the gate's numbering was compared with SIFTS, the EBI's residue-level map from PDB entries
  to UniProt. SIFTS and this project's own alignment align the same deposited sequence to the same UniProt release, so
  the two are not independent.
- For the entries in case b (6W1N, 6X32, 6X33, 6X34, 6X35 and 6X36), the gate's numbering was checked by this project's alignment alone,
  not against SIFTS, which maps none of their RyR1 chains.

**What it is not.** These are measurements of deposited models at one place, the gate. They do not say how a channel
conducts, what state it is in inside a cell, or what any variant does. Local model quality at the gate is not assessed
here. The classes, the two groups and the words beside them hold for these 26 structures, chosen as above; they
are not a census of RyR1's structures.

**What is in the graph, and what is not.** S13's table (`graph/tables/s13_gate_remeasurement.tsv`, a copy of
`curation/s13_gate_remeasurement.tsv` with seven column names changed: five
made lower-case, and two renamed,
`class_at_minus_0.5A` to `class_at_minus_0_5` and `class_at_plus_0.5A` to `class_at_plus_0_5`), its 19 current check records, with the
19 they revise, and the gate cases are graph records. For S13's table, the records were written after
the run, from the run's own output as this project's working transcripts hold it, and name the run whose output they
hold. The first 19 were re-issued on 14 October 2026, each new record naming the one it revises
(`checks.tsv`, column `revises`) and its note saying, field by field, what changed: S13.G1-prime, S13.G2-prime and S13.P5-plus-2A had
stated their control or outcome wrongly; S13.P2-A, S13.P2-B, S13.P3-A, S13.P3-B and S13.P5-minus-2A gained the row of the criteria they are
judged by; and the other eleven changed in no fact. Two of the records they rest on, the methods of
S13's run and of the numbering check, cite those transcripts by identifier and are withheld (`withheld.tsv`, summarised
in `withheld_records.json`). The release's builder, which is not published, checks the graph in an export mode that
excuses a reference only if `withheld.tsv` names it. A plain `channelscope validate` on `graph/` reports
43 references it cannot resolve (rule V07), all of them to the two withheld records:
38 from the check result records, 2 from the run records and 3 from the table records
(each check record, current or revised, names S13's method). A reader can match each to `withheld.tsv` by hand, but
cannot recompute those two records' identifiers.

Two tables and 20 check results are outside the graph. O2's table and the 9ZO8/9ZOE table ship as files with
their headers, as the survey does, and their checks (O2's two checks and six planted faults; the
evening run's two checks and ten planted faults) are read from those headers into `checks.tsv`,
not recorded. The recording tool reads a run's environment from the run records on either side of it, each within 24
hours, or from the run's own header, and O2's run has neither; the 9ZO8/9ZOE script pins its imported code through
another table's header, which the tool does not read, and its printout's line for each planted fault was not kept.
S13's table holds every structure's radius by A and by O2's window, re-measured and checked equal to those two tables at
the hundredth (check R0). R0 holds on the arithmetic that ran: where O2's window has a second reading at its edge, another platform's arithmetic can take it, as the Linux run of 14 October 2026 (UTC) did for 6X33 (`rerun/logs/linux_20261014_run_38632949031_gate.log`), and S13's code stops at any difference at the hundredth, so on that arithmetic its run would have stopped there.

**The re-run.** `rerun/rerun_gate.py` fetches each coordinate file by its retrieval record, checks its SHA-256,
re-measures all 26 with the release's code, and compares every radius at the hundredth and every class strictly.
It compares every atom, zg* − zg and O2's window too, admitting three readings that the method leaves to the platform, each named where it occurs: zg* − zg, the gate's own height less O2's height along B's axis (column `zg_star_minus_zg`), by its magnitude, since the axis is an eigenvector whose sign LAPACK may return either way; O2's window with its 3 Å edge samples kept or dropped; and an atom whose value ties, within 1e-9 Å, with the one the platform finds (in symmetric models, the same atom in another of the four chains). On each entry's own values it then plants faults that the comparison must catch, and readings it must admit. This release's build ran it (Windows AMD64, CPython 3.12.14, zlib 1.3.2, numpy 2.5.3; `rerun/logs/build_rerun.log`): all 26 the same, 0 with an admitted reading, O2's window with a second reading in 11, tied atoms in 5, and all 404 plants as stated. It wrote every reading of O2's window to `rerun/window_readings.tsv`; which edge sample that table calls lower or upper follows the sign of B's axis as this build's LAPACK returned it, and where atoms tie it names this build's pick. On 14 October 2026 (UTC), the re-run as it then stood, which compared those three readings strictly, passed on this project's Windows machine (`rerun/logs/windows_20261014_gate.log`) and failed on Linux in three places, all of these kinds (`rerun/logs/linux_20261014_run_38632949031_gate.log`): the sign of zg* − zg for 8X4A and 8X4C, and O2's window for 6X33 (3.89 Å against 4.05 Å). The PDB released revision 1.1 of 9ZO8 and 9ZOE on 14 October 2026, after both were measured at revision 1.0,
which it no longer serves. For these two the harness rebuilds the measured file from the file the PDB serves now, with
the patch this release carries (`rerun/patches/`, applied by `rerun/rebuild_revision.py`): it puts back
13 lines of 1.0 in place of 13 of 1.1, removes
the 40 lines 1.1 added, and compresses the text with zlib at level 9 behind the
measured file's own gzip header. The rebuilt file must then have the SHA-256 its retrieval record holds, like any
other. The rebuild depends on the deflate library of the Python that runs it: it gave the measured bytes with zlib
1.3.2 on Windows (this build's re-run, above, and the clean-clone re-run of 14 October 2026, UTC: `rerun/logs/windows_20261014_python.log`
and `rerun/logs/windows_20261014_gate.log`) and with zlib 1.3 on Linux (the workflow run that day: `rerun/logs/linux_20261014_run_38632949031_python.log` and
`rerun/logs/linux_20261014_run_38632949031_gate.log`), and, in a separate test that day whose log this release does not carry,
with zlib 1.3.2 on Linux; while a Python whose zlib is zlib-ng, as CPython 3.14's Windows
builds are, gives other bytes, which are refused with the cause named; so the repository's commands pin CPython 3.12.
The pin fixes the interpreter, not the zlib a Python links. Each patch was made by a script of this project, named in
the patch with its SHA-256 and commit, from the two held files, each checked against its retrieval record, and was
written only once it rebuilt the measured file byte for byte. Anyone can check a patch by the SHA-256s it must give,
but no one else can make it again, since the PDB no longer serves the measured revision. If the PDB revises another of the
26 entries, that entry's re-run is refused; `revisions.tsv` names the revision each structure was measured at.

The scripts in `code/` are the ones that ran, less one docstring or comment line each that named a working session
(`code/code_changes.tsv`); `code/codedigest.py` shows that each copy holds the same code as the script that ran
(`code/digests.tsv`). Two of check S's tests cannot run outside this project's working history, and the harness
reports both as not run: F10 pins the bytes that ran, which carry a session identifier, and F11, whose code names a
file of this project's working tree, tests the run guard against one of its commits. Both ship as they ran. The harness
writes no bytecode, and without `--cache` it removes its temporary folder at the end.

**Names from the project's working tree.** The criteria, the code, the records, the curation files' headers and the
patches are carried as they were committed, ran or were made, so they name files of this project's working tree
(paths beginning `how/` or `what/`), which this repository does not publish, its commits, and its working orders
(SO-DOMAIN-nn). `manifest.json` names this release's builder by its path there, and each patch the script that made
it; neither is published.

**Licence.** What ChannelScope made is under CC BY 4.0. The structures' data and the RCSB's answers come from the PDB
under CC0 1.0, with the structures' authors credited, as the PDB encourages. The wwPDB's usage policy says: "Data files contained in the PDB archive are available under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication. Users of PDB data are encouraged to attribute the original authors of the PDB structure data where possible."
The RCSB PDB's usage policy repeats it and adds: "All data provided by RCSB PDB programmatic APIs are available under the same license." Both pages, as read on 12 October 2026, are in
this release with their retrieval records (`graph/raw/wwpdb/2026-10-12/usage_policies.html` and `graph/raw/rcsb/2026-10-12/usage_policy.html`). The three UniProt
entries under `graph/raw/uniprot/` (P11716, E9PZQ0 and P16960), carried with their retrieval records, are UniProt's,
under CC BY 4.0 with UniProt's disclaimer, as its licence page says; that page, as read on 11 October 2026, is carried
in the mappings release (`releases/ryr1_mappings_v0.1/graph/raw/uniprot/2026-10-11/help_license.json`). The patches in
`rerun/patches/` hold lines of the PDB's own files for 9ZO8 and 9ZOE, under the same CC0 1.0, their depositors credited
(`citations.tsv`). The quotations from
papers are short
passages given for citation, each with its locator (`quotations.tsv`); each paper's own terms, where this project holds
them, are in `citations.tsv`, and govern any other use.
