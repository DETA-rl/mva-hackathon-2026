import pysam
bam = pysam.AlignmentFile(__import__("os").environ["REPL_BAM"], "rb")
contig = "chr15" if "chr15" in bam.references else "15"
tl = []
n_pairs = 0
for r in bam.fetch(contig, int(__import__("os").environ["REPL_P1_WINDOW_START"]), int(__import__("os").environ["REPL_P1_WINDOW_END"])):
    if not r.is_read1 or r.is_unmapped or r.mate_is_unmapped or r.is_secondary or r.is_supplementary or r.mapping_quality < 30: continue
    if r.template_length == 0: continue
    n_pairs += 1
    tl.append(abs(r.template_length))
print("contig used:", contig)
print("proper read1 templates in window (MAPQ>=30):", n_pairs)
print("max |TLEN| in window:", max(tl) if tl else None)
print("templates with |TLEN| >= 1000:", sum(1 for t in tl if t >= 1000))
print("templates with |TLEN| >= 4000 (span from the first candidate site to the next het site needs >= " + __import__("os").environ["REPL_P1_GAP1"] + "):", sum(1 for t in tl if t >= int(__import__("os").environ["REPL_P1_GAP1"])))
