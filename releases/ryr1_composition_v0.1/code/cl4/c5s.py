"""c5s.py - C5-S, the joins that rest on path A alone, tested by coordinates against 9PWO (the criteria, *C5-S*). The
drafter's `kabsch`, `icp`, `Pair.fit`, `Pair.decide` and `rule_b` (s21_rule_compare.py), with version 3's three
changes as script v3_05 ran them: labels and anchors from CL-2's joined residues only; departing segments left out of
the anchors by residue; a tie for the commonest offset made "not determinable". Here the files come through check C1's
guard, the labels from CL-4's reading of CL-2's tables, and the join's outcome keeps the offset of a "counts against".
"""
from __future__ import annotations

import collections

import numpy as np

THR, HALF, MIN_N, FRAC = 2.0, 15, 10, 0.75
REGIONS = (40, 60, 80)
WOLL = ["6W1N", "6X32", "6X33", "6X34", "6X35", "6X36"]
REFERENCE = ("9PWO", "A")


def ca_atoms(text: str, chain: str) -> dict[int, tuple[np.ndarray, str]]:
    """author number -> (the first CA gemmi finds, whatever its alternate location; one-letter type). Residues with an
    insertion code are skipped."""
    import gemmi
    st = gemmi.make_structure_from_block(gemmi.cif.read_string(text).sole_block())
    out = {}
    for rs in st[0][chain]:
        a = rs.find_atom("CA", "*")
        if a is None or rs.seqid.icode not in (" ", ""):
            continue
        out[rs.seqid.num] = (np.array([a.pos.x, a.pos.y, a.pos.z]),
                             gemmi.find_tabulated_residue(rs.name).one_letter_code.upper())
    return out


def labelled(ch, cas: dict, departing: set[int], shift: int = 0) -> dict[int, tuple]:
    """label -> (CA, type, in a departing segment) for the chain's joined residues; `shift` moves every label (C5-S-P)."""
    out = {}
    for r in ch.residues:
        if r.joined:
            xyz, t = cas[r.n]
            out[r.species + shift] = (xyz, t, r.seg in departing)
    return out


def kabsch(P, Q):
    pc, qc = P.mean(0), Q.mean(0)
    U, S, Vt = np.linalg.svd((P - pc).T @ (Q - qc))
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    return R, qc - R @ pc


def icp(A, B, R, t, cuts=(12.0, 9.0, 6.0, 4.0, 3.0), iters=50):
    for c in cuts:
        for _ in range(iters):
            X = A @ R.T + t
            dist = np.linalg.norm(X[:, None, :] - B[None, :, :], axis=2)
            j = dist.argmin(1)
            keep = dist[np.arange(len(A)), j] < c
            if keep.sum() < 10:
                break
            R2, t2 = kabsch(A[keep], B[j[keep]])
            done = np.allclose(R2, R, atol=1e-6) and np.allclose(t2, t, atol=1e-4)
            R, t = R2, t2
            if done:
                break
    return R, t


class Pair:
    def __init__(self, woll: dict, ref: dict):
        self.labs = np.array(sorted(woll))
        self.wxyz = np.array([woll[l][0] for l in self.labs])
        self.wtype = np.array([woll[l][1] for l in self.labs])
        self.wdep = np.array([woll[l][2] for l in self.labs], dtype=bool)
        self.rnum = np.array(sorted(ref))
        self.rxyz = np.array([ref[m][0] for m in self.rnum])
        self.rtype = {m: ref[m][1] for m in ref}

    def fit(self, plab, region):
        inr = np.abs(self.labs - plab) <= region
        rin = np.abs(self.rnum - plab) <= region + 30
        if inr.sum() < 20 or rin.sum() < 20:
            return None
        B = self.rxyz[rin]
        cand = (~inr) & (~self.wdep) & np.isin(self.labs, self.rnum)
        idx = np.where(cand)[0]
        same = np.array([self.rtype.get(int(self.labs[i])) == self.wtype[i] for i in idx], dtype=bool)
        idx = idx[same] if len(idx) else idx
        if len(idx) < 10:
            return None
        rpos = {int(m): k for k, m in enumerate(self.rnum)}
        Q = self.rxyz[[rpos[int(self.labs[i])] for i in idx]]
        near = np.linalg.norm(Q[:, None, :] - B[None, :, :], axis=2).min(1) <= 20.0
        if near.sum() < 10:
            return None
        R, t = kabsch(self.wxyz[idx[near]], Q[near])
        A = self.wxyz[inr]
        R, t = icp(A, B, R, t)
        X = A @ R.T + t
        dist = np.linalg.norm(X[:, None, :] - B[None, :, :], axis=2)
        j = dist.argmin(1)
        return self.labs[inr], self.rnum[rin][j], dist[np.arange(len(A)), j]

    def decide(self, plab, region):
        f = self.fit(plab, region)
        if f is None:
            return ("not determinable", None, 0, {})
        labs, near, dmin = f
        sel = (np.abs(labs - plab) <= HALF) & (dmin < THR)
        n = int(sel.sum())
        if n < MIN_N:
            return ("not determinable", None, n, {})
        c = collections.Counter((near[sel] - labs[sel]).tolist())
        top = c.most_common()
        if len(top) > 1 and top[0][1] == top[1][1]:
            return ("not determinable", None, n, dict(c))
        mode = top[0][0]
        if mode != 0:
            return ("counts against", mode, n, dict(c))
        return ("consistent" if c.get(0, 0) / n >= FRAC else "not determinable", 0, n, dict(c))


def rule_b(fits: list[tuple]) -> tuple[str, int | None]:
    dec = [(f[0], f[1]) for f in fits if f[0] in ("consistent", "counts against")]
    if len(dec) < 2 or len(set(dec)) != 1:
        return "not determinable", None
    return dec[0]


def test_join(pair: Pair, p: int) -> dict:
    fits = [pair.decide(p, r) for r in REGIONS]
    verdict, offset = rule_b(fits)
    return {"verdict": verdict, "offset": offset,
            "fits": [{"region": r, "verdict": f[0], "offset": f[1], "window": f[2],
                      "offsets": {str(k): v for k, v in sorted(f[3].items())}} for r, f in zip(REGIONS, fits)]}


def segment_rule(tests: list[dict]) -> list[tuple[str, str, int]]:
    """The segment rule: in one chain, if at least two sampled joins of one CL-2 segment count against and they are
    at least half of that segment's sampled joins there, every join of that segment in that chain is withdrawn."""
    by = collections.defaultdict(list)
    for t in tests:
        by[(t["entry"], t["chain"], t["segment"])].append(t["verdict"])
    return sorted(k for k, v in by.items() if v.count("counts against") >= 2
                  and v.count("counts against") * 2 >= len(v))
