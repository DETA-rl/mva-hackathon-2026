from huggingface_hub import snapshot_download
p = snapshot_download("SageBio/mva-hackathon-2026-data", repo_type="dataset",
                      local_dir="/home/[redacted]/Documents/HACKATON/data", max_workers=16)
print("DONE", p)
