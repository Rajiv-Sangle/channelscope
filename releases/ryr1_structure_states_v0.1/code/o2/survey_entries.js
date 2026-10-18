"use strict";
/*
 * survey_entries.js: the sprint's O2, the survey by condition, part 1: which PDB entries hold RyR1, from which species,
 * mapped to UniProt or not, by which method, with which ligands, and what each entry's own title says of its state.
 * ChannelScope's agent, [a working record, not public] (2026-10-06). Node, no dependencies.
 * Run from the vault root: node how/runtime/channelscope/o2/survey_entries.js [--write]
 *
 * Inputs: the raw files of plans A, A2, B and B2 (what/evidence_graph/curation/fetch_poc_o2_survey_*.yaml), each
 * checked against its retrieval record's sha256 before it is read, and the UniProt entries of rabbit (2026-09-29), pig
 * and mouse (2026-10-06).
 *
 * How an entity is called RyR1 (in this order; the basis is kept in the table):
 *   1. its UniProt reference is a RyR1 accession (P21817, P11716, P16960, E9PZQ0);
 *   2. its description or gene names RyR1 ("ryanodine receptor 1", "ryanodine receptor type 1", "RyR1", gene RYR1);
 *   3. for an unmapped pig entity, its deposited sequence: most of its 30-residue windows occur verbatim in pig RyR1
 *      (P16960) and many fewer in rabbit RyR1, which tells RyR1 from RyR2 and pig from rabbit.
 * A mutation is read from the deposited sequence at the UniProt position, located by its two flanks (12 residues each),
 * never from the entity's mutation field: pig 6X34's is empty though its title says R615C (probe, 2026-10-06).
 *
 * What counts against the claims it checks, fixed before its first run (claims FR-03 to FR-07 and FR-29 in
 * what/context/context_channelscope_claims_register.md):
 *  S1 an input file's sha256 differs from its retrieval record, or has no record;
 *  S2 human RyR1 (P21817) maps to entries other than exactly 6UHI and 6UHS, or either is a full-length construct;
 *  S3 rabbit RyR1 is not 160 entries mapped to P11716 plus 9 unmapped; or the mapped set differs from 2026-10-03's;
 *  S4 mouse RyR1 is not exactly 8VJJ, 8VJK, 8VK3, 8VK4, 9NMN, 9NMO, 9NMP, 9NMQ and 9NMR, or any title names a mutant,
 *     or any deposited RyR1 sequence differs from UniProt E9PZQ0 at any position (plan B3's sequences; this clause was
 *     added after the first run, on titles alone, and before any check of the sequences);
 *  S5 pig RyR1 is not exactly 6W1N, 6X32, 6X33, 6X34, 6X35, 6X36 and 9PWO, or an unmapped one is not pig RyR1 by
 *     sequence;
 *  S6 human RyR2 (Q92736) is not 26 entries;
 *  S7 the residue at pig 615 is not C in 6X34, 6X35, 6X36 and 9PWO and R in 6W1N, 6X32 and 6X33; or the residue at
 *     rabbit 523 is not S in 7T64, 7T65, 9CGP and 9CGQ; or rabbit 164 is not C in 6WOT.
 * Controls: a planted fault for each of S1 to S7, each of which must be reported, or the run is void.
 */
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const VAULT = path.resolve(__dirname, "../../../..");
const G = path.join(VAULT, "what/evidence_graph");
const RAW = "raw/rcsb/2026-10-06/";
const OUT = path.join(G, "curation/o2_structure_survey.tsv");
const sha = (b) => "sha256:" + crypto.createHash("sha256").update(b).digest("hex");

