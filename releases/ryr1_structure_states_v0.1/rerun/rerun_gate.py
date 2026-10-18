#!/usr/bin/env python3
"""rerun_gate.py - re-run the gate measurement of release ryr1_structure_states_v0.1 from public sources, and compare.

None of the three runs can be re-run from the release as they stand: S13's script refuses unless its files are
unchanged since a commit of this project's private history, and both later scripts refuse unless o2/gate.py hashes to
the bytes that ran, which carry a session id. So this harness (CL-3's notes v3, *The re-run*):
- checks the release's code first: each copy's code digest (codedigest.py: the code without comments and docstrings)
  must equal the digest recorded for the code that ran (code/digests.tsv), so the copy differs from what ran in
  comments alone;
- runs check S, the synthetic tests of s13/check_gate_b_fixed.py, on that code. Two tests cannot run outside the
  private history and are reported as not run: F10 pins the bytes that ran, and F11 tests the run guard against one
  of its commits. Every other test must pass and its control must be caught;
- takes each of the 26 coordinate files from a cache folder, or fetches it from its retrieval record's URL, and
  refuses an entry whose file's SHA-256 is not the one its retrieval record holds. The PDB released revision 1.1 of
  9ZO8 and 9ZOE on 14 October 2026, after both were measured at revision 1.0, which it no longer serves: for these
  two, the harness rebuilds the measured file from the file served, with the patch in patches/ and
  rebuild_revision.py, and the rebuilt file must then have the SHA-256 the record holds. What it fetches it keeps in
  the cache folder: the file served under its own name (<entry>.served.cif.gz), and the rebuilt one under the measured
  file's; a file already there is read and never replaced. The rebuild needs zlib's output: a Python whose zlib is
  zlib-ng (as CPython 3.14's Windows builds are) gives other bytes, which are refused, with the cause named. For any
  other entry the PDB revises, revisions.tsv names the revision this release measured, and the entry is refused;
- measures each entry with the release's code unchanged: implementation A (o2/gate.py, gate_a, and the atom that sets
  it), the fixed B and O2's window (s13/gate_b_fixed.py), and compares them with the release's table
  (graph/tables/s13_gate_remeasurement.tsv). Strictly: every radius at the hundredth, every class, G1' and the
  classes at the lines moved by 0.5 A. Every atom, zg* - zg and O2's window are compared too, admitting only the
  readings the method itself leaves to the platform, each named where it occurs (compare(), below). B's axis is an
  eigenvector, whose sign LAPACK may return either way and whose last bits differ between builds. So:
  - zg* - zg, a height along that axis, is compared by its magnitude, written with two decimals;
  - O2's window keeps the samples within 3 A of O2's height, and whether each of the two at exactly 3 A is kept is
    decided by rounding; a replica of its arithmetic gives all four readings (both kept, both dropped, either one
    kept), and the release's value and atom must match one of them;
  - two atoms tie when, on this platform, their values differ by no more than 1e-9 A (in symmetric models the four
    chains' copies of an atom do), and an atom is admitted if it ties with the one this platform finds, as replicas
    of A's, the fixed B's and the window's arithmetic show;
  each replica must give the measurement's own value and atom exactly, or the entry is refused. It prints each entry's
  four window readings where they differ, and its ties;
- runs, on every entry's real values, controls of that comparison: planted faults it must catch (each radius, each
  class, G1', the classes at the moved lines, each atom renamed, the fixed B's atom in a chain whose copy does not
  tie, O2's window outside its readings or with another reading's atom, zg* - zg's magnitude or a doubled sign) and
  plants it must admit (zg* - zg's sign; a tied copy of the fixed B's atom; each other reading of the window). A plant
  that changes nothing fails; one that cannot be made for an entry is named.
It writes nothing in the release, no bytecode beside its code, and, without --cache, removes its temporary folder at
the end. With --readings PATH, a path outside the release, it also writes each measured entry's five readings of O2's
window (as computed, and the four by its 3 A edge), with the atom that sets each, as a tab-separated table; the
release's own copy of that table (rerun/window_readings.tsv) was written so by its build. Exit 0 only if check S passes but for F10 and F11, no entry is refused, every entry compares the same or
with the admitted readings alone, and every control behaves as stated.

    python rerun_gate.py [--cache DIR] [--retrievals FILE] [--only ENTRY ...] [--no-check-s]
Needs Python 3.12 with numpy, biopython 1.88 and gemmi 0.7.5 (the versions the measurement used).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True  # the release's folders are left as they are: no .pyc beside its code
RELEASE = Path(__file__).resolve().parents[1]
PATCHES = Path(__file__).resolve().parent / "patches"
CODE = RELEASE / "code"
TABLE = RELEASE / "graph" / "tables" / "s13_gate_remeasurement.tsv"
RETRIEVALS = RELEASE / "graph" / "records" / "retrieval.jsonl"
REVISIONS = RELEASE / "revisions.tsv"
NOT_RUN = {"F10": "it pins the bytes that ran, which carry a session id; the code digest stands in for it",
           "F11": "it tests the run guard against a commit of this project's private history"}
STRICT = ["radius_a", "radius_b_fixed", "class_a", "class_b_fixed", "g1_prime_agree", "class_at_minus_0_5",
          "class_at_plus_0_5"]
TIE = 1e-9  # two atoms tie when, on the platform that runs this, their values differ by no more than this (A)
TWO_DECIMALS = re.compile(r"-?[0-9]+[.][0-9][0-9]")
EDGE_WORDS = {"both kept": "both kept", "both dropped": "both dropped",
              "the lower kept only": "the lower kept and the upper dropped",
              "the upper kept only": "the upper kept and the lower dropped"}


def a_ties(g, gbf, model, chains, gate) -> tuple[float, str, set]:
    """A's value and atom, by a_with_atom, and every atom whose value is within TIE of it, by a replica of
    a_with_atom's own arithmetic, which must give the same value and atom, else ValueError."""
    value, label = gbf.a_with_atom(g, model, chains, gate)
    res = [model[cid][(" ", gate, " ")] for cid in chains]
    ca = np.array([r["CA"].coord for r in res], dtype=float)
    c = ca.mean(axis=0)
    n = np.linalg.svd(ca - c)[2][-1]
    vals = []
    for cid, r in zip(chains, res):
        for a in r:
            el = a.element.strip().upper()
            if el == "H" or el not in g.RADII:
                continue
            v = a.coord.astype(float) - c
            perp = v - v.dot(n) * n
            vals.append((np.linalg.norm(perp) - g.RADII[el], "%s:%s %d %s" % (cid, r.get_resname(), gate, a.get_id())))
    best = min(v for v, _ in vals)
    if best != value or next(lab for v, lab in vals if v == best) != label:
        raise ValueError("A's tie replica does not give a_with_atom's value and atom")
    return value, label, {lab for v, lab in vals if v - best <= TIE}


