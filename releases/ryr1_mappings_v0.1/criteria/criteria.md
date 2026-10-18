# The criteria, as committed

From the release `ryr1_mappings_v0.1`. Each check's criterion is given at the commit that first held it and at each commit that amended it before the check's recorded run. The commits are in the project's private working history. Roles in square brackets stand where the source names a person, another project, a session or a local path; `criteria.json` lists each replacement.

## G1 (human (M01))

**Commit `79ff30b445f40b755b2cf966e8f0887d60faae65`, 2026-09-28 22:03:58 IST** (private working history)

| G1 | **Genome to protein.** Translating the MANE Select coding sequence, assembled from GRCh38 by the exon model, gives exactly P21817-1 and NP_000531.2: 5,038 residues and a stop | Any residue differs, or the stop is missing or early |

## G2 (human (M01))

**Commit `79ff30b445f40b755b2cf966e8f0887d60faae65`, 2026-09-28 22:03:58 IST** (private working history)

| G2 | **Two annotations agree.** Ensembl (ENST00000359596.8) and RefSeq (NM_000540.3) give the same coding exon boundaries on GRCh38. MANE Select means they should | Any coding boundary differs. The difference is investigated before going on |

## G3 (human (M01))

**Commit `79ff30b445f40b755b2cf966e8f0887d60faae65`, 2026-09-28 22:03:58 IST** (private working history)

| G3 | **The map is complete and exact.** Every coding base maps to exactly one position in one codon: 15,117 bases, 5,038 codons plus a stop, three bases per residue. A codon split by an intron maps to both exons. The count of split codons equals the count recomputed independently from the exon model (50 at design). The strand is read from the annotation, never assumed | A residue has other than three bases; a base is used twice; the split-codon counts disagree; or the strand is hard-coded |

## G4 (human (M01))

**Commit `79ff30b445f40b755b2cf966e8f0887d60faae65`, 2026-09-28 22:03:58 IST** (private working history)

| G4 | **Independent descriptions agree.** Sample variants, by a rule fixed now:<br>• ClinVar VCV000012964;<br>• the RYR1 variants ClinVar lists as reviewed by an expert panel, taken at even spacing along GRCh38 to give 20;<br>• the first intronic variant and the first split-codon variant in position order, if the set has none.<br>For each, ClinVar's GRCh38 position, its `c.` description and its `p.` description all agree with the map. An intronic variant maps to no residue | Any disagreement |

## G5 (human (M01))

**Commit `79ff30b445f40b755b2cf966e8f0887d60faae65`, 2026-09-28 22:03:58 IST** (private working history)

| G5 | **Coordinates carry their assembly.** A genome position given without its assembly, or on GRCh37, is refused. A GRCh37 position appears only as a cross-reference quoted from its source | Any position is used without its assembly |

## G6 (human (M01))

**Commit `a5b65834f873dac7810c4de45fa60ef4c86f184e`, 2026-09-28 23:31:54 IST** (private working history)

| G6 | **The archive's recorded exon map.** *Added 2026-09-28, after G1–G5 were committed (`79ff30b`), on re-reading the archive at the operator's prompting. It adds a comparison and loosens nothing.* The archive holds a coordinate-derived exon→residue map for all 106 exons on the same transcript and protein (`what/references/ryr1_exon_domain_map.md`, with its data bundle; read-only). Our re-derived map gives the same residue range for each exon, and reproduces the five published HGVS→exon anchors the archive records: R614C→17, R530H→15, Ser2843→54, I4898T→102, A2437V→45. The archive is a quarry, not a source (SO-DOMAIN-10): our map is built from our own logged calls first, and only then compared | Any exon's residue range differs, or any anchor lands in a different exon. The difference is investigated; either side may be wrong. A difference traced to a different transcript or assembly on the archive's side is recorded and dismissed, not tuned away |

## A1 (human (M01))

**Commit `8e84a8bc130fda0d9f7f230da70c4095a191ee62`, 2026-09-28 16:09:25 IST** (private working history)

| A1 | **One human numbering.** UniProt P21817-1 (sequence version 3) and RefSeq NP_000531.2 (MANE Select) are identical, residue for residue. At design they matched: MD5 `0566ca43dd75ad82b878f07bc52bf46a`, retrieved 2026-09-28 | They differ. The mission then records both numberings, and a mapping between them, before going on |

## A2 (human (M01))

**Commit `8e84a8bc130fda0d9f7f230da70c4095a191ee62`, 2026-09-28 16:09:25 IST** (private working history)

