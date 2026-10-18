"""extract_rows.py - one residue's rows of each CL-4 table, for the article (the criteria, *Residue 614, the article's
worked example*): each file begins with its table's column line and holds the rows byte for byte; a manifest names,
for each file, its table record, the full table's path and SHA-256, and the line numbers taken; and one records file,
JSON Lines, holds every record the rows name and every record reachable from them through provenance, each exactly as
its line in the graph. A record that cites this project's working transcripts by identifier is withheld, as the
releases withhold it (the operator's answer (a) to CL-3's question 1), and the manifest lists it with its SHA-256.

    uv run --project how/runtime/channelscope python -I how/runtime/channelscope/cl4/extract_rows.py \
        COMMIT SCOPE RESIDUE OUT_DIR
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "src"))
import build_ryr1_mappings_release as cl1  # noqa: E402  (its committed closure: the validator's own references)

UUID = re.compile(r"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")
ID = re.compile(r"cs:[a-z_]+\.[A-Za-z0-9_-]{32}")


def sha(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def main(commit: str, scope: str, residue: int, out: Path) -> None:
    ctx = cl1.load()
    prefix = f"tables/cl4/{commit}/{scope}/"
    tabs = sorted((r for r in ctx.records if r.type == "table" and r.path.startswith(prefix)), key=lambda r: r.name)
    out.mkdir(parents=True, exist_ok=True)
    manifest, start = {"commit": commit, "scope": scope, "residue": residue, "files": [], "withheld": []}, set()
    for t in tabs:
        data = (cl1.GRAPH / t.path).read_bytes()
        if sha(data) != t.sha256:
            raise SystemExit(f"{t.path} is not its record's")
        lines = data.split(b"\n")
        cols = lines[0].decode("utf-8").split("\t")
        if "human_position" not in cols:
            continue
        i = cols.index("human_position")
        take = [k for k, ln in enumerate(lines[1:], 2) if ln and ln.split(b"\t")[i] == str(residue).encode()]
        body = b"\n".join([lines[0], *(lines[k - 1] for k in take)]) + b"\n"
        name = f"{t.name}_{residue}.tsv"
        (out / name).write_bytes(body)
        manifest["files"].append({"file": name, "sha256": sha(body), "table_record": t.id, "table_path": t.path,
                                  "table_sha256": t.sha256, "lines_taken": take})
        start |= {t.id} | {m for k in take for m in ID.findall(lines[k - 1].decode("utf-8"))}
    closure = cl1.compute_closure(ctx, sorted(start))
    kept = []
    for rid in sorted(closure):
        line = ctx.lines[rid]
        if UUID.search(line.decode("utf-8")):
            manifest["withheld"].append({"record": rid, "sha256": sha(line.rstrip(b"\n")),
                                         "reason": "cites this project's working transcripts by identifier"})
        else:
            kept.append(line.rstrip(b"\n"))
    (out / f"records_{residue}.jsonl").write_bytes(b"\n".join(kept) + b"\n")
    manifest["records_file"] = {"file": f"records_{residue}.jsonl", "records": len(kept),
                                "sha256": sha(b"\n".join(kept) + b"\n")}
    (out / "manifest.json").write_bytes((json.dumps(manifest, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print(json.dumps({f["file"]: len(f["lines_taken"]) for f in manifest["files"]}),
          f"records {len(kept)}, withheld {len(manifest['withheld'])}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), Path(sys.argv[4]))
