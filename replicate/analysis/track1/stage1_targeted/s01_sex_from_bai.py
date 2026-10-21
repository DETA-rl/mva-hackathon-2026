# S0.1: per-contig mapped/unmapped read counts from the BAI pseudo-bin (37450). Read-only.
import gzip, struct, sys
bam = __import__("os").environ["REPL_BAM"]
bai = bam + ".bai"
with gzip.open(bam, "rb") as f:
    assert f.read(4) == b"BAM\x01"
    l_text = struct.unpack("<i", f.read(4))[0]
    f.read(l_text)
    n_ref = struct.unpack("<i", f.read(4))[0]
    names = []
    for _ in range(n_ref):
        l_name = struct.unpack("<i", f.read(4))[0]
        name = f.read(l_name)[:-1].decode()
        f.read(4)
        names.append(name)
with open(bai, "rb") as f:
    assert f.read(4) == b"BAI\x01"
    n = struct.unpack("<i", f.read(4))[0]
    counts = {}
    for r in range(n):
        n_bin = struct.unpack("<i", f.read(4))[0]
        mapped = unmapped = None
        for _ in range(n_bin):
            bin_id, n_chunk = struct.unpack("<Ii", f.read(8))
            chunks = f.read(16 * n_chunk)
            if bin_id == 37450 and n_chunk == 2:
                _, _, mapped, unmapped = struct.unpack("<QQQQ", chunks)
        n_intv = struct.unpack("<i", f.read(4))[0]
        f.read(8 * n_intv)
        counts[names[r]] = (mapped, unmapped)
autosomes = [f"chr{i}" for i in range(1, 23)]
a_mean = sum(counts[c][0] for c in autosomes) / 22
for c in ["chrX", "chrY", "chr15", "chr11", "chr18", "chr19", "chrM"]:
    m = counts.get(c, (None, None))[0]
    if m is None:
        print(f"{c}: NA")
    else:
        print(f"{c}: mapped={m} ratio_to_autosome_mean={m / a_mean:.4f}")
print(f"autosome_mean_mapped={a_mean:.0f}")
