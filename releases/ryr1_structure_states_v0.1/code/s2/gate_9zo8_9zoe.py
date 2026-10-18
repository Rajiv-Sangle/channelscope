#!/usr/bin/env python3
"""gate_9zo8_9zoe.py - S2, draft 3's facts: rabbit 9ZO8 and 9ZOE's pore at the gate, under O2's committed criteria.

O2's two implementations are imported from how/runtime/channelscope/o2/gate.py unchanged. This script refuses to run
unless that file's hash equals the one in o2_gate_measurements.tsv's header (the committed run's code; its criteria
were committed in b932329). It first re-measures O2's 24 structures and requires every radius to equal the committed
table to the hundredth, which shows that this environment reproduces that run. Then it measures 9ZO8 and 9ZOE, with
O2's checks G1 and G2 and O2's six planted faults, and four more on the new entries.
ChannelScope's agent, [a working record, not public], 2026-10-06.

    uv run --project how/runtime/channelscope --with gemmi python how/runtime/channelscope/s2/gate_9zo8_9zoe.py [--write]
"""
import gzip
import hashlib
import importlib.util
import json
import sys
from importlib.metadata import version
from pathlib import Path

VAULT = Path(__file__).resolve().parents[4]
GRAPH = VAULT / "what" / "evidence_graph"
GATE_PY = VAULT / "how" / "runtime" / "channelscope" / "o2" / "gate.py"
O2_TABLE = GRAPH / "curation" / "o2_gate_measurements.tsv"
OUT = GRAPH / "curation" / "s2_gate_9zo8_9zoe.tsv"

# The new entries: species, the depositors' words (their titles' state words, as O2's survey table records them) and
# the pore class those words imply.
NEW = {
    "9ZO8": ("Oryctolagus cuniculus", "closed pore", "closed"),
    "9ZOE": ("Oryctolagus cuniculus", "open pore", "open"),
}


