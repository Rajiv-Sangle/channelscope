---
type: manifest
status: active
created: 2026-10-18
updated: 2026-10-19
last_edited_by: agent_claude
tags: [channelscope, manifest, adna]
adna_conformance: starter
adna_standard: "2.5"
adna_deployment: embedded
---

# ChannelScope: manifest

**What it is.** ChannelScope gathers, from public sources, the evidence about the residues of one ion channel, human
RyR1, and records where each value came from. Its question is what a missense variant, one that changes a single amino
acid, does to RyR1's structure and function. This version does not answer it, and it classifies no variant. `README.md`
says what is claimed, what failed, and what is not claimed.

**Version.** 0.1.1: version 0.1.0's releases and code, unchanged, with this aDNA layer added. Against 0.1.0 it adds
`MANIFEST.md`, `STATE.md` and `.agentic/`, and changes `README.md`, `CLAUDE.md`, `AGENTS.md`, `CITATION.cff` (the
version) and `SHA256SUMS`. In the README: two lines of its layout block and one paragraph for this layer; a footnote
naming the source of each quotation and outside description that named none; wordings brought to their sources, among
them HGVS and HOLE no longer called "the standard" and "a standard program", MANE's Select set and gnomAD's post in
their own words, the state bullet's heading and words under *What can go wrong*, and one footnote's line ranges; and
three corrections, each in its source's words: the reason for 8VJK's closed gate, with what the same paper says of
8VJJ; the protein form that HGVS gives a predicted change, p.(Arg614Cys); and the count of 22 structures with words
naming a state, which is the record of the code that first measured each structure. Its sections are reordered:
why RyR1, where ChannelScope is going (the aim and its premises, each with what would count against it), how it
works and what can go wrong, then what this version has, its results and failures, and what it shows of the aim,
with the next steps. The former *Roadmap*'s table is split between the second and the last of these, its
cells unchanged but for two premises and one counter said in full, which had pointed at the cell beside them,
and its opening question, which the README's opening asks, is not repeated. It links the explanatory article,
which the exon map's row had called not yet published, and thanks those who helped.
`CITATION.cff` says how to cite it.

**What it holds**, each described in `README.md`:
- `releases/`: the mappings from human RyR1 to rabbit, mouse and pig RyR1; the gate's state in 26 structures; the
  evidence for 299 residues fixed in advance; and the exon map of the human transcript;
- `checks/structure_numbering/`: the 26 structures' residue numbering, checked by this project's alignment, and
  against SIFTS for the 20 it maps;
- `code/`: the Python package that the README's checks and re-runs use, its environment pinned;
- `SHA256SUMS`: the SHA-256 of every other file.

**Licences.** The code is under the MIT licence (`LICENSE`); what ChannelScope made is under CC BY 4.0; each source's
part is under that source's own terms, as `README.md` (*Licence*) and each release's README state them.

## As an aDNA project
This repository follows [aDNA](https://github.com/aDNA-Network/aDNA) (Agentic DNA), in its own words "a knowledge
architecture standard for AI-native projects", open source under the MIT licence, at its **Starter** conformance level, version 2.5 of the standard, in its
**embedded** form: the project's knowledge, operations and people sit in `.agentic/what/`, `.agentic/how/` and
`.agentic/who/`, and the governance files (`CLAUDE.md`, `MANIFEST.md`, `STATE.md`, `AGENTS.md`, `README.md`) at the
root. The embedded form leaves every path of the code and the releases where version 0.1.0 put them.

**How the level was checked.** aDNA's own validator, `adna_validate.py`, from aDNA's repository at the commit named in
`.agentic/who/governance/governance_channelscope.md`, run on this release with `--level starter --verbose`, reports
Starter conformance with no error and no warning. Run without a level, it reports Standard with three warnings
(`what/decisions/`, `how/sessions/active/` and `how/sessions/history/` absent); it never checks sessions, which
Standard requires, so Standard is not claimed, and neither is Full. **What it does not check:** it tests that the
required files and folders exist and that each content file in `.agentic/` carries aDNA's base frontmatter. It does
not test what the files say. **Two departures from the standard, which the validator does not test:** `README.md`
carries no frontmatter (section 7.1 asks it of root governance files), so that it reads cleanly on GitHub; and
`CLAUDE.md` gives the project's map, rules and startup under its own headings, without the collision-prevention tier
and session-closing protocol that section 4.2 also sets out.

**Where the work happens.** ChannelScope is developed in a private aDNA vault, as aDNA itself is, and published here as
reviewed, tagged releases. How to contribute: `.agentic/who/coordination/AGENTS.md`.