def b_fixed_ties(g, gbf, st, gate, rb: float, by: str) -> set:
    """Every atom whose value is within TIE of the fixed B's, by a replica of gate_b_fixed's arithmetic as the table ran
    it (no move, no ring, read at the narrowest height), which must give gate_b_fixed's value and atom exactly, else
    ValueError."""
    model = st[0]
    chains = sorted([ch for ch in model], key=lambda ch: -len(ch))[:4]
    tm, atoms = [], []
    for ch in chains:
        for r in ch:
            if gate - 117 <= r.seqid.num <= gate + 100:
                tm += [a.pos.tolist() for a in r if a.element.name.upper() in g.RADII]
            for a in r:
                el = a.element.name.upper()
                if el in g.RADII:
                    atoms.append((a.pos.tolist(), g.RADII[el], r.seqid.num == gate and r.seqid.icode == " ",
                                  "%s:%s %d %s" % (ch.name, r.name, r.seqid.num, a.name)))
    tm = np.array(tm, dtype=float)
    c = tm.mean(axis=0)
    w, v = np.linalg.eigh(np.cov((tm - c).T))
    k = int(np.argmax([abs(w[i] - np.mean([w[j] for j in range(3) if j != i])) for i in range(3)]))
    n = v[:, k] / np.linalg.norm(v[:, k])
    P = np.array([p for p, _, _, _ in atoms], dtype=float)
    R = np.array([rr for _, rr, _, _ in atoms], dtype=float)
    isg = np.array([f for _, _, f, _ in atoms])
    labels = [lab for _, _, _, lab in atoms]
    rel = P - c
    along = rel.dot(n)
    radial = np.linalg.norm(rel - np.outer(along, n), axis=1)
    heights = []
    for ch in chains:
        mine = np.array([isg[i] and labels[i].startswith(ch.name + ":") for i in range(len(labels))])
        j = np.flatnonzero(mine)[np.argmin((radial - R)[mine])]
        heights.append(along[j])
    zr = float(np.mean(heights)) + 0.0
    inslab = np.abs(along - zr) <= gbf.SLAB_HALF
    d = np.linalg.norm(P - (c + zr * n), axis=1) - R
    d[~inslab] = np.inf
    j = int(np.argmin(d))
    if float(d[j]) != rb or labels[j] != by:
        raise ValueError("the fixed B's tie replica does not give gate_b_fixed's value and atom")
    return {labels[i] for i in np.flatnonzero(d - d[j] <= TIE)}


