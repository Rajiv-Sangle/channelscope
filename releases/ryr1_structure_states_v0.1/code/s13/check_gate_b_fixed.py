#!/usr/bin/env python3
"""check_gate_b_fixed.py - check S: gate_b_fixed.py on synthetic pores only. Committed with the criteria, before the
run; revised after independent critiques, before any run. No real structure is read: the real run comes after the
criteria's commit (decision S13), and runs these tests again first (run_tests), so that their result is part of its
record. ChannelScope's agent (a fork of [a working record, not public]), 2026-10-06.

    uv run --project how/runtime/channelscope --with gemmi==0.7.5 --with biopython==1.88 python how/runtime/channelscope/s13/check_gate_b_fixed.py
(biopython 1.88 and numpy 2.5.3 are the project's lock, how/runtime/channelscope/uv.lock.)

A synthetic pore: four S6-like helices around z, C4-symmetric, residues 4820 to 5037 (the gate 4937 -117 to +100, the
span B's axis uses), written as mmCIF so that both parsers read it, with an FKBP-like fifth chain far away unless
fkbp=False. The gate residue is an isoleucine whose CD1 is r_gate + 1.70 A from the axis, so A reads r_gate; cd1_dz
lowers CD1 below the gate's CA plane (O2's zg, the centroid of all its heavy atoms, then sits 1 to 2 A from it).
Optionally a second constriction one helical turn below: glutamine 4933 with its NE2 2.55 A from the axis and 5.0 A
below the gate's CA plane: O2's failure case, a narrower ring below an open gate.

Each test runs on the real code or input, then on a planted fault it must reject:
  F1  B with O2's window (gate_b_window, 3 A) equals O2's gate_b exactly on seven pores and O2's fault flags (control:
      the fixed B put in its place on a ring pore must differ)
  F2  accuracy at 1.0, 2.5, 4.5 and 5.5 A: A within 0.005 A, the fixed B within 0.05 A and set by the gate residue,
      classed closed, indeterminate, open, open (control: pointed at alanine 4936, both must refuse)
  F3  open gates of 4.5 and 5.5 A over a closed ring: A open, the fixed B within 0.05 A of A and set by the gate, and O2's
      B not open (control: the first draft's B, a point at O2's zg over all atoms, in its place)
  F4  closed gates whose CD1 sits 1.0, 1.5 and 2.0 A below the CA plane: the fixed B within 0.05 A of A and set by CD1
      (control: the slab centred on O2's zg instead of zg*)
  F5  O2's missed planted fault: a closed gate over the ring, its atoms moved 4 A outward: A and the fixed B read open
      (control: O2's B in the fixed B's place)
  F6  refusals by faults in the structure text itself: one RyR1 chain's atoms removed, with and without the FKBP chain;
      and the gate residues renamed valine (control: the unfaulted text must not be refused)
  F7  planted fault P4: a ring planted one turn below zg* leaves the fixed B exactly as it was, on three pores (control:
      the same ring planted 1.0 A below zg* must change it)
  F8  planted fault P5: the fixed B read 2 A above or below zg* fails G1' against A (control: read at zg*)
  F9  planted fault P6: an open gate's atoms moved 3 A inward read closed by both (control: B read 3 A away from zg*)
  F10 the hash pin: the true o2/gate.py passes; a copy with one character changed is refused (control: the change)
  F11 the run guard, against a02283b so that it holds after the criteria's commit too: refuses the run there (the
      criteria and both scripts are absent); passes for files committed unchanged there; refuses a file changed since,
      and a name that is not a commit (control: a guard that never refuses)
  F12 live test L1's synthetic analogue: with CD1 off the CA-CB line, each gate side chain turned 120 degrees about
      CA-CB in the text; A registers the turn, and the fixed B agrees with A within 0.05 A (control: B read 3 A away)
  F13 live test L2's synthetic analogue: over the ring, O2's window is set by GLN 4933 and the fixed B is not; O2's
      window with its atom equals it without (control: the first draft's point probe, which the ring sets)
  F14 A's atom: a_with_atom gives exactly gate_a's value and names the gate's CD1, on a closed, an open and a turned
      pore (control: the replica with C's radius 1.60 A must refuse, as its value no longer equals gate_a's)
  F15 the run's plumbing, end to end: run_body and write_record on synthetic stand-ins for the six structures the run
      names, into a scratch file: a complete record, a row for each, and every perturbation's line written in full
      (control: a wrong committed radius, so that R0 stops it)
  F16 a stop after R0 still writes the record, with the error and the rows done (9NMO left out, so P3 cannot run;
      control: a dry run that nothing stops)
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_b_fixed as gbf  # noqa: E402

GATE = 4937
OLDER_COMMIT = "a02283b"  # holds o2/gate.py and o2_gate_measurements.tsv as they are now; STATE.md has changed since


def _rot(k):
    th = np.radians(90.0 * k)
    return np.array([[np.cos(th), -np.sin(th), 0.0], [np.sin(th), np.cos(th), 0.0], [0.0, 0.0, 1.0]])


def _outward(p):
    v = np.array([p[0], p[1], 0.0])
    return v / np.linalg.norm(v)


def synthetic_cif(r_gate, ring=False, gate_resname="ILE", cd1_dz=0.0, fkbp=True, gate=GATE):
    """mmCIF text of a synthetic pore (see the module's docstring)."""
    x0 = r_gate + 7.5
    base = []
    for m in range(gate - 117, gate + 101):
        i = m - gate
        phi = np.radians(180.0 + 100.0 * i)
        ca = np.array([x0 + 2.3 * np.cos(phi), 2.3 * np.sin(phi), 1.5 * i])
        out = _outward(ca)
        c = ca + np.array([0.0, 0.0, 1.0])
        atoms = [("N", "N", ca + np.array([0.0, 0.0, -1.0])), ("CA", "C", ca), ("C", "C", c), ("O", "O", c + 1.23 * out)]
        if m == gate:
            name = gate_resname
            atoms += [("CB", "C", np.array([r_gate + 3.67, 0.0, 0.0])),
                      ("CG2", "C", np.array([r_gate + 3.3, 1.2, 0.3])),
                      ("CG1", "C", np.array([r_gate + 2.6, -0.8, 0.0])),
                      ("CD1", "C", np.array([r_gate + 1.70, 0.0, cd1_dz]))]
        elif ring and m == gate - 4:
            name = "GLN"
            psi = np.arctan2(ca[1], ca[0])
            tip = np.array([2.55 * np.cos(psi), 2.55 * np.sin(psi), -5.0])
            steps = [ca + (tip - ca) * f for f in (0.2, 0.4, 0.6, 0.8)]
            atoms += [("CB", "C", steps[0]), ("CG", "C", steps[1]), ("CD", "C", steps[2]),
                      ("OE1", "O", tip + 1.0 * _outward(tip)), ("NE2", "N", tip)]
        else:
            name = "ALA"
            atoms += [("CB", "C", ca + 1.53 * out)]
        for nm, el, xyz in atoms:
            base.append((m, name, nm, el, xyz))
    lines = ["data_SYNTH", "#", "loop_", "_entity.id", "_entity.type", "_entity.pdbx_description",
             "1 polymer 'Ryanodine receptor 1'", "2 polymer 'Peptidyl-prolyl cis-trans isomerase FKBP1B'", "#",
             "loop_", "_entity_poly.entity_id", "_entity_poly.type", "_entity_poly.pdbx_strand_id",
             "1 'polypeptide(L)' A,B,C,D", "2 'polypeptide(L)' E", "#", "loop_"]
    lines += ["_atom_site." + f for f in ("group_PDB", "id", "type_symbol", "label_atom_id", "label_alt_id",
                                           "label_comp_id", "label_asym_id", "label_entity_id", "label_seq_id",
                                           "pdbx_PDB_ins_code", "Cartn_x", "Cartn_y", "Cartn_z", "occupancy",
                                           "B_iso_or_equiv", "auth_seq_id", "auth_comp_id", "auth_asym_id",
                                           "auth_atom_id", "pdbx_PDB_model_num")]
    serial = 0
    for k, ch in enumerate("ABCD"):
        rot = _rot(k)
        for m, name, nm, el, xyz in base:
            serial += 1
            p = rot @ xyz
            lines.append("ATOM %d %s %s . %s %s 1 %d ? %.3f %.3f %.3f 1.00 50.00 %d %s %s %s 1" % (
                serial, el, nm, name, ch, m - (gate - 118), p[0], p[1], p[2], m, name, ch, nm))
    if fkbp:
        for j in range(1, 61):
            ca = np.array([60.0 + 2.3 * np.cos(np.radians(100.0 * j)), 2.3 * np.sin(np.radians(100.0 * j)),
                           40.0 + 1.5 * j])
            for nm, el, xyz in (("N", "N", ca - [0, 0, 1.0]), ("CA", "C", ca), ("C", "C", ca + [0, 0, 1.0])):
                serial += 1
                lines.append("ATOM %d %s %s . ALA E 2 %d ? %.3f %.3f %.3f 1.00 50.00 %d ALA E %s 1" % (
                    serial, el, nm, j, xyz[0], xyz[1], xyz[2], j, nm))
    return "\n".join(lines + ["#", ""])


def a_of(g, text, gate=GATE, move_out=0.0):
    m, ch = g.load_a(text)
    return g.gate_a(m, ch, gate, move_out=move_out)


def g1_prime(g, ra, rb):
    return g.classify(ra) == g.classify(rb) and abs(ra - rb) <= gbf.TOLERANCE


def first_draft_b(g, st, gate, **kw):
    """The first draft's fixed B: one probe point at O2's zg, over all atoms (no slab)."""
    return gbf.gate_b_fixed(g, st, gate, height="centroid", half_depth=np.inf, **kw)


# ------------------------------------------------------------------------------------------------------ the tests
def f1(g, fn, pores):
    bad = []
    for label, text in pores:
        st = g.load_b(text)
        for flags in ({}, {"move_out": 4.0}):
            if fn(g, st, GATE, **flags) != g.gate_b(st, GATE, **flags):
                bad.append("%s %s differs from O2's" % (label, flags))
        for flags in ({"rename": True}, {"drop_chain": True}):
            outcome = []
            for f in (lambda: fn(g, st, GATE, **flags), lambda: g.gate_b(st, GATE, **flags)):
                try:
                    outcome.append(f())
                except g.Refused:
                    outcome.append("refused")
            if outcome[0] != outcome[1]:
                bad.append("%s %s: %r v O2's %r" % (label, flags, outcome[0], outcome[1]))
    return bad


def f2(g, gate=GATE, log=None):
    bad = []
    for built, cls in ((1.0, "closed"), (2.5, "indeterminate"), (4.5, "open"), (5.5, "open")):
        text = synthetic_cif(built)
        try:
            ra = a_of(g, text, gate)
            rb, by = gbf.gate_b_fixed(g, g.load_b(text), gate)
        except g.Refused as e:
            bad.append("built %.1f: refused (%s)" % (built, e))
            continue
        if log is not None:
            log.append("F2 built %.1f: A %.3f, fixed B %.3f set by %s" % (built, ra, rb, by))
        if abs(ra - built) > 0.005 or abs(rb - built) > 0.05 or " %d " % gate not in by:
            bad.append("built %.1f: A %.3f, B %.3f set by %s" % (built, ra, rb, by))
        if (g.classify(ra), g.classify(rb)) != (cls, cls):
            bad.append("built %.1f: classed %s and %s, not %s" % (built, g.classify(ra), g.classify(rb), cls))
    return bad


def f3(g, bfn, log=None):
    bad = []
    for built in (4.5, 5.5):
        text = synthetic_cif(built, ring=True)
        st = g.load_b(text)
        ra = a_of(g, text)
        rb, by = bfn(g, st, GATE)
        o2 = g.gate_b(st, GATE)
        if log is not None:
            log.append("F3 gate %.1f over a ring: A %.3f, fixed B %.3f set by %s, O2's B %.3f" % (built, ra, rb, by, o2))
        if g.classify(ra) != "open":
            bad.append("gate %.1f: A %.2f not open" % (built, ra))
        if not g1_prime(g, ra, rb) or abs(ra - rb) > 0.05 or "%d CD1" % GATE not in by:
            bad.append("gate %.1f: A %.2f, B %.2f set by %s" % (built, ra, rb, by))
        if g.classify(o2) == "open":
            bad.append("gate %.1f: O2's B %.2f is open, so the pore does not reproduce O2's failure" % (built, o2))
    return bad


def f4(g, height, log=None):
    bad = []
    for dz in (-1.0, -1.5, -2.0):
        text = synthetic_cif(1.0, cd1_dz=dz)
        ra = a_of(g, text)
        rb, by = gbf.gate_b_fixed(g, g.load_b(text), GATE, height=height)
        if log is not None:
            log.append("F4 CD1 %.1f A below the CA plane: A %.3f, fixed B %.3f set by %s" % (-dz, ra, rb, by))
        if abs(ra - 1.0) > 0.005 or abs(rb - ra) > 0.05 or "%d CD1" % GATE not in by:
            bad.append("CD1 %.1f below: A %.3f, B %.3f set by %s" % (-dz, ra, rb, by))
    return bad


def f5(g, bfn):
    text = synthetic_cif(1.0, ring=True)
    ra = a_of(g, text, move_out=4.0)
    rb = bfn(g, g.load_b(text), GATE, move_out=4.0)
    rb = rb[0] if isinstance(rb, tuple) else rb
    bad = []
    if g.classify(ra) != "open":
        bad.append("A reads %.2f after the move, not open" % ra)
    if g.classify(rb) != "open":
        bad.append("B reads %.2f after the move, not open" % rb)
    return bad


def refused(g, text):
    out = {}
    try:
        a_of(g, text)
        out["A"] = False
    except g.Refused:
        out["A"] = True
    try:
        gbf.gate_b_fixed(g, g.load_b(text), GATE)
        out["B"] = False
    except g.Refused:
        out["B"] = True
    return out


def f6(g, cases):
    bad = []
    for label, text in cases:
        r = refused(g, text)
        if not (r["A"] and r["B"]):
            bad.append("%s: refused by %s" % (label, [k for k, v in r.items() if v] or "neither"))
    return bad


def f7(g, ring):
    bad = []
    for built in (1.0, 4.5, 5.5):
        st = g.load_b(synthetic_cif(built))
        plain = gbf.gate_b_fixed(g, st, GATE)[0]
        ringed = gbf.gate_b_fixed(g, st, GATE, ring=ring)[0]
        if abs(ringed - plain) >= 0.005:
            bad.append("gate %.1f: %.3f with the ring, %.3f without" % (built, ringed, plain))
    return bad


def f8(g, shifts):
    text = synthetic_cif(1.0)
    ra = a_of(g, text)
    bad = []
    for s in shifts:
        rb = gbf.gate_b_fixed(g, g.load_b(text), GATE, dz=s)[0]
        if g1_prime(g, ra, rb):
            bad.append("read %+.1f A from zg*: B %.2f passes G1' against A %.2f" % (s, rb, ra))
    return bad


def f9(g, dz):
    text = synthetic_cif(4.5)
    ra = a_of(g, text, move_out=-3.0)
    rb = gbf.gate_b_fixed(g, g.load_b(text), GATE, move_out=-3.0, dz=dz)[0]
    bad = []
    if g.classify(ra) != "closed" or g.classify(rb) != "closed":
        bad.append("moved 3 A inward: A %.2f, B %.2f, not both closed" % (ra, rb))
    return bad


def f10(text, header):
    problem = gbf.pin_problem(text, header)
    return [] if problem is None else ["the pin refuses this text: " + problem]


def f11(guard):
    bad = []
    if not guard(OLDER_COMMIT, gbf.DEPENDS):
        bad.append("--run at %s, which lacks the criteria and both scripts, would not be refused" % OLDER_COMMIT)
    if guard(OLDER_COMMIT, [gbf.GATE_PY, gbf.O2_TABLE]):
        bad.append("files committed unchanged at %s are refused" % OLDER_COMMIT)
    if not guard(OLDER_COMMIT, [gbf.VAULT / "STATE.md"]):
        bad.append("STATE.md, changed since %s, is not refused" % OLDER_COMMIT)
    if not guard("notacommit", [gbf.GATE_PY]):
        bad.append("a name that is not a commit is not refused")
    return bad


def f12(g, dz, log=None):
    """L1's synthetic analogue: CD1 1.5 A below the CA plane, then each gate side chain turned 120 degrees about CA-CB
    in the text. A and the fixed B must agree within 0.05 A after the turn, and A must register it (change > 0.1 A)."""
    text = synthetic_cif(1.0, cd1_dz=-1.5)
    turned = gbf.edited_text(text, GATE, turn_deg=gbf.TURN_DEG)
    a0, a1 = a_of(g, text), a_of(g, turned)
    b1, by = gbf.gate_b_fixed(g, g.load_b(turned), GATE, dz=dz)
    if log is not None:
        log.append("F12 turned %.0f degrees: A %.3f (was %.3f), fixed B %.3f set by %s" % (gbf.TURN_DEG, a1, a0, b1, by))
    bad = []
    if abs(a1 - a0) <= 0.1:
        bad.append("A did not register the turn (%.3f, was %.3f)" % (a1, a0))
    if abs(a1 - b1) > 0.05:
        bad.append("after the turn A %.3f and the fixed B %.3f differ" % (a1, b1))
    return bad


def f13(g, bfn):
    """L2's synthetic analogue: on a 4.5 A gate over the ring, O2's window is set by GLN 4933 and the fixed B must not
    be; O2's window with its atom equals O2's window without it."""
    st = g.load_b(synthetic_cif(4.5, ring=True))
    w_val, w_by = gbf.gate_b_window(g, st, GATE, 3.0, with_atom=True)
    bad = []
    if w_val != gbf.gate_b_window(g, st, GATE, 3.0):
        bad.append("O2's window with its atom gives %r, without it %r" % (w_val, gbf.gate_b_window(g, st, GATE, 3.0)))
    if gbf.residue_of(w_by) != "GLN 4933":
        bad.append("O2's window set by %s, not GLN 4933" % w_by)
    b_by = bfn(g, st, GATE)[1]
    if gbf.residue_of(b_by) == gbf.residue_of(w_by):
        bad.append("the fixed B is set by %s, as O2's window is" % b_by)
    return bad


def f14(g, radii=None):
    """A's atom: the replica equals gate_a exactly and names the gate's CD1."""
    texts = [("closed", synthetic_cif(1.0)), ("open", synthetic_cif(4.5)),
             ("turned", gbf.edited_text(synthetic_cif(1.0, cd1_dz=-1.5), GATE, turn_deg=gbf.TURN_DEG))]
    bad = []
    for label, text in texts:
        m, ch = g.load_a(text)
        try:
            value, by = gbf.a_with_atom(g, m, ch, GATE, radii=radii)
        except ValueError as e:
            bad.append("%s: %s" % (label, e))
            continue
        if value != g.gate_a(m, ch, GATE) or "%d CD1" % GATE not in by:
            bad.append("%s: %r set by %s" % (label, value, by))
    return bad


DRY = {"5TB0": ("Oryctolagus cuniculus", 1.0, False), "5T9V": ("Oryctolagus cuniculus", 4.2, False),
       "9NMO": ("Mus musculus", 1.0, False), "7M6L": ("Oryctolagus cuniculus", 5.0, True),
       "7T65": ("Oryctolagus cuniculus", 5.5, True), "6X35": ("Sus scrofa", 4.2, True)}
NAMED = ["P1-A", "P1-B", "P2-A", "P2-B", "P3-A", "P3-B", "P4", "P5 +2 A", "P5 -2 A", "P6-A", "P6-B", "L1", "L2 7M6L",
         "L2 7T65", "L2 6X35"]


def dry_run(g, wrong_r0=False, drop=None):
    """run_body and write_record on synthetic stand-ins for the structures the run names (the real run's plumbing,
    end to end, on no real structure). Returns (status, the record's text)."""
    import tempfile
    ids = {k: v for k, v in DRY.items() if k != drop}
    species = {pid: s for pid, (s, _, _) in ids.items()}
    words = {pid: ("synthetic", None) for pid in ids}
    texts = {pid: synthetic_cif(r, ring=ring, gate=g.GATE[s]) for pid, (s, r, ring) in ids.items()}
    committed = {}
    for pid, s in species.items():
        m, ch = g.load_a(texts[pid])
        committed[pid] = (s, "%.2f" % g.gate_a(m, ch, g.GATE[s]),
                          "%.2f" % gbf.gate_b_window(g, g.load_b(texts[pid]), g.GATE[s], 3.0))
    if wrong_r0:
        committed["5TB0"] = (committed["5TB0"][0], "9.99", committed["5TB0"][2])
    rows, results, status = [], [], "complete"
    try:
        gbf.run_body(g, species, words, committed, texts, rows, results)
    except Exception as e:
        status = "stopped: %s: %s" % (type(e).__name__, e)
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "dry_run.tsv"
        gbf.write_record(["# dry run on synthetic stand-ins"], status, rows, results, out=out)
        return status, out.read_text(encoding="utf-8")


def f15(g, wrong_r0=False):
    """The run's plumbing: a complete record, a row for every structure, and every perturbation written in full."""
    status, text = dry_run(g, wrong_r0=wrong_r0)
    bad = [] if status == "complete" else ["the dry run " + status]
    lines = text.splitlines()
    bad += ["no row for %s" % pid for pid in DRY if not any(l.startswith(pid + "\t") for l in lines)]
    bad += ["no full line for %s" % nm for nm in NAMED if not any(l.startswith("# %s [" % nm) for l in lines)]
    return bad


def f16(g, drop):
    """A stop after R0 still writes the record, with the error and the rows done (9NMO left out, so P3 cannot run)."""
    status, text = dry_run(g, drop=drop)
    bad = []
    if not status.startswith("stopped") or "# Run: stopped" not in text:
        bad.append("no stop recorded (%s)" % status)
    if not any(l.startswith("5TB0\t") for l in text.splitlines()):
        bad.append("the rows done before the stop are not in the record")
    return bad


def run_tests(g):
    """Check S: every test with its control. Returns ([(name, problems, fault, fault_problems)], log)."""
    log = []
    pores = [("closed", synthetic_cif(1.0)), ("open", synthetic_cif(4.5)), ("wide", synthetic_cif(5.5)),
             ("open over a ring", synthetic_cif(4.5, True)), ("wide over a ring", synthetic_cif(5.5, True)),
             ("closed over a ring", synthetic_cif(1.0, True)), ("CD1 2 A low", synthetic_cif(1.0, cd1_dz=-2.0))]
    gate_text = gbf.GATE_PY.read_text(encoding="utf-8")
    header = gbf.O2_TABLE.read_text(encoding="utf-8").splitlines()[1]
    clean = synthetic_cif(1.0)
    faulted = [("chain A's atoms removed, FKBP present", gbf.edited_text(clean, GATE, drop_chain="A")),
               ("chain A's atoms removed, no FKBP chain",
                gbf.edited_text(synthetic_cif(1.0, fkbp=False), GATE, drop_chain="A")),
               ("gate residues renamed valine in the text", gbf.edited_text(clean, GATE, rename_to="VAL"))]
    tests = [
        ("F1 O2's window reproduces O2's B",
         f1(g, lambda gg, st, gate, **kw: gbf.gate_b_window(gg, st, gate, 3.0, **kw), pores),
         "the fixed B in its place",
         f1(g, lambda gg, st, gate, **kw: gbf.gate_b_fixed(gg, st, gate, **{k: v for k, v in kw.items()
                                                                            if k == "move_out"})[0], pores[3:5])),
        ("F2 accuracy at 1.0, 2.5, 4.5, 5.5 A", f2(g, log=log), "pointed at alanine 4936", f2(g, gate=GATE - 1)),
        ("F3 open gates over a closed ring", f3(g, gbf.gate_b_fixed, log), "the first draft's point probe",
         f3(g, first_draft_b)),
        ("F4 CD1 1 to 2 A from O2's zg", f4(g, "narrowest", log), "slab centred on O2's zg", f4(g, "centroid")),
        ("F5 O2's missed planted fault", f5(g, gbf.gate_b_fixed), "O2's B in its place",
         f5(g, lambda gg, st, gate, **kw: gg.gate_b(st, gate, **kw))),
        ("F6 refusals by faults in the text", f6(g, faulted), "the unfaulted text", f6(g, [("unfaulted", clean)])),
        ("F7 P4: a ring one turn below changes nothing", f7(g, gbf.RING), "the ring 1.0 A below zg*",
         f7(g, (-1.0, 2.55, "N"))),
        ("F8 P5: read 2 A off zg*, G1' fails", f8(g, (2.0, -2.0)), "read at zg*", f8(g, (0.0,))),
        ("F9 P6: gate atoms 3 A inward read closed", f9(g, 0.0), "B read 3 A from zg*", f9(g, 3.0)),
        ("F10 the hash pin", f10(gate_text, header), "one character changed",
         f10(gate_text.replace("e", "E", 1), header)),
        ("F11 the run guard", f11(gbf.committed_problems), "a guard that never refuses", f11(lambda c, p: [])),
        ("F12 L1: gate side chains turned, A and B agree", f12(g, 0.0, log), "B read 3 A from zg*", f12(g, 3.0)),
        ("F13 L2: the ring sets O2's window, not the fixed B", f13(g, gbf.gate_b_fixed),
         "the first draft's point probe", f13(g, first_draft_b)),
        ("F14 A's atom equals gate_a and is CD1", f14(g), "C's radius 1.60 A in the replica",
         f14(g, radii=dict(g.RADII, C=1.60))),
        ("F15 the run's record, end to end (dry run)", f15(g), "a wrong committed radius (R0 stops)",
         f15(g, wrong_r0=True)),
        ("F16 a stop after R0 is recorded", f16(g, "9NMO"), "nothing stops it", f16(g, None)),
    ]
    return tests, log


def main():
    g = gbf.load_gate_module()
    tests, log = run_tests(g)
    failed = 0
    for name, problems, fault, fault_problems in tests:
        caught = bool(fault_problems)
        failed += bool(problems) + (not caught)
        print("%-46s %s; control (%s): %s" % (name, "pass" if not problems else "FAIL: " + "; ".join(problems),
                                               fault, "caught" if caught else "NOT CAUGHT"))
    for line in log:
        print("  " + line)
    print("checks: %d pass, %d fail; controls: %d caught, %d missed" % (
        sum(1 for t in tests if not t[1]), sum(1 for t in tests if t[1]),
        sum(1 for t in tests if t[3]), sum(1 for t in tests if not t[3])))
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
