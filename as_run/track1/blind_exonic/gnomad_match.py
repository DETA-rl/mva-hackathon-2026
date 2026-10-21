# Match child exonic calls to gnomAD v4.1 exome sites via remote tabix (regional queries only). Writes to the project folder.
import pysam, time, collections, sys
D = "/home/[redacted]/Documents/HACKATON/_private/blind_gnomad/"
calls = []
for line in open(D + "child_exonic_calls.tsv"):
    if line.startswith("chrom"):
        continue
    c, p, r, a, gt, flt, genes = line.rstrip("\n").split("\t")
    calls.append((c, int(p), r, a, gt, flt, genes))
calls.sort(key=lambda x: (x[0], x[1]))
# merge into regions: gap < 200 kb joins the same region
regions = []
for c, p, r, a, gt, flt, g in calls:
    if regions and regions[-1][0] == c and p - regions[-1][2] < 200000:
        regions[-1][2] = p
        regions[-1][3].append((p, r, a, gt, flt, g))
    else:
        regions.append([c, p, p, [(p, r, a, gt, flt, g)]])
print("calls", len(calls), flush=True)
base = "https://gnomad-public-us-east-1.s3.amazonaws.com/release/4.1/vcf/exomes/gnomad.exomes.v4.1.sites.{}.vcf.bgz"
K, N = int(sys.argv[1]), int(sys.argv[2])
regions = [r for i, r in enumerate(regions) if i % N == K]
import os
part = D + f"child_exonic_gnomad_exomes.part{K}.tsv"
done_keys = set()
if os.path.exists(part):
    for line in open(part):
        f_ = line.rstrip("\n").split("\t")
        if len(f_) >= 8 and f_[0] != "chrom":
            done_keys.add((f_[0], f_[1], f_[2], f_[3]))
    # drop a possibly torn last line before appending
    lines = [l for l in open(part) if l.count("\t") == 11]
    with open(part, "w") as fh_:
        fh_.writelines(lines)
    out = open(part, "a")
else:
    out = open(part, "w")
    out.write("chrom\tpos\tref\talt\tgt\tfilter\tgenes\tgnomad_status\tgnomad_af\tgnomad_ac\tgnomad_an\tgnomad_filter\n")
handles = {}
done = 0
t0 = time.time()
for c, s, e, items in regions:
    items = [it for it in items if (c, str(it[0]), it[1], it[2]) not in done_keys]
    if not items:
        continue
    if c == "M":
        # gnomAD exome release has no chrM file; mtDNA is only in the genome release
        for p, r, a, gt, flt, g in items:
            out.write(f"{c}\t{p}\t{r}\t{a}\t{gt}\t{flt}\t{g}\tnot_in_exome_release\tNA\tNA\tNA\tNA\n")
        out.flush()
        continue
    chrom = "chr" + c
    if c not in handles:
        handles[c] = pysam.VariantFile(base.format(chrom))
    found = collections.defaultdict(list)
    for attempt in range(6):
        try:
            tb = pysam.VariantFile(base.format(chrom)) if attempt else handles[c]
            handles[c] = tb
            found = collections.defaultdict(list)
            lo = max(0, s - 1)
            while lo <= e:
                hi = min(e + 1, lo + 100000)
                for rec in tb.fetch(chrom, lo, hi):
                    found[rec.pos].append(rec)
                lo = hi
            break
        except (OSError, ValueError) as ex:
            print("retry", c, s, attempt, str(ex)[:80], flush=True)
            time.sleep(5 * (attempt + 1))
    for p, r, a, gt, flt, g in items:
        status, af, ac, an, gflt = "absent_site", "NA", "NA", "NA", "NA"
        if p in found:
            status = "site_present_alt_absent"
            for rec in found[p]:
                if rec.ref == r and a in rec.alts:
                    i = rec.alts.index(a)
                    status = "found"
                    af = rec.info["AF"][i] if "AF" in rec.info else "NA"
                    ac = rec.info["AC"][i] if "AC" in rec.info else "NA"
                    an = rec.info["AN"] if "AN" in rec.info else "NA"
                    gflt = ",".join(rec.filter.keys()) or "PASS"
                    break
        out.write(f"{c}\t{p}\t{r}\t{a}\t{gt}\t{flt}\t{g}\t{status}\t{af}\t{ac}\t{an}\t{gflt}\n")
    done += 1
    if done % 200 == 0:
        out.flush()
        print(f"regions {done}/{len(regions)} elapsed {int(time.time()-t0)}s", flush=True)
out.close()
print("DONE", int(time.time()-t0), "s", flush=True)