def window_readings(g, gbf, st, gate, rw: float, rw_by: str) -> dict:
    """O2's window under each reading of its 3 A edge, as {reading: (value at the hundredth, atom, every atom within TIE
    of the value)}, by a replica of gate_b_window's arithmetic (half-width 3, no move, no ring). Samples less than 3 A
    from O2's zg (by more than 1e-9 A) are always kept and those beyond 3 A (by more than 1e-9 A) never; the lower and
    the upper edge sample are each kept or dropped, so four readings. "as computed" keeps a sample as gate_b_window does
    (abs(z - zg) <= 3.0) and must give its value and atom exactly, else ValueError."""
    model = st[0]
    chains = sorted([ch for ch in model], key=lambda ch: -len(ch))[:4]
    gate_atoms, tm = [], []
    for ch in chains:
        found = None
        for r in ch:
            if r.seqid.num == gate and r.seqid.icode == " ":
                found = r
            if gate - 117 <= r.seqid.num <= gate + 100:
                tm += [a.pos.tolist() for a in r if a.element.name.upper() in g.RADII]
        gate_atoms += [(a.pos.tolist(), a.element.name.upper()) for a in found if a.element.name.upper() in g.RADII]
    tm = np.array(tm, dtype=float)
    c = tm.mean(axis=0)
    w, v = np.linalg.eigh(np.cov((tm - c).T))
    k = int(np.argmax([abs(w[i] - np.mean([w[j] for j in range(3) if j != i])) for i in range(3)]))
    n = v[:, k] / np.linalg.norm(v[:, k])
    gp = np.array([p for p, _ in gate_atoms], dtype=float).mean(axis=0)
    zg = (gp - c).dot(n)
    allatoms, labels = [], []
    for ch in chains:
        for r in ch:
            for a in r:
                el = a.element.name.upper()
                if el in g.RADII:
                    allatoms.append((a.pos.tolist(), g.RADII[el], r.seqid.num == gate))
                    labels.append("%s:%s %d %s" % (ch.name, r.name, r.seqid.num, a.name))
    P = np.array([p for p, _, _ in allatoms], dtype=float)
    R = np.array([rr for _, rr, _ in allatoms], dtype=float)
    rel = P - c
    along = rel.dot(n)
    radial_d = np.linalg.norm(rel - np.outer(along, n), axis=1)
    near = (np.abs(along - zg) <= 15.0) & (radial_d <= 25.0)
    Pn, Rn = P[near], R[near]
    ln = [lab for lab, keep in zip(labels, near) if keep]
    samples = []  # (kind, kept as gate_b_window keeps it, the values at that height)
    for z in np.arange(zg - 12.0, zg + 12.0001, 0.25):
        off = z - zg
        if abs(off) > 3.0 + 1e-9:
            continue
        kind = "inner" if abs(off) < 3.0 - 1e-9 else ("lower" if off < 0 else "upper")
        p_ = c + z * n
        samples.append((kind, not abs(z - zg) > 3.0, np.linalg.norm(Pn - p_, axis=1) - Rn))
    if sorted(kind for kind, _, _ in samples if kind != "inner") != ["lower", "upper"]:
        raise ValueError("O2's window replica does not find one sample at each 3 A edge")

    def reading(keep):
        best, label = None, None
        for kind, kept, vals in samples:
            if keep(kind, kept):
                i = int(np.argmin(vals))
                if best is None or float(vals[i]) < best:
                    best, label = float(vals[i]), ln[i]
        ties = set()
        for kind, kept, vals in samples:
            if keep(kind, kept):
                ties |= {ln[i] for i in np.flatnonzero(vals - best <= TIE)}
        return best, label, ties

    raw = {"as computed": reading(lambda kind, kept: kept),
           "both kept": reading(lambda kind, kept: True),
           "both dropped": reading(lambda kind, kept: kind == "inner"),
           "the lower kept only": reading(lambda kind, kept: kind != "upper"),
           "the upper kept only": reading(lambda kind, kept: kind != "lower")}
    if raw["as computed"][0] != rw or raw["as computed"][1] != rw_by:
        raise ValueError("O2's window replica does not give gate_b_window's value and atom")
    return {k: (gbf.fmt(v), a, t) for k, (v, a, t) in raw.items()}