| A2 | **Isoforms are guarded.** A position given on P21817-2 or P21817-3 (which lack residues 3481–3485 and 3865–3869, respectively) is refused, or translated explicitly. Tested at a position after each deletion | Any such query silently uses P21817-1 numbers |

## A3 (human (M01))

**Commit `8e84a8bc130fda0d9f7f230da70c4095a191ee62`, 2026-09-28 16:09:25 IST** (private working history)

| A3 | **Two aligners agree.** Global alignments from two independent implementations (method A: Biopython's `PairwiseAligner`; method B: a separately written program chosen in objective 4, not a wrapper around A) give the same residue pairs | Any pair differs, unless the difference is a gap that can be placed in more than one position with an equal score. Each such residue is listed and flagged *ambiguous* in the mapping |

## A4 (human (M01))

**Commit `8e84a8bc130fda0d9f7f230da70c4095a191ee62`, 2026-09-28 16:09:25 IST** (private working history)

| A4 | **Indels map to nothing, and the arithmetic closes.** Every residue in an insertion or deletion maps to "no correspondence", never to a neighbour. Aligned pairs + human-only residues = 5,038, and aligned pairs + rabbit-only residues = 5,037 | A residue in an indel maps to a residue, or either sum fails |

## A5 (human (M01))

**Commit `8e84a8bc130fda0d9f7f230da70c4095a191ee62`, 2026-09-28 16:09:25 IST** (private working history)

| A5 | **Round trip.** Human to rabbit to human returns the starting residue at every aligned position. Wherever the alignment calls a pair identical, its amino acids match | Any exception |

## A6 (human (M01))

**Commit `8e84a8bc130fda0d9f7f230da70c4095a191ee62`, 2026-09-28 16:09:25 IST** (private working history)

| A6 | **The depositors' own correspondences.** Some rabbit structures' papers state the human equivalent of a residue they mutated or discuss. The candidates, from entry titles on 2026-09-28, are the Y523S mutant entries (7T64, 7T65, 9CGP, 9CGQ) and the R164C entry (6WOT). The mapping gives the stated human residue, with the same amino acid. The list comes from the papers (objective 3) and is committed before the mapping is queried. An entry whose paper states no equivalent is dropped, with the reason recorded | Any mismatch. A mismatch is investigated as a possible error on either side |

**Commit `a5b65834f873dac7810c4de45fa60ef4c86f184e`, 2026-09-28 23:31:54 IST** (private working history)

| A6 | **The depositors' own correspondences.** Some rabbit structures' papers state the human equivalent of a residue they mutated or discuss. The candidates, from entry titles on 2026-09-28, are the Y523S mutant entries (7T64, 7T65, 9CGP, 9CGQ) and the R164C entry (6WOT). The mapping gives the stated human residue. The list comes from the papers (objective 3) and is committed before the mapping is queried. An entry whose paper states no equivalent is dropped, with the reason recorded.<br>**Amended 2026-09-28,** after A1–A10 were committed (`8e84a8b`), from a source read for the tetramer question ([a working note, not public]). It adds four correspondences and one exception; it loosens nothing else.<br>• **Four correspondences seeded now,** stated outright by Xu et al. 2008 and verified against its text: human G4899 ↔ rabbit G4898; human ΔV4927/I4928 ↔ rabbit ΔV4926/I4927; human R109 ↔ rabbit R110; human M485 ↔ rabbit L486.<br>• **The offset changes sign** along the chain: +1 near the C-terminus, −1 near the N-terminus. A constant shift is not merely imprecise, it has the wrong sign somewhere.<br>• **The amino-acid clause now has an exception.** The original wording required the same amino acid on both sides. At human 485 the species genuinely differ — human methionine, rabbit leucine — and the authors flag it: "Because Leu-486 in the rabbit sequence is not conserved…". Where the source states non-conservation, a differing residue is expected, not a failure | A stated correspondence is not reproduced by the mapping. An amino-acid mismatch fails **unless** the source itself states the position is not conserved between species, in which case the mapping must still give the stated residue number. A mismatch is investigated as a possible error on either side |

**Commit `70db3fb561f62f182ed938c1793733ac0bacaca1`, 2026-10-03 02:10:43 IST** (private working history)

| A6 | **The depositors' own correspondences.** Some rabbit structures' papers state the human equivalent of a residue they mutated or discuss. The candidates, from entry titles on 2026-09-28, are the Y523S mutant entries (7T64, 7T65, 9CGP, 9CGQ) and the R164C entry (6WOT). The mapping gives the stated human residue. The list comes from the papers (objective 3) and is committed before the mapping is queried. An entry whose paper states no equivalent is dropped, with the reason recorded.<br>**Amended 2026-09-28,** after A1–A10 were committed (`8e84a8b`), from a source read for the tetramer question ([a working note, not public]). It adds four correspondences and one exception; it loosens nothing else.<br>• **Four correspondences seeded now,** stated outright by Xu et al. 2008 and verified against its text: human G4899 ↔ rabbit G4898; human ΔV4927/I4928 ↔ rabbit ΔV4926/I4927; human R109 ↔ rabbit R110; human M485 ↔ rabbit L486.<br>• **The offset changes sign** along the chain: +1 near the C-terminus, −1 near the N-terminus. A constant shift is not merely imprecise, it has the wrong sign somewhere.<br>• **The amino-acid clause now has an exception.** The original wording required the same amino acid on both sides. At human 485 the species genuinely differ — human methionine, rabbit leucine — and the authors flag it: "Because Leu-486 in the rabbit sequence is not conserved…". Where the source states non-conservation, a differing residue is expected, not a failure<br>**Added 2026-10-03, on the operator's word (01:50 IST), before any mapping exists:** a ninth correspondence, A6-09, from Rossi et al. 2007 ([a working note, not public]), found on 2026-10-02 while reading for release `exon_map_v0.4`. Its Methods: "the human deletion mutant R4837fsX4839 corresponds to rabbit R4836fsX4838", that is human 4837 ↔ rabbit 4836, +1 as Xu 2008 states near the C-terminus. The paper names no rabbit residue, so the amino-acid clause does not apply on the rabbit side; the mapping must give the stated number. It adds a way to fail and loosens nothing ([a working note, not public]) | A stated correspondence is not reproduced by the mapping. An amino-acid mismatch fails **unless** the source itself states the position is not conserved between species, in which case the mapping must still give the stated residue number. A mismatch is investigated as a possible error on either side |

**Commit `0bf812c5daf223825968fbfb898a9a4e63ced03a`, 2026-10-03 14:00:22 IST** (private working history)

| A6 | **The depositors' own correspondences.** Some rabbit structures' papers state the human equivalent of a residue they mutated or discuss. The candidates, from entry titles on 2026-09-28, are the Y523S mutant entries (7T64, 7T65, 9CGP, 9CGQ) and the R164C entry (6WOT). The mapping gives the stated human residue. The list comes from the papers (objective 3) and is committed before the mapping is queried. An entry whose paper states no equivalent is dropped, with the reason recorded.<br>**Amended 2026-09-28,** after A1–A10 were committed (`8e84a8b`), from a source read for the tetramer question ([a working note, not public]). It adds four correspondences and one exception; it loosens nothing else.<br>• **Four correspondences seeded now,** stated outright by Xu et al. 2008 and verified against its text: human G4899 ↔ rabbit G4898; human ΔV4927/I4928 ↔ rabbit ΔV4926/I4927; human R109 ↔ rabbit R110; human M485 ↔ rabbit L486.<br>• **The offset changes sign** along the chain: +1 near the C-terminus, −1 near the N-terminus. A constant shift is not merely imprecise, it has the wrong sign somewhere.<br>• **The amino-acid clause now has an exception.** The original wording required the same amino acid on both sides. At human 485 the species genuinely differ — human methionine, rabbit leucine — and the authors flag it: "Because Leu-486 in the rabbit sequence is not conserved…". Where the source states non-conservation, a differing residue is expected, not a failure<br>**Added 2026-10-03, on the operator's word (01:50 IST), before any mapping exists:** a ninth correspondence, A6-09, from Rossi et al. 2007 ([a working note, not public]), found on 2026-10-02 while reading for release `exon_map_v0.4`. Its Methods: "the human deletion mutant R4837fsX4839 corresponds to rabbit R4836fsX4838", that is human 4837 ↔ rabbit 4836, +1 as Xu 2008 states near the C-terminus. The paper names no rabbit residue, so the amino-acid clause does not apply on the rabbit side; the mapping must give the stated number. It adds a way to fail and loosens nothing ([a working note, not public])<br>**Added 2026-10-03, on the operator's word (13:46 IST), before any mapping exists:** a tenth correspondence, A6-10, from Nayak and Samsó 2022 (eLife 11:e75568), found the same day while reading for [a working note, not public]. Its Results: "FF 4923–4924 (human sequence; equivalent to rabbit FF 4922–4923)", a two-residue stretch in S6, human 4923–4924 ↔ rabbit 4922–4923, +1 near the C-terminus as Xu 2008 and Rossi 2007 state. Both sides are named FF, so the amino-acid clause applies. It adds a way to fail and loosens nothing | A stated correspondence is not reproduced by the mapping. An amino-acid mismatch fails **unless** the source itself states the position is not conserved between species, in which case the mapping must still give the stated residue number. A mismatch is investigated as a possible error on either side |

## A7 (human (M01))

**Commit `8e84a8bc130fda0d9f7f230da70c4095a191ee62`, 2026-09-28 16:09:25 IST** (private working history)

| A7 | **An independent figure.** Global identity and the count of aligned pairs agree with [a peer]'s recorded realignment: 96.86% over 5,029 pairs ([a peer's project], 2026-09-28) | The difference exceeds 0.5 percentage points or 10 pairs, and stated parameter differences don't explain it |

