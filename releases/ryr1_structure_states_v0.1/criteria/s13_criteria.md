<!-- context_channelscope_s13_remeasurement_criteria.md as committed in b8b2e54a3b15a49ba8b4388e1fef8f5d4aa8d7a9; working-note references replaced as criteria/replacements.json lists -->
---
type: context
subtype: criteria
status: active
created: 2026-10-06
updated: 2026-10-06
last_edited_by: lumen
owner: agent
mission: mission_channelscope_poc_sprint
tags: [s13, o2, gate, re-measurement, criteria, pre-registration]
---

# S13: the gate measured again, with B read at the gate's own height (criteria)

> **Status: criteria, committed before the run.** Nothing in this note had run on a real structure when it was
> committed.
> - **Its critiques:** it was revised after independent critiques, each finding answered, and every change to B was
>   made before any real run.
> - **The run:** `how/runtime/channelscope/s13/gate_b_fixed.py --run COMMIT` runs once. Its guard refuses unless every
>   input it names is in that commit and unchanged since. From check R0 on, every run writes its record, with any error
>   that stops it, and a record is never overwritten.
> - **Check S, the synthetic tests, can be run alone** with `uv run --project how/runtime/channelscope --with
>   gemmi==0.7.5 --with biopython==1.88 python how/runtime/channelscope/s13/check_gate_b_fixed.py`. Biopython 1.88 and
>   numpy 2.5.3 are the project's lock.
>
> Written by a fork of session `[a working record, not public]`.

## Why this measurement
- **The decision** (S13, the operator, 2026-10-06, 14:24:08 IST; [a working note, not public]): accept O2's
  classes as measured; measure the gate again with implementation B fixed, as a new measurement whose pass rules are
  committed before it runs, keeping the first run intact; and source the 2 Å and 3 Å lines before any public use. The
  same note adds: "any pore radius quoted in public is program A's, the direct measure of the gate".
- **The fault** (O2's diagnosis, [a working note, not public]): B took the least probe value within
  3 Å of the gate's height, and in open channels that window reached a second constriction below the gate. It caused
  check G1's radius failures (7M6L, 7T65, 6X35) and the one missed planted fault (5TB0, gate moved 4 Å outward, held
  at 1.98 Å).

## The structures
O2's 24 (9NMO, 9NMN, 9NMQ, 9NMP, 8VJJ, 8VJK, 8X4A, 8X4B, 8X4C, 7M6A, 7M6L, 5TB0, 5T9V, 7T64, 7T65, 9CGP, 9CGQ, 6W1N,
6X32, 6X33, 6X34, 6X35, 6X36, 9PWO), and rabbit 9ZO8 and 9ZOE, measured under O2's criteria after its run
(`curation/s2_gate_9zo8_9zoe.tsv`): 26 in all, 14 closed and 12 open by run 1. The gate residue is O2's (rabbit I4937,
mouse and pig I4935).

## What is measured
- **A, unchanged.** Imported from `how/runtime/channelscope/o2/gate.py`. Refused unless that file hashes to the pinned
  `sha256:d54a4159…59ca2`, written into the script, and O2's table names the same hash.
- **B, O2's window, kept as a second, named quantity.** O2's B as it ran (`gate_b_window`, 3 Å), recomputed for all 26,
  with the atom that sets it, and checked against the committed tables (R0), as `s2/gate_9zo8_9zoe.py` did. It is
  reported beside the fixed B and is not a check of the pore.
