# The ledger

From the release `ryr1_mappings_v0.1`. One row for each criterion and each amendment, each execution written, each build, each trial and each recorded run, in India Standard Time. A commit is cited only where the event is that commit, by its full hash; the commits are in the project's private working history, which the public repository's fresh history does not include. Every other event is cited as "a working record, not public": the session transcripts that hold them are kept, and their SHA-256s are given below. A run is cited by its record, which this release carries. So the order is attested by this ledger, not shown.

## The codon map and the human numbering (checks G1 to G6, A1 and A2)

| Step | When (IST) | Source |
|---|---|---|
| Criteria G1 to G5 committed | 2026-09-28 22:03:58 | commit `79ff30b445f40b755b2cf966e8f0887d60faae65` (private working history) |
| Criterion G6 committed | 2026-09-28 23:31:54 | commit `a5b65834f873dac7810c4de45fa60ef4c86f184e` (private working history) |
| Criteria A1 and A2 committed | 2026-09-28 16:09:25 | commit `8e84a8bc130fda0d9f7f230da70c4095a191ee62` (private working history) |
| G4's execution written | 2026-09-29 08:51:14 | a working record, not public |
| G4's execution committed, before any check ran | 2026-09-29 08:57:05 | commit `9599b0f5bc76592ff1a47890ac9847f0e508d55f` (private working history) |
| The codon map built | 2026-09-29 09:04:40 to 09:04:40 | run `cs:run.CWish7UlWLtKUPc1Do-2IFvxkK5UyQSv` |
| G6's comparison and A2's execution written | 2026-09-29 09:07:18 | a working record, not public |
| The check code with its planted faults written, and edited four times | 2026-09-29 09:09:16 to 09:10:02 | a working record, not public |
| A trial on a scratch copy of the graph: every check passes, every control detected | 2026-09-29 09:10:15 to 09:10:22 | a working record, not public |
| **The recorded run** | 2026-09-29 09:11:02 to 09:11:03 | run `cs:run.70f58VB_AanLbpKj4P2z4jT6eTqNz75y` |
| The execution, the planted faults and the results committed | 2026-09-29 09:13:00 | commit `b46690d77461569afb157254dbff80777f58a3ef` (private working history) |
| An estimated time in the session's notes corrected to the recorded one | 2026-09-29 09:15:21 to 09:15:24 | a working record, not public |

## The human-rabbit mapping (checks A3 to A11)

