"""Download the organisers' dataset (gated Hugging Face dataset SageBio/mva-hackathon-2026-data) at the commit we used.

Usage:
  python tools/dl.py [--local-dir DIR] [--vcf-only] [--revision COMMIT]

Accept the dataset terms on Hugging Face first, then log in (`hf auth login`) or set HF_TOKEN. The default folder
is $MVA_WORK/mva-hackathon-2026-data; set the config's MVA_DATA to the same folder. --vcf-only fetches the two
files the quick tier reads from the dataset (WGS_EX2312012_HGWCNDSX7.vcf.gz and its .tbi, file names as on the
dataset card); without it all files are fetched (about 85 GB, including the eight FASTQs that the alignment step
ALIGN-01 needs). Needs huggingface_hub (not part of env/requirements-quick.txt; `pip install huggingface_hub`).

The as-run version of this script is as_run/track1/alignment/dl.py (it had our folder hard-coded).
The organisers' terms require deleting the data after the event.
"""
import argparse
import os
import sys

REPO = "SageBio/mva-hackathon-2026-data"
COMMIT = "59e322d27f399006b398d366d33e703e48a29914"      # a later commit (9f155b0) changed only the README
VCF = ["WGS_EX2312012_HGWCNDSX7.vcf.gz", "WGS_EX2312012_HGWCNDSX7.vcf.gz.tbi"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--local-dir", help="download folder (default: $MVA_WORK/mva-hackathon-2026-data)")
    ap.add_argument("--vcf-only", action="store_true", help="only the VCF and its index (enough for the quick tier "
                                                            "together with a BAM)")
    ap.add_argument("--revision", default=COMMIT, help=f"dataset commit (default {COMMIT[:7]}, the one we used)")
    a = ap.parse_args()
    d = a.local_dir
    if not d:
        if not os.environ.get("MVA_WORK"):
            sys.exit("give --local-dir, or set MVA_WORK (the download goes to $MVA_WORK/mva-hackathon-2026-data)")
        d = os.path.join(os.environ["MVA_WORK"], "mva-hackathon-2026-data")
    from huggingface_hub import snapshot_download
    p = snapshot_download(REPO, repo_type="dataset", revision=a.revision, local_dir=d, max_workers=16,
                          allow_patterns=VCF if a.vcf_only else None,
                          ignore_patterns=None if a.vcf_only else ["README.md", ".gitattributes"])
    print("DONE", p)


if __name__ == "__main__":
    main()
