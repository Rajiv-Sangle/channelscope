"""columns.py - the column line of each of CL-4's nine tables, as the criteria fix it (*The outputs and their column
line*): name, type, required, description, and for record columns the record type each must name. The order is the
tables'. A human position's column names numbering:P21817-1.sv3; a partner's position names none."""
from __future__ import annotations

H = "numbering:P21817-1.sv3"

# (name, datatype, required, description, unit, numbering)
TABLES = {
    "cl4_set": [
        ("human_position", "integer", True, "A residue of P21817-1 named by at least one included ClinVar record", None, H),
        ("human_residue", "string", True, "P21817-1's amino acid there, one letter", None, None),
        ("n_records", "integer", True, "Included ClinVar records at this residue", None, None),
        ("in_c5_sample", "boolean", True, "True if C5 re-derives this residue", None, None),
        ("clinvar_records", "string", True, "The retrievals of the held search and of the summary batch or batches "
                                            "holding this residue's records", None, None),
        ("uniprot_record", "string", True, "The retrieval of P21817.json", None, None)],
    "cl4_partners": [
        ("human_position", "integer", True, "The set residue", None, H),
        ("species", "string", True, "The partner's species", None, None),
        ("partner_numbering", "string", True, "The numbering the partner position indexes", None, None),
        ("correspondence", "string", True, "pair or no-correspondence, as the mapping table commits it", None, None),
        ("partner_position", "integer", False, "The partner's position in partner_numbering; empty with no "
                                               "correspondence", None, None),
        ("partner_residue", "string", False, "The partner's amino acid, one letter", None, None),
        ("reliability", "string", True, "standard or lowered, as committed", None, None),
        ("reliability_reasons", "string", False, "As committed: ;-separated reason codes", None, None),
        ("ambiguous", "boolean", True, "As committed", None, None),
        ("mapping_column", "integer", True, "The mapping table's column (its key) for this row", None, None),
        ("mapping_table", "string", True, "The mapping table's record", None, None),
        ("c7_blind_plus1", "boolean", False, "True if the partner's next residue is the same amino acid, so C7 cannot "
                                             "see a slip of +1; empty with no partner", None, None),
        ("c7_blind_minus1", "boolean", False, "The same for the previous residue (a slip of -1)", None, None),
        ("partner_numbering_record", "string", True, "The numbering record of partner_numbering", None, None),
        ("a6_entries", "string", False, "The A6 entries that attach to this residue (rabbit rows only), "
                                        ";-separated, by L1's rule", None, None),
        ("a6_record", "string", False, "A6's check-result record, where a6_entries is filled", None, None)],
    "cl4_structures": [
        ("human_position", "integer", True, "The set residue", None, H),
        ("species", "string", True, "The entry's species, as CL-2's entries table writes it", None, None),
        ("partner_numbering", "string", True, "As in cl4_partners", None, None),
        ("partner_position", "integer", True, "The partner's position in partner_numbering", None, None),
        ("partner_residue", "string", True, "The partner's amino acid, one letter", None, None),
        ("entry", "string", True, "The PDB entry", None, None),
        ("chain", "string", True, "A RyR1 chain, auth_asym_id", None, None),
        ("status", "string", True, "joined, not joined, modelled, not placed, not determinable, not modelled, entry "
                                   "not analysed or withdrawn (C5-S), by L2's rule", None, None),
        ("join_path", "string", False, "For joined and withdrawn (C5-S) rows: agree or path A only, the CL-2 "
                                       "segment's status; empty otherwise", None, None),
        ("checked_against_sifts", "boolean", False, "For the same rows: the segment's checked_against_sifts; empty "
                                                    "otherwise", None, None),
        ("not_joined_reason", "string", False, "The reason, in the forms L2's rule gives; empty for joined and not "
                                               "modelled", None, None),
        ("author_number", "integer", False, "The residue's _atom_site.auth_seq_id, where L2's rule shows one", None,
         None),
        ("structure_residue", "string", False, "That residue's label_comp_id, three letters, from the atom records",
         None, None),
        ("differs_from_reference", "boolean", False, "For joined rows: true where CL-2's exceptions table lists the "
                                                     "residue as a declared difference", None, None),
        ("declaration", "string", False, "Where differs_from_reference is true: that exceptions row's declared "
                                         "value", None, None),
        ("cl2_segment", "integer", False, "CL-2's segment holding the residue at author_number", None, None),
        ("gate_case", "string", True, "The entry's gate case, CL-3's mark: a, b, c or d", None, None),
        ("gate_case_reason", "string", False, "CL-3's reason for case c or d", None, None),
        ("state_class_a", "string", True, "closed, open or indeterminate by measure A (S13's class_a)", None, None),
        ("state_class_b", "string", True, "The same by measure B at the gate's height (class_b_fixed)", None, None),
        ("state_class_minus_0_5", "string", True, "The classes by A and by B, written A/B, with both lines moved "
                                                  "down by 0.5 A (class_at_minus_0_5)", None, None),
        ("state_class_plus_0_5", "string", True, "The same, with both lines moved up by 0.5 A (class_at_plus_0_5)",
         None, None),
        ("gate_radius_a", "number", True, "The pore's radius at the gate by measure A, as S13 writes it", "Å", None),
        ("deposited_words", "string", True, "The words that name the state, verbatim from S13's table", None, None),
        ("deposited_implies", "string", True, "The state those words imply, verbatim from S13's table", None, None),
        ("local_model_quality", "string", True, "Fixed text: not assessed", None, None),
        ("c5s_verdict", "string", False, "For a join C5-S tested: consistent, counts against or not determinable",
         None, None),
        ("c5s_check_result", "string", False, "C5-S's check-result record, or for a join withdrawn with its "
                                              "segment, the record of C5-S's segment rule", None, None),
        ("structure_record", "string", True, "The mmCIF's retrieval record", None, None),
        ("numbering_tables", "string", True, "CL-2's table records read for the row", None, None),
        ("state_table", "string", True, "S13's table record", None, None),
        ("gate_case_table", "string", True, "CL-3's gate-case table record", None, None),
        ("mapping_table", "string", True, "The mapping table's record", None, None)],
    "cl4_structure_counts": [
        ("human_position", "integer", True, "The set residue", None, H),
        ("species", "string", True, "The species", None, None),
        ("class_measure", "string", True, "A; and B too if S13's table gives any entry different classes by A and "
                                          "by B", None, None),
        ("entries", "integer", True, "Entries of this species among the 26", None, None),
        ("entries_joined_closed_agree", "integer", True, "Entries joined on agree, gate case a or b, class closed",
         None, None),
        ("entries_joined_open_agree", "integer", True, "The same, class open", None, None),
        ("entries_joined_closed_path_a_only", "integer", True, "Entries joined on path A only (none on agree), gate "
                                                               "case a or b, class closed", None, None),
        ("entries_joined_open_path_a_only", "integer", True, "The same, class open", None, None),
        ("entries_joined_indeterminate", "integer", True, "Entries joined either way, gate case a or b, class "
                                                          "indeterminate", None, None),
        ("entries_joined_gate_case_c_or_d", "integer", True, "Entries joined either way whose gate case is c or d",
         None, None),
        ("entries_withdrawn_c5s", "integer", True, "Entries whose status is withdrawn (C5-S)", None, None),
        ("entries_not_joined", "integer", True, "Entries whose status is not joined", None, None),
        ("entries_modelled_not_placed", "integer", True, "Entries whose status is modelled, not placed", None, None),
        ("entries_not_determinable", "integer", True, "Entries whose status is not determinable", None, None),
        ("entries_not_modelled", "integer", True, "Entries whose status is not modelled", None, None),
        ("entries_not_analysed", "integer", True, "Entries CL-2 did not analyse", None, None),
        ("structures_table", "string", True, "The record of cl4_structures these counts come from", None, None)],
    "cl4_gnomad": [
        ("human_position", "integer", True, "S2's residue", None, H),
        ("variant_id", "string", True, "gnomAD's identifier: GRCh38 chromosome, position, reference and alternate base",
         None, None),
        ("hgvsc", "string", True, "gnomAD's c. name on ENST00000359596.8", None, None),
        ("hgvsp", "string", True, "gnomAD's p. name", None, None),
        ("ref_aa", "string", True, "S2's reference amino acid, one letter", None, None),
        ("alt_aa", "string", True, "S2's new amino acid, one letter", None, None),
        ("exome_present", "boolean", True, "True where gnomAD returned exome data (S2's exome_ac not empty)", None,
         None),
        ("exome_ac", "integer", False, "Exome allele count", None, None),
        ("exome_an", "integer", False, "Exome allele number", None, None),
        ("exome_filters", "string", False, "gnomAD's exome filters, verbatim; empty with exome_present true means none",
         None, None),
        ("genome_present", "boolean", True, "As exome_present, for genomes", None, None),
        ("genome_ac", "integer", False, "Genome allele count", None, None),
        ("genome_an", "integer", False, "Genome allele number", None, None),
        ("genome_filters", "string", False, "As exome_filters, for genomes", None, None),
        ("joint_ac", "integer", False, "Joint allele count", None, None),
        ("joint_an", "integer", False, "Joint allele number", None, None),
        ("observed_pass", "boolean", True, "S2's rule: an allele count above 0 with no filter, in the exomes or the "
                                           "genomes", None, None),
        ("flags", "string", False, "gnomAD's variant flags, verbatim", None, None),
        ("gnomad_dataset", "string", True, "Fixed: gnomad_r4", None, None),
        ("gnomad_label", "string", True, "Fixed: gnomAD v4.1.2, the browser's label at commit 528b499", None, None),
        ("gnomad_label_record", "string", True, "The retrieval of the browser's dataset metadata", None, None),
        ("gnomad_table", "string", True, "S2's table record", None, None),
        ("attribution", "string", True, "Fixed attribution text", None, None),
        ("attribution_record", "string", True, "The retrieval of gnomAD's terms of use", None, None)],
    "cl4_clinvar": [
        ("human_position", "integer", True, "N from the title", None, H),
        ("uid", "integer", True, "ClinVar's variation identifier (the summary's uid)", None, None),
        ("accession_version", "string", True, "The record's accession and version", None, None),
        ("title", "string", True, "Verbatim", None, None),
        ("protein_change", "string", True, "p.XaaNYaa, from the title", None, None),
        ("ref_residue", "string", True, "Xaa, one letter", None, None),
        ("alt_residue", "string", True, "Yaa, one letter", None, None),
        ("description", "string", True, "germline_classification.description, verbatim", None, None),
        ("review_status", "string", True, "Verbatim", None, None),
        ("last_evaluated", "string", True, "Verbatim, as held", None, None),
        ("subset", "string", True, "VUS, not VUS, or VUS-high (apart) (Q1, option (c))", None, None),
        ("n_conditions", "integer", True, "Entries of trait_set", None, None),
        ("n_conditions_with_mondo", "integer", True, "Of them, entries with a Mondo identifier", None, None),
        ("clinvar_retrieval", "string", True, "The retrieval of the summary batch holding the record", None, None),
        ("attribution", "string", True, "Fixed attribution text", None, None),
        ("attribution_record", "string", True, "The retrieval of ClinVar's maintenance and use page", None, None)],
    "cl4_clinvar_conditions": [
        ("human_position", "integer", True, "The record's residue", None, H),
        ("accession_version", "string", True, "The record", None, None),
        ("condition_index", "integer", True, "The entry's place in the held trait_set, from 1", None, None),
        ("condition_name", "string", True, "trait_name, verbatim", None, None),
        ("mondo_id", "string", False, "MONDO: and seven digits, from trait_xrefs with db_source MONDO; empty where "
                                      "ClinVar gives none", None, None),
        ("mondo_given", "boolean", True, "True where ClinVar's record gives a Mondo identifier for this condition",
         None, None),
        ("clinvar_retrieval", "string", True, "The retrieval of the summary batch", None, None)],
    "cl4_exclusions": [
        ("uid", "integer", True, "ClinVar's variation identifier", None, None),
        ("accession_version", "string", True, "The record", None, None),
        ("title", "string", True, "Verbatim", None, None),
        ("rule", "integer", True, "The first rule it fails: 1, 2 or 3", None, None),
        ("reason", "string", True, "What failed", None, None),
        ("clinvar_retrieval", "string", True, "The retrieval of the summary batch", None, None)],
    "cl4_vus_counts": [
        ("subset", "string", True, "VUS, and under Q1's option (c) also VUS-high (apart)", None, None),
        ("unit", "string", True, "records or residues", None, None),
        ("join_scope", "string", True, "agree, or agree or path A only", None, None),
        ("species", "string", True, "A species, or any", None, None),
        ("class_measure", "string", True, "A; and B too if S13's table gives any entry different classes", None, None),
        ("n_total", "integer", True, "Records or residues in the subset", None, None),
        ("n_closed", "integer", True, "Joined, within the scope, in at least one entry of class closed and gate case "
                                      "a or b", None, None),
        ("n_open", "integer", True, "The same, class open", None, None),
        ("n_both", "integer", True, "Both of the above", None, None),
        ("n_joined_other_only", "integer", True, "Joined in at least one entry, but in none of class closed or open "
                                                 "with gate case a or b", None, None),
        ("n_not_joined", "integer", True, "Joined in no entry", None, None),
        ("clinvar_table", "string", True, "The record of cl4_clinvar", None, None),
        ("structures_table", "string", True, "The record of cl4_structures", None, None)],
}