// ---------- inputs, each against its retrieval record ----------
const retrievals = fs.readFileSync(path.join(G, "records/retrieval.jsonl"), "utf8").trim().split(/\n/).map(JSON.parse);
const INPUTS = [
  "search_entries_P21817.json", "search_entries_P11716.json", "search_entries_P16960.json", "search_entries_E9PZQ0.json",
  "search_entries_Q92736.json", "search_entities_rabbit_ryanodine.json", "search_entities_mouse_ryanodine.json",
  "search_entities_pig_ryanodine.json", "search_entities_human_ryanodine.json", "search_entities_gene_RYR1.json",
  "search_entities_desc_RyR1.json", "search_entities_desc_RyR.json", "graphql_o2_entries_part1.json",
  "graphql_o2_entries_part2.json", "graphql_o2_entries_part3.json", "graphql_o2_mutant_set_sequences.json",
  "graphql_o2_mouse_sequences.json",
].map((f) => RAW + f).concat(["raw/rcsb/2026-10-03/search_entries_P11716.json", "raw/uniprot/2026-09-29/P11716.json",
  "raw/uniprot/2026-10-06/P16960.json", "raw/uniprot/2026-10-06/E9PZQ0.json"]);
function load() {
  const files = {}, used = {}, S1 = [];
  for (const rel of INPUTS) {
    const p = path.join(G, rel);
    if (!fs.existsSync(p)) { S1.push(`S1: ${rel} is missing`); continue; }
    const bytes = fs.readFileSync(p);
    const recs = retrievals.filter((r) => r.stored_at === rel);
    const rec = recs[recs.length - 1];
    if (!rec) S1.push(`S1: ${rel} has no retrieval record`);
    else if (rec.generated !== sha(bytes)) S1.push(`S1: ${rel} differs from its retrieval record ${rec.id}`);
    files[rel] = JSON.parse(bytes.toString("utf8"));
    used[rel] = rec ? rec.id : null;
  }
  return { files, used, S1 };
}

// ---------- classification ----------
const RYR1_ACC = { P21817: "human", P11716: "rabbit", P16960: "pig", E9PZQ0: "mouse" };
const RYR2_ACC = { Q92736: "human" };
function windows30(seq, ref) { let n = 0, k = 0; for (let i = 0; i + 30 <= seq.length; i += 30) { n++; if (ref.includes(seq.slice(i, i + 30))) k++; } return { k, n }; }
function residueAt(seq, ref, pos, flank = 12) {
  const L = ref.slice(pos - 1 - flank, pos - 1), R = ref.slice(pos, pos + flank);
  const i = seq.indexOf(L), j = i >= 0 ? seq.indexOf(R, i + L.length) : -1;
  return i < 0 || j < 0 ? null : seq.slice(i + L.length, j);
}
const STATE_WORDS = /\b(open pore|closed pore|open state|closed state|open conformation|closed conformation|primed|open|closed)\b/gi;

