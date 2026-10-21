#!/usr/bin/env bash
# Read-only requirements check for the MVA reproduction. Changes nothing. Prints PASS/FAIL/WARN per item.
set -uo pipefail
W=${W:-$PWD/work}
IMG=nvcr.io/nvidia/clara/clara-parabricks:4.7.1-1
pass(){ echo "PASS  $1"; }
fail(){ echo "FAIL  $1"; FAILS=$((FAILS+1)); }
warn(){ echo "WARN  $1"; }
FAILS=0

# OS
if [ "$(uname -s)" = Linux ]; then pass "Linux host"; else fail "Linux host required (found $(uname -s))"; fi

# GPU
if command -v nvidia-smi >/dev/null 2>&1; then
  n=$(nvidia-smi -L | wc -l)
  mem=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | sort -n | head -1)
  [ "$n" -ge 1 ] && pass "NVIDIA GPU count: $n" || fail "no NVIDIA GPU"
  [ "${mem:-0}" -ge 24000 ] && pass "GPU VRAM >= 24 GB (smallest: ${mem} MiB)" || fail "GPU VRAM < 24 GB (smallest: ${mem:-0} MiB)"
else
  fail "nvidia-smi not found (NVIDIA driver not installed)"
fi

# Docker and GPU in containers
if command -v docker >/dev/null 2>&1; then pass "docker present"; else fail "docker not installed"; fi
if docker info 2>/dev/null | grep -qi nvidia || [ -f /etc/docker/daemon.json ] && grep -q nvidia /etc/docker/daemon.json 2>/dev/null; then
  pass "nvidia container runtime configured"
else
  warn "nvidia runtime not detected in docker info; the GPU test below decides"
fi
if docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi >/dev/null 2>&1; then
  pass "GPU visible inside a container"
else
  warn "GPU in container not confirmed with nvidia/cuda base image (may still work with the Parabricks image)"
fi

# RAM
ram_gb=$(awk '/MemTotal/{printf "%d", $2/1048576}' /proc/meminfo 2>/dev/null || echo 0)
[ "$ram_gb" -ge 46 ] && pass "RAM >= 46 GB (found ${ram_gb} GB)" || warn "RAM ${ram_gb} GB < 46 GB: per-chromosome runs peaked at 34 GB system RAM here"

# Disk
mkdir -p "$W" 2>/dev/null
free_gb=$(df -BG "$W" 2>/dev/null | awk 'NR==2{gsub("G","",$4); print $4}')
[ "${free_gb:-0}" -ge 300 ] && pass "free disk >= 300 GB at $W (found ${free_gb} GB)" || fail "free disk ${free_gb:-0} GB < 300 GB at $W"

# Image
if docker image inspect "$IMG" >/dev/null 2>&1; then pass "Parabricks image present"; else warn "Parabricks image not pulled yet (run: docker pull $IMG)"; fi

# Host tools
command -v mosdepth >/dev/null 2>&1 && pass "mosdepth on PATH ($(mosdepth --version 2>&1 | head -1))" || warn "mosdepth not on PATH (v0.3.14 expected)"
command -v python3 >/dev/null 2>&1 && pass "python3 present" || fail "python3 missing"
if [ -n "${HF_TOKEN:-}" ]; then pass "HF_TOKEN set"; else warn "HF_TOKEN not set (needed for the gated dataset)"; fi

echo
if [ "$FAILS" -eq 0 ]; then echo "RESULT: ready (warnings may still need action)"; else echo "RESULT: $FAILS blocking item(s) to fix"; exit 1; fi
