---
type: governance
status: active
created: 2026-10-11
updated: 2026-10-18
last_edited_by: agent_claude
tags: [channelscope, governance, agent-guide]
---

# ChannelScope: a guide for an AI agent in this repository

ChannelScope assembles evidence about the residues of one ion channel, RyR1, and keeps the provenance of every value.
This repository is its first public version, a proof of concept. Read `README.md` first: it says what is claimed, what
failed, and what is not claimed.

This guide is for an AI agent, such as Claude Code, that a user runs in a clone of this repository. It says how to check
the clone and re-derive the results, and which rules to keep when using or extending the evidence.

**This repository is an aDNA project.** The project was built with agents working under aDNA (Agentic DNA,
https://github.com/aDNA-Network/aDNA), in its own words "a knowledge architecture standard for AI-native projects", and
this repository follows it at aDNA's Starter level, in its embedded form: `MANIFEST.md` says what the project is and how
that level was checked, `STATE.md` says where it stands, and `.agentic/` holds its context, backlog and templates, how
to contribute, and how it is governed. It carries none of the project's private working records.

**Starting a session:** read `README.md`, `MANIFEST.md` and `STATE.md`, then `.agentic/AGENTS.md`. To work inside an aDNA
workspace, clone this repository into it as `channelscope.aDNA`, as `README.md` shows.

## What is here

| Path | What it holds |
|---|---|
| `README.md` | The claims, the results, what failed, the premises, and what is not claimed |
| `releases/ryr1_mappings_v0.1/` | Residue mappings from human RyR1 to rabbit, mouse and pig RyR1 |
| `releases/ryr1_structure_states_v0.1/` | The pore's radius at the gate of 26 RyR1 structures, and each structure's measured state |
| `releases/ryr1_composition_v0.1/` | For a residue set fixed in advance, the evidence about each residue, side by side |
| `releases/exon_map_v0.5.3/` | The exons of human RYR1's transcript on GRCh38, with its codons, residues and sequences: the files an explanatory article's exon-map figure reads. It keeps no records and cannot be rebuilt here; its README says why |
| `checks/structure_numbering/` | The 26 structures' residue numbering, checked against SIFTS where it maps them (20 of 26) and by this project's alignment |
| `code/` | The `channelscope` Python package, its `pyproject.toml` and the pinned `uv.lock` |
| `SHA256SUMS` | The SHA-256 of every other file |
| `MANIFEST.md`, `STATE.md` | What the project is, its aDNA level and how it was checked; where it stands |
| `.agentic/` | The aDNA layer: context, backlog, templates, how to contribute, and governance |

`releases/AGENTS.md` explains how a release is laid out; `code/AGENTS.md` explains how to run the package.

## Checking a clone

1. **Every file.** `sha256sum -c SHA256SUMS` must report every file as OK. The repository's `.gitattributes` keeps
   every file's bytes as committed, so the sums hold on any platform.
2. **The results.** `README.md`, in *Re-running the results*, gives each command that re-derives a result here and what
   it compares. Each runs through [uv](https://docs.astral.sh/uv/), which makes the pinned environment on first use
   (CPython 3.12, which `code/.python-version` pins); the two scripts that need no package also run with any Python
   3.10 or later. Two of them fetch coordinate files from the Protein Data Bank and refuse any file whose SHA-256
   differs from its record's. For 9ZO8 and 9ZOE, which the PDB revised after they were measured, they rebuild the file
   measured from the PDB's later revision with a patch the release carries, and the rebuilt file must have its
   record's SHA-256; a Python whose zlib is zlib-ng compresses otherwise, and is refused with the cause named.
3. **The records.** `uv run --project code channelscope --graph releases/<release>/graph validate` checks a release's
   records against the schema. It also reports what a release does not carry: a reference to a record the release
   withholds (rule V07), and a raw answer whose bytes it does not carry (rule V08). Each such item is named in the
   release's `withheld.tsv`. Expect 1 finding for the mappings release (V08), 43 for the states release (V07) and 13
   for the composition release (8 V07 and 5 V08), and nothing else. With findings, the command exits with code 1, so
   an exit code of 1 with exactly those findings is the expected result. The exon map's release has no `graph/`: check
   its files against the SHA-256 its `manifest.json` gives (step 1 covers them too).

Report each outcome as it comes out, failures included, with the command that produced it.

## Rules to keep

- **Provenance on every value.** A value names its source, an identifier there, the version or retrieval date, and the
  method that produced it, with the method's version. Add or change no value without them.
- **Signals, not verdicts.** No single source or predictor decides. Evidence that disagrees stays side by side; it is
  never merged into one verdict.
- **No claim beyond the README.** This repository claims no variant's effect or its direction, no pathogenicity, no
  clinical use and no structure prediction. ClinVar says its information "is not intended for direct diagnostic use or
  medical decision-making without review by a genetics professional" (its page on maintenance and use,
  https://www.ncbi.nlm.nih.gov/clinvar/docs/maintenance_use/, read on 30 September 2026; the page is not carried here).
- **Say which numbering.** A residue number names its numbering (a UniProt sequence and its version, or a structure's
  author numbering) and, across species, the mapping that joins them.
- **Transfer is a premise.** Carrying evidence from RyR1 to another protein, such as its paralogue RyR2, is a premise
  until it has been tested.
- **Checks that can fail.** A new check states beforehand what result would count against it, and is run on input with
  a fault planted in it, which it must catch.
- **Sources keep their terms.** Each source's part is under that source's terms, as `README.md` (*Licence*) and each
  release's README state them.
