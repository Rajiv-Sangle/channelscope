"""common.py - CL-4's inputs, each read once through check C1's guard, and the small readers the build shares.

The criteria are `what/context/context_channelscope_cl4_composition_criteria_v3.md` (version 3, with the operator's
answers to Q1 to Q3 committed in 2004787). Every input named in its table *The inputs, each with its record* is read
here and nowhere else: a raw snapshot is refused unless its SHA-256 and size equal its retrieval record's, a derived
table unless they equal its table record's, and the A6 table unless it equals its blob at the build's commit. A
planted fault corrupts the bytes this guard is given (C1-P), never a file.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT = HERE.parents[3]
GRAPH = VAULT / "what" / "evidence_graph"
CRITERIA = "what/context/context_channelscope_cl4_composition_criteria_v3.md"
MISSION = "mission_channelscope_poc_sprint"

CLINVAR_SEARCH = "cs:retrieval.LZXj7wr6TidQhydfhP215YfYX94sb-yg"
CLINVAR_BATCHES = ["cs:retrieval.PNXvfeq3vV_HZaou_sauo8UQEfmL6M0X", "cs:retrieval.m3LSpuTeDIuCl6DQZhO0yCz9CU2PxUZR"]
CLINVAR_USE_PAGE = "cs:retrieval.DVFq5yeaAE238whGncB4dGFJxDrQVVOD"
UNIPROT = {"human": "cs:retrieval.VPdG0C8dOG0RdRCDH3o7hwF0-y22z2qQ",
           "Oryctolagus cuniculus": "cs:retrieval.72qWZyUw2nYc8JFq6a01ifDXUgHzhNgc",
           "Mus musculus": "cs:retrieval.3zXqsU_s_QP4ULOQ6dzkTr2bdaQuY4Uc",
           "Sus scrofa": "cs:retrieval.RgMUbxHrN4da3VwfkCujOspT9VXLVJoq"}
SPECIES = ["Oryctolagus cuniculus", "Mus musculus", "Sus scrofa"]
NUMBERING = {"human": "numbering:P21817-1.sv3", "Oryctolagus cuniculus": "numbering:P11716.sv1",
             "Mus musculus": "numbering:E9PZQ0.sv1", "Sus scrofa": "numbering:P16960.sv2"}
MAPPING = {"Oryctolagus cuniculus": "cs:table.5URsZZtyhn3vUFBvDH0dg0YxVwduVhjo",
           "Mus musculus": "cs:table.9708f3rPzqExweM8kfbZH1egpdG4nNKI",
           "Sus scrofa": "cs:table.nt5DASs63Krm6eTtUVxT7Q3GgKRa_nFu"}
A6_RECORD = "cs:check_result.R2g8_EbkE2AkRkXlt0hrjWN5bMxBofK1"
A6_FILE = "what/references/a6_stated_correspondences.tsv"
CL2 = {"entries": "cs:table.M297DUgTR3XktfSgcAekIpqsa2hkNz58", "segments": "cs:table.txYgUtvq3af8irDMd4I7NEE8-IqG315J",
       "exceptions": "cs:table.amBLEL9GbR16BHY8P3amE1M0wnN3fpDj"}
S13_TABLE = "cs:table.lVP1WAqwY-tpBjgn7zQrADn2rHj-4G1X"
GATE_TABLE = "cs:table.v1so1647WJQq0KHTyCdXdNiaXtzAC3n6"
S2_TABLE = "cs:table.I0xlK4TRDyLn6cYRuZII24uhzEyknnv2"
GNOMAD_LABEL = "cs:retrieval.dMNnflVo8QOV-vkgafiAldeVHTWNVVu8"
GNOMAD_POST = "cs:retrieval.3B8TFgYeCMaieBwPtQqNwmqspVv8Y791"
GNOMAD_TERMS = "cs:retrieval.grVhkUqc4-d3DYE_XaRfXrbt5goL3uGn"
ENTRIES = ["5T9V", "5TB0", "6W1N", "6X32", "6X33", "6X34", "6X35", "6X36", "7M6A", "7M6L", "7T64", "7T65", "8VJJ",
           "8VJK", "8X4A", "8X4B", "8X4C", "9CGP", "9CGQ", "9NMN", "9NMO", "9NMP", "9NMQ", "9PWO", "9ZO8", "9ZOE"]
THREE = {"Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C", "Gln": "Q", "Glu": "E", "Gly": "G", "His": "H",
         "Ile": "I", "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F", "Pro": "P", "Ser": "S", "Thr": "T", "Trp": "W",
         "Tyr": "Y", "Val": "V"}
ONE_TO_THREE = {v: k.upper() for k, v in THREE.items()}


class Refused(Exception):
    """Check C1: an input whose bytes are not its record's."""


def sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def git_bytes(*args: str) -> bytes:
    return subprocess.run(["git", "-C", str(VAULT), *args], check=True, capture_output=True).stdout


def records(kind: str) -> list[dict]:
    p = GRAPH / "records" / f"{kind}.jsonl"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def read_tsv(data: bytes) -> tuple[list[str], list[dict]]:
    """A graph table: no comment lines, the first line its columns. A cell is never altered."""
    lines = data.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    cols = lines[0].split("\t")
    rows = []
    for ln in lines[1:]:
        cells = ln.split("\t")
        if len(cells) != len(cols):
            raise ValueError(f"a row has {len(cells)} cells, the column line {len(cols)}")
        rows.append(dict(zip(cols, cells)))
    return cols, rows


def guard(name: str, data: bytes, expected_sha: str, expected_bytes: int | None) -> bytes:
    if sha(data) != expected_sha or (expected_bytes is not None and len(data) != expected_bytes):
        raise Refused(f"{name}: SHA-256 {sha(data)[:20]}…, {len(data)} bytes; its record says "
                      f"{expected_sha[:20]}…, {expected_bytes} bytes")
    return data


@dataclass
class Inputs:
    """Every input, read and guarded once. `corrupt` maps a path to a function applied to its bytes before the guard
    (planted fault C1-P only)."""
    corrupt: dict = field(default_factory=dict)
    retrievals: dict = field(default_factory=dict)
    tables: dict = field(default_factory=dict)
    numberings: dict = field(default_factory=dict)
    data: dict = field(default_factory=dict)
    by_path: dict = field(default_factory=dict)

    def __post_init__(self):
        self.retrievals = {r["id"]: r for r in records("retrieval")}
        self.tables = {r["id"]: r for r in records("table")}
        self.numberings = {r["identifier"]: r for r in records("numbering")}
        self.by_path = {r["stored_at"]: r for r in self.retrievals.values()}
        self.checks = {r["id"]: r for r in records("check_result")}

    def _read(self, rel: str) -> bytes:
        data = (GRAPH / rel).read_bytes()
        return self.corrupt[rel](data) if rel in self.corrupt else data

    def raw(self, rid: str) -> bytes:
        """A snapshot named by its retrieval record, guarded by that record's SHA-256 and size."""
        if rid not in self.data:
            r = self.retrievals[rid]
            self.data[rid] = guard(r["stored_at"], self._read(r["stored_at"]), r["generated"], r["response"]["bytes"])
        return self.data[rid]

    def raw_at(self, rel: str) -> tuple[str, bytes]:
        r = self.by_path[rel]
        return r["id"], self.raw(r["id"])

    def table(self, tid: str) -> tuple[list[str], list[dict]]:
        if tid not in self.data:
            t = self.tables[tid]
            self.data[tid] = guard(t["path"], self._read(t["path"]), t["sha256"], t["bytes"])
        return read_tsv(self.data[tid])

    def a6(self) -> tuple[list[str], list[dict]]:
        if "a6" not in self.data:
            blob = git_bytes("show", f"HEAD:{A6_FILE}")
            data = (VAULT / A6_FILE).read_bytes()
            data = self.corrupt[A6_FILE](data) if A6_FILE in self.corrupt else data
            self.data["a6"] = guard(A6_FILE, data, sha(blob), len(blob))
        lines = [ln for ln in self.data["a6"].decode("utf-8").split("\n") if ln]
        cols = lines[0].split("\t")
        rows = []
        for ln in lines[1:]:  # a committed reference file, not a graph table: a row may leave its empty last cells out
            cells = ln.split("\t")
            if len(cells) > len(cols):
                raise ValueError(f"{A6_FILE}: a row has more cells than the column line")
            rows.append(dict(zip(cols, cells + [""] * (len(cols) - len(cells)))))
        return cols, rows

    def json(self, rid: str) -> dict:
        return json.loads(self.raw(rid))

    def mmcif(self, entry: str) -> tuple[str, str]:
        rid, data = self.raw_at(f"cache/rcsb/2026-10-06/{entry}.cif.gz")
        return rid, gzip.decompress(data).decode("utf-8")

    def sifts(self, entry: str) -> tuple[str, bytes]:
        rid, data = self.raw_at(f"cache/sifts/2026-10-11/{entry.lower()}.xml.gz")
        return rid, gzip.decompress(data)

    def sequence(self, species: str) -> str:
        return self.json(UNIPROT[species])["sequence"]["value"]

    def numbering_record(self, species: str) -> str:
        return self.numberings[NUMBERING[species]]["id"]
