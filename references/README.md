# Shipped references

## The bibliography of both reports

`BIBLIOGRAPHY.md` lists every work cited in either report, 108 of them, resolved against PubMed:
first author, year, journal, title, DOI, PMC id, licence and which report cites it. All 108 resolve,
so no citation in either report is invented, and none is retracted or under an expression of
concern as of the collection date. `bibliography.json` is the same data for a machine.

`papers/<pmid>/` holds the retrieved record of each one: `meta.json` and `abstract.txt` as NCBI
E-utilities returns it, plus `fulltext.txt` for the four whose licence permits redistribution.
`papers/README.md` states why the other bodies are not copied here and how to retrieve them.
Rebuild all of it with `python3 citations/collect_references.py` from the repository root.

## The ClinGen gene curation list

`ClinGen_gene_curation_list_GRCh38.tsv` is an unmodified copy of the ClinGen gene curation list, GRCh38, release of
16 Oct 2026 (the date in its second header line), downloaded on 2026-10-17 from
`https://ftp.clinicalgenome.org/ClinGen_gene_curation_list_GRCh38.tsv`: 249,270 bytes, sha256
`18af35bf83fee59c86f02a2ab49089f36718ddb7abae5bf80acb2f4785ec98c1` (also in `replicate/expected.yaml`, input
`clingen_gene_curation`).

It is read by the external step SV-MANTA (`replicate/EXTERNAL_STEPS.md`). The upstream URL serves a file that ClinGen
replaces at each release, and we found no archive of earlier releases, so the exact release we used cannot be
re-fetched from upstream. It is shipped so that the step can be redone with the input it used.

ClinGen curated content is released under CC0 1.0 Universal; the attribution ClinGen requests is in `NOTICE`.