| Step | When (IST) | Source |
|---|---|---|
| Criteria A3 to A10 committed | 2026-09-28 16:09:25 | commit `8e84a8bc130fda0d9f7f230da70c4095a191ee62` (private working history) |
| Criterion A11 committed | 2026-09-28 17:03:02 | commit `258d6d96d721291549e2a612baaab34591a38716` (private working history) |
| A6's criterion amended | 2026-09-28 23:31:54 | commit `a5b65834f873dac7810c4de45fa60ef4c86f184e` (private working history) |
| A6's criterion, and A8's, amended | 2026-10-03 02:10:43 | commit `70db3fb561f62f182ed938c1793733ac0bacaca1` (private working history) |
| A6's criterion amended | 2026-10-03 14:00:22 | commit `0bf812c5daf223825968fbfb898a9a4e63ced03a` (private working history) |
| A6's list committed (row A6-03 marked as in conflict with A6-02 in the same source) | 2026-09-29 10:54:35 | commit `ba1f22e3cdcf0906cf9389d14c73300134ff128e` (private working history) |
| A6's list amended | 2026-10-03 02:10:43 | commit `70db3fb561f62f182ed938c1793733ac0bacaca1` (private working history) |
| A6's list amended | 2026-10-03 14:00:22 | commit `0bf812c5daf223825968fbfb898a9a4e63ced03a` (private working history) |
| An alignment trial in a scratch folder: the score, the 256 alignments of equal score, the counts and the ambiguous positions printed | 2026-10-03 20:03:18 to 20:03:32 | a working record, not public |
| A trial build of the mapping on a scratch graph | 2026-10-03 20:06:06 to 20:06:17 | a working record, not public |
| The mapping built | 2026-10-03 20:08:39 to 20:08:47 | run `cs:run.4uhAfq3jcNmN1xcSTlt9eDmHPIrzhVRw` |
| The build committed | 2026-10-03 20:16:18 | commit `f2f2dbbce41e09214b29712b410e3c2f3c34e4d7` (private working history) |
| Seen before the execution was written: the counts, the ambiguous positions and the ten runs of residues present in one species only, which bound the eleven stretches A11 compares; so the outcomes of A3, A4, A7 and part of A11 were foreseeable, and A6's was predicted (nine entries reproduced, A6-03 not) | before 2026-10-03 20:20:16 | a working record, not public |
| The checks' execution written | 2026-10-03 20:20:16 | a working record, not public |
| The check code with its planted faults written, and edited four times | 2026-10-03 20:22:56 to 20:23:51 | a working record, not public |
| Trial 1 on a copy of the graph: stopped with a code error before printing any outcome | 2026-10-03 20:23:55 to 20:24:20 | a working record, not public |
| The code edited twice | 2026-10-03 20:24:29 to 20:24:31 | a working record, not public |
| Trial 2 on a copy of the graph: complete; outcomes printed (A6 fails, the rest pass) | 2026-10-03 20:24:34 to 20:25:06 | a working record, not public |
| **The recorded run**, with the code unchanged since trial 2 | 2026-10-03 20:26:23 to 20:26:38 | run `cs:run.hY0Ai_Pe9GSyMNvD1i18M7T7UF_ryGfx` |
| The execution, the planted faults and the results committed | 2026-10-03 20:36:02 | commit `bcf9df5aa32db07ebe0bb3cd51b31a6d60c2fcf7` (private working history) |

## The human-mouse and human-pig mappings (O4)

| Step | When (IST) | Source |
|---|---|---|
| The criteria files written | 2026-10-06 18:45:29 to 18:45:36 | a working record, not public |
| Trial attempt 1 on a scratch graph: stopped at A5's planted fault, written for rabbit, before printing any outcome | 2026-10-06 18:47:28 to 18:47:47 | a working record, not public |
| A5's planted fault rewritten for these species | 2026-10-06 18:48:01 | a working record, not public |
| Trial 2: every check passes, every control detected | 2026-10-06 18:48:04 to 18:49:48 | a working record, not public |
| The runner and its planted faults written, with one edit | 2026-10-06 19:03:20 to 19:03:28 | a working record, not public |
| The runner's own trial on a scratch graph, both species: every check passes, every control detected | 2026-10-06 19:05:25 to 19:07:19 | a working record, not public |
| The criteria files' note on their runner updated | 2026-10-06 19:28:11 to 19:28:15 | a working record, not public |
| Criteria, runner and planted faults committed | 2026-10-06 19:40:05 | commit `c26fd2320eca49d8577ceb9a8659eb0d6b54ced3` (private working history) |
| The mouse and pig proteins and numberings recorded | 2026-10-06 19:40:53 to 19:40:53 | run `cs:run.0U78KEAhbQoDVMwMgL5szotJ9ncXiJtJ` |
| The human-mouse mapping built | 2026-10-06 19:40:58 to 19:41:05 | run `cs:run.Xa8BBIoV9LZOgYfbKJYRiGIc9rzfK5oh` |
| The human-pig mapping built | 2026-10-06 19:41:09 to 19:41:11 | run `cs:run.AAHs4faLhRZwzsPejIrTwiUvm3nA2Qsq` |
| **The recorded run, mouse** | 2026-10-06 19:41:26 to 19:42:08 | run `cs:run.ZahjTHNNcidtcs7TSvZxp30BTATPB71O` |
| **The recorded run, pig** | 2026-10-06 19:42:11 to 19:42:38 | run `cs:run.1yTUjV_7nydWMQlWqVgFOCap1qFPoN35` |

## The code each run ran

Every run record carries a digest of the whole package (`software.code_digest`). Recomputed at each commit of the package, it names the commit each run's code was taken from.

