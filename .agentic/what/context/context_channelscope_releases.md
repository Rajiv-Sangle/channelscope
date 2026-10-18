---
type: context
status: active
created: 2026-10-18
updated: 2026-10-18
last_edited_by: agent_claude
tags: [channelscope, context, releases, provenance]
---

# How ChannelScope's releases fit together

A human residue reaches an animal structure in three steps, and each can slip without an error message: its partner in
the species, the structure's own numbering, and the structure's state. The releases take those steps in that order, and
the fourth joins them. `README.md`, *The results*, gives each with its checks; this guide only says which to read for
what.

| Step | Where | Read it for |
|---|---|---|
| 1. The partner in rabbit, mouse and pig | `releases/ryr1_mappings_v0.1/` | Which residue a human residue is in each species, with each mapping's reliability flag |
| 2. The structure's numbering | `checks/structure_numbering/` | Whether a structure's residue numbers match UniProt's, checked two ways for 20 structures and by alignment alone for 6 |
| 3. The structure's state at the gate | `releases/ryr1_structure_states_v0.1/` | Whether each structure's gate is closed or open, measured, beside the words its depositors or papers use |
| 4. The evidence around a residue | `releases/ryr1_composition_v0.1/` | For 299 residues fixed in advance, steps 1 to 3 joined with ClinVar's records and gnomAD's variants, side by side, with no verdict |
| The exon map | `releases/exon_map_v0.5.3/` | Where each exon, codon and residue of the human transcript lies on GRCh38 |

**How a value is traced.** Each release keeps typed records in its `graph/`: where each input came from, the method
that produced each value, and the checks run on it. *How ChannelScope works* in `README.md` explains the record types;
`releases/AGENTS.md` explains a release's layout. The exon map keeps no records, and its README says why.

**Before using a value,** read its release's README for what the value means and what it does not, and *What can go
wrong* in `README.md` for the slips each step guards against.
