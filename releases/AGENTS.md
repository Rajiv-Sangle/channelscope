# releases/: how a release is laid out

Each folder here is one release, built and checked by its own builder before it was written. Every release but the
exon map's (below) holds:

- `README.md`: what the release holds, how it was checked, and the sources' terms;
- `graph/`: its records and data. `graph/records/` holds the records as JSON Lines, one record per line, of one type
  per file (a retrieval, a method, a run, a table, a check result, and others). A record's `id` is a digest of its
  content, so a record changed in place no longer matches its `id`. `graph/tables/` holds the tables, each described
  by a table record; `graph/raw/` holds the sources' answers as retrieved, most of them named by a retrieval record
  with its SHA-256 (in the states release, the survey's answers from the RCSB are listed in `rcsb_answers.tsv`
  instead);
- `withheld.tsv`: what the release does not carry, each with its SHA-256 and the reason, such as coordinate files that
  are fetched rather than stored, or records that cite the project's working sessions (summarised in a JSON file);
- `ledger.md`: the order in which the criteria were committed and the runs were made;
- `manifest.json` and `ro-crate-metadata.json`: every file with its SHA-256;
- `rerun/` or `a6/`: the scripts that re-derive a result from the release's files, as `README.md` at the repository's
  root lists them.

A derived record's `provenance` names what it was derived from (`used`), the run that made it (`was_generated_by`)
and the method (`method`). To trace a value, follow those identifiers through `graph/records/`.

`exon_map_v0.5.3` is laid out differently: a flat folder of the files an explanatory article's exon-map figure reads,
with a header (`exon_map_header_v0.5.3.json`) that holds each value's sources and terms, a `README.md`, a
`withheld.tsv`, and a `manifest.json` that gives every other file's SHA-256, the changes from the release before it,
and the checks its build ran. It has no `graph/`, `ledger.md`, RO-Crate or re-run scripts, and its builder is not
published; its README says why.
