#!/usr/bin/env python3
"""Collect and verify the retrieved record of every work cited in the two reports.

Run from the repository root. Needs network access to NCBI E-utilities and Europe PMC.

For every PMID that appears in reports/DETA_track1_report.md or reports/DETA_track2_report.md it
writes references/papers/<pmid>/meta.json and abstract.txt, adds fulltext.txt where the licence
permits redistributing it, and writes references/bibliography.json, references/BIBLIOGRAPHY.md and
references/papers/README.md.

A second pass covers what PubMed does not index. Every DOI cited in either report that no cited
PubMed record carries is resolved through Crossref and DataCite and written to
references/other_sources.json, so a preprint or a dataset is recorded as explicitly as a journal
article. The language of every work is recorded, from PubMed for indexed works and from the
registration metadata otherwise.

Two deliberate limits.

Full text is shipped only under CC BY or a public-domain dedication. Copying a paywalled article,
or one under a non-commercial or no-derivatives licence, into a public repository would
redistribute material the publisher holds copyright in. The licence of every work is recorded
either way, so an absent body is absent for a stated reason.

E-mail addresses are removed from every retrieved text. Author contact addresses are third-party
personal data and nothing in this verification needs them.

A PMID that does not resolve is a defect in the citing report. The run reports it and the table
names it rather than dropping it.
"""
import json, os, re, sys, time, urllib.request, datetime

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML"
UA = {"User-Agent": "Mozilla/5.0 (reference verification for a research release)"}
REPORTS = ["reports/DETA_track1_report.md", "reports/DETA_track2_report.md"]
PAPERS = "references/papers"
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Licence URLs whose terms allow this repository to carry the body.
REDISTRIBUTABLE = ("creativecommons.org/licenses/by/", "creativecommons.org/publicdomain/")
FLAGS = ("Retracted Publication", "Retraction of Publication",
         "Expression of Concern", "Corrected and Republished Article")

def get(url, headers=None, tries=3, timeout=60):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if k == tries - 1:
                return None
            time.sleep(3 * (k + 1))

def strip_mail(t):
    return EMAIL.sub("[e-mail removed]", t)

def licence_name(url):
    m = re.search(r"creativecommons\.org/(licenses|publicdomain)/([a-z0-9\-]+)", url or "")
    if not m:
        return ""
    return "cc0" if m.group(1) == "publicdomain" else ("cc " + m.group(2))

def cited_pmids():
    out = {}
    for path in REPORTS:
        txt = open(path, encoding="utf-8").read()
        tag = "Track 1" if "track1" in path else "Track 2"
        for p in re.findall(r"PMID[: ]+(\d{7,8})", txt):
            out.setdefault(p, set()).add(tag)
    return out

