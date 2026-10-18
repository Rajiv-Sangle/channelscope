<!-- context_channelscope_cl2_numbering_criteria.md as committed in 125f89f9de4f3535727e96ab6ceb6444f9fdaa38, the section 'The gate residue, and what CL-3 does with it'; working-note references replaced as criteria/replacements.json lists -->
**The gate residue, and what CL-3 does with it** (fixed here so that it is committed before the run; it was drafted in
CL-3's notes, version 2, and its critique found that it left out "path A only" and that a rule governing public counts
must be pre-registered). R14 reads the gate residue at S13's author number in every RyR1 chain of each entry. CL-2 may
not change any radius or class, and this rule changes none. *(Amended after the critique of version 2.2, finding S2:
the first wording had no case for an unusable run or an entry with no analysed chain, its cases overlapped, and its
use could not fail mechanically.)* Each chain's gate reading falls in exactly one case, tested in this order:
- **(c) Not checked, or not as expected:** anything that is not (a) or (b) below. That includes a species position
  other than the author number; disputed; identity low; an undeclared or declared difference; a SIFTS anomaly; neither
  path; not modelled; a short departing run (R11c); a residue-level "path A only" inside a chain SIFTS maps; and any
  other outcome that leaves the gate residue unjoined.
- **(b) Checked by this project's alignment alone:** the chain has no SIFTS position at all (path S "none" or another
  accession for the chain), and its gate residue is joined, "path A only", at offset 0, inside a run of offset 0 that
  holds at least 10 modelled residues on each side of the gate. *(The anchoring condition answers the critique's
  point that path A alone can be wrong without a flag, as at author 2092; author 4925–4945 is unbroken at offset 0 in
  all six Woll et al. entries in the critique's emulation.)*
- **(a) Checked against SIFTS:** the gate residue is joined, "agree", at offset 0, the residue is an isoleucine, and
  it is not identity low.

**An entry takes its worst chain's case,** (c) worst, then (b), then (a). **(d) No usable reading:** if CL-2's run
stopped or is marked unusable, or the entry has no analysed RyR1 chain (refused by R7, excluded by R1, or path A
refused), no case can be read for it. Then it leaves PC-3's counts, as in (c), and CL-3's text says why; and if the
whole run is unusable, CL-3's text states that no entry's gate numbering was checked by CL-2.

**What CL-3 does with each case:**
- (a): nothing changes. CL-3's text may say the entry's gate numbering was compared with SIFTS, and adds that SIFTS and
  this project's alignment align the same deposited sequence to the same UniProt release, so they are not independent.
- (b): the entry stays in PC-3's counts, marked "gate numbering checked by this project's alignment alone, not against
  SIFTS". No sentence of CL-3's says such an entry was compared with SIFTS.
- (c) and (d): the entry keeps its radius and class in CL-3's table, marked with the reason; it leaves PC-3's counts,
  the two groups and the sensitivity statements until it is measured again under criteria committed first; and
  CL-3's text names it.
- **In every case** CL-3's text states the blind spot its notes describe: the residue before the gate is also an
  isoleucine in all four species (and the one after it an aspartate), so a model numbered one higher at the gate would
  pass both implementations' check.

**How its use is checked, mechanically:** CL-3's builder derives each entry's case from CL-2's entries and segments
tables by its own code, not by hand, and two planted faults must move an entry: one gate's outcome set to "disputed" in
a copy of the entries table (that entry must become (c)), and one (b) entry's anchoring run cut to 5 residues in a copy
of the segments table (it must become (c)). **What would count against the rule's use:** a (c) or (d) entry left in
PC-3's counts, a (b) entry described as compared with SIFTS, or a planted fault that moves no entry.