KEYS = {"cl4_set": ["human_position"], "cl4_partners": ["human_position", "species"],
        "cl4_structures": ["human_position", "entry", "chain"],
        "cl4_structure_counts": ["human_position", "species", "class_measure"], "cl4_gnomad": ["variant_id"],
        "cl4_clinvar": ["accession_version"], "cl4_clinvar_conditions": ["accession_version", "condition_index"],
        "cl4_exclusions": ["accession_version"],
        "cl4_vus_counts": ["subset", "unit", "join_scope", "species", "class_measure"]}

# record column -> (the record type it must name, several allowed, the value columns it backs)
RECORD_COLUMNS = {
    "cl4_set": {"clinvar_records": ("retrieval", True, ["human_position", "n_records"]),
                "uniprot_record": ("retrieval", False, ["human_residue"])},
    "cl4_partners": {"mapping_table": ("table", False, ["correspondence", "partner_position", "reliability"]),
                     "partner_numbering_record": ("numbering", False, ["c7_blind_plus1", "c7_blind_minus1"]),
                     "a6_record": ("check_result", False, ["a6_entries"])},
    "cl4_structures": {"c5s_check_result": ("check_result", False, ["c5s_verdict"]),
                       "structure_record": ("retrieval", False, ["structure_residue"]),
                       "numbering_tables": ("table", True, ["status", "join_path", "author_number"]),
                       "state_table": ("table", False, ["state_class_a", "gate_radius_a"]),
                       "gate_case_table": ("table", False, ["gate_case"]),
                       "mapping_table": ("table", False, ["partner_position", "partner_residue"])},
    "cl4_structure_counts": {"structures_table": ("table", False, ["entries"])},
    "cl4_gnomad": {"gnomad_label_record": ("retrieval", False, ["gnomad_label"]),
                   "gnomad_table": ("table", False, ["variant_id", "exome_ac", "genome_ac"]),
                   "attribution_record": ("retrieval", False, ["attribution"])},
    "cl4_clinvar": {"clinvar_retrieval": ("retrieval", False, ["title", "description"]),
                    "attribution_record": ("retrieval", False, ["attribution"])},
    "cl4_clinvar_conditions": {"clinvar_retrieval": ("retrieval", False, ["condition_name", "mondo_id"])},
    "cl4_exclusions": {"clinvar_retrieval": ("retrieval", False, ["title", "reason"])},
    "cl4_vus_counts": {"clinvar_table": ("table", False, ["n_total"]),
                       "structures_table": ("table", False, ["n_closed", "n_open"])},
}
