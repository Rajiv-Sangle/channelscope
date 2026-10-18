#!/usr/bin/env python3
"""gate_b_fixed.py - S13's re-measurement: each structure's pore at the gate, by O2's implementation A unchanged and by
implementation B fixed to the gate's own height. Committed with its criteria, before the run; revised after independent
critiques, before any run. Its pass rules are in what/context/context_channelscope_s13_remeasurement_criteria.md. --run
refuses to read any real structure until every file in DEPENDS is in one commit and unchanged since (decision S13: the
rules are committed before the run). From check R0 on, every run writes its record, with any error that stops it, and a
record is never overwritten.

Decision S13 (the operator, 2026-10-06 14:24:08 IST; what/context/questions/qanote_decision_points_explained.md): accept
O2's classes as measured; measure the gate again with B fixed, as a new measurement whose pass rules are committed before
it runs, keeping the first run intact.

A is imported from how/runtime/channelscope/o2/gate.py unchanged, refused unless that file hashes to GATE_PY_SHA256 and
o2_gate_measurements.tsv's header names the same hash.

The fixed B keeps O2's B parser (gemmi), chain choice (the four longest polymer chains; refused when fewer than four
exist) and axis (the transmembrane region's centroid, the gate's residue -117 to +100, along its distinct principal
axis), and changes where and over what the probe reads (all decided before any real run):
  - its height, zg*: the mean, over the four chains, of the height along B's axis of each chain's gate-residue heavy
    atom nearest the axis (less its radius), the atoms A measures. O2's zg, the centroid of all the gate residues' heavy
    atoms, can sit 1 to 2 A from the side-chain atoms that close the pore;
  - its atoms: only heavy atoms within a slab 2.5 A deep (1.25 A either side of zg*), less than half a helical turn
    (5.4 A), so that a constriction one turn away cannot set it; atoms just outside the slab, which may lie nearer the
    probe, are ignored;
  - its value: the least, over those atoms, of the distance from the probe at zg* on B's axis less the atom's radius,
    reported with the atom that sets it.
O2's B itself, with its 3 A window, stays a second, named quantity ("B, O2's window"): recomputed by gate_b_window, with
the atom that sets it, and checked against the committed tables (check R0).

    uv run --project how/runtime/channelscope --with gemmi==0.7.5 --with biopython==1.88 python how/runtime/channelscope/s13/check_gate_b_fixed.py
    uv run --project how/runtime/channelscope --with gemmi==0.7.5 --with biopython==1.88 python how/runtime/channelscope/s13/gate_b_fixed.py --run COMMIT
(biopython 1.88 and numpy 2.5.3 are the project's lock, how/runtime/channelscope/uv.lock.)

ChannelScope's agent (a fork of [a working record, not public]), 2026-10-06.
"""
import gzip
import hashlib
import importlib.util
import json
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
VAULT = Path(__file__).resolve().parents[4]
GRAPH = VAULT / "what" / "evidence_graph"
GATE_PY = VAULT / "how" / "runtime" / "channelscope" / "o2" / "gate.py"
GATE_PY_SHA256 = "sha256:d54a41599787f383d4612a404dd72928ac51afef84866ef1b8524db39b759ca2"  # O2's committed run
O2_TABLE = GRAPH / "curation" / "o2_gate_measurements.tsv"
S2_TABLE = GRAPH / "curation" / "s2_gate_9zo8_9zoe.tsv"
RETRIEVALS = GRAPH / "records" / "retrieval.jsonl"
CRITERIA = VAULT / "what" / "context" / "context_channelscope_s13_remeasurement_criteria.md"
CHECKS = HERE / "check_gate_b_fixed.py"
OUT = GRAPH / "curation" / "s13_gate_remeasurement.tsv"
# Every committed file the run reads or relies on. The coordinate files are git-ignored, so each is checked against its
# retrieval record instead.
DEPENDS = [CRITERIA, Path(__file__).resolve(), CHECKS, GATE_PY, O2_TABLE, S2_TABLE, RETRIEVALS]
TOLERANCE = 1.0   # A and B's radii, A; O2's check G1, committed in b932329, unchanged
SLAB_HALF = 1.25  # A: the slab is 2.5 A deep, less than half a helical turn (5.4 A)
TURN_DEG = 120.0  # live test L1: each gate isoleucine's side chain turned about its CA-CB bond
NEW = {"9ZO8": ("Oryctolagus cuniculus", "closed pore", "closed"),
       "9ZOE": ("Oryctolagus cuniculus", "open pore", "open")}