def sha256(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()


def load_gate_module():
    code = sha256(GATE_PY.read_text(encoding="utf-8").replace("\r\n", "\n").encode())
    header = O2_TABLE.read_text(encoding="utf-8").splitlines()[1]
    if ("(code %s;" % code) not in header:
        sys.exit("refused: o2/gate.py's hash %s is not the committed run's: %s" % (code, header))
    spec = importlib.util.spec_from_file_location("o2_gate", GATE_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, code


def read_inputs(pids):
    retr = [json.loads(l) for l in (GRAPH / "records" / "retrieval.jsonl").read_text(encoding="utf-8").splitlines()
            if l.strip()]
    texts, inputs, problems = {}, {}, []
    for pid in pids:
        rel = "cache/rcsb/2026-10-06/%s.cif.gz" % pid
        data = (GRAPH / rel).read_bytes()
        rec = [r for r in retr if r.get("stored_at") == rel]
        if not rec or rec[-1]["generated"] != sha256(data):
            problems.append("input %s does not match its retrieval record" % pid)
            continue
        inputs[pid] = rec[-1]["id"]
        texts[pid] = gzip.decompress(data).decode("utf-8")
    return texts, inputs, problems


def measure(g, text, species):
    gate, notes = g.GATE[species], []
    try:
        ma, chains = g.load_a(text)
        ra = g.gate_a(ma, chains, gate)
    except g.Refused as e:
        ra = None
        notes.append(str(e))
    try:
        rb = g.gate_b(g.load_b(text), gate)
    except g.Refused as e:
        rb = None
        notes.append(str(e))
    return ra, rb, notes


def fmt(r):
    return "%.2f" % r if r is not None else "-"


def main():
    g, gate_code = load_gate_module()
    committed = {}
    for line in O2_TABLE.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or line.startswith("entry\t"):
            continue
        f = line.split("\t")
        committed[f[0]] = (f[3], f[4])
    texts, inputs, F = read_inputs(list(committed) + list(NEW))
    if F:
        sys.exit("refused: " + "; ".join(F))

    # 1. The committed run, reproduced to the hundredth.
    repro, again = [], {}
    for pid, (want_a, want_b) in committed.items():
        ra, rb, _ = measure(g, texts[pid], g.S[pid][0])
        again[pid] = (ra, rb)
        if (fmt(ra), fmt(rb)) != (want_a, want_b):
            repro.append("%s: A %s (committed %s), B %s (committed %s)" % (pid, fmt(ra), want_a, fmt(rb), want_b))
    print("reproduction of O2's committed run: %d of %d structures equal to the hundredth by both implementations"
          % (len(committed) - len(repro), len(committed)))
    for d in repro:
        print("  DIFFERS " + d)
    if repro:
        sys.exit("refused: this environment does not reproduce O2's committed run, so no new entry is measured")

    # 2. The new entries, under O2's committed criteria.
    rows = []
    for pid, (species, words, expect) in NEW.items():
        ra, rb, notes = measure(g, texts[pid], species)
        F += ["%s (%s)" % (n, pid) for n in notes]
        ca_ = g.classify(ra) if ra is not None else "refused"
        cb_ = g.classify(rb) if rb is not None else "refused"
        g1 = ra is not None and rb is not None and ca_ == cb_ and abs(ra - rb) <= 1.0
        agree = None if expect is None else (ca_ == expect and cb_ == expect)
        rows.append(dict(pid=pid, species=species, gate=g.GATE[species], ra=ra, rb=rb, ca=ca_, cb=cb_, g1=g1,
                         words=words, expect=expect, agree=agree,
                         lo="%s/%s" % (g.classify_at(ra, -0.5) if ra is not None else "-",
                                       g.classify_at(rb, -0.5) if rb is not None else "-"),
                         hi="%s/%s" % (g.classify_at(ra, 0.5) if ra is not None else "-",
                                       g.classify_at(rb, 0.5) if rb is not None else "-")))
    g1_fail = [r["pid"] for r in rows if not r["g1"]]
    a5, b5 = again["5TB0"]
    a9, b9 = again["5T9V"]
    g2 = (g.classify(a5) == "closed" and g.classify(b5) == "closed"
          and g.classify(a9) == "open" and g.classify(b9) == "open")

    # 3. Planted faults: O2's six, as gate.py plants them, then four on the new entries.
    caught = []

    def refused(fn):
        try:
            fn()
        except g.Refused:
            return True
        return False

    m, ch = g.load_a(texts["5TB0"])
    caught.append(("A: 5TB0 gate atoms moved 4 A outward reads open",
                   g.classify(g.gate_a(m, ch, 4937, move_out=4.0)) == "open"))
    caught.append(("B: 5TB0 gate atoms moved 4 A outward reads open",
                   g.classify(g.gate_b(g.load_b(texts["5TB0"]), 4937, move_out=4.0)) == "open"))
    m, ch = g.load_a(texts["5T9V"])
    caught.append(("A: 5T9V with a chain removed is refused", refused(lambda: g.gate_a(m, ch[:3], 4937))))
    caught.append(("B: 5T9V with a chain removed is refused",
                   refused(lambda: g.gate_b(g.load_b(texts["5T9V"]), 4937, drop_chain=True))))
    caught.append(("A: renamed gate residues are refused",
                   refused(lambda: g.gate_a(*g.load_a(texts["9NMO"]), 4935, rename=True))))
    caught.append(("B: renamed gate residues are refused",
                   refused(lambda: g.gate_b(g.load_b(texts["9NMO"]), 4935, rename=True))))
    m, ch = g.load_a(texts["9ZO8"])
    caught.append(("A: 9ZO8 gate atoms moved 4 A outward reads open",
                   g.classify(g.gate_a(m, ch, 4937, move_out=4.0)) == "open"))
    caught.append(("B: 9ZO8 gate atoms moved 4 A outward reads open",
                   g.classify(g.gate_b(g.load_b(texts["9ZO8"]), 4937, move_out=4.0)) == "open"))
    m, ch = g.load_a(texts["9ZOE"])
    caught.append(("A: 9ZOE with a chain removed is refused", refused(lambda: g.gate_a(m, ch[:3], 4937))))
    caught.append(("B: 9ZOE with a chain removed is refused",
                   refused(lambda: g.gate_b(g.load_b(texts["9ZOE"]), 4937, drop_chain=True))))

    libs = "biopython %s, gemmi %s, numpy %s" % (version("biopython"), version("gemmi"), version("numpy"))
    print("libraries: " + libs)
    print("%-5s %-22s %5s  %6s %6s  %-13s %-13s %-4s  %s" % ("entry", "species", "gate", "A", "B", "A class",
                                                            "B class", "G1", "deposited -> agrees?"))
    for r in rows:
        print("%-5s %-22s %5d  %6s %6s  %-13s %-13s %-4s  %s -> %s" % (
            r["pid"], r["species"], r["gate"], fmt(r["ra"]), fmt(r["rb"]), r["ca"], r["cb"],
            "ok" if r["g1"] else "FAIL", r["words"],
            {True: "agrees", False: "DISAGREES", None: "no expectation"}[r["agree"]]))
    print("\nG1 (A and B agree): %s" % ("pass" if not g1_fail else "FAIL: " + ", ".join(g1_fail)))
    print("G2 (5TB0 closed, 5T9V open, by both, re-measured): %s" % ("pass" if g2 else "FAIL"))
    print("refusals and input problems: %s" % ("; ".join(F) if F else "none"))
    print("planted faults: %d of %d caught" % (sum(1 for _, ok in caught if ok), len(caught)))
    for name, ok in caught:
        print("  %s %s" % ("caught" if ok else "NOT CAUGHT", name))

    if "--write" in sys.argv:
        code = sha256(Path(__file__).read_text(encoding="utf-8").replace("\r\n", "\n").encode())
        head = ["entry", "species", "gate_residue", "radius_A", "radius_B", "class_A", "class_B", "g1_agree",
                "class_at_minus_0.5A", "class_at_plus_0.5A", "deposited_words", "deposited_implies", "measured_agrees"]
        lines = ["\t".join([r["pid"], r["species"], "I%d" % r["gate"], fmt(r["ra"]), fmt(r["rb"]), r["ca"], r["cb"],
                            "yes" if r["g1"] else "no", r["lo"], r["hi"], r["words"], r["expect"] or "-",
                            {True: "yes", False: "NO", None: "-"}[r["agree"]]]) for r in rows]
        prov = ("# s2_gate_9zo8_9zoe.tsv: rabbit 9ZO8 and 9ZOE's pore radius at the gate (A), by O2's two implementations,\n"
                "# as how/runtime/channelscope/s2/gate_9zo8_9zoe.py measured it (code %s), importing o2/gate.py unchanged\n"
                "# (code %s; criteria committed in b932329). Libraries: %s. Generated; never edited.\n"
                "# O2's committed run reproduced first: %d of %d structures equal to the hundredth by both implementations\n"
                "# Inputs (retrieval records): %s\n# G1 %s; G2 %s (re-measured); planted faults %d of %d caught (%s)\n" % (
                    code, gate_code, libs, len(committed) - len(repro), len(committed),
                    "; ".join("%s=%s" % (p, inputs[p]) for p in list(NEW) + ["5TB0", "5T9V", "9NMO"]),
                    "pass" if not g1_fail else "FAIL: " + ", ".join(g1_fail), "pass" if g2 else "FAIL",
                    sum(1 for _, ok in caught if ok), len(caught),
                    "; ".join(n for n, ok in caught if not ok) or "none missed"))
        OUT.write_text(prov + "\t".join(head) + "\n" + "\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print("\nwritten: %s %s" % (OUT.relative_to(VAULT), sha256(OUT.read_bytes())))


if __name__ == "__main__":
    main()
