# Changelog

All notable changes to this bench are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning is not strictly semver — each numbered release is a public
publication point with its own data set.

## [Unreleased]

### Added
- README: cross-engine confirmation note in TL;DR + Related reading
  pointer to sibling repo
  [`thc1006/qwen3.6-vllm-2x3090`](https://github.com/thc1006/qwen3.6-vllm-2x3090).
  vLLM 0.19.1 with `--speculative-config method=mtp k=1` (qwen3.6's
  built-in MTP heads) on 2× RTX 3090 also nets a 12 % slowdown vs
  no-MTP baseline (111 vs 126 tok/s) with variance 65× larger.
  Establishes that the negative finding is engine-independent for this
  model on Ampere — not a llama.cpp implementation gap.
- README: applicability note (iv) — batched multi-user serving caveat,
  with cross-link to the vLLM MTP single-stream confirmation.

### Older Unreleased entries (carried over from before today)
- `v2_3090_followup/results_v2.json` — machine-readable summary of all
  v2 runs (per-prompt `llama-cli` stats + per-config mean / min / max /
  std), extracted from the `.log` artefacts.
- `v2_3090_followup/extract_results.py` — the extraction script used to
  produce the above JSON.
- `v2_3090_followup/plot_v2.py` + `plot_v2_configs.png` — horizontal
  bar chart comparing all 9 original-commit configs against baseline,
  with master-commit cross-check annotation.
- `CHANGELOG.md` — this file.

## [v2.0] — 2026-04-22

Follow-up bench addressing [Oleg-dM's comment](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/discussions/14)
on the HF-discussion thread for `unsloth/Qwen3.6-35B-A3B-GGUF`.

### Added
- `v2_3090_followup/` — fresh single-3090 bench on a different
  physical 3090 covering:
  - baseline (no spec-decode)
  - `--draft-min 2 --draft-max 32` (Oleg's suggestion)
  - `--draft-min 2 --draft-max 16` and `--draft-max 64` (bracketing sweep)
  - default `--draft-min=5` variants (`--draft-max 8/16/32` + bare `-md`)
  - srogmann-style `--draft-min 48 --draft-max 64`
  - `--verbose` per-token acceptance dump
- **Cross-check on current master** `bcb5eeb64`
  (post PR #22227 `speculative-simple: add checkpoint support`) — 3 key
  configs re-run on master hardware to rule out stale-commit artefact.
- 45 per-prompt `llama-cli` logs + `verbose.log`.
- `v2_3090_followup/SUMMARY.md` with methodology + full result table.
- `v2_3090_followup/bench_3090_oleg.sh` reproducible script.
- v2 section appended to `BENCHMARK_ENV.md` documenting the v2
  hardware, toolchain, and both commits tested.
- `.gitignore` negation for `v2_3090_followup/**/*.log` so bench
  evidence survives `git clean` and `git add -A` round-trips.

### Changed
- `README.md` — UPDATE banner summarising v2 findings and linking to
  the follow-up artefacts.
- `pr_comment.md` — UPDATE note so the historical llama.cpp PR-comment
  draft stays consistent with the repo state.

### Key findings
- Oleg's `--draft-min 2 --draft-max 32` beats the `--draft-min=5`
  defaults by +18 % (65.0 vs 55.3 tok/s) but is still −54 % vs
  baseline 139.9 tok/s.
- Aggressive `--draft-min 48 --draft-max 64` is the **least bad**
  recipe at 85.6 tok/s (−39 %) — counter-intuitively, the "wasteful"
  large-window config amortises verify + KV-management overhead
  better than tight windows.
- 100 % draft acceptance is genuine: source read of
  `common/speculative.cpp` (`impl->n_acc_tokens += n_accepted;` in
  `common_speculative_accept()`) + `--verbose` run emitting
  `draft acceptance rate = 1.00000 (115 accepted / 115 generated)`.
- Master cross-check gives identical numbers within ±0.3 % noise, so
  the regression is architectural rather than a stale-commit artefact.

### Conclusion of v1 stands
On a consumer RTX 3090 with Qwen3.6-35B-A3B at Q4_K_M, **no
speculative decoding configuration is a net win** — regardless of
commit, regardless of draft-min / draft-max, regardless of which
measurement regime. H100 / H200 or NVLinked pairs may flip the sign.

## [v1.0] — 2026-04-21

Initial public release of the spec-decode benchmark matrix.

### Added
- 19-configuration bench matrix on a single RTX 3090 (of the two on s1)
  via `llama-server` at commit `9789512` (post PR #19493 merge).
- `Qwen3.6-35B-A3B-UD-Q4_K_XL` main + `Qwen3.5-0.8B-Q4_K_M` draft
  (vocab-matched, 248320 vocab size).
- llama-server-based Python bench runner (`bench_runner.py`) plus
  three shell driver scripts (`run_matrix.sh`, `run_p0_matrix.sh`,
  `run_verify_matrix.sh`).
- Analysis plots: bar chart, per-prompt heatmap, accept-vs-speed
  scatter (in `analysis/`).
- Per-config JSON results in `results/` + `results/verify/`.
- `pr_comment.md` draft for llama.cpp PR #19493 / Issue #20039.
- `BENCHMARK_ENV.md` environment snapshot (s1, 2× RTX 3090,
  i7-11700, Ubuntu 24.04).
- `collect_env.sh` helper to regenerate the env snapshot.

### Key finding
No speculative-decode configuration achieves a net speedup over the
non-speculative baseline of 135.7 tok/s. Mean decode drops 3–12 %
across ngram-cache, ngram-mod, and classic draft-model variants, with
a bimodal tail reaching 59–67 tok/s on reasoning / code prompts
despite 100 % draft acceptance. Interpretation aligned with
MoESD (arXiv 2505.19645) and Utility-Driven SD (arXiv 2506.20675):
for a 3B-active MoE, draft batch K stays below the expert-saturation
threshold (~94 tokens for this sparsity), so each drafted token pulls
new experts through the memory hierarchy and verification pays for
the union.

[Unreleased]: https://github.com/thc1006/qwen3.6-speculative-decoding-rtx3090/compare/v2.0...HEAD
[v2.0]: https://github.com/thc1006/qwen3.6-speculative-decoding-rtx3090/releases/tag/v2.0
[v1.0]: https://github.com/thc1006/qwen3.6-speculative-decoding-rtx3090/releases/tag/v1.0