def compare(row: dict, got: dict, windows: dict) -> tuple[list[str], list[str]]:
    """(differences, admitted) between the release's row and the re-run's values. Radii, classes, G1' and the classes
    at the moved lines must be equal. An atom may differ only by a tie on this platform (within TIE); O2's window must
    equal one of its readings, value and atom; zg* - zg must have the release's magnitude, written with two decimals.
    Each admitted difference is named."""
    differ, admitted = [], []
    for c in STRICT:
        if got[c] != row[c]:
            differ.append(f"{c} {got[c]!r} against {row[c]!r}")
    for col, ties in (("a_set_by", got["a_ties"]), ("b_fixed_set_by", got["b_ties"])):
        if got[col] == row[col]:
            continue
        if row[col] in ties:
            admitted.append(f"{col} {got[col]!r} against {row[col]!r}: on this platform both set the radius to within "
                            f"{TIE:g} A, a tie that rounding decides")
        else:
            differ.append(f"{col} {got[col]!r} against {row[col]!r}")
    value, label = row["radius_b_o2_window"], row["o2_window_set_by"]
    found = [k for k, (v, a, ties) in windows.items() if v == value and label in ties]
    if not found:
        differ.append(f"O2's window {windows['as computed'][:2]!r} against {(value, label)!r} (its readings by its edge: "
                      + "; ".join(f"{k} {v} {a}" for k, (v, a, _) in windows.items() if k != "as computed") + ")")
    else:
        k = "as computed" if "as computed" in found else found[0]
        if k != "as computed":
            admitted.append(f"O2's window {windows['as computed'][0]} against {value}: the release's reading has its two "
                            f"samples at exactly 3 A {EDGE_WORDS[k]}, which O2's arithmetic decides by rounding")
        if label != windows[k][1]:
            admitted.append(f"o2_window_set_by {windows[k][1]!r} against {label!r}: on this platform both set the "
                            f"window's value to within {TIE:g} A, a tie that rounding decides")
    mine, theirs = got["zg_star_minus_zg"], row["zg_star_minus_zg"]
    if not (TWO_DECIMALS.fullmatch(mine) and TWO_DECIMALS.fullmatch(theirs)) or mine.lstrip("-") != theirs.lstrip("-"):
        differ.append(f"zg_star_minus_zg {mine!r} against {theirs!r}")
    elif mine != theirs:
        admitted.append(f"zg_star_minus_zg {mine} against {theirs}: the same magnitude; the sign follows B's axis, an "
                        f"eigenvector, whose direction LAPACK leaves arbitrary")
    return differ, admitted