- **B, fixed.** It keeps O2's parser (gemmi), chain choice (the four longest polymer chains) and axis (the
  transmembrane region's centroid, the gate's residue −117 to +100, along its distinct principal axis). What changes,
  all decided before any real run:
  1. **The height, zg\*:** the mean, over the four chains, of the height along B's axis of each chain's gate-residue
     heavy atom nearest the axis (less its radius). These are the atoms A measures. O2's zg, the centroid of all the
     gate residues' heavy atoms, can sit 1 to 2 Å from the side-chain atoms that close the pore, and a slab centred on
     it misread synthetic pores whose CD1 sat 1.5 to 2.0 Å below the CA plane (check F4's control).
  2. **The atoms:** only heavy atoms within a slab 2.5 Å deep, 1.25 Å either side of zg\*, less than half a helical
     turn (5.4 Å). Atoms just outside the slab are ignored, though they may lie nearer the probe. Revision 1's B, a
     probe point at the gate's height over all atoms, still read a ring one turn below whenever the gate was wider than
     about 4.2 Å. On a synthetic 5.5 Å gate it read 4.208 Å, set by the ring's GLN 4933 NE2, so G1′ failed by 1.29 Å;
     the fixed B reads 5.500 Å, set by ILE 4937 CD1 (F3). 7T65, 9ZOE, 9PWO and 8X4B read wider than 5.2 Å by A.
  3. **The value:** the least distance, from the probe at zg\* on B's axis, of an atom within the slab, less that
     atom's radius. The run records the atom that sets it.
  4. **A refusal:** when fewer than four polymer chains exist. O2's B has no such check: it takes the four longest, so
     given three it measures three.
- **Unchanged:** the atom radii (C 1.70, N 1.55, O 1.52, S 1.80 Å); the classes (closed below 2.0 Å, open above 3.0 Å,
  indeterminate between). Each class is also given at thresholds 0.5 Å lower and higher (columns `class_at_minus_0.5A`
  and `class_at_plus_0.5A`, A/B, as O2's table gives them).

**What the agreement can and cannot show.**
- **What it tests:** both A and the fixed B read the gate ring, and zg\* is set by the same atoms A measures. Their
  agreement therefore tests the parser, the chain choice and the axis, not the pore's shape by a second, independent
  route.
- **The class half of G1′ is already known for the 12 open structures:**
  - the fixed B reads only some of the atoms O2's window read at a height within its reach, so it can read no
    narrower than O2's window, less at most 0.125 Å for the window's 0.25 Å steps;
  - O2's window read all 12 at 3.20 Å or more (run 1; 4.07 Å for 9ZOE);
  - so the fixed B will class them open, provided zg\* lies within 3 Å of O2's zg. The run reports zg\* − zg for every
    structure.
  The class half is a live test only for the 14 closed structures.
- **The radius half is largely known for five open structures:** 7M6L, 7T65, 6X35, 8X4B and 9NMN, where O2's diagnosis
  read B at the gate's height (a point probe at O2's zg) within 0.31 Å of A. It is new for the other 21.

**I4937 in open structures.** Melville et al. 2022 (`melville_ryr1_membrane_embedded_2022.html`, after Figure 4's
caption): "In liposomes and detergent, the pore helix rotates such that I4937 is no longer within the pore in the open
state of the channel. In the open state in liposomes, the radius of the pore residue could not be measured at I4937
(Smart et al., 1993), though by estimation it remains at approximately 4 Å".
- **What it means here:** in an open structure, A gives how far I4937's atoms sit from the axis, which is then not
  necessarily the pore's radius. The fixed B gives the least distance at I4937's height over the atoms within the slab,
  set by whatever lines the pore there.
- **O2's diagnosis** saw B at the gate's height agree with A within 0.31 Å in five open structures, so there the two
  may still read one ring. The run says which atom sets B.

## Checks and perturbations, each with what fails it

**Live** means the outcome depends on the real structure in a way not known beforehand. The other entries are labelled
for what they are.

| Entry | What it tests | Kind | It fails, or is missed, if |
|---|---|---|---|
| S | The synthetic tests F1 to F16 (`s13/check_gate_b_fixed.py`), run again by the run itself before any real structure. F14 tests the replica that names A's atom; F15 and F16 dry-run the run's record end to end on synthetic stand-ins | — | Any test fails, or any control is not caught. The run then refuses |
| R0 | A and O2's window reproduce the committed radii first | live | Any of the 26 differs at the hundredth from `o2_gate_measurements.tsv` or `s2_gate_9zo8_9zoe.tsv` |
| G1′ | A and the fixed B agree | class half live for the 14 closed; radius half live for 21 | For any structure, their classes differ, or their radii differ by more than 1.0 Å |
| G2′ | The positive controls (Woll and Van Petegem 2022: 5TB0 "a closed RyR1 pore", 5T9V "an open RyR1") | only 5TB0's fixed B is live (A's classes are committed, and 5T9V's fixed B is open in advance) | Either is classed otherwise by A or the fixed B |
| P1-A | 5TB0's gate atoms 4 Å outward | arithmetic: `gate_a` adds the move to every distance | A does not class it open |
| P1-B | The same, for the fixed B | seen in O2's diagnosis: "At the gate's own height B reads 4.19 Å, which is open" (O2's note) | The fixed B does not class it open |
| P2 | 5T9V with one RyR1 chain's atoms removed from the structure text | live | Either implementation measures it rather than refusing it |
| P3 | 9NMO with its gate residues renamed valine in the structure text | live | Either implementation measures it rather than refusing it |
| P4 | 5T9V with a ring of four nitrogen atoms planted 5.4 Å below zg\*, 2.55 Å from B's axis | by construction: the slab drops it | The fixed B with the ring differs from it without by 0.005 Å or more |
| P5 | 5TB0 with the fixed B read 2 Å above, then 2 Å below zg\* | live | G1′ passes for either shifted reading |
| P6-A | 5T9V's gate atoms 3 Å inward | arithmetic | A does not class it closed |
| P6-B | The same, for the fixed B | by construction: the moved atoms stay in the slab, nearest | The fixed B does not class it closed |
| L1 | 5TB0 with each gate isoleucine's side chain (atoms beyond CB) turned 120° about its CA–CB bond in the structure text; A's atom (from a replica of A's arithmetic that must equal `gate_a` exactly) and the fixed B's atom are recorded | live | A and the fixed B disagree on the turned structure (G1′), or the turn moved A by less than 0.1 Å (then L1 tested nothing) |
| L2 | 7M6L, 7T65 and 6X35, whose O2's window O2's diagnosis found set by a residue one turn below | live: the real second constriction, not a planted one | The fixed B is set by the same residue as O2's window, when that residue is not the gate |

Revision 1's P3 renamed by a flag in O2's code, which raises the refusal itself (`o2/gate.py`, lines 101 and 144), so it
could not fail. P2 and P3 now edit the structure text; L1 and L2 are new and live.

**Why the tolerance stays at 1.0 Å.** It is O2's check G1, committed in `b932329` before O2's first run. O2's diagnosis
has since seen B agree with A within 0.31 Å at the gate's own height, on five structures. A tighter tolerance chosen now
would be chosen knowing that outcome. The critiques judged keeping it defensible.

## How each outcome is read, fixed before the run
- **All pass:** see *What the result may and may not change*.
- **R0 fails, or anything stops the run after R0 begins:** the run writes its record with the error and whatever it
  had measured, and measures nothing further. Nothing is re-run without finding the cause, and since the record is
  never overwritten, a new run needs the operator's word.
- **G1′'s class half fails (possible only among the 14 closed, if zg\* lies within 3 Å of zg):** the structure goes back
  to the operator, as S13 reopened for it. No class changes meanwhile.
- **G1′'s radius half fails:** the structure is listed with both radii and the atom that set B. If that atom is not the
  gate residue's, the record says "the pore at I4937's height is lined by" that residue, as Melville et al. lead one to
  expect in open structures. The claim that two implementations read the gate itself is not made for it.
- **G2′ fails** (in practice, 5TB0's fixed B not closed): the fixed B does not read the closed gate of a published
  closed pore. No fixed-B value is used for any claim, the record is kept, and the failure goes to the operator.
- **P1-B is missed** (5TB0 moved 4 Å outward not read open): another atom within the slab holds the closed reading.
  This contradicts O2's diagnosis (4.19 Å at the gate's height by a point probe). The claim that the fixed B reads the
  gate itself is not made for any closed structure. The record carries P1-B's value and the atom that held it.
- **P2 or P3 is missed** (a faulted file measured, not refused): that implementation's refusal does not protect it, so
  its values are not used for any claim until the cause is found. A fix after the run needs the operator's word.
- **P5 is missed** (a reading 2 Å off the gate still passes G1′ on 5TB0, which may happen if its pore stays narrow
  there): read as a limit of G1′, not a failure of the measurement. Any agreement claimed then carries "G1′ cannot
  detect a reading 2 Å off the gate's height in a closed pore".
- **L1 is missed:**
  - if A and the fixed B disagree on the turned gate, they do not follow the same atoms when the gate's side chains move;
  - if the turn moved A by less than 0.1 Å, L1 tested nothing on real 5TB0.
  Either way, the agreement claim does not rest on L1, and the record carries both values and both atoms.
- **L2 is missed** (the fixed B still set by the residue one turn below): the slab has not excluded the real second
  constriction there. The claim is not made for that structure.
- **P1-A, P4, P6-A or P6-B is missed:** the code is not what this note describes, since these can only pass. The run's
  values are not used, and the cause is found first.

Whatever the outcome, nothing is tuned after the run. A change to the code or these rules needs the operator's word, and
is a new measurement.

## The guard, and every input the run depends on
`--run COMMIT` resolves COMMIT to its full hash, which it records, never a symbolic name. It refuses unless each of these
is in that commit and unchanged since:
- this note;
- `how/runtime/channelscope/s13/gate_b_fixed.py`;
- `how/runtime/channelscope/s13/check_gate_b_fixed.py`;
- `how/runtime/channelscope/o2/gate.py`;
- `what/evidence_graph/curation/o2_gate_measurements.tsv`;
- `what/evidence_graph/curation/s2_gate_9zo8_9zoe.tsv`;
- `what/evidence_graph/records/retrieval.jsonl`.

The 26 coordinate files are git-ignored, so each is checked against its retrieval record instead.

**What the run records:**
- it reruns check S first and refuses if any test or control fails;
- its record carries check S's counts and the library versions (Biopython, gemmi, numpy);
- every run on real structures writes `curation/s13_gate_remeasurement.tsv`, and refuses if that file exists;
- for each structure, A's value and atom, the fixed B's value and atom, O2's window's value and atom, and zg\* − zg;
- every check and perturbation on its own line, written in full with its values and atoms;
- from check R0 on, any stop, whether R0's own failure or an error, writes the record with the error and what was
  measured before it (dry-run by F15 and F16).

**Already committed** (`c26fd23`): `s2_gate_9zo8_9zoe.tsv`, its script, its fetch plan, and the retrieval records of
9ZO8 and 9ZOE. **To be committed together before the run:** this note and both s13 scripts.

Check F11 tests the guard against `a02283b`, so that it still holds after the criteria's commit:
- it refuses the run there, where the criteria and scripts are absent;
- it passes for files committed unchanged there;
- it refuses a file changed since;
- it refuses a name that is not a commit.

## What the result may and may not change
- **If every check passes:** run 1's qualified sentence ("in open channels the two corroborate a wide pore rather than
  reading the gate twice") stays as it is. Beside it goes a new, dated sentence: "S13's re-measurement: A and B read at
  the gate's own height agree, with the atom that sets B named". For open structures it adds "the class half known in
  advance". The fixed B's radii may then stand beside A's in this vault's records.
- **What it cannot change:**
  - the classes, accepted under S13;
  - O2's first run and its table, including its check G1 failure and its missed planted fault;
  - the pairs O3's rule chose;
  - which radius is quoted in public, which stays A's.
- **Draft 3 and the pair 9ZO8/9ZOE:** draft 3 may cite the run only as what it is, since it measures state, not a
  feature on E or G, and so may precede O3's commit:
  - for 9ZOE, the radius and the atom that sets B. Its class half was known in advance, so it is no corroboration of
    its class, which rests on A, O2's window and the depositors' words;
  - for 9ZO8, a closed structure, the class half is a live test.
  A G1′ failure for either goes into draft 3's limits; it does not by itself drop the pair. Any change to the candidate
  pairs goes to the operator.

## The 2 Å and 3 Å lines, before any public use

**Status: no source found.** O2's note calls the lines "this survey's convention, not a value from the literature". No
snapshot in `what/references/_snapshots/` and no quotation table states them. The archive's own radii (its
`what/references/ryr1_states_templates_numbering.md`: 7M6A "open" at 3.2 Å) carry the 7M6A state mislabel, so they are
not a source (SO-DOMAIN-10).

**What the vault holds that bears on them.** These are candidates, not yet quotation rows: each must be quoted and
checked before use.

| Source (snapshot) | Locator | Words |
|---|---|---|
| Yan et al. 2015 (`yan_rabbit_ryr1_near_atomic_2015.xml`) | "A closed channel" | "The pore radius at the constriction point is less than 1 Å, impermeable to a completely dehydrated Ca 2+ ion." |
| Zalk et al. 2015 (`zalk_mammalian_ryr_structure_2015.xml`) | "RyR1 is a 6TM ion channel" | "… and the diameter of hydrated Ca 2+ (8.2 Å 27 ) we conclude that the pore is in a non-conducting state." |
| des Georges et al. 2016 (`des_georges_ryr1_gating_activation_2016.html`; already row `desgeorges2016_constricted`, FR-16) | "Activation Module Changes that Prime the Channel for Opening" | "The pore remains constricted at I4937 to an aperture insufficient to allow passage of a hydrated monovalent or divalent cation." |
| Nayak and Samsó 2022 (`nayak_samso_ryr1_ca_inactivation_2022.xml`) | "Differences between closed, open, and inactivated conformations" | Closed: "a radius constricting to 1 Å at the known hydrophobic gate Ile4937". Inactivated: "a pore diameter at the Ile4937 gate of ~2 Å when considering the side chains … making it impermeable to Ca 2+ ions" |
| Iyer et al. 2020 (`iyer_r164c_equivalent_site_sciadv_2020.xml`) | "Mutant RyR1 exhibits a closed-dilated pore under closed-state conditions" | "an increased radius from 0.8 Å (PDB: 5TB0) to ~1.2 Å at the gating residue, I4937" |
| Iyer et al. 2022 (`iyer_y522s_cryoem_pnas_2022.xml`) | "The Pore Is Marginally Affected by the Mutation." | "remained closed, with a radius of 1.0 Å at the gating residue Ile4937" |
| Weninger et al. 2026 (`weninger_rosuvastatin_ryr1_ncomms_2026.html`) | Results, "Structure of RyR1 in complex with rosuvastatin" | "(calculated using HOLE) confirmed the closed and open conformations (minimum pore radius: ~0.8 versus ~3.0 Å, respectively)" |
| Melville et al. 2022 (`melville_ryr1_membrane_embedded_2022.html`) | The text after Figure 4's caption (its nearest heading) | "the pore helix rotates such that I4937 is no longer within the pore in the open state of the channel. In the open state in liposomes, the radius of the pore residue could not be measured at I4937 ( Smart et al., 1993 ), though by estimation it remains at approximately 4 Å" |
| Wei et al. 2025 (`wei_ryr1_s0_gating_2025.xml`) | "Conformational transitions of the whole and TM domain of RyR1 in different structures." | "The pore diameter expands from 6.2 to 13.8 Å, which indicates the channel is in the open state" |

**A reading.**
- **Closed:** the closed radii reported at RyR1's gate are 0.8 to 1.2 Å, all below the 2.0 Å line.
- **Open:** one open radius by HOLE (about 3.0 Å, Weninger et al. 2026) would not count as open under this survey's
  lines, which ask for more than 3.0 Å: it would be indeterminate. That is the paper behind 9ZOE, which A reads at
  5.28 Å. Melville et al. could not measure the open pore at I4937 and estimate about 4 Å.
- **The published numbers are not A's measure.** HOLE reports the largest sphere along the whole pathway, so its
  minimum may sit at another constriction. A is the gate's own heavy atoms' least distance from the axis, less their
  radii. Whether Weninger et al.'s minimum lies at the gate is not stated in the words above.
- So anchoring the lines to these papers would itself be a premise.

**Proposed for public use (the operator's to decide):** give A's radius, the depositors'
words and the class. With the class, say that the lines are this survey's convention, and set beside them the quoted
published radii, checked as quotation rows, with the method difference stated. The alternative is no class in public:
the radius and the depositors' words alone.

## Choices that rest on synthetic pores, and other limits
- zg\* reads the atoms A measures, through B's own axis: a loss of independence, named above.
- The slab's depth (2.5 Å), P4's geometry and L1's turn (120°) were chosen on synthetic pores, not on any real
  structure.
- L2 takes 7M6L, 7T65 and 6X35 from O2's diagnosis. The run recomputes which residue sets O2's window for each, and
  does not assume it.

## See Also
- [a working note, not public]: O2's criteria, run and diagnosis
- [a working note, not public]: decision S13
- [a working note, not public]: 9ZO8 and 9ZOE's gate under O2's criteria
