# Environment

- `requirements-quick.txt`: the 7 packages the quick tier needs (numpy, scipy, pandas, pysam, PyYAML and their
  dependencies python-dateutil and six), pinned to the versions of the full freeze. A fresh venv with only these
  reproduced every quick-tier result of the full environment (about 310 MB).
- `requirements_freeze.txt`: `pip freeze` of the analysis virtualenv (Python 3.13.5), 99 packages. The
  `flash_attn` line pointed at a local source build; it is rewritten here as a version pin
  (flash_attn 2.8.3.post2, built from source for the Evo 2 run). It cannot be installed in one
  `pip install -r` command: see "Full tier" below.
- `requirements-full-binary.txt`: the freeze without torch, flash_attn and transformer_engine_torch (step 2 below).
- `requirements-test.txt`: pytest, for the test suite only.
- `containers.txt`: Docker images (with digests) used for alignment (`tools/fq2bam.sh`) and SV calling.
- `system.txt`: GPU and driver of the machine that ran the analyses.

## Full tier (GPU steps), in this order

```
python3.13 -m venv .venv-full
.venv-full/bin/pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cu130    # we ran 2.14.1+cu130
.venv-full/bin/pip install --no-deps -r env/requirements-full-binary.txt
.venv-full/bin/pip install --no-deps --no-build-isolation flash_attn==2.8.3.post2 transformer_engine_torch==2.20.2
```

The last command compiles CUDA code: it needs the CUDA 13 toolkit (`nvcc`; ours 13.1), `ninja`, and a lot of
RAM and time (set `MAX_JOBS` to limit parallel compile jobs). `--no-build-isolation` lets the builds see the torch
installed in step 1 (without it, pip fails with "No module named 'torch'"). The full venv is about 6.9 GB.
These commands are the order we used; the full-tier install has not been re-run from scratch in a clean room
(the quick tier has).

Evo 2 deviation (disclosed in the register): RTX 3090 (sm_86) cannot run FP8, so the Evo 2 7B
config was copied and `use_fp8_input_projections` set to False (`replicate/analysis/models/evo2/configs/evo2-7b-1m.yml`,
as-run copy in `as_run/models/evo2/configs/`). Inference ran in bf16 on one GPU with
`NVTE_ALLOW_UNSAFE_PICKLE_EXTRA_STATE=1` set for that process only, after checking the weights' sha256 against
the Hugging Face LFS object id.