def bumped(value: str) -> str:
    return f"{float(value) + 0.01:.2f}"


def other_class(c: str) -> str:
    return "open" if c != "open" else "closed"


def controls(row: dict, got: dict, windows: dict, chains: list[str]) -> tuple[int, list[str], list[str]]:
    """Planted faults compare() must catch, and plants it must admit, each made on the re-run's own values as a row
    (base), which must first compare clean, so that a real difference cannot mask or mimic a control's outcome.
    Returns (plants made, controls that did not behave as stated, plants that cannot be made for this entry)."""
    base = dict(row)
    base.update({k: v for k, v in got.items() if k in row})
    if compare(base, got, windows) != ([], []):
        return 0, ["the re-run's own values do not compare clean"], []
    own, rest = base["b_fixed_set_by"].split(":", 1)
    copies = [f"{c}:{rest}" for c in chains if c != own]
    tied = [x for x in copies if x in got["b_ties"]]
    untied = [x for x in copies if x not in got["b_ties"]]
    z = base["zg_star_minus_zg"]
    lo, hi = base["class_at_minus_0_5"].split("/"), base["class_at_plus_0_5"].split("/")
    W = ("radius_b_o2_window", "o2_window_set_by")
    plants = [  # (name, column or columns, planted value or values, "caught" or "admitted")
        ("A's radius changed by 0.01 A", "radius_a", bumped(base["radius_a"]), "caught"),
        ("the fixed B's radius changed by 0.01 A", "radius_b_fixed", bumped(base["radius_b_fixed"]), "caught"),
        ("A's class changed", "class_a", other_class(base["class_a"]), "caught"),
        ("the fixed B's class changed", "class_b_fixed", other_class(base["class_b_fixed"]), "caught"),
        ("G1' changed", "g1_prime_agree", "no" if base["g1_prime_agree"] == "yes" else "yes", "caught"),
        ("a class at the lines less 0.5 A changed", "class_at_minus_0_5", f"{other_class(lo[0])}/{lo[1]}", "caught"),
        ("a class at the lines plus 0.5 A changed", "class_at_plus_0_5", f"{hi[0]}/{other_class(hi[1])}", "caught"),
        ("A's atom renamed", "a_set_by", base["a_set_by"] + "X", "caught"),
        ("the fixed B's atom renamed", "b_fixed_set_by", base["b_fixed_set_by"] + "X", "caught"),
        ("O2's window's atom renamed", "o2_window_set_by", base["o2_window_set_by"] + "X", "caught"),
        ("O2's window outside all its readings", "radius_b_o2_window",
         f"{max(float(v) for v, _, _ in windows.values()) + 0.01:.2f}", "caught"),
        ("zg* - zg's magnitude changed by 0.01", "zg_star_minus_zg",
         ("-" if z.startswith("-") else "") + bumped(z.lstrip("-")), "caught"),
        ("zg* - zg written with two signs", "zg_star_minus_zg", "--" + z.lstrip("-"), "caught"),
        ("zg* - zg's sign flipped", "zg_star_minus_zg", z[1:] if z.startswith("-") else "-" + z, "admitted"),
    ]
    not_made = []
    if untied:
        plants.append(("the fixed B's atom in a chain whose copy does not tie", "b_fixed_set_by", untied[0], "caught"))
    else:
        not_made.append("the fixed B's atom in a chain whose copy does not tie: every chain's copy ties")
    if tied:
        plants.append(("the fixed B's atom in a chain whose copy ties", "b_fixed_set_by", tied[0], "admitted"))
    else:
        not_made.append("the fixed B's atom in a chain whose copy ties: no other chain's copy ties")
    seen = {windows["as computed"][:2]}
    for k, (v, a, _) in windows.items():
        if (v, a) not in seen:
            seen.add((v, a))
            plants.append((f"O2's window read with {EDGE_WORDS[k]}", W, (v, a), "admitted"))
    pairs = [(v, a2) for v, _, _ in windows.values() for v2, a2, _ in windows.values()
             if v2 != v and not any(vv == v and a2 in tt for vv, _, tt in windows.values())]
    if pairs:
        plants.append(("O2's window: one reading's value with another reading's atom", W, pairs[0], "caught"))
    bad = []
    for name, col, value, want in plants:
        planted = dict(base)
        planted.update(dict(zip(col, value)) if isinstance(col, tuple) else {col: value})
        if planted == base:
            bad.append(f"{name}: the plant changed nothing")
            continue
        differ, admitted = compare(planted, got, windows)
        if want == "caught" and not differ:
            bad.append(f"{name}: not caught")
        if want == "admitted" and (differ or not admitted):
            bad.append(f"{name}: not admitted as a named reading")
    return len(plants), bad, not_made


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    head = lines[0].split("\t")
    return [dict(zip(head, ln.split("\t"))) for ln in lines[1:]]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def check_code() -> list[str]:
    cd = load("codedigest", CODE / "codedigest.py")
    bad = []
    for r in rows(CODE / "digests.tsv"):
        got = cd.digest(CODE / r["path"])
        if got != r["codedigest_of_the_code_that_ran"]:
            bad.append(f"{r['path']}: code digest {got}, the code that ran {r['codedigest_of_the_code_that_ran']}")
    return bad