RING = (-5.4, 2.55, "N")  # P4 (by construction): four nitrogen atoms one turn below zg*, 2.55 A from B's axis
# The structures whose O2's window O2's diagnosis found set by a residue one turn below the gate (live test L2)
DIAGNOSED = ("7M6L", "7T65", "6X35")


def sha256(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()


def code_hash(text):
    return sha256(text.replace("\r\n", "\n").encode())


def pin_problem(gate_text, header_line):
    """None if gate.py's text hashes to the pinned code and the committed table names it; else the reason."""
    code = code_hash(gate_text)
    if code != GATE_PY_SHA256:
        return "o2/gate.py's hash %s is not the pinned %s" % (code, GATE_PY_SHA256)
    if ("(code %s;" % code) not in header_line:
        return "o2_gate_measurements.tsv's header does not name the pinned hash"
    return None


def load_gate_module():
    problem = pin_problem(GATE_PY.read_text(encoding="utf-8"), O2_TABLE.read_text(encoding="utf-8").splitlines()[1])
    if problem:
        sys.exit("refused: " + problem)
    spec = importlib.util.spec_from_file_location("o2_gate", GATE_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ring_points(c, n, height, radial):
    u = np.cross(n, [1.0, 0.0, 0.0])
    if np.linalg.norm(u) < 1e-6:
        u = np.cross(n, [0.0, 1.0, 0.0])
    u = u / np.linalg.norm(u)
    vv = np.cross(n, u)
    return [c + height * n + radial * (np.cos(np.radians(t)) * u + np.sin(np.radians(t)) * vv)
            for t in (0.0, 90.0, 180.0, 270.0)]


# ---------------------------------------------------------------------------------- B, O2's window (a named second value)
def gate_b_window(g, st, gate, half_window, move_out=0.0, rename=False, drop_chain=False, ring=None, with_atom=False):
    """O2's gate_b, line for line, with the probe's window as a parameter: half_window=3.0 is O2's B. with_atom=True
    also returns the atom that sets the value (a parallel list of labels; the arithmetic is O2's). ring=(dz, radial,
    element) plants four atoms dz A along B's axis from O2's zg, at radial A from the axis."""
    model = st[0]
    chains = sorted([ch for ch in model], key=lambda ch: -len(ch))[:4]
    if drop_chain:
        chains = sorted([ch for ch in model], key=lambda ch: -len(ch))
        chains = chains[1:5]
    gate_atoms, tm = [], []
    for ch in chains:
        found = None
        for r in ch:
            if r.seqid.num == gate and r.seqid.icode == " ":
                found = r
            if gate - 117 <= r.seqid.num <= gate + 100:
                tm += [a.pos.tolist() for a in r if a.element.name.upper() in g.RADII]
        if found is None or found.name != "ILE" or rename:
            raise g.Refused("B: a chain among the four longest has no isoleucine at %d" % gate)
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
    if ring is not None:
        allatoms += [(p.tolist(), g.RADII[ring[2]], False) for p in _ring_points(c, n, zg + ring[0], ring[1])]
        labels += ["planted ring"] * 4
    P = np.array([p for p, _, _ in allatoms], dtype=float)
    R = np.array([rr for _, rr, _ in allatoms], dtype=float)
    if move_out:
        isg = np.array([f for _, _, f in allatoms])
        rel = P[isg] - c
        perp = rel - np.outer(rel.dot(n), n)
        P[isg] = P[isg] + (perp / np.linalg.norm(perp, axis=1)[:, None]) * move_out
    rel = P - c
    along = rel.dot(n)
    radial_d = np.linalg.norm(rel - np.outer(along, n), axis=1)
    near = (np.abs(along - zg) <= 15.0) & (radial_d <= 25.0)
    Pn, Rn = P[near], R[near]
    ln = [lab for lab, keep in zip(labels, near) if keep]
    best, best_label = None, None
    for z in np.arange(zg - 12.0, zg + 12.0001, 0.25):
        if abs(z - zg) > half_window:
            continue
        p = c + z * n
        vals = np.linalg.norm(Pn - p, axis=1) - Rn
        i = int(np.argmin(vals))
        val = float(vals[i])
        if best is None or val < best:
            best, best_label = val, ln[i]
    return (best, best_label) if with_atom else best


# ------------------------------------------------------------------------------------------------------ the fixed B
def gate_b_fixed(g, st, gate, move_out=0.0, ring=None, dz=0.0, half_depth=SLAB_HALF, height="narrowest",
                 with_heights=False):
    """The fixed B: (radius, the atom that sets it as "chain:resname resnum atom"), and with_heights=True adds zg* - zg,
    the reading height less O2's. move_out moves the gate residues' heavy atoms along their perpendicular from B's axis
    (negative: inward); ring plants four atoms (P4); dz shifts the reading height along the axis (P5). height="centroid"
    reads at O2's zg instead of zg* (used only by the checks, to show why zg* is needed)."""
    model = st[0]
    chains = sorted([ch for ch in model], key=lambda ch: -len(ch))[:4]
    if len(chains) != 4:
        raise g.Refused("B: %d polymer chains, fewer than 4" % len(chains))
    tm, atoms = [], []  # atoms: (xyz, radius, is_gate, label)
    for ch in chains:
        found = None
        for r in ch:
            if r.seqid.num == gate and r.seqid.icode == " ":
                found = r
            if gate - 117 <= r.seqid.num <= gate + 100:
                tm += [a.pos.tolist() for a in r if a.element.name.upper() in g.RADII]
            for a in r:
                el = a.element.name.upper()
                if el in g.RADII:
                    atoms.append((a.pos.tolist(), g.RADII[el], r.seqid.num == gate and r.seqid.icode == " ",
                                  "%s:%s %d %s" % (ch.name, r.name, r.seqid.num, a.name)))
        if found is None or found.name != "ILE":
            raise g.Refused("B: a chain among the four longest has no isoleucine at %d" % gate)
    tm = np.array(tm, dtype=float)
    c = tm.mean(axis=0)
    w, v = np.linalg.eigh(np.cov((tm - c).T))
    k = int(np.argmax([abs(w[i] - np.mean([w[j] for j in range(3) if j != i])) for i in range(3)]))
    n = v[:, k] / np.linalg.norm(v[:, k])
    P = np.array([p for p, _, _, _ in atoms], dtype=float)
    R = np.array([rr for _, rr, _, _ in atoms], dtype=float)
    isg = np.array([f for _, _, f, _ in atoms])
    labels = [lab for _, _, _, lab in atoms]
    if move_out:
        rel = P[isg] - c
        perp = rel - np.outer(rel.dot(n), n)
        P[isg] = P[isg] + (perp / np.linalg.norm(perp, axis=1)[:, None]) * move_out
    rel = P - c
    along = rel.dot(n)
    radial = np.linalg.norm(rel - np.outer(along, n), axis=1)
    z_centroid = float(along[isg].mean())
    heights = []
    for ch in chains:
        mine = np.array([isg[i] and labels[i].startswith(ch.name + ":") for i in range(len(labels))])
        j = np.flatnonzero(mine)[np.argmin((radial - R)[mine])]
        heights.append(along[j])
    z_narrowest = float(np.mean(heights))
    zr = (z_centroid if height == "centroid" else z_narrowest) + dz
    if ring is not None:
        P = np.vstack([P, np.array(_ring_points(c, n, zr + ring[0], ring[1]))])
        R = np.concatenate([R, np.full(4, g.RADII[ring[2]])])
        labels = labels + ["planted ring"] * 4
        along = (P - c).dot(n)
    inslab = np.abs(along - zr) <= half_depth
    d = np.linalg.norm(P - (c + zr * n), axis=1) - R
    d[~inslab] = np.inf
    j = int(np.argmin(d))
    if not np.isfinite(d[j]):
        raise g.Refused("B: no atom within the slab")
    if with_heights:
        return float(d[j]), labels[j], z_narrowest - z_centroid
    return float(d[j]), labels[j]


# ---------------------------------------------------------------------------------------- perturbations in the text
def edited_text(text, gate, rename_to=None, drop_chain=None, turn_deg=None):
    """The structure text with, through gemmi's mmCIF document and nothing else changed: the gate residues' names
    changed (rename_to); one chain's atoms removed (drop_chain, an author chain ID); or each gate isoleucine's side-chain
    atoms beyond CB turned turn_deg degrees about its CA-CB bond (turn_deg)."""
    import gemmi
    doc = gemmi.cif.read_string(text)
    tab = doc.sole_block().find("_atom_site.", ["auth_asym_id", "auth_seq_id", "label_comp_id", "auth_comp_id",
                                                "auth_atom_id", "Cartn_x", "Cartn_y", "Cartn_z"])
    if rename_to:
        for row in tab:
            if row[1] == str(gate):
                row[2] = rename_to
                row[3] = rename_to
    if drop_chain:
        for i in reversed([i for i, row in enumerate(tab) if row[0] == drop_chain]):
            tab.remove_row(i)
    if turn_deg is not None:
        frames = {}
        for row in tab:
            if row[1] == str(gate) and row[4] in ("CA", "CB"):
                frames.setdefault(row[0], {})[row[4]] = np.array([float(row[5]), float(row[6]), float(row[7])])
        th = np.radians(turn_deg)
        for row in tab:
            f = frames.get(row[0], {})
            if row[1] == str(gate) and row[4] not in ("N", "CA", "C", "O", "CB") and "CA" in f and "CB" in f:
                axis = (f["CB"] - f["CA"]) / np.linalg.norm(f["CB"] - f["CA"])
                p = np.array([float(row[5]), float(row[6]), float(row[7])]) - f["CB"]
                q = (p * np.cos(th) + np.cross(axis, p) * np.sin(th) + axis * axis.dot(p) * (1 - np.cos(th))
                     + f["CB"])
                row[5], row[6], row[7] = "%.3f" % q[0], "%.3f" % q[1], "%.3f" % q[2]
    return doc.as_string()


# ----------------------------------------------------------------------------------------------------- the run guard
def resolve(commit):
    out = subprocess.run(["git", "-C", str(VAULT), "rev-parse", "--verify", "--quiet", commit + "^{commit}"],
                         capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def committed_problems(commit, paths):
    """Problems that forbid the run: the commit must resolve, and each path must be in it and unchanged since."""
    full = resolve(commit)
    if full is None:
        return ["%s is not a commit" % commit]
    bad = []
    for p in paths:
        rel = p.relative_to(VAULT).as_posix()
        if subprocess.run(["git", "-C", str(VAULT), "cat-file", "-e", "%s:%s" % (full, rel)],
                          capture_output=True).returncode != 0:
            bad.append("%s is not in commit %s" % (rel, full))
        elif subprocess.run(["git", "-C", str(VAULT), "diff", "--quiet", full, "--", rel],
                            capture_output=True).returncode != 0:
            bad.append("%s has changed since commit %s" % (rel, full))
    return bad


def committed_values():
    """The committed radii: O2's 24 and the two measured after it. entry -> (species, radius_A, radius_B O2's window)."""
    vals = {}
    for table in (O2_TABLE, S2_TABLE):
        for line in table.read_text(encoding="utf-8").splitlines():
            if line.startswith("#") or line.startswith("entry\t"):
                continue
            f = line.split("\t")
            vals[f[0]] = (f[1], f[3], f[4])
    return vals


def fmt(x):
    return "%.2f" % x if x is not None else "-"


def residue_of(label):
    """'A:GLN 4933 NE2' -> 'GLN 4933'."""
    return " ".join(label.split(":", 1)[1].split()[:2]) if label and ":" in label else label



class RunStop(Exception):
    """A planned stop after check R0 has begun (R0 itself failing)."""


def a_with_atom(g, model, chains, gate, radii=None):
    """A's value, from O2's gate_a unchanged, with the atom that sets it: a replica of gate_a's arithmetic (no move) that
    must give exactly gate_a's value, else ValueError. radii replaces O2's atom radii (used only by check S's control)."""
    value = g.gate_a(model, chains, gate)
    radii = g.RADII if radii is None else radii
    res = [model[cid][(" ", gate, " ")] for cid in chains]
    ca = np.array([r["CA"].coord for r in res], dtype=float)
    c = ca.mean(axis=0)
    n = np.linalg.svd(ca - c)[2][-1]
    best, label = None, None
    for cid, r in zip(chains, res):
        for a in r:
            el = a.element.strip().upper()
            if el == "H" or el not in radii:
                continue
            v = a.coord.astype(float) - c
            perp = v - v.dot(n) * n
            val = np.linalg.norm(perp) - radii[el]
            if best is None or val < best:
                best, label = val, "%s:%s %d %s" % (cid, r.get_resname(), gate, a.get_id())
    if best != value:
        raise ValueError("A's replica gives %r where gate_a gives %r" % (best, value))
    return value, label


def run_body(g, species, words, committed, texts, rows, results):
    """Everything from check R0 on. Fills rows and results as it goes, so that a stop leaves what was done."""
    ra, rw, rw_by = {}, {}, {}
    for pid in species:
        gate = g.GATE[species[pid]]
        try:
            m, ch = g.load_a(texts[pid])
            ra[pid] = g.gate_a(m, ch, gate)
        except g.Refused:
            ra[pid] = None
        try:
            rw[pid], rw_by[pid] = gate_b_window(g, g.load_b(texts[pid]), gate, 3.0, with_atom=True)
        except g.Refused:
            rw[pid], rw_by[pid] = None, "-"
        if (fmt(ra[pid]), fmt(rw[pid])) != (committed[pid][1], committed[pid][2]):
            raise RunStop("R0 failed for %s: A %s and O2's window %s, committed %s and %s" % (
                pid, fmt(ra[pid]), fmt(rw[pid]), committed[pid][1], committed[pid][2]))
    results.append("R0: pass (A and O2's window equal the committed radii, to the hundredth, for all %d)" % len(species))
    for pid in species:
        gate = g.GATE[species[pid]]
        m, ch = g.load_a(texts[pid])
        _, a_by = a_with_atom(g, m, ch, gate)
        try:
            rb, by, dzg = gate_b_fixed(g, g.load_b(texts[pid]), gate, with_heights=True)
        except g.Refused as e:
            rb, by, dzg = None, "refused (%s)" % e, None
        ca_ = g.classify(ra[pid]) if ra[pid] is not None else "refused"
        cb_ = g.classify(rb) if rb is not None else "refused"
        g1 = ra[pid] is not None and rb is not None and ca_ == cb_ and abs(ra[pid] - rb) <= TOLERANCE
        rows.append(dict(pid=pid, species=species[pid], gate=gate, ra=ra[pid], a_by=a_by, rb=rb, by=by, ca=ca_,
                         cb=cb_, g1=g1, rw=rw[pid], rw_by=rw_by[pid], words=words[pid], dzg=dzg,
                         lo="%s/%s" % (g.classify_at(ra[pid], -0.5) if ra[pid] is not None else "-",
                                       g.classify_at(rb, -0.5) if rb is not None else "-"),
                         hi="%s/%s" % (g.classify_at(ra[pid], 0.5) if ra[pid] is not None else "-",
                                       g.classify_at(rb, 0.5) if rb is not None else "-")))
    by_pid = {r["pid"]: r for r in rows}
    g1_fail = [r["pid"] for r in rows if not r["g1"]]
    results.append("G1' (A and the fixed B: the same class, radii within %.1f A): %s" % (
        TOLERANCE, "pass" if not g1_fail else "FAIL: " + ", ".join(g1_fail)))
    t, v = by_pid["5TB0"], by_pid["5T9V"]
    g2 = (t["ca"], t["cb"], v["ca"], v["cb"]) == ("closed", "closed", "open", "open")
    results.append("G2' (5TB0 closed, 5T9V open, by both; its live part is 5TB0's fixed B): %s. 5TB0: A %s, fixed B %s "
                   "(set by %s); 5T9V: A %s, fixed B %s (set by %s)" % (
                       "pass" if g2 else "FAIL", fmt(t["ra"]), fmt(t["rb"]), t["by"], fmt(v["ra"]), fmt(v["rb"]),
                       v["by"]))

    def add(name, kind, ok, detail):
        results.append("%s [%s] %s: %s" % (name, kind, "caught" if ok else "NOT CAUGHT", detail))

    def try_a(text, gate):
        try:
            m, ch = g.load_a(text)
            return False, "A measured %.2f" % g.gate_a(m, ch, gate)
        except g.Refused as e:
            return True, "A refused (%s)" % e

    def try_b(text, gate):
        try:
            val, by = gate_b_fixed(g, g.load_b(text), gate)
            return False, "the fixed B measured %.2f, set by %s" % (val, by)
        except g.Refused as e:
            return True, "the fixed B refused (%s)" % e

    m, ch = g.load_a(texts["5TB0"])
    a1 = g.gate_a(m, ch, 4937, move_out=4.0)
    add("P1-A", "arithmetic", g.classify(a1) == "open",
        "5TB0's gate atoms 4 A outward: A %.2f (unmoved %.2f), %s" % (a1, t["ra"], g.classify(a1)))
    b1, b1_by = gate_b_fixed(g, g.load_b(texts["5TB0"]), 4937, move_out=4.0)
    add("P1-B", "seen in O2's diagnosis", g.classify(b1) == "open",
        "5TB0's gate atoms 4 A outward: the fixed B %.2f, set by %s, %s" % (b1, b1_by, g.classify(b1)))
    first = g.load_a(texts["5T9V"])[1][0]
    dropped = edited_text(texts["5T9V"], 4937, drop_chain=first)
    ok, detail = try_a(dropped, 4937)
    add("P2-A", "live", ok, "5T9V with chain %s's atoms removed from the text: %s" % (first, detail))
    ok, detail = try_b(dropped, 4937)
    add("P2-B", "live", ok, "5T9V with chain %s's atoms removed from the text: %s" % (first, detail))
    renamed = edited_text(texts["9NMO"], 4935, rename_to="VAL")
    ok, detail = try_a(renamed, 4935)
    add("P3-A", "live", ok, "9NMO with its gate residues renamed valine in the text: %s" % detail)
    ok, detail = try_b(renamed, 4935)
    add("P3-B", "live", ok, "9NMO with its gate residues renamed valine in the text: %s" % detail)
    st = g.load_b(texts["5T9V"])
    plain, plain_by = gate_b_fixed(g, st, 4937)
    ringed, ringed_by = gate_b_fixed(g, st, 4937, ring=RING)
    add("P4", "by construction", abs(ringed - plain) < 0.005,
        "5T9V: the fixed B %.3f without the planted ring (set by %s), %.3f with it (set by %s)" % (
            plain, plain_by, ringed, ringed_by))
    rv, rv_by = gate_b_window(g, st, 4937, 3.0, ring=RING, with_atom=True)
    results.append("P4's ring and O2's window: %.2f, set by %s" % (rv, rv_by))
    for shift in (2.0, -2.0):
        b5, b5_by = gate_b_fixed(g, g.load_b(texts["5TB0"]), 4937, dz=shift)
        agree = g.classify(t["ra"]) == g.classify(b5) and abs(t["ra"] - b5) <= TOLERANCE
        add("P5 %+.0f A" % shift, "live", not agree,
            "5TB0 read %+.0f A from the gate's height: the fixed B %.2f, set by %s, against A %.2f (set by %s); G1' %s"
            % (shift, b5, b5_by, t["ra"], t["a_by"], "passes" if agree else "fails"))
    m, ch = g.load_a(texts["5T9V"])
    a6 = g.gate_a(m, ch, 4937, move_out=-3.0)
    add("P6-A", "arithmetic", g.classify(a6) == "closed",
        "5T9V's gate atoms 3 A inward: A %.2f (unmoved %.2f), %s" % (a6, v["ra"], g.classify(a6)))
    b6, b6_by = gate_b_fixed(g, g.load_b(texts["5T9V"]), 4937, move_out=-3.0)
    add("P6-B", "by construction", g.classify(b6) == "closed",
        "5T9V's gate atoms 3 A inward: the fixed B %.2f, set by %s, %s" % (b6, b6_by, g.classify(b6)))
    turned = edited_text(texts["5TB0"], 4937, turn_deg=TURN_DEG)
    m, ch = g.load_a(turned)
    a_t, a_t_by = a_with_atom(g, m, ch, 4937)
    b_t, b_t_by = gate_b_fixed(g, g.load_b(turned), 4937)
    agree = g.classify(a_t) == g.classify(b_t) and abs(a_t - b_t) <= TOLERANCE
    moved = abs(a_t - t["ra"]) > 0.1
    add("L1", "live", agree and moved,
        "5TB0 with each gate side chain turned %.0f degrees about CA-CB in the text: A %.2f (unturned %.2f), set by %s; "
        "the fixed B %.2f, set by %s; G1' %s; the turn %s" % (
            TURN_DEG, a_t, t["ra"], a_t_by, b_t, b_t_by, "passes" if agree else "fails",
            "moved A by %.2f A" % abs(a_t - t["ra"]) if moved else "did not move A by 0.1 A or more, so L1 tested nothing"))
    for pid in DIAGNOSED:
        r = by_pid[pid]
        other = residue_of(r["rw_by"])
        ok = residue_of(r["by"]) != other or other.endswith(" %d" % r["gate"])
        add("L2 %s" % pid, "live", ok, "%s: O2's window %s, set by %s; the fixed B %s, set by %s" % (
            pid, fmt(r["rw"]), r["rw_by"], fmt(r["rb"]), r["by"]))


def write_record(head_lines, status, rows, results, out=None):
    """Write the run's record to out (OUT unless check S's dry run passes a scratch path); return its sha256."""
    out = OUT if out is None else out
    head = ["entry", "species", "gate_residue", "radius_A", "a_set_by", "radius_B_fixed", "b_fixed_set_by", "class_A",
            "class_B_fixed", "g1_prime_agree", "class_at_minus_0.5A", "class_at_plus_0.5A", "radius_B_o2_window",
            "o2_window_set_by", "zg_star_minus_zg", "deposited_words", "deposited_implies"]
    lines = ["\t".join([r["pid"], r["species"], "I%d" % r["gate"], fmt(r["ra"]), r["a_by"], fmt(r["rb"]), r["by"],
                        r["ca"], r["cb"], "yes" if r["g1"] else "no", r["lo"], r["hi"], fmt(r["rw"]), r["rw_by"],
                        fmt(r["dzg"]), r["words"][0], r["words"][1] or "-"]) for r in rows]
    text = "\n".join(head_lines + ["# Run: " + status] + ["# " + x for x in results]) + "\n" + "\t".join(head) + "\n"
    if lines:
        text += "\n".join(lines) + "\n"
    out.write_text(text, encoding="utf-8", newline="\n")
    return sha256(out.read_bytes())


def main():
    if "--run" not in sys.argv:
        sys.exit(__doc__)
    asked = sys.argv[sys.argv.index("--run") + 1]
    bad = committed_problems(asked, DEPENDS)
    if bad:
        sys.exit("refused: " + "; ".join(bad))
    commit = resolve(asked)
    if OUT.exists():
        sys.exit("refused: %s exists; a run's record is never overwritten" % OUT.relative_to(VAULT))
    g = load_gate_module()
    # Check S, the synthetic tests, run here so that their result is part of this run's record
    sys.path.insert(0, str(HERE))
    import check_gate_b_fixed as chk
    tests, _ = chk.run_tests(g)
    s_fail = [name for name, problems, _, fault_problems in tests if problems or not fault_problems]
    s_line = "Check S: %d tests, %d pass; %d controls caught" % (
        len(tests), sum(1 for x in tests if not x[1]), sum(1 for x in tests if x[3]))
    if s_fail:
        sys.exit("refused: check S failed (%s); %s" % ("; ".join(s_fail), s_line))
    libs = "biopython %s, gemmi %s, numpy %s" % (version("biopython"), version("gemmi"), version("numpy"))
    species = {pid: s for pid, (s, _, _) in g.S.items()}
    words = {pid: (w, e) for pid, (_, w, e) in g.S.items()}
    for pid, (s, w, e) in NEW.items():
        species[pid], words[pid] = s, (w, e)
    committed = committed_values()
    retr = [json.loads(l) for l in RETRIEVALS.read_text(encoding="utf-8").splitlines() if l.strip()]
    texts, inputs = {}, {}
    for pid in species:
        rel = "cache/rcsb/2026-10-06/%s.cif.gz" % pid
        data = (GRAPH / rel).read_bytes()
        rec = [r for r in retr if r.get("stored_at") == rel]
        if not rec or rec[-1]["generated"] != sha256(data):
            sys.exit("refused: input %s does not match its retrieval record; nothing was measured" % pid)
        inputs[pid] = rec[-1]["id"]
        texts[pid] = gzip.decompress(data).decode("utf-8")
    head_lines = [
        "# s13_gate_remeasurement.tsv: the pore at the gate (A), by O2's A and by B fixed to the gate's own height (a 2.5 A",
        "# slab at the height of the gate residues' narrowest atoms), with O2's window as a second value, as",
        "# how/runtime/channelscope/s13/gate_b_fixed.py measured it (code %s) at commit %s," % (
            code_hash(Path(__file__).read_text(encoding="utf-8")), commit),
        "# where its criteria, its checks and every input it names are committed. Generated; never edited.",
        "# %s. Libraries: %s." % (s_line, libs),
        "# Inputs (retrieval records): %s" % "; ".join("%s=%s" % kv for kv in inputs.items()),
    ]
    rows, results, status = [], [], "complete"
    try:
        run_body(g, species, words, committed, texts, rows, results)
    except Exception as e:  # any stop from check R0 on is recorded, with what was done before it
        status = "stopped: %s: %s" % (type(e).__name__, e)
    digest = write_record(head_lines, status, rows, results)
    print("S13 re-measurement at commit %s; %s; %s" % (commit, s_line, libs))
    for r in rows:
        print("%-5s A %6s (%s)  B fixed %6s (%s)  %-13s %-13s %s  O2's window %s (%s)  zg*-zg %s" % (
            r["pid"], fmt(r["ra"]), r["a_by"], fmt(r["rb"]), r["by"], r["ca"], r["cb"], "ok" if r["g1"] else "FAIL",
            fmt(r["rw"]), r["rw_by"], fmt(r["dzg"])))
    for line in results:
        print(line)
    print("Run: %s\nwritten: %s %s" % (status, OUT.relative_to(VAULT), digest))
    if status != "complete":
        sys.exit(1)


if __name__ == "__main__":
    main()
