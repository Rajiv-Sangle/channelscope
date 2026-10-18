---
type: governance
status: active
created: 2026-10-18
updated: 2026-10-18
last_edited_by: agent_claude
tags: [channelscope, governance, licence, rules, adna]
---

# ChannelScope's governance

**The maintainer** is the project's author, named in `CITATION.cff`. The project was built with Claude, Anthropic's AI
model, under the author's direction (`README.md`, under its title).

**Licences.** The code is under the MIT licence (`LICENSE`). What ChannelScope made is under CC BY 4.0. Each source's
part stays under that source's own terms, as `README.md` (*Licence*) and each release's README state them.

**The rules.** Every change keeps the rules in the root `CLAUDE.md`, *Rules to keep*: provenance on every value;
signals, not verdicts; no claim beyond the README; the numbering named; transfer kept a premise until tested; checks
that can fail; and each source's terms kept. They are kept there, in one place, so that an agent reads them first.

**How a rule changes.** A rule changes only by the maintainer's decision, recorded in the release that carries the
change, and every file that states or depends on the old rule is corrected in the same change.

**How the aDNA level was checked.** `MANIFEST.md` declares aDNA's Starter level. It was checked with aDNA's validator,
`.adna/what/lattices/tools/adna_validate.py` from github.com/aDNA-Network/aDNA at commit
`1a2544692645f267b507ca3714e8ae46b2e86b50` (the file's SHA-256
`7f9780d80f77c4a69a9f284ec655580e75ce8de00145ed7ea909e607f67bc263`), run on this release's files with
`--level starter --verbose`: it reports no error and no warning. The validator tests that the required files and folders exist and that
each content file in `.agentic/` carries aDNA's base frontmatter; it does not test what the files say. To check it
yourself: `python adna_validate.py <this repository> --level starter --verbose`, with PyYAML installed.
