"""c5n.py - C5-N, the joins where CL-2's two paths agree, re-derived by a second code path that does not import CL-2's
code or CL-4's reading of CL-2's tables (the criteria, *C5-N*): for every `agree` row at a sampled residue, the entry's
SIFTS file must give, for the row's chain and author number, the row's partner position on the species' UniProt
accession, and the entry's mmCIF must have a CA atom there. A second code path on CL-2's inputs, not a second source.
The build hands this module the guarded bytes; it reads them with the standard library and gemmi alone."""
from __future__ import annotations

import xml.etree.ElementTree as ET

ACCESSION = {"Oryctolagus cuniculus": "P11716", "Mus musculus": "E9PZQ0", "Sus scrofa": "P16960"}
NS = "{http://www.ebi.ac.uk/pdbe/docs/sifts/eFamily.xsd}"


def sifts_positions(xml: bytes, chains: set[str], accession: str) -> dict[tuple[str, str], str]:
    """(chain, PDB residue number as SIFTS writes it) -> the UniProt position SIFTS gives on `accession`."""
    out = {}
    for _, el in ET.iterparse(__import__("io").BytesIO(xml), events=("end",)):
        if el.tag != NS + "residue":
            continue
        pdb = uni = None
        for x in el.findall(NS + "crossRefDb"):
            if x.get("dbSource") == "PDB" and x.get("dbChainId") in chains:
                pdb = (x.get("dbChainId"), x.get("dbResNum"))
            elif x.get("dbSource") == "UniProt" and x.get("dbAccessionId") == accession:
                uni = x.get("dbResNum")
        if pdb and uni and pdb[1] != "null":
            out[pdb] = uni
        el.clear()
    return out


def ca_present(text: str) -> set[tuple[str, int]]:
    import gemmi
    block = gemmi.cif.read_string(text).sole_block()
    t = block.find("_atom_site.", ["auth_asym_id", "auth_seq_id", "label_atom_id", "pdbx_PDB_model_num",
                                   "pdbx_PDB_ins_code"])
    first, out = None, set()
    for row in t:
        first = first or row[3]
        if row[3] == first and row[2] == "CA" and row[4] in ("?", "."):
            out.add((row[0], int(row[1])))
    return out


def rederive(rows: list[dict], sifts_xml: dict[str, bytes], mmcif_text: dict[str, str]) -> list[dict]:
    """rows: entry, chain, species, author_number, partner_position (every `agree` row at a sampled residue).
    Returns one result per row: equal or not, and what each file gave."""
    out, cache = [], {}
    for r in rows:
        key = (r["entry"], r["species"])
        if key not in cache:
            chains = {x["chain"] for x in rows if x["entry"] == r["entry"]}
            cache[key] = (sifts_positions(sifts_xml[r["entry"]], chains, ACCESSION[r["species"]]),
                          ca_present(mmcif_text[r["entry"]]))
        pos, cas = cache[key]
        got = pos.get((r["chain"], str(r["author_number"])))
        ca = (r["chain"], r["author_number"]) in cas
        out.append({**r, "sifts_position": got, "ca": ca,
                    "equal": got is not None and int(got) == r["partner_position"] and ca})
    return out
