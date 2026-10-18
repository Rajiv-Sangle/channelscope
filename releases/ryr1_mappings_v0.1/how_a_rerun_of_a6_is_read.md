# How a re-run of check A6 is read

Fixed on 11 October 2026, before any recorded re-run. It applies to every re-run of check A6 on the first run's list, and to every re-run on a changed list until that list has a reading of its own, committed before the re-runs it governs. A re-run is the known case if, and only if, all four of these hold:
1. its `list_sha256` equals the first run's, `sha256:9c26f62fc31d6e61d8dae4efd8cf69e5f785e19e9dad8a3c77048ec30f53fa98`;
2. all ten rows of its `results` are identical to the first run's, row for row, with the same fields and values (below). Since A6 computes its roll-up from the rows, this also fixes "reproduced": 9 and "not_reproduced": ["A6-03"];
3. its `investigation_window` is identical: human 159-168 GEKVRVGDDI, rabbit 160-169 GEKVRVGDDL;
4. its planted fault is caught, which here means that the fault's `reproduced` count is below the real run's (5 against 9 in the first run). The label "detected" is not enough, since A6's faulted runs always fail.

A known re-run is the source error this release explains, and A6's outcome is still "fail". Any other result is news: a changed list, a different `not_reproduced`, a changed value in any row, a changed window, or a fault that does not lower the count. Each difference is investigated on both sides, as a possible error in the source or in ours (the sequence version, the map, the code), with neither presumed right. A difference is put down to an error in the source only on evidence that does not come from our map: the sequences at the stated positions, the source's own other statements, or another source.

`a6/run_a6.py` runs check A6 alone from this release's files and prints each condition and the reading.

The first run's values, as its record holds them:

```json
{
  "list_sha256": "sha256:9c26f62fc31d6e61d8dae4efd8cf69e5f785e19e9dad8a3c77048ec30f53fa98",
  "results": [
    {
      "human": [
        522
      ],
      "human_letters": "Y",
      "id": "A6-01",
      "mapped_rabbit": [
        523
      ],
      "not_conserved_by_source": false,
      "rabbit_letters_at_stated": "Y",
      "reproduced": true,
      "stated_human": "Y",
      "stated_rabbit": [
        523
      ],
      "stated_rabbit_letters": "Y"
    },
    {
      "human": [
        163
      ],
      "human_letters": "R",
      "id": "A6-02",
      "mapped_rabbit": [
        164
      ],
      "not_conserved_by_source": false,
      "rabbit_letters_at_stated": "R",
      "reproduced": true,
      "stated_human": "R",
      "stated_rabbit": [
        164
      ],
      "stated_rabbit_letters": "R"
    },
    {
      "human": [
        164
      ],
      "human_letters": "V",
      "id": "A6-03",
      "mapped_rabbit": [
        165
      ],
      "not_conserved_by_source": false,
      "rabbit_letters_at_stated": "R",
      "reproduced": false,
      "stated_human": "R",
      "stated_rabbit": [
        164
      ],
      "stated_rabbit_letters": "R"
    },
    {
      "human": [
        156
      ],
      "human_letters": "R",
      "id": "A6-04",
      "mapped_rabbit": [
        157
      ],
      "not_conserved_by_source": false,
      "rabbit_letters_at_stated": "R",
      "reproduced": true,
      "stated_human": "R",
      "stated_rabbit": [
        157
      ],
      "stated_rabbit_letters": "R"
    },
    {
      "human": [
        4899
      ],
      "human_letters": "G",
      "id": "A6-05",
      "mapped_rabbit": [
        4898
      ],
      "not_conserved_by_source": false,
      "rabbit_letters_at_stated": "G",
      "reproduced": true,
      "stated_human": "G",
      "stated_rabbit": [
        4898
      ],
      "stated_rabbit_letters": "G"
    },
    {
      "human": [
        4927,
        4928
      ],
      "human_letters": "VI",
      "id": "A6-06",
      "mapped_rabbit": [
        4926,
        4927
      ],
      "not_conserved_by_source": false,
      "rabbit_letters_at_stated": "VI",
      "reproduced": true,
      "stated_human": "VI",
      "stated_rabbit": [
        4926,
        4927
      ],
      "stated_rabbit_letters": "VI"
    },
    {
      "human": [
        109
      ],
      "human_letters": "R",
      "id": "A6-07",
      "mapped_rabbit": [
        110
      ],
      "not_conserved_by_source": false,
      "rabbit_letters_at_stated": "R",
      "reproduced": true,
      "stated_human": "R",
      "stated_rabbit": [
        110
      ],
      "stated_rabbit_letters": "R"
    },
    {
      "human": [
        485
      ],
      "human_letters": "M",
      "id": "A6-08",
      "mapped_rabbit": [
        486
      ],
      "not_conserved_by_source": true,
      "rabbit_letters_at_stated": "L",
      "reproduced": true,
      "stated_human": "M",
      "stated_rabbit": [
        486
      ],
      "stated_rabbit_letters": "L"
    },
    {
      "human": [
        4837
      ],
      "human_letters": "Q",
      "id": "A6-09",
      "mapped_rabbit": [
        4836
      ],
      "not_conserved_by_source": false,
      "rabbit_letters_at_stated": "Q",
      "reproduced": true,
      "stated_human": "Q",
      "stated_rabbit": [
        4836
      ],
      "stated_rabbit_letters": "not stated"
    },
    {
      "human": [
        4923,
        4924
      ],
      "human_letters": "FF",
      "id": "A6-10",
      "mapped_rabbit": [
        4922,
        4923
      ],
      "not_conserved_by_source": false,
      "rabbit_letters_at_stated": "FF",
      "reproduced": true,
      "stated_human": "FF",
      "stated_rabbit": [
        4922,
        4923
      ],
      "stated_rabbit_letters": "FF"
    }
  ],
  "investigation_window": {
    "human_159_168": "GEKVRVGDDI",
    "rabbit_160_169": "GEKVRVGDDL"
  },
  "reproduced": 9,
  "not_reproduced": [
    "A6-03"
  ],
  "fault_reproduced": 5
}
```