## A8 (human (M01))

**Commit `8e84a8bc130fda0d9f7f230da70c4095a191ee62`, 2026-09-28 16:09:25 IST** (private working history)

| A8 | **The store holds it properly.** Every record validates against schema v0.1 and carries provenance, and the mapping table's checksum is in its record. A clean re-run from the logged calls reproduces the table's checksum | Any invalid record, or a checksum mismatch. A new UniProt entry version with an unchanged sequence version is explained, not failed |

**Commit `70db3fb561f62f182ed938c1793733ac0bacaca1`, 2026-10-03 02:10:43 IST** (private working history)

| A8 | **The store holds it properly.** Every record validates against schema v0.1 and carries provenance, and the mapping table's checksum is in its record. A clean re-run from the logged calls reproduces the table's checksum<br>**Clarified 2026-10-03 by the operator (01:50 IST), before any alignment:** "schema v0.1" is read as "the schema version the release declares", option 2 of [a working note, not public]. Nothing that lets A8 fail is removed. Objective 5 reports A8 against the declared version, with the count of records valid under v0.1 beside it | Any invalid record, or a checksum mismatch. A new UniProt entry version with an unchanged sequence version is explained, not failed |

## A9 (human (M01))

**Commit `8e84a8bc130fda0d9f7f230da70c4095a191ee62`, 2026-09-28 16:09:25 IST** (private working history)