def check_s(g, gbf) -> tuple[list[str], list[str]]:
    sys.path.insert(0, str(CODE / "s13"))
    gbf.GATE_PY = CODE / "o2" / "gate.py"
    gbf.O2_TABLE = RELEASE / "curation" / "o2_gate_measurements.tsv"
    gbf.S2_TABLE = RELEASE / "curation" / "s2_gate_9zo8_9zoe.tsv"
    chk = load("check_gate_b_fixed", CODE / "s13" / "check_gate_b_fixed.py")
    tests, _ = chk.run_tests(g)
    report, bad = [], []
    for name, problems, fault, fault_problems in tests:
        key = name.split()[0]
        if key in NOT_RUN:
            report.append(f"{name}: not run here: {NOT_RUN[key]}")
            continue
        ok = not problems and bool(fault_problems)
        report.append(f"{name}: {'pass' if not problems else 'FAIL'}; control ({fault}): "
                      f"{'caught' if fault_problems else 'NOT CAUGHT'}")
        if not ok:
            bad.append(name)
    return report, bad


def write_new(path: Path, data: bytes) -> None:
    """Write a file in one step, so that an interrupted run leaves no partial file under its name."""
    part = path.with_name(path.name + ".part")
    part.write_bytes(data)
    os.replace(part, path)