function classify(files) {
  const entries = [1, 2, 3].flatMap((i) => files[RAW + `graphql_o2_entries_part${i}.json`].data.entries);
  const seqs = {};
  for (const e of files[RAW + "graphql_o2_mutant_set_sequences.json"].data.entries)
    for (const p of e.polymer_entities) seqs[p.rcsb_id] = p.entity_poly.pdbx_seq_one_letter_code_can.replace(/\s/g, "");
  const U = { rabbit: files["raw/uniprot/2026-09-29/P11716.json"].sequence.value,
    pig: files["raw/uniprot/2026-10-06/P16960.json"].sequence.value, mouse: files["raw/uniprot/2026-10-06/E9PZQ0.json"].sequence.value };
  const rows = [];
  for (const e of entries) {
    for (const p of e.polymer_entities) {
      const desc = p.rcsb_polymer_entity.pdbx_description || "";
      const orgs = [...new Set((p.rcsb_entity_source_organism || []).map((o) => o.ncbi_scientific_name).filter(Boolean))];
      const genes = (p.rcsb_entity_source_organism || []).flatMap((o) => (o.rcsb_gene_name || []).map((g) => g.value));
      const accs = ((p.rcsb_polymer_entity_container_identifiers || {}).reference_sequence_identifiers || [])
        .filter((x) => x.database_name === "UniProt").map((x) => x.database_accession);
      const a1 = accs.find((a) => RYR1_ACC[a]), a2 = accs.find((a) => RYR2_ACC[a]);
      let iso = null, basis = "";
      if (a1) { iso = "RyR1"; basis = `UniProt ${a1}`; }
      else if (a2) { iso = "RyR2"; basis = `UniProt ${a2}`; }
      else if (/ryanodine receptor (type )?1\b|\bryr1\b/i.test(desc) || genes.some((g) => /^ryr1$/i.test(g))) { iso = "RyR1"; basis = `description "${desc}"`; }
      else if (/ryanodine receptor (type )?2\b|\bryr2\b/i.test(desc) || genes.some((g) => /^ryr2$/i.test(g))) { iso = "RyR2"; basis = `description "${desc}"`; }
      else if (/ryanodine receptor (type )?3\b|\bryr3\b/i.test(desc) || genes.some((g) => /^ryr3$/i.test(g))) { iso = "RyR3"; basis = `description "${desc}"`; }
      else if (/ryanodine/i.test(desc) && orgs.length === 1 && orgs[0] === "Sus scrofa" && seqs[p.rcsb_id]) {
        const wp = windows30(seqs[p.rcsb_id], U.pig), wr = windows30(seqs[p.rcsb_id], U.rabbit);
        if (wp.k / wp.n >= 0.5 && wp.k > 1.5 * wr.k) { iso = "RyR1"; basis = `sequence: ${wp.k}/${wp.n} 30-residue windows verbatim in pig RyR1 P16960, ${wr.k} in rabbit P11716`; }
        else { iso = "unresolved"; basis = `sequence: ${wp.k}/${wp.n} in pig RyR1, ${wr.k} in rabbit`; }
      } else if (/ryanodine/i.test(desc) && /\bryr2\b/i.test(e.struct.title)) { iso = "RyR2"; basis = `title "${e.struct.title}"`; }
      else if (/ryanodine|\bryr\b/i.test(desc)) { iso = "unresolved"; basis = `description "${desc}"`; }
      if (!iso) continue;
      const species = orgs.length === 1 ? orgs[0] : orgs.join("+");
      let mutation = "";
      const s = seqs[p.rcsb_id];
      if (s && iso === "RyR1") {
        if (species === "Sus scrofa") { const r = residueAt(s, U.pig, 615); mutation = r === null ? "615 unread" : (r === "R" ? "R615 (wild type)" : `R615${r}`); }
        if (species === "Oryctolagus cuniculus") {
          const r523 = residueAt(s, U.rabbit, 523), r164 = residueAt(s, U.rabbit, 164);
          mutation = [r523 === "Y" ? "Y523 (wild type)" : `Y523${r523}`, r164 === "R" ? "R164 (wild type)" : `R164${r164}`].join("; ");
        }
      }
      const words = [...new Set((e.struct.title.match(STATE_WORDS) || []).map((w) => w.toLowerCase()))];
      rows.push({ entry: e.rcsb_id, entity: p.rcsb_id, iso, basis, species, uniprot: accs.join(",") || "-",
        sample_len: p.entity_poly.rcsb_sample_sequence_length, method: (e.exptl || []).map((x) => x.method).join("+"),
        resolution: (e.rcsb_entry_info.resolution_combined || ["-"])[0],
        released: ((e.rcsb_accession_info || {}).initial_release_date || "-").slice(0, 10),
        doi: (e.rcsb_primary_citation || {}).pdbx_database_id_DOI || "-",
        ligands: (e.nonpolymer_entities || []).map((n) => n.nonpolymer_comp.chem_comp.id).join(","),
        title: e.struct.title, title_state_words: words.join(", ") || "-", mutation });
    }
  }
  return rows;
}

