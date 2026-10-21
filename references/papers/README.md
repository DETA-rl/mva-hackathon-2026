# The retrieved record of every cited work

One folder per PMID, 110 in all, for every work cited in either report. Collected on 2026-10-21T11:21:07Z
with `citations/collect_references.py`.

| file | what it is |
|---|---|
| `meta.json` | identifiers, title, authors, journal, date, DOI, PMC id, licence, which report cites it |
| `abstract.txt` | the PubMed record as NCBI E-utilities returns it |
| `fulltext.txt` | present only where the licence permits redistribution (4 folders) |

## Why most folders hold no full text

Copying a paywalled article, or one under a non-commercial or no-derivatives licence, into
a public repository redistributes material the publisher holds copyright in. The body is
shipped only under CC BY or a public-domain dedication. `meta.json` records the licence for
every work and `BIBLIOGRAPHY.md` shows it in the table, so what is absent is absent for a
stated reason rather than silently.

The point of this collection is that a reader can check that each citation is real, says
what the report says it says, and is retrievable. Retrieval happens at the source, by the
PubMed link and the DOI in every folder.

## What it shows

All 110 PMIDs resolve, so no citation in either report is invented. None is retracted or
under an expression of concern as of the collection date. Re-running the collector
reproduces this folder and will show any record whose status has changed since.

E-mail addresses are removed from the retrieved text.