| A9 | **CQ-02 answers.** For positions fixed now, the query returns the expected shape: rabbit residue or "no correspondence", method, local identity, gap flag. The positions: human 1 and 5,038; the residue on each side of every indel; human 614 and 4938. A residue inside an insertion returns "no correspondence" (CQ-02's tier-1 check) | Wrong shape, a missing field, or the insertion check fails |

## A10 (human (M01))

**Commit `8e84a8bc130fda0d9f7f230da70c4095a191ee62`, 2026-09-28 16:09:25 IST** (private working history)

| A10 | **The visual is honest.** [a peer]'s figure reads release v0.1, not the working store. Its independent check is its own ([a peer's project]'s SO-DOMAIN-03), and the operator has reviewed it. Where it is hosted is the operator's decision (D1) | Any of these is missing |

## A11 (human (M01))

**Commit `258d6d96d721291549e2a612baaab34591a38716`, 2026-09-28 17:03:02 IST** (private working history)

| A11 | **The archive's recorded segments.** *Added 2026-09-28, after A1–A10 were committed (`8e84a8b`) and after Lumen saw a one-line summary of the archive's recorded offsets in its ontology (§5).* It adds a comparison and loosens nothing. Where the archive's grounding note (`what/references/ryr1_states_templates_numbering.md` §2, read-only) gives an exact offset for a segment, our mapping gives the same offset there. The archive calls its segment boundaries approximate, so boundaries are compared only at indels our two aligners agree on | An exact offset differs. The difference is investigated; the archive is a quarry, not a source (SO-DOMAIN-10), so either side may be wrong |

## O4 (mouse) (human-mouse)

**Commit `c26fd2320eca49d8577ceb9a8659eb0d6b54ced3`, 2026-10-06 19:40:05 IST** (private working history)