| Run | Its code digest | The package at commit |
|---|---|---|
| `cs:run.fkysLjLGSoLkQZi1xPrp4mT-_Y3WXNS5` | `sha256:e57f0aea4b0b30474a4f31b96eaef80868e00280dd4e1b091b8cd210ad4500b2` | none found |
| `cs:run.CWish7UlWLtKUPc1Do-2IFvxkK5UyQSv` | `sha256:edf2fca549556f885ca993881bea3a8f412330b6673ee0962986d6459abc4d18` | `3ff0ce97e51935a463d490467812bee864f103b4` |
| `cs:run.70f58VB_AanLbpKj4P2z4jT6eTqNz75y` | `sha256:01d6f47f31cf6e238f9ed6895c2257e5e3d8bd3fe980773ad81b1cb9103895bf` | `b46690d77461569afb157254dbff80777f58a3ef` |
| `cs:run.4uhAfq3jcNmN1xcSTlt9eDmHPIrzhVRw` | `sha256:5ec09edaf10765bb98d75265c04a4cb572704a144510d373063cb0eb78baefb8` | `f2f2dbbce41e09214b29712b410e3c2f3c34e4d7` |
| `cs:run.hY0Ai_Pe9GSyMNvD1i18M7T7UF_ryGfx` | `sha256:064f50de9b694dc40c31d4beb61e5fc9612f42bacfd47aac81114791b6a61c7f` | `bcf9df5aa32db07ebe0bb3cd51b31a6d60c2fcf7` |
| `cs:run.0U78KEAhbQoDVMwMgL5szotJ9ncXiJtJ` | `sha256:40d94dbae12672507ac78c9a7223c7cfad089feebdb4d58c584d68abbac72d7a` | `c26fd2320eca49d8577ceb9a8659eb0d6b54ced3` |
| `cs:run.Xa8BBIoV9LZOgYfbKJYRiGIc9rzfK5oh` | `sha256:40d94dbae12672507ac78c9a7223c7cfad089feebdb4d58c584d68abbac72d7a` | `c26fd2320eca49d8577ceb9a8659eb0d6b54ced3` |
| `cs:run.AAHs4faLhRZwzsPejIrTwiUvm3nA2Qsq` | `sha256:40d94dbae12672507ac78c9a7223c7cfad089feebdb4d58c584d68abbac72d7a` | `c26fd2320eca49d8577ceb9a8659eb0d6b54ced3` |
| `cs:run.ZahjTHNNcidtcs7TSvZxp30BTATPB71O` | `sha256:40d94dbae12672507ac78c9a7223c7cfad089feebdb4d58c584d68abbac72d7a` | `c26fd2320eca49d8577ceb9a8659eb0d6b54ced3` |
| `cs:run.1yTUjV_7nydWMQlWqVgFOCap1qFPoN35` | `sha256:40d94dbae12672507ac78c9a7223c7cfad089feebdb4d58c584d68abbac72d7a` | `c26fd2320eca49d8577ceb9a8659eb0d6b54ced3` |

Where a row says "none found", no commit of the package holds code with that run's digest.

## The working records behind it

The private ledger, which names each working record and the line of it that holds each event, has the SHA-256 `4662331f0d4bd719715c52ffdc4ac5a670fe09d7c513cc2bdb58eb5ee8490470`. The working records it cites have these SHA-256s:

- working record 1: `d7754f940149339b4d02f17d86669071976dab43406b92fe5b1d6c5ecced34bc`
- working record 2: `1694fafbab7ac3fc8cb3e7d8b52daef785d216f1b346c746a78c48ba862d3e2b`
- working record 3: `262bf59e8b0df9e01ee76556cc9a4549faa5c014ecc61d8ef14191275744114b`
- working record 4: `5c886c7822209355f74dae803c02096e0662384aa813adaed4fcfaa5e0d77ffb`
- working record 5: `65ab5aa968daa9877652351a45945154c6d81c3426cd350aa2063fe18951f574`
