# The residue numbering of 26 RyR1 structures, checked against SIFTS where it maps them

A structure in the Protein Data Bank numbers its residues as its authors chose (the *author numbers*). This check
aligns every modelled residue of every RyR1 chain in 26 cryo-EM structures to the species' UniProt sequence, and
joins those its rules allow, so that values measured on a structure can later be joined to the right residue of the
protein. Its rules were committed
before the SIFTS files were fetched. It was run on 11 October 2026 (11:13 to 11:40 UTC), and its outcome was
"usable".

## The structures and references
- **Rabbit** (13 structures): UniProt P11716. **Mouse** (6): E9PZQ0. **Pig** (7): P16960. UniProt release 2026_03.
- The structure files were fetched from RCSB on 6 October 2026, and the SIFTS files from EBI on 11 October 2026. Each
  file was checked against the SHA-256 recorded when it was fetched.

## Two paths for every residue
- **Path S:** the UniProt position SIFTS gives the residue.
- **Path A:** the position this project's own global alignment gives it (BLOSUM62; gap open −10, extend −0.5), aligning
  the entity's deposited sequence to the species' UniProt sequence. It uses neither SIFTS nor the author numbers.

Per residue, the two are compared:
- **agree:** both give the same position. The residue's UniProt position is that value. It *departs* if that value
  differs from its author number.
- **disputed:** they differ. The residue is reported and not joined.
- **path A only:** SIFTS gives no position for the chain, or maps it to another accession. The position is path A's,
  marked "not checked against SIFTS".
- **path S only:** path A leaves a gap or an ambiguity. Reported, and not joined.

Both paths align the same deposited sequence to the same UniProt release, so their agreement checks the join; it is
not independent evidence.

**Segments.** Within a chain, modelled residues in author order are grouped into the longest runs that share the same
outcome and the same offsets (UniProt position minus author number, on each path). A run whose identity with the
reference is below 0.98 is flagged "identity low", and its residues are not joined. The rules, as amended before the
run (version 2.1; the order is attested by the project's records, not shown), apply this to every run, whatever its
length. A residue is joined only if its segment allows it and the exceptions table
does not list it as not joined.

**Outcome per chain:** *equal* (every compared residue agrees, offset 0); *departs* (at least one segment agrees at a
non-zero offset; each is listed); *disputed* (any disputed residue, or a run whose identity with the reference is low);
*path A only* (read on path A alone, and marked).

## The tables
Each table begins with comment lines (`#`) that record the code's checksum, the libraries and their versions, the
references with their UniProt release, the input files with their retrieval records, the run's UTC times and platform,
and every check with its outcome.

| File | One row per | What it holds |
|---|---|---|
| `cl2_numbering_entries.tsv` | entry, chain and entity | Which entities were analysed as RyR1, the identity with the reference, the outcome, and the counts behind it (modelled, compared, agree, disputed, path A only, UNK, insertion codes, outside the reference) |
| `cl2_numbering_segments.tsv` | segment | Author and UniProt ranges, both offsets, identity, unmodelled gaps, whether it departs, and whether its residues are joined |
| `cl2_numbering_exceptions.tsv` | residue or run not joined as usual | UNK runs, insertion codes, residues outside the reference, disputed and identity-low residues, residues differing from the reference, and others not joined, each with the reason |

## What it found
- **The 20 structures SIFTS maps** (13 rabbit, 6 mouse, pig 9PWO): *equal*. No residue is disputed.
- **The six pig structures of Woll et al. (2021)** (6W1N, 6X32 to 6X36;
  [doi:10.1038/s41467-021-21141-3](https://doi.org/10.1038/s41467-021-21141-3)): SIFTS maps none of them, so they
  are read on path A alone. In 6W1N and 6X32 to 6X35, author residues 2736 to 2939 correspond to P16960's 2737 to 2940
  (offset +1) in every RyR1 chain: 180 modelled residues per chain, at identity 1.0. In 6X36 that region holds only
  unknown (UNK) residues. Path A's outcomes were known before the run, and check K8 expected this departure; what
  the run added was the comparison with SIFTS, for the 20 structures it maps.
- **Two stretches of these pig structures are left unjoined by the rules,** each in every RyR1 chain and each named
  in `cl2_numbering_segments.tsv`. Author residue 2092 in 6X32 to 6X36 is a run of one residue that the alignment
  places 45 positions below its author number, apart from its neighbours; the rules leave such a short departing run
  unjoined (rule R11c). In 6X32, author residues 2490 to 2534 sit at their own numbers, but match P16960 at 43 of
  their 45 residues (0.9556), low identity by the rules, so they are not joined either.
- **The gate residue** (I4937 in rabbit, I4935 in mouse and pig) sits at that author number in all 104 RyR1 chains:
  80 checked against SIFTS, 24 on path A alone.

## The planted faults, each caught
Each was run on a corrupted copy of the real input, and each was caught (the table headers give the details). Three
of the checks had no planted fault of their own: K8, the known departure below, K9, an accounting of each chain's
residues, and K10, a report of SIFTS's residue names against the held reference.
- a structure file with one byte changed: refused, its checksum differing from its retrieval record;
- a rabbit structure given the pig reference: refused by the species guard; with the guard off, its chains were found
  not to be RyR1 of that species by sequence, and no residue was joined;
- 100 residues renumbered by one in a structure file, once alone and once with SIFTS's cross-references shifted to
  match: none joined;
- 30 SIFTS positions moved by one: all 30 disputed, none joined;
- a chain's tail renumbered by one from residue 4001, in the structure file and in SIFTS: every residue kept its
  UniProt position and join status, and the shift showed as a change of offset;
- 20 residues renamed unknown (UNK): none compared or joined;
- a chain that is not RyR1 renamed "Ryanodine receptor 1": not treated as RyR1.

## Not yet here
The code that produced the tables, and the rules in full (with their amendments, each committed before the run, in
the project's private working history). The
tables' records are in the composition release's graph (`releases/ryr1_composition_v0.1/graph/records/`): a table
record for each table's copy there (`graph/tables/cl2_numbering_*.tsv`) and the run's record; the run's method record
is withheld there, with a summary.