```yaml
# O4: what the mouse mapping's checks read. Proposed by a trial on 2026-10-06 (a fork of
# [a working record, not public]); nothing here is pre-registered until the main session commits it, and
# `channelscope m01 check-mapping` cannot read it as it stands (see `runner`).
# - A3, A4, A5: M01's criteria as written, with planted faults fitted to this alignment (M01's own faults name
#   human-rabbit positions).
# - A9: M01's criterion, with CQ-02's answers filtered to this mapping: CQ-02 answers once per mapping, so once mouse
#   and pig sit beside rabbit, a human residue has three answers.
# - A8: validation, the table's checksum against its record, and a re-run from the graph before the build. M01's
#   re-run from a named commit and its UniProt replay (a network call) wait for the real build.
# - A6, A7, A11 do not apply as written (rabbit's papers; [a peer]'s human-rabbit figure; the archive's rabbit table).
#   Stand-ins below, each a statement already held in this vault, never fetched for this.
build_inputs: curation/build_o4_mapping_mouse.yaml
runner: "channelscope o4 check-mapping (how/runtime/channelscope/src/channelscope/o4.py), written on 2026-10-06 after this file was, since M01's run_mapping_checks reads A6's rabbit list, A7's figure and A11's rabbit table, and its faults name human-rabbit positions"
a9_human_positions: [1, 5038, 614, 4938]
controls:
  - id: O4-mouse-gate
    human: "4938"
    object: "4935"
    residue: I
    source: "O2's reading by flanking sequence in each UniProt entry ([a working note, not public], Part 2): human I4938, mouse I4935"
a6_stand_in:
  - id: O4-mouse-01
    human: "4898"
    object: "4895"
    residue: I
    snapshot: what/references/_snapshots/zvaritch_ryr1_it_heterozygote_2009.html
    quotation: "Ryr1 I4895T/wt (IT/+) mice express a knockin mutation corresponding to the human I4898T EC-uncoupling mutation"
a7_stand_in: "none held in this vault; proposed: identity and pair count from a third, independently written aligner, or an independent check like [a peer]'s of 2026-10-04"
a11: "not applicable: the archive's grounding note gives human-to-rabbit and human-to-pig tables only"
```

## O4 (pig) (human-pig)

**Commit `c26fd2320eca49d8577ceb9a8659eb0d6b54ced3`, 2026-10-06 19:40:05 IST** (private working history)

```yaml
# O4: what the pig mapping's checks read. Proposed by a trial on 2026-10-06 (a fork of
# [a working record, not public]); nothing here is pre-registered until the main session commits it, and
# `channelscope m01 check-mapping` cannot read it as it stands (see `runner`).
# - A3, A4, A5: M01's criteria as written, with planted faults fitted to this alignment (M01's own faults name
#   human-rabbit positions).
# - A9: M01's criterion, with CQ-02's answers filtered to this mapping: CQ-02 answers once per mapping, so once mouse
#   and pig sit beside rabbit, a human residue has three answers.
# - A8: validation, the table's checksum against its record, and a re-run from the graph before the build. M01's
#   re-run from a named commit and its UniProt replay (a network call) wait for the real build.
# - A6, A7 do not apply as written (rabbit's papers; [a peer]'s human-rabbit figure). Stand-ins below, each a statement
#   already held in this vault, never fetched for this.
# - A11 applies in kind: the archive's grounding note has a human-to-pig table beside its rabbit one, compared the
#   same way (as residue pairs; ambiguous residues left uncompared; the archive a quarry, either side may be wrong).
build_inputs: curation/build_o4_mapping_pig.yaml
runner: "channelscope o4 check-mapping (how/runtime/channelscope/src/channelscope/o4.py), written on 2026-10-06 after this file was, since M01's run_mapping_checks reads A6's rabbit list, A7's figure and A11's rabbit table, and its faults name human-rabbit positions"
a9_human_positions: [1, 5038, 614, 4938]
controls:
  - id: O4-pig-gate
    human: "4938"
    object: "4935"
    residue: I
    source: "O2's reading by flanking sequence in each UniProt entry ([a working note, not public], Part 2): human I4938, pig I4935"
a6_stand_in:
  - id: O4-pig-01
    human: "614"
    object: "615"
    residue: R
    snapshot: what/references/_snapshots/woll_pig_ryr1_r615c_cryoem_2021.xml
    quotation: "we employed a known homolog to the human R614C MH RyR1 mutation, identified in pigs"
    quotation_2: "The homologous pig R615C mutation provided the original link between MH and RyR1"
a7_stand_in: "none held in this vault; proposed: identity and pair count from a third, independently written aligner, or an independent check like [a peer]'s of 2026-10-04"
a11_archive_note: [a local path]
a11_table_header: "**Human → pig (P16960):**"
```