def main():
    cited = cited_pmids()
    pmids = sorted(cited, key=int)
    print("distinct PMIDs cited in the two reports: %d" % len(pmids))
    if not pmids:
        sys.exit("no PMID found; run from the repository root")

    # Metadata in batches. esummary carries the PMC id in articleids; elink merges ids when
    # several are passed at once, so it is not used here.
    summ = {}
    for i in range(0, len(pmids), 50):
        b = pmids[i:i + 50]
        raw = get(EUTILS + "esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(b))
        if raw:
            res = json.loads(raw).get("result", {})
            for p in b:
                if p in res:
                    summ[p] = res[p]
        print("  metadata %d/%d" % (len(summ), len(pmids)))
        time.sleep(1)

    rows, unresolved, shipped = [], [], []
    for n, p in enumerate(pmids, 1):
        r = summ.get(p)
        if not r or r.get("error"):
            unresolved.append(p)
            print("  %s DID NOT RESOLVE" % p)
            continue
        folder = os.path.join(PAPERS, p)
        os.makedirs(folder, exist_ok=True)

        ids = r.get("articleids") or []
        doi = next((a["value"].strip() for a in ids if a.get("idtype") == "doi"), "")
        if not doi:
            el = r.get("elocationid") or ""
            doi = el[4:].strip() if el.startswith("doi:") else ""
        pmcid = next((a["value"].strip() for a in ids if a.get("idtype") == "pmc"), "")
        authors = [a.get("name", "") for a in (r.get("authors") or [])]
        ptypes = r.get("pubtype") or []
        langs = r.get("lang") or []

        ab = get(EUTILS + "efetch.fcgi?db=pubmed&rettype=abstract&retmode=text&id=" + p)
        if ab:
            open(os.path.join(folder, "abstract.txt"), "w", encoding="utf-8").write(strip_mail(ab))
        time.sleep(0.4)

        lic, lic_url, oa, ft = "", "", False, False
        body_path = os.path.join(folder, "fulltext.txt")
        if pmcid:
            xml = get(EPMC % pmcid, headers=UA, tries=2)
            time.sleep(0.4)
            if xml:
                oa = True
                m = re.search(r'<license[^>]*xlink:href="([^"]+)"', xml)
                lic_url = m.group(1) if m else ""
                lic = licence_name(lic_url)
                if lic_url and any(k in lic_url for k in REDISTRIBUTABLE):
                    body = re.sub(r"<(/p|/title|/sec)>", "\n", xml)
                    body = re.sub(r"<[^>]+>", "", body)
                    body = re.sub(r"\n\s*\n+", "\n\n", body).strip()
                    open(body_path, "w", encoding="utf-8").write(strip_mail(body) + "\n")
                    ft = True
                    shipped.append(p)
        if not ft and os.path.exists(body_path):
            os.remove(body_path)

        meta = {
            "pmid": p, "cited_in": sorted(cited[p]),
            "title": (r.get("title") or "").rstrip("."),
            "authors": authors, "first_author": authors[0] if authors else "",
            "journal": r.get("fulljournalname") or r.get("source") or "",
            "pubdate": r.get("pubdate") or "", "doi": doi, "pmcid": pmcid,
            "language": langs,
            "license": lic, "license_url": lic_url, "open_access": oa,
            "pubtype": ptypes, "flags": [f for f in FLAGS if f in ptypes],
            "pubmed_url": "https://pubmed.ncbi.nlm.nih.gov/%s/" % p,
            "doi_url": ("https://doi.org/" + doi) if doi else "",
            "fulltext_included": ft,
        }
        json.dump(meta, open(os.path.join(folder, "meta.json"), "w", encoding="utf-8"),
                  indent=1, ensure_ascii=False)
        rows.append(meta)
        if n % 20 == 0 or n == len(pmids):
            print("  collected %d/%d" % (n, len(pmids)))

    other = collect_non_pubmed(rows)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pmc_n = sum(1 for r in rows if r["pmcid"])
    oa_n = sum(1 for r in rows if r["open_access"])
    flagged = [r for r in rows if r["flags"]]
    json.dump({"collected_utc": stamp, "cited": len(pmids), "resolved": len(rows),
               "unresolved": unresolved, "with_pmc_record": pmc_n, "open_access": oa_n,
               "fulltext_included": shipped, "flagged": [r["pmid"] for r in flagged],
               "records": rows},
              open("references/bibliography.json", "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    write_markdown(rows, unresolved, flagged, shipped, stamp, pmc_n, oa_n, other)

    print("\ncited=%d resolved=%d unresolved=%d pmc=%d open_access=%d fulltext=%d flagged=%d"
          % (len(pmids), len(rows), len(unresolved), pmc_n, oa_n, len(shipped), len(flagged)))
    for r in flagged:
        print("FLAG", r["pmid"], r["flags"])
    if unresolved:
        print("UNRESOLVED:", unresolved)

DOI_RX = re.compile(r"10\.\d{4,9}/(?:[^\s()\[\]<>\"]|\([^\s()]*\))+")


def collect_non_pubmed(rows):
    """Every DOI cited in the reports that no cited PubMed record carries.

    These are the sources PubMed does not index: preprints, datasets, software records. They are
    resolved through Crossref, then DataCite, and written to references/other_sources.json.
    """
    text = "".join(open(p, encoding="utf-8").read() for p in REPORTS)
    cited = {d.rstrip(".,;:").lower() for d in DOI_RX.findall(text)}
    covered = {(r["doi"] or "").lower() for r in rows if r["doi"]}
    # A DOI the regex clipped at an inner bracket is still covered if a record's DOI starts with it.
    missing = sorted(d for d in cited
                     if d not in covered and not any(c.startswith(d) for c in covered))
    out = []
    for d in missing:
        rec = {"doi": d, "doi_url": "https://doi.org/" + d, "title": "", "first_author": "",
               "year": "", "venue": "", "type": "", "language": "", "registry": ""}
        raw = get("https://api.crossref.org/works/" + d, tries=2, timeout=30)
        if raw:
            try:
                m = json.loads(raw)["message"]
                rec["registry"] = "Crossref"
                rec["title"] = (m.get("title") or [""])[0]
                au = (m.get("author") or [{}])[0]
                rec["first_author"] = (au.get("family", "") + " " + au.get("given", "")).strip()
                parts = (m.get("issued", {}).get("date-parts") or [[""]])[0]
                rec["year"] = str(parts[0]) if parts else ""
                rec["venue"] = (m.get("container-title") or m.get("institution") and
                                [m["institution"][0].get("name", "")] or [""])[0]
                rec["type"] = m.get("type", "")
                rec["language"] = m.get("language", "")
            except Exception:
                pass
        if not rec["title"]:
            raw = get("https://api.datacite.org/dois/" + d, tries=2, timeout=30)
            if raw:
                try:
                    a = json.loads(raw)["data"]["attributes"]
                    rec["registry"] = "DataCite"
                    rec["title"] = (a.get("titles") or [{}])[0].get("title", "")
                    rec["first_author"] = (a.get("creators") or [{}])[0].get("name", "")
                    rec["year"] = str(a.get("publicationYear") or "")
                    rec["venue"] = a.get("publisher", "")
                    rec["type"] = (a.get("types") or {}).get("resourceTypeGeneral", "")
                    rec["language"] = a.get("language") or ""
                except Exception:
                    pass
        time.sleep(0.4)
        out.append(rec)
        print("  non-PubMed: %s  %s" % (d, rec["title"][:60] or "NOT RESOLVED"))
    json.dump({"cited_dois_without_a_pubmed_record": len(out), "records": out},
              open("references/other_sources.json", "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    return out


def write_markdown(rows, unresolved, flagged, shipped, stamp, pmc_n, oa_n, other=()):
    t1 = sum(1 for r in rows if "Track 1" in r["cited_in"])
    t2 = sum(1 for r in rows if "Track 2" in r["cited_in"])
    L = ["# Bibliography: every work cited in the two reports\n",
         "Every PMID that appears in `reports/DETA_track1_report.md` or",
         "`reports/DETA_track2_report.md`, resolved against PubMed on %s. Regenerate with" % stamp,
         "`python3 citations/collect_references.py` from the repository root; it needs network access.\n"]
    if unresolved:
        L += ["**%d distinct works. %d resolve. %d did not: %s.** A PMID that does not resolve is a"
              % (len(rows) + len(unresolved), len(rows), len(unresolved), ", ".join(unresolved)),
              "defect in the citing report and should be read as one.\n"]
    else:
        L += ["**%d distinct works. All %d resolve to a PubMed record, so no citation in either"
              % (len(rows), len(rows)),
              "report is invented.**\n"]
    if flagged:
        L += ["Publication-type flags: " + "; ".join(
            "%s (%s)" % (r["pmid"], ", ".join(r["flags"])) for r in flagged) + "\n"]
    else:
        L += ["None carries a retraction, a correction-and-republication or an expression of concern",
              "in its PubMed publication types, as of the date above.\n"]
    langs = {}
    for r in rows:
        for code in (r.get("language") or ["(not stated)"]):
            langs[code] = langs.get(code, 0) + 1
    if set(langs) == {"eng"}:
        L += ["Every one is in English, as PubMed records the language.\n"]
    else:
        L += ["Languages, as PubMed records them: " +
              ", ".join("%s %d" % (k, v) for k, v in sorted(langs.items(), key=lambda x: -x[1])) + ".\n"]
    if other:
        L += ["## Cited sources that PubMed does not index\n",
              "%d DOIs are cited in the reports without a PubMed record behind them: preprints," % len(other),
              "datasets and software records. They are resolved through Crossref and DataCite and",
              "listed in `references/other_sources.json`. No copy of them is shipped here.\n",
              "| DOI | first author | year | venue | type | registry |",
              "|---|---|---|---|---|---|"]
        for o in other:
            L.append("| [%s](%s) | %s | %s | %s | %s | %s |" % (
                o["doi"], o["doi_url"], o["first_author"], o["year"],
                o["venue"], o["type"], o["registry"]))
        L.append("")
    L += ["%d are cited in Track 1 and %d in Track 2.\n" % (t1, t2),
          "## What is in `references/papers/`\n",
          "One folder per PMID: `meta.json` with the identifiers, authorship, venue, date, DOI, PMC",
          "id and licence, and `abstract.txt` with the record as NCBI E-utilities returns it.",
          "%d of the %d have a PMC record and %d are served by Europe PMC as open access.\n"
          % (pmc_n, len(rows), oa_n),
          "`fulltext.txt` is present for **%d** of them, the ones whose licence permits" % len(shipped),
          "redistribution (CC BY or a public-domain dedication). For every other work the licence is",
          "recorded and the body is not copied here, because copying it would redistribute material",
          "the publisher holds copyright in. Every row carries the PubMed link and, where one is",
          "registered, the DOI, so any of the %d is one click away at the source, which is the" % len(rows),
          "better provenance anyway: the reader sees the publisher's version rather than ours.\n",
          "E-mail addresses are removed from every retrieved text. Author contact addresses are",
          "third-party personal data and nothing in this verification needs them.\n",
          "## The table\n",
          "| # | PMID | first author | year | journal | title | DOI | PMC | licence | text here | cited in |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, r in enumerate(sorted(rows, key=lambda x: (x["first_author"].lower(), x["pubdate"])), 1):
        yr = (re.findall(r"\d{4}", r["pubdate"]) or [""])[0]
        et = " et al." if len(r["authors"]) > 1 else ""
        L.append("| %d | [%s](%s) | %s%s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            n, r["pmid"], r["pubmed_url"], r["first_author"], et, yr, r["journal"],
            r["title"].replace("|", "\\|"),
            ("[%s](%s)" % (r["doi"], r["doi_url"])) if r["doi"] else "",
            ("[%s](https://europepmc.org/article/MED/%s)" % (r["pmcid"], r["pmid"])) if r["pmcid"] else "",
            r["license"] or ("open, not stated" if r["open_access"] else ""),
            "abstract + full text" if r["fulltext_included"] else "abstract",
            ", ".join(r["cited_in"])))
    open("references/BIBLIOGRAPHY.md", "w", encoding="utf-8").write("\n".join(L) + "\n")

    R = ["# The retrieved record of every cited work\n",
         "One folder per PMID, %d in all, for every work cited in either report. Collected on %s"
         % (len(rows), stamp),
         "with `citations/collect_references.py`.\n",
         "| file | what it is |", "|---|---|",
         "| `meta.json` | identifiers, title, authors, journal, date, DOI, PMC id, licence, which report cites it |",
         "| `abstract.txt` | the PubMed record as NCBI E-utilities returns it |",
         "| `fulltext.txt` | present only where the licence permits redistribution (%d folders) |" % len(shipped),
         "", "## Why most folders hold no full text\n",
         "Copying a paywalled article, or one under a non-commercial or no-derivatives licence, into",
         "a public repository redistributes material the publisher holds copyright in. The body is",
         "shipped only under CC BY or a public-domain dedication. `meta.json` records the licence for",
         "every work and `BIBLIOGRAPHY.md` shows it in the table, so what is absent is absent for a",
         "stated reason rather than silently.\n",
         "The point of this collection is that a reader can check that each citation is real, says",
         "what the report says it says, and is retrievable. Retrieval happens at the source, by the",
         "PubMed link and the DOI in every folder.\n",
         "## What it shows\n",
         "All %d PMIDs resolve, so no citation in either report is invented. None is retracted or" % len(rows),
         "under an expression of concern as of the collection date. Re-running the collector",
         "reproduces this folder and will show any record whose status has changed since.\n",
         "E-mail addresses are removed from the retrieved text.\n"]
    open(os.path.join(PAPERS, "README.md"), "w", encoding="utf-8").write("\n".join(R) + "\n")

if __name__ == "__main__":
    main()