def coordinates(entry: str, cache: Path, retrievals: list[dict]) -> tuple[bytes | None, str]:
    rel = f"cache/rcsb/2026-10-06/{entry}.cif.gz"
    recs = [r for r in retrievals if r.get("stored_at") == rel]
    if not recs:
        return None, f"no retrieval record stored {rel}"
    rec = recs[-1]
    path = cache / f"{entry}.cif.gz"
    fetched = not path.exists()  # a file already in the cache folder is read, and never replaced or renamed
    if fetched:
        with urllib.request.urlopen(rec["request"]["url"], timeout=120) as resp:
            data = resp.read()
    else:
        data = path.read_bytes()
    if sha256(data) == rec["generated"]:
        if fetched:
            write_new(path, data)
        return data, rec["id"]
    patch_file = PATCHES / f"{entry}.json"
    if not patch_file.is_file():
        rev = {r["entry"]: r for r in rows(REVISIONS)}.get(entry, {})
        return None, (f"its file is not the one retrieval record {rec['id']} holds ({rec['generated']}); this release "
                      f"measured revision {rev.get('structure_model_revision', '?')} of {rev.get('revision_date', '?')},"
                      f" and holds no patch to rebuild it from the file the PDB serves now")
    patch = json.loads(patch_file.read_text(encoding="utf-8"))
    rb = load("rebuild_revision", PATCHES.parent / "rebuild_revision.py")
    if fetched:
        write_new(cache / f"{entry}.served.cif.gz", data)  # what the PDB serves, kept under its own name
    try:
        rebuilt = rb.rebuild(data, patch)
    except rb.NotRebuilt as e:
        return None, f"its file is not the one retrieval record {rec['id']} holds, and could not be rebuilt from it: {e}"
    if sha256(rebuilt) != rec["generated"]:  # the guard, with the SHA-256 the record holds
        return None, f"its file is not the one retrieval record {rec['id']} holds; {rb.why_refused(patch)}"
    if fetched:
        write_new(path, rebuilt)
    return rebuilt, f"{rec['id']}, rebuilt from revision {patch['from']['revision']} with patches/{entry}.json"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache")
    ap.add_argument("--retrievals")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--no-check-s", action="store_true")
    ap.add_argument("--readings", help="also write each entry's five readings of O2's window (as computed, and its four "
                    "by the 3 A edge) to this tab-separated file, which must lie outside the release")
    a = ap.parse_args(argv)
    if a.readings and Path(a.readings).resolve().is_relative_to(RELEASE.resolve()):
        print("--readings: the file must lie outside the release")
        return 2
    failures = check_code()
    for f in failures:
        print(f"CODE: {f}")
    g = load("o2_gate", CODE / "o2" / "gate.py")
    sys.path.insert(0, str(CODE / "s13"))
    gbf = load("gate_b_fixed", CODE / "s13" / "gate_b_fixed.py")
    if not a.no_check_s:
        report, bad = check_s(g, gbf)
        for line in report:
            print(f"check S: {line}")
        failures += [f"check S: {b}" for b in bad]
    retrievals = [json.loads(x) for x in Path(a.retrievals or RETRIEVALS).read_text(encoding="utf-8").splitlines() if x]
    cache = Path(a.cache) if a.cache else Path(tempfile.mkdtemp(prefix="rerun_gate_"))
    cache.mkdir(parents=True, exist_ok=True)
    try:
        return measure(a, g, gbf, cache, retrievals, failures)
    finally:
        if not a.cache:
            shutil.rmtree(cache, ignore_errors=True)


