# code/: the channelscope package

`code/` holds the `channelscope` Python package (`src/channelscope/`), its `pyproject.toml` and `uv.lock`, which pins
every dependency's version. With [uv](https://docs.astral.sh/uv/) installed, `uv run --project code ...` makes the
environment on first use and runs a command in it. `code/.python-version` pins CPython 3.12, which uv reads: the
rebuild of two coordinate files that the PDB revised after they were measured needs zlib's output, and a Python whose
zlib is zlib-ng (as CPython 3.14's Windows builds are) compresses otherwise, so its rebuilt files would be refused.

- `uv run --project code channelscope --help` lists the commands. Pass `--graph` every time: the default it names is
  the project's working graph, which this repository does not hold.
- `uv run --project code channelscope --graph releases/<release>/graph validate` checks a release's records against the
  schema, for each release that has a `graph/` (the exon map's release has none).
- The re-run scripts in each release add their own needs on the command line, as `README.md` at the repository's root
  gives them (for example `--with gemmi==0.7.5`).

The lines of the package changed for publication are listed in `releases/ryr1_mappings_v0.1/code_changes.tsv`. The
states and composition releases also carry the scripts that built their tables, as they ran (each release's `code/`
folder), with their SHA-256 beside the ones the records give.
