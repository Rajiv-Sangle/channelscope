# The survey's word list, and what it misses

The survey's column `title_state_words` holds the words of each entry's title that match this pattern of `o2/survey_entries.js` (as committed in b9323291dd69625d6b498139cb3b669fdbec3196):

    /\b(open pore|closed pore|open state|closed state|open conformation|closed conformation|primed|open|closed)\b/gi

It misses:
- titles that name a state with another word: 7TDG, 9S16, 9S1H, 9S4L, 9S4N, 9S5A, 9S5C, 9S5E, 9S5F (among the unmeasured electron-microscopy entries; listed in `survey_unmeasured.tsv`, column `state_named_but_not_caught`);
- "closed-inactivated", which it reads as "closed": 7TDI, 7TDJ, 7TDK.