def measure(a, g, gbf, cache: Path, retrievals: list[dict], failures: list[str]) -> int:
    table = rows(TABLE)
    same = with_admitted = plants = edges = tied = matched = 0
    readings = ["entry\treading\tradius_b_o2_window\to2_window_set_by"]
    for row in table:
        entry = row["entry"]
        if a.only and entry not in a.only:
            continue
        matched += 1
        data, basis = coordinates(entry, cache, retrievals)
        if data is None:
            failures.append(f"{entry}: refused: {basis}")
            print(f"{entry}: refused: {basis}")
            continue
        text = gzip.decompress(data).decode("utf-8")
        gate = int(row["gate_residue"][1:])
        m, ch = g.load_a(text)
        ra = g.gate_a(m, ch, gate)
        st_b = g.load_b(text)  # read, never changed, by both B's: one parse serves every reading
        rb, by, dzg = gbf.gate_b_fixed(g, st_b, gate, with_heights=True)
        rw, rw_by = gbf.gate_b_window(g, st_b, gate, 3.0, with_atom=True)
        try:
            _, a_by, a_tie = a_ties(g, gbf, m, ch, gate)
            b_tie = b_fixed_ties(g, gbf, st_b, gate, rb, by)
            windows = window_readings(g, gbf, st_b, gate, rw, rw_by)
        except ValueError as e:
            failures.append(f"{entry}: refused: {e}")
            print(f"{entry}: refused: {e}")
            continue
        chains = [c.name for c in sorted([c for c in st_b[0]], key=lambda c: -len(c))[:4]]  # as B selects them
        got = {"radius_a": gbf.fmt(ra), "a_set_by": a_by, "radius_b_fixed": gbf.fmt(rb), "b_fixed_set_by": by,
               "class_a": g.classify(ra), "class_b_fixed": g.classify(rb),
               "g1_prime_agree": "yes" if g.classify(ra) == g.classify(rb) and abs(ra - rb) <= gbf.TOLERANCE else "no",
               "class_at_minus_0_5": f"{g.classify_at(ra, -0.5)}/{g.classify_at(rb, -0.5)}",
               "class_at_plus_0_5": f"{g.classify_at(ra, 0.5)}/{g.classify_at(rb, 0.5)}",
               "radius_b_o2_window": gbf.fmt(rw), "o2_window_set_by": rw_by, "zg_star_minus_zg": gbf.fmt(dzg),
               "a_ties": a_tie, "b_ties": b_tie}
        readings += [f"{entry}\t{k}\t{v}\t{atom}" for k, (v, atom, _) in windows.items()]
        differ, admitted = compare(row, got, windows)
        n_plants, bad, not_made = controls(row, got, windows, chains)
        plants += n_plants
        if differ:
            failures.append(f"{entry}: " + "; ".join(differ))
        else:
            same += 1
            with_admitted += bool(admitted)
        failures += [f"{entry}: control: {b}" for b in bad]
        state = ("DIFFERS: " + "; ".join(differ) if differ else "same") + (
            ("; admitting: " if differ else ", admitting: ") + "; ".join(admitted) if admitted else "")
        print(f"{entry}: {state} (A {got['radius_a']}, fixed B {got['radius_b_fixed']}, O2's window "
              f"{got['radius_b_o2_window']}; {basis})")
        if len({v for v, _, _ in windows.values()}) > 1:
            edges += 1
            print("  O2's window by its two samples at exactly 3 A: "
                  + "; ".join(f"{EDGE_WORDS[k]} {v}" for k, (v, _, _) in windows.items() if k != "as computed"))
        ties_here = [(col, sorted(t)) for col, t in (("A's atom", a_tie), ("the fixed B's atom", b_tie),
                                                     ("O2's window's atom", windows["as computed"][2])) if len(t) > 1]
        if ties_here:
            tied += 1
            print("  ties on this platform: " + "; ".join(f"{col}: {', '.join(t)}" for col, t in ties_here))
        near = [name for name, x in (("radius_a", ra), ("radius_b_fixed", rb), ("zg_star_minus_zg", dzg))
                if abs((abs(x) * 100) % 1 - 0.5) < 1e-6]
        if near:
            print(f"  within 1e-8 A of a rounding boundary at the hundredth: {', '.join(near)}")
        for b in bad:
            print(f"  control: {b}")
        for nm in not_made:
            print(f"  control not made: {nm}")
    if a.only and not matched:
        failures.append(f"--only: no entry of the table is {a.only}")
    print(f"rerun: {same} entries the same ({with_admitted} of them with admitted readings, each named above); "
          f"O2's window differs by its edge in {edges}; atoms tie in {tied}; controls: {plants} plants, "
          f"{'all as stated' if not any(': control: ' in f for f in failures) else 'NOT all as stated'}; "
          f"{len(failures)} failures")
    if a.readings:
        Path(a.readings).write_bytes(("\n".join(readings) + "\n").encode("utf-8"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