// ---------- the claims' checks ----------
const eq = (a, b) => a.length === b.length && [...a].sort().join() === [...b].sort().join();
function check(files, rows) {
  const F = [];
  const ids = (rel) => files[RAW + rel].result_set.map((x) => x.identifier);
  const r1 = (sp) => rows.filter((r) => r.iso === "RyR1" && r.species === sp);
  const entriesOf = (rs) => [...new Set(rs.map((r) => r.entry))];
  // S2
  const hum = ids("search_entries_P21817.json");
  if (!eq(hum, ["6UHI", "6UHS"])) F.push(`S2: P21817 maps to ${hum.join(",")}`);
  for (const r of rows.filter((r) => ["6UHI", "6UHS"].includes(r.entry) && r.iso === "RyR1")) if (r.sample_len >= 4000) F.push(`S2: ${r.entry} is full-length`);
  // S3
  const rab = entriesOf(r1("Oryctolagus cuniculus"));
  const mapped = entriesOf(r1("Oryctolagus cuniculus").filter((r) => r.uniprot.includes("P11716")));
  const old = files["raw/rcsb/2026-10-03/search_entries_P11716.json"].result_set.map((x) => x.identifier);
  if (mapped.length !== 160 || rab.length - mapped.length !== 9) F.push(`S3: rabbit RyR1 ${rab.length} entries, ${mapped.length} mapped`);
  if (!eq(ids("search_entries_P11716.json"), old)) F.push("S3: the P11716 set differs from 2026-10-03's");
  // S4
  const mou = r1("Mus musculus");
  if (!eq(entriesOf(mou), ["8VJJ", "8VJK", "8VK3", "8VK4", "9NMN", "9NMO", "9NMP", "9NMQ", "9NMR"])) F.push(`S4: mouse RyR1 ${entriesOf(mou).join(",")}`);
  for (const r of mou) if (/mutant|[A-Z]\d+[A-Z]\b/.test(r.title)) F.push(`S4: ${r.entry}'s title names a mutant`);
  const ref = files["raw/uniprot/2026-10-06/E9PZQ0.json"].sequence.value;
  const ms = files[RAW + "graphql_o2_mouse_sequences.json"].data.entries.flatMap((e) => e.polymer_entities
    .filter((p) => /ryanodine/i.test(p.rcsb_polymer_entity.pdbx_description))
    .map((p) => [e.rcsb_id, p.entity_poly.pdbx_seq_one_letter_code_can.replace(/\s/g, "")]));
  if (ms.length !== 9) F.push(`S4: ${ms.length} mouse RyR1 sequences, not 9`);
  for (const [e, q] of ms) if (q !== ref) F.push(`S4: ${e}'s deposited sequence differs from E9PZQ0`);
  // S5
  const pig = r1("Sus scrofa");
  if (!eq(entriesOf(pig), ["6W1N", "6X32", "6X33", "6X34", "6X35", "6X36", "9PWO"])) F.push(`S5: pig RyR1 ${entriesOf(pig).join(",")}`);
  for (const r of rows.filter((r) => r.species === "Sus scrofa" && r.uniprot === "-" && r.iso !== "RyR1" && /ryanodine/i.test(r.basis + r.title) && !/RyR2/.test(r.iso))) F.push(`S5: unmapped pig ${r.entry} is ${r.iso}`);
  // S6
  if (ids("search_entries_Q92736.json").length !== 26) F.push(`S6: Q92736 maps to ${ids("search_entries_Q92736.json").length}`);
  // S7
  const want = { "6X34": "R615C", "6X35": "R615C", "6X36": "R615C", "9PWO": "R615C", "6W1N": "R615 (wild type)", "6X32": "R615 (wild type)", "6X33": "R615 (wild type)" };
  for (const [e, m] of Object.entries(want)) { const r = pig.find((x) => x.entry === e); if (!r || r.mutation !== m) F.push(`S7: ${e} reads ${r ? r.mutation : "nothing"}, not ${m}`); }
  for (const e of ["7T64", "7T65", "9CGP", "9CGQ"]) { const r = rows.find((x) => x.entry === e && x.iso === "RyR1"); if (!r || !/^Y523S; R164 \(wild type\)$/.test(r.mutation)) F.push(`S7: ${e} reads ${r ? r.mutation : "nothing"}`); }
  { const r = rows.find((x) => x.entry === "6WOT" && x.iso === "RyR1"); if (!r || !/Y523 \(wild type\); R164C/.test(r.mutation)) F.push(`S7: 6WOT reads ${r ? r.mutation : "nothing"}`); }
  return F;
}

