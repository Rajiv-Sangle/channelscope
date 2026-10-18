"""make_c5_plans.py - write C5's two fetch plans from the held inputs, before anything is fetched (the criteria, *The
fetches*): `curation/fetch_close_cl4_c5_clinvar.yaml` (each included record at a sampled residue: its summary, then
its full record) and `curation/fetch_close_cl4_c5_gnomad.yaml` (the release check first, then each S2 variant at a
sampled residue, by the API's per-variant query). The plans are committed before `channelscope fetch` runs them.

    uv run --project how/runtime/channelscope python -I how/runtime/channelscope/cl4/make_c5_plans.py FETCH_DATE
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import GRAPH, Inputs  # noqa: E402
from layers import clinvar, gnomad, partners  # noqa: E402
from sample import c5_sample  # noqa: E402

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
QUERY = ('{"query": "{ variant(variantId: \\"%s\\", dataset: gnomad_r4) { variant_id exome { ac an filters } '
         'genome { ac an filters } joint { ac an filters } } }"}')


def main(date: str) -> None:
    inp = Inputs()
    cv = clinvar(inp)
    sample = c5_sample(inp, cv["set"], partners(inp, cv["set"]))
    want = set(sample["all"])
    recs = sorted((r for r in cv["included"] if r["n"] in want), key=lambda r: int(r["uid"]))
    variants = gnomad(inp, sample["all"])
    head = (f"# CL-4's check C5 (the criteria v3, *C5: the re-derivation, in detail*), written by cl4/make_c5_plans.py "
            f"from the held inputs\n# on {date}, before any of these calls was made. The sample: the nine departure "
            f"residues, the 30 drawn and the four\n# worked residues (Q2, answered (c)): {len(want)} residues.\n")
    cl = [head.rstrip("\n"), f"# ClinVar (C5-C): {len(recs)} included records at the sampled residues, each by its "
          "summary, whose accession_version pins the\n# release, then its full record (VCV XML), as "
          "fetch_exon_map_v0_4_clinvar_indels.yaml did. NCBI calls send tool=channelscope and\n# no e-mail address. "
          "Run with `channelscope fetch <this file>`.", "calls:"]
    for r in recs:
        u = r["uid"]
        note = f'["{r["accession_version"]} at human {r["n"]}"]'
        cl += [f"  - name: esummary_{u}", "    source: source:clinvar",
               f"    url: {EUTILS}/esummary.fcgi?db=clinvar&id={u}&retmode=json&tool=channelscope",
               f"    stored_at: raw/clinvar/{date}/c5_esummary_{u}.json",
               f"    release_json: result.{u}.accession_version", "    pause_s: 0.4", f"    notes: {note}",
               f"  - name: vcv_{u}", "    source: source:clinvar",
               f"    url: {EUTILS}/efetch.fcgi?db=clinvar&rettype=vcv&is_variationid&id={u}&tool=channelscope",
               f"    stored_at: raw/clinvar/{date}/c5_vcv_{u}.xml",
               f"    release_json: result.{u}.accession_version", f"    release_from_call: esummary_{u}",
               "    pause_s: 0.4", f"    notes: {note}"]
    gn = [head.rstrip("\n"), f"# gnomAD (C5-G): first the release check, as S2's plans did: the browser's head commit "
          "on main (GitHub's API),\n# its dataset-metadata/metadata.ts on main (read straight after; the head could "
          "move between the two calls,\n# and the second call's release is the first's sha), and gnomAD's news page. "
          f"Then each of S2's {len(variants)} variants at\n# the sampled residues, by the API's per-variant query "
          "(variant(variantId, dataset: gnomad_r4); exome, genome and\n# joint asked for ac, an and filters, each "
          "declared by the held schema introspection of 2026-10-06). The API\n# states no release. Run with "
          "`channelscope fetch <this file>`.", "calls:",
          "  - name: gnomad_browser_head", "    source: source:gnomad",
          "    url: https://api.github.com/repos/broadinstitute/gnomad-browser/commits/main",
          "    accept: application/json", f"    stored_at: raw/gnomad/{date}/c5_github_commit_main.json",
          "    release_json: sha", '    notes: ["The browser\'s head commit on main: its sha, date and message"]',
          "  - name: gnomad_dataset_labels_head", "    source: source:gnomad",
          "    url: https://raw.githubusercontent.com/broadinstitute/gnomad-browser/main/dataset-metadata/metadata.ts",
          f"    stored_at: raw/gnomad/{date}/c5_browser_dataset_metadata_main.ts", "    release_json: sha",
          "    release_from_call: gnomad_browser_head", "    pause_s: 0.5",
          '    notes: ["The label of gnomad_r4 on main; a later release is recorded if it is not gnomAD v4.1.2"]',
          "  - name: gnomad_news", "    source: source:gnomad", "    url: https://gnomad.broadinstitute.org/news/",
          f"    stored_at: raw/gnomad/{date}/c5_news.html", "    release_absent: unknown", "    pause_s: 1.0",
          '    notes: ["gnomAD\'s news page: a later release is recorded if it lists one after v4.1.2"]']
    for v in variants:
        vid = v["variant_id"]
        gn += [f"  - name: variant_{vid.replace('-', '_')}", "    source: source:gnomad",
               "    url: https://gnomad.broadinstitute.org/api", "    http_method: POST",
               "    content_type: application/json", "    accept: application/json",
               f"    body: '{QUERY % vid}'", f"    stored_at: raw/gnomad/{date}/c5_variant_{vid}.json",
               "    release_absent: unknown", "    pause_s: 6.0", f'    notes: ["S2 row at human {v["human_position"]}"]']
    for name, lines in (("fetch_close_cl4_c5_clinvar.yaml", cl), ("fetch_close_cl4_c5_gnomad.yaml", gn)):
        (GRAPH / "curation" / name).write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    print(f"residues {len(want)}; ClinVar records {len(recs)} ({2 * len(recs)} calls); gnomAD variants "
          f"{len(variants)} ({len(variants) + 3} calls); total {2 * len(recs) + len(variants) + 3}")


if __name__ == "__main__":
    main(sys.argv[1])
