#!/usr/bin/env python3
"""gate.py - O2, part 2: each structure's pore measured at the gate, by two independent implementations.

The criteria were committed before this script first ran (what/context/context_channelscope_o2_survey_by_condition.md,
commit b932329). ChannelScope's agent, [a working record, not public], 2026-10-06.

    uv run --project how/runtime/channelscope --with gemmi python how/runtime/channelscope/o2/gate.py [--write]

A (Biopython's MMCIFParser): RyR1 chains by entity description; the axis through the centroid of the four gate CA
atoms, normal to their best-fit plane; the radius is the least distance from the axis to a heavy atom of the four gate
residues, less that atom's radius.
B (gemmi): RyR1 chains as the four longest polymer chains; the axis through the transmembrane region's centroid (the
gate's residue -117 to +100, four chains), along its distinct principal axis; the radius is a probe's: along the axis,
12 A either side of the gate's height in 0.25 A steps, the distance to the nearest heavy atom of the four chains less
its radius, and the least of these within 3 A of the gate's height.
They share only the list of structures and the gate's number in each species. Inputs are the cache's coordinate files,
each checked against its retrieval record before it is read.
"""
import gzip
import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np

VAULT = Path(__file__).resolve().parents[4]
GRAPH = VAULT / "what" / "evidence_graph"
OUT = GRAPH / "curation" / "o2_gate_measurements.tsv"
RADII = {"C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80}
GATE = {"Oryctolagus cuniculus": 4937, "Mus musculus": 4935, "Sus scrofa": 4935}
CLOSED_BELOW, OPEN_ABOVE = 2.0, 3.0

# Each structure: species, and its depositors' words (titles; for 7M6A, 9CGP and 9CGQ also their papers'; for the
# controls, Woll and Van Petegem 2022's), and the pore class those words imply, or None where they imply none.
S = {
    "9NMO": ("Mus musculus", "closed pore", "closed"), "9NMN": ("Mus musculus", "open pore", "open"),
    "9NMQ": ("Mus musculus", "closed pore", "closed"), "9NMP": ("Mus musculus", "open pore", "open"),
    "8VJJ": ("Mus musculus", "EGTA-only dataset (no state word)", None),
    "8VJK": ("Mus musculus", "high-Ca2+/CFF/ATP dataset (no state word)", None),
    "8X4A": ("Oryctolagus cuniculus", "closed state", "closed"), "8X4B": ("Oryctolagus cuniculus", "open state", "open"),
    "8X4C": ("Oryctolagus cuniculus", "20 uM Ca2+, 2 mM ATP (no state word)", None),
    "7M6A": ("Oryctolagus cuniculus", "primed model (paper); Closed state model (7M6L's record)", "closed"),
    "7M6L": ("Oryctolagus cuniculus", "open model (paper)", "open"),
    "5TB0": ("Oryctolagus cuniculus", "a closed RyR1 pore (Woll and Van Petegem 2022): positive control", "closed"),
    "5T9V": ("Oryctolagus cuniculus", "an open RyR1 (Woll and Van Petegem 2022): positive control", "open"),
    "7T64": ("Oryctolagus cuniculus", "closed state", "closed"), "7T65": ("Oryctolagus cuniculus", "open state", "open"),
    "9CGP": ("Oryctolagus cuniculus", "the closed state without Ca (paper)", "closed"),
    "9CGQ": ("Oryctolagus cuniculus", "the open state with Ca (paper)", "open"),
    "6W1N": ("Sus scrofa", "WT, 5 mM EGTA (no state word)", None),
    "6X32": ("Sus scrofa", "closed", "closed"), "6X33": ("Sus scrofa", "open", "open"),
    "6X34": ("Sus scrofa", "open (title); intermediate (paper)", "open"),
    "6X35": ("Sus scrofa", "open", "open"), "6X36": ("Sus scrofa", "closed", "closed"),
    "9PWO": ("Sus scrofa", "Open Conformation", "open"),
}


def sha256(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()


def classify(r):
    return "closed" if r < CLOSED_BELOW else ("open" if r > OPEN_ABOVE else "indeterminate")


def classify_at(r, shift):
    return "closed" if r < CLOSED_BELOW + shift else ("open" if r > OPEN_ABOVE + shift else "indeterminate")


class Refused(Exception):
    pass


# ---------------------------------------------------------------------------------------- implementation A (Biopython)
def load_a(text):
    from Bio.PDB import MMCIFParser
    from Bio.PDB.MMCIF2Dict import MMCIF2Dict
    d = MMCIF2Dict(io.StringIO(text))
    st = MMCIFParser(QUIET=True).get_structure("x", io.StringIO(text))
    ids = d["_entity_poly.entity_id"]
    strands = d["_entity_poly.pdbx_strand_id"]
    desc = dict(zip(d["_entity.id"], d["_entity.pdbx_description"]))
    chains = []
    for eid, s in zip(ids, strands):
        dsc = desc.get(eid, "").lower()
        if ("ryanodine" in dsc or "ryr1" in dsc) and "receptor 2" not in dsc:
            chains += [c.strip() for c in s.split(",")]
    return st[0], chains


def gate_a(model, chains, gate, move_out=0.0, rename=False):
    if len(chains) != 4:
        raise Refused("A: %d RyR1 chains, not 4" % len(chains))
    res = []
    for cid in chains:
        if cid not in model:
            raise Refused("A: chain %s missing" % cid)
        ch = model[cid]
        r = ch[(" ", gate, " ")] if (" ", gate, " ") in ch else None
        if r is None or r.get_resname() != "ILE" or rename:
            raise Refused("A: chain %s has no isoleucine at %d" % (cid, gate))
        res.append(r)
    ca = np.array([r["CA"].coord for r in res], dtype=float)
    c = ca.mean(axis=0)
    n = np.linalg.svd(ca - c)[2][-1]
    best = None
    for r in res:
        for a in r:
            el = a.element.strip().upper()
            if el == "H" or el not in RADII:
                continue
            v = a.coord.astype(float) - c
            perp = v - v.dot(n) * n
            dist = np.linalg.norm(perp) + move_out
            val = dist - RADII[el]
            best = val if best is None else min(best, val)
    return best


# --------------------------------------------------------------------------------------------- implementation B (gemmi)
def load_b(text):
    import gemmi
    doc = gemmi.cif.read_string(text)
    st = gemmi.make_structure_from_block(doc.sole_block())
    st.remove_hydrogens()
    return st


def gate_b(st, gate, move_out=0.0, rename=False, drop_chain=False):
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
                tm += [a.pos.tolist() for a in r if a.element.name.upper() in RADII]
        if found is None or found.name != "ILE" or rename:
            raise Refused("B: a chain among the four longest has no isoleucine at %d" % gate)
        gate_atoms += [(a.pos.tolist(), a.element.name.upper()) for a in found if a.element.name.upper() in RADII]
    tm = np.array(tm, dtype=float)
    c = tm.mean(axis=0)
    w, v = np.linalg.eigh(np.cov((tm - c).T))
    k = int(np.argmax([abs(w[i] - np.mean([w[j] for j in range(3) if j != i])) for i in range(3)]))
    n = v[:, k] / np.linalg.norm(v[:, k])
    g = np.array([p for p, _ in gate_atoms], dtype=float).mean(axis=0)
    zg = (g - c).dot(n)
    allatoms = []
    for ch in chains:
        for r in ch:
            for a in r:
                el = a.element.name.upper()
                if el in RADII:
                    allatoms.append((a.pos.tolist(), RADII[el], r.seqid.num == gate))
    P = np.array([p for p, _, _ in allatoms], dtype=float)
    R = np.array([rr for _, rr, _ in allatoms], dtype=float)
    if move_out:
        isg = np.array([f for _, _, f in allatoms])
        rel = P[isg] - c
        perp = rel - np.outer(rel.dot(n), n)
        P[isg] = P[isg] + (perp / np.linalg.norm(perp, axis=1)[:, None]) * move_out
    rel = P - c
    along = rel.dot(n)
    radial = np.linalg.norm(rel - np.outer(along, n), axis=1)
    near = (np.abs(along - zg) <= 15.0) & (radial <= 25.0)
    Pn, Rn = P[near], R[near]
    best = None
    for z in np.arange(zg - 12.0, zg + 12.0001, 0.25):
        if abs(z - zg) > 3.0:
            continue
        p = c + z * n
        val = float(np.min(np.linalg.norm(Pn - p, axis=1) - Rn))
        best = val if best is None else min(best, val)
    return best


# ------------------------------------------------------------------------------------------------------------- run
def main():
    retr = [json.loads(l) for l in (GRAPH / "records" / "retrieval.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    rows, F, inputs = [], [], {}
    texts = {}
    for pid, (species, words, expect) in S.items():
        rel = "cache/rcsb/2026-10-06/%s.cif.gz" % pid
        data = (GRAPH / rel).read_bytes()
        rec = [r for r in retr if r.get("stored_at") == rel]
        if not rec or rec[-1]["generated"] != sha256(data):
            F.append("input %s does not match its retrieval record" % pid)
            continue
        inputs[pid] = rec[-1]["id"]
        texts[pid] = gzip.decompress(data).decode("utf-8")
    for pid, (species, words, expect) in S.items():
        if pid not in texts:
            continue
        gate = GATE[species]
        try:
            ma, chains = load_a(texts[pid])
            ra = gate_a(ma, chains, gate)
        except Refused as e:
            ra, F = None, F + [str(e) + " (" + pid + ")"]
        try:
            rb = gate_b(load_b(texts[pid]), gate)
        except Refused as e:
            rb, F = None, F + [str(e) + " (" + pid + ")"]
        ca_, cb_ = (classify(ra) if ra is not None else "refused"), (classify(rb) if rb is not None else "refused")
        g1 = ra is not None and rb is not None and ca_ == cb_ and abs(ra - rb) <= 1.0
        agree = None if expect is None else (ca_ == expect and cb_ == expect)
        rows.append(dict(pid=pid, species=species, gate=gate, ra=ra, rb=rb, ca=ca_, cb=cb_, g1=g1, words=words,
                         expect=expect, agree=agree,
                         lo="%s/%s" % (classify_at(ra, -0.5) if ra is not None else "-", classify_at(rb, -0.5) if rb is not None else "-"),
                         hi="%s/%s" % (classify_at(ra, 0.5) if ra is not None else "-", classify_at(rb, 0.5) if rb is not None else "-")))
    g1_fail = [r["pid"] for r in rows if not r["g1"]]
    ctl = {r["pid"]: r for r in rows}
    g2 = ("5TB0" in ctl and ctl["5TB0"]["ca"] == "closed" and ctl["5TB0"]["cb"] == "closed"
          and "5T9V" in ctl and ctl["5T9V"]["ca"] == "open" and ctl["5T9V"]["cb"] == "open")

    # planted faults
    caught = []
    m, ch = load_a(texts["5TB0"])
    caught.append(("A: 5TB0 gate atoms moved 4 A outward reads open", classify(gate_a(m, ch, 4937, move_out=4.0)) == "open"))
    caught.append(("B: 5TB0 gate atoms moved 4 A outward reads open", classify(gate_b(load_b(texts["5TB0"]), 4937, move_out=4.0)) == "open"))
    m, ch = load_a(texts["5T9V"])
    try:
        gate_a(m, ch[:3], 4937); caught.append(("A: 5T9V with a chain removed is refused", False))
    except Refused:
        caught.append(("A: 5T9V with a chain removed is refused", True))
    try:
        gate_b(load_b(texts["5T9V"]), 4937, drop_chain=True); caught.append(("B: 5T9V with a chain removed is refused", False))
    except Refused:
        caught.append(("B: 5T9V with a chain removed is refused", True))
    for name, fn in (("A", lambda: gate_a(*load_a(texts["9NMO"]), 4935, rename=True)),
                     ("B", lambda: gate_b(load_b(texts["9NMO"]), 4935, rename=True))):
        try:
            fn(); caught.append(("%s: renamed gate residues are refused" % name, False))
        except Refused:
            caught.append(("%s: renamed gate residues are refused" % name, True))

    print("O2 gate: %d structures measured" % len(rows))
    print("%-5s %-22s %5s  %6s %6s  %-13s %-13s %-4s  %s" % ("entry", "species", "gate", "A", "B", "A class", "B class", "G1", "deposited -> agrees?"))
    for r in rows:
        print("%-5s %-22s %5d  %6s %6s  %-13s %-13s %-4s  %s -> %s" % (
            r["pid"], r["species"], r["gate"], "%.2f" % r["ra"] if r["ra"] is not None else "-",
            "%.2f" % r["rb"] if r["rb"] is not None else "-", r["ca"], r["cb"], "ok" if r["g1"] else "FAIL",
            r["words"], {True: "agrees", False: "DISAGREES", None: "no expectation"}[r["agree"]]))
    print("\nG1 (A and B agree): %s" % ("pass" if not g1_fail else "FAIL: " + ", ".join(g1_fail)))
    print("G2 (5TB0 closed, 5T9V open, by both): %s" % ("pass" if g2 else "FAIL"))
    print("refusals and input problems: %s" % ("; ".join(F) if F else "none"))
    print("planted faults: %d of %d caught" % (sum(1 for _, ok in caught if ok), len(caught)))
    for name, ok in caught:
        print("  %s %s" % ("caught" if ok else "NOT CAUGHT", name))

    if "--write" in sys.argv:
        code = sha256((Path(__file__).read_text(encoding="utf-8")).replace("\r\n", "\n").encode())
        head = ["entry", "species", "gate_residue", "radius_A", "radius_B", "class_A", "class_B", "g1_agree",
                "class_at_minus_0.5A", "class_at_plus_0.5A", "deposited_words", "deposited_implies", "measured_agrees"]
        lines = ["\t".join([r["pid"], r["species"], "I%d" % r["gate"], "%.2f" % r["ra"] if r["ra"] is not None else "-",
                            "%.2f" % r["rb"] if r["rb"] is not None else "-", r["ca"], r["cb"], "yes" if r["g1"] else "no",
                            r["lo"], r["hi"], r["words"], r["expect"] or "-",
                            {True: "yes", False: "NO", None: "-"}[r["agree"]]]) for r in rows]
        prov = ("# o2_gate_measurements.tsv: each structure's pore radius at the gate (A), by two implementations, as\n"
                "# how/runtime/channelscope/o2/gate.py measured it (code %s; criteria committed in b932329). Generated; never edited.\n"
                "# Inputs (retrieval records): %s\n# G1 %s; G2 %s; planted faults %d of %d caught\n" % (
                    code, "; ".join("%s=%s" % kv for kv in inputs.items()), "pass" if not g1_fail else "FAIL",
                    "pass" if g2 else "FAIL", sum(1 for _, ok in caught if ok), len(caught)))
        OUT.write_text(prov + "\t".join(head) + "\n" + "\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print("\nwritten: %s %s" % (OUT.relative_to(VAULT), sha256(OUT.read_bytes())))


if __name__ == "__main__":
    main()