// ---------- run, controls, report ----------
const { files, used, S1 } = load();
const rows = classify(files);
const findings = S1.concat(check(files, rows));
const clone = (o) => JSON.parse(JSON.stringify(o));
const controls = [
  ["S1", () => { const b = Buffer.from(fs.readFileSync(path.join(G, INPUTS[0]))); b[b.length - 2] ^= 1; return sha(b) === retrievals.find((r) => r.stored_at === INPUTS[0]).generated ? [] : ["S1: planted byte change"]; }],
  ["S2", () => { const f = clone(files); f[RAW + "search_entries_P21817.json"].result_set.push({ identifier: "9XXX" }); return check(f, rows); }],
  ["S3", () => check(files, rows.filter((r) => r.entry !== "7UMZ"))],
  ["S4", () => { const rs = clone(rows); rs.find((r) => r.entry === "9NMO" && r.iso === "RyR1").title += " mutant R163C"; return check(files, rs); }],
  ["S4", () => { const f = clone(files); const p = f[RAW + "graphql_o2_mouse_sequences.json"].data.entries[0].polymer_entities
    .find((x) => /ryanodine/i.test(x.rcsb_polymer_entity.pdbx_description));
    p.entity_poly.pdbx_seq_one_letter_code_can = p.entity_poly.pdbx_seq_one_letter_code_can.replace(/\s/g, "").replace(/^(.{523})Y/, "$1S");
    return check(f, rows); }],
  ["S5", () => { const rs = clone(rows); rs.find((r) => r.entry === "6W1N" && r.iso === "RyR1").species = "Oryctolagus cuniculus"; return check(files, rs); }],
  ["S6", () => { const f = clone(files); f[RAW + "search_entries_Q92736.json"].result_set.pop(); return check(f, rows); }],
  ["S7", () => { const rs = clone(rows); rs.find((r) => r.entry === "6X33" && r.iso === "RyR1").mutation = "R615C"; return check(files, rs); }],
];
const base = new Set(findings);
const ctl = controls.map(([k, f]) => { const got = f().filter((x) => !base.has(x)); return `${got.some((x) => x.startsWith(k + ":")) ? "caught" : "NOT CAUGHT"}: ${k}`; });

const by = {};
for (const r of rows) { const k = `${r.species} | ${r.iso}`; (by[k] = by[k] || new Set()).add(r.entry); }
console.log(`O2 survey, part 1 (${new Date().toISOString()}): ${INPUTS.length} inputs, each against its retrieval record`);
for (const [k, s] of Object.entries(by).sort()) console.log(`  ${k.padEnd(62)} ${String(s.size).padStart(4)} entries`);
console.log(`\nFINDINGS (${findings.length}):`); findings.forEach((f) => console.log("  " + f));
console.log(`\ncontrols (${ctl.filter((c) => c.startsWith("caught")).length} of ${ctl.length} caught):`); ctl.forEach((c) => console.log("  " + c));

if (process.argv.includes("--write")) {
  if (findings.length || ctl.some((c) => !c.startsWith("caught"))) { console.log("\nNOT WRITTEN: findings or an uncaught control"); process.exit(1); }
  const keep = rows.filter((r) => r.iso === "RyR1").sort((a, b) => a.species.localeCompare(b.species) || a.entry.localeCompare(b.entry));
  const head = ["entry", "entity", "species", "isoform_basis", "uniprot", "method", "resolution_A", "released", "sample_length",
    "ligands_ccd", "title", "title_state_words", "mutation_read_from_sequence", "citation_doi"];
  const lines = keep.map((r) => [r.entry, r.entity, r.species, r.basis, r.uniprot, r.method, r.resolution, r.released, r.sample_len,
    r.ligands, r.title, r.title_state_words, r.mutation || "-", r.doi].map((v) => String(v).replace(/[\t\n]/g, " ")).join("\t"));
  const prov = `# o2_structure_survey.tsv: every PDB entry holding a RyR1 entity, as plans A, A2, B and B2 of 2026-10-06 found them. Generated by how/runtime/channelscope/o2/survey_entries.js --write; never edited by hand.\n# Inputs (retrieval records): ${INPUTS.map((i) => `${i}=${used[i]}`).join("; ")}\n`;
  fs.writeFileSync(OUT, prov + head.join("\t") + "\n" + lines.join("\n") + "\n");
  console.log(`\nwritten: ${path.relative(VAULT, OUT)} (${keep.length} RyR1 entities), ${sha(fs.readFileSync(OUT))}`);
}
