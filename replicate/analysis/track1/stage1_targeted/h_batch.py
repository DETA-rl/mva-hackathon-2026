# Read-only batch: H02 pileup, H03 discordant/split rates, H12 chrX depth, H05 allele balance, H06 het-gap proxy.
import pysam, gzip, collections
BAM = __import__("os").environ["REPL_BAM"]
VCF = __import__("os").environ["REPL_VCF"]
out = {}
with pysam.AlignmentFile(BAM, "rb") as f:
    # H02: bases at chr15:40117088 (1-based); public annotation: dbSNP rs576524605, the upstream allele reported by Ochiai 2014; not a variant of the child
    cov = f.count_coverage("chr15", 40117087, 40117088, quality_threshold=20, read_callback=lambda r: (not r.is_duplicate) and r.mapping_quality >= 20)
    bases = {b: int(cov[i][0]) for i, b in enumerate("ACGT")}
    out["H02_pos_40117088_bases(A,C,G,T)"] = bases
    def rates(chrom, s, e):
        tot = clip = disc = split = 0
        for r in f.fetch(chrom, s, e):
            if r.is_unmapped or r.is_secondary or r.is_supplementary or r.is_duplicate or r.mapping_quality < 20: continue
            tot += 1
            if r.has_tag("SA"): split += 1
            cig = r.cigartuples or []
            if cig and ((cig[0][0] == 4 and cig[0][1] >= 20) or (cig[-1][0] == 4 and cig[-1][1] >= 20)): clip += 1
            if r.is_paired and not r.mate_is_unmapped and (r.next_reference_id != r.reference_id or abs(r.template_length) > 1000): disc += 1
        return dict(reads=tot, split=split, clip20=clip, discordant=disc, split_per1k=round(1000*split/max(tot,1),3), clip_per1k=round(1000*clip/max(tot,1),3), disc_per1k=round(1000*disc/max(tot,1),3))
    out["H03_BUB1B_intron_region"] = rates("chr15", 40160984, 40221137)  # public gene annotation: the BUB1B gene span (GENCODE v44) with a few bp of flank; not a variant position
    out["H03_background_chr15_60Mb"] = rates("chr15", 60000000, 60061000)
    # H12: chrX depth at NAA10 vs chrX background vs autosome reference region
    def depth(chrom, s, e):
        return sum(1 for r in f.fetch(chrom, s, e) if not (r.is_unmapped or r.is_duplicate or r.mapping_quality < 20))
    d_naa = depth("chrX", 153928799, 153935083)  # public gene annotation: the NAA10 gene span (GRCh38) with flank; not a variant position
    d_xbg = depth("chrX", 100000000, 106284000)
    d_auto = depth("chr1", 100000000, 106284000)
    out["H12_depth_reads_NAA10_6.3kb"] = d_naa
    out["H12_depth_reads_chrX_bg_6.3Mb"] = d_xbg
    out["H12_depth_reads_chr1_bg_6.3Mb"] = d_auto
    out["H12_NAA10_to_chrX_bg_ratio"] = round(d_naa / max(d_xbg, 1), 3)
# H05 and H06 from VCF, one pass
ab_low = collections.Counter(); ab_all = collections.Counter(); het_pos = collections.defaultdict(list); chrx_calls = 0
with gzip.open(VCF, "rt") as fh:
    for line in fh:
        if line[0] == "#": continue
        c = line.rstrip("\n").split("\t")
        chrom, pos, filt = c[0], int(c[1]), c[6]
        if chrom == "X": chrx_calls += 1
        if filt != "PASS": continue
        d = dict(zip(c[8].split(":"), c[9].split(":")))
        gt = d.get("GT", "")
        try:
            ad = [int(x) for x in d.get("AD", "").split(",")]
            dp = int(d.get("DP", 0))
        except ValueError:
            continue
        if gt in ("0/1", "0|1", "1|0") and dp >= 20 and len(ad) >= 2:
            ab_all[chrom] += 1
            if ad[1] / dp < 0.15: ab_low[chrom] += 1
        if gt in ("0/1", "0|1", "1|0", "1/2") and chrom.isdigit():
            het_pos[chrom].append(pos)
out["H05_chrX_calls_all_filters"] = chrx_calls
out["H05_het_PASS_DP20_sites_per_chr_lowVAF(<15%)_over_total"] = {k: f"{ab_low[k]}/{ab_all[k]}" for k in sorted(ab_all, key=lambda x: (len(x), x))}
gaps = []
for chrom, ps in het_pos.items():
    ps.sort()
    for a, b in zip(ps, ps[1:]):
        gaps.append((b - a, chrom, a, b))
gaps.sort(reverse=True)
out["H06_top10_het_gaps_bp(chr,start,end)"] = [(g[0], g[1], g[2], g[3]) for g in gaps[:10]]
out["H06_gaps_over_3Mb_count"] = sum(1 for g in gaps if g[0] >= 3_000_000)
for k, v in out.items(): print(k, "=>", v)
