# Changelog

All notable changes to this bench are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning is not strictly semver — each numbered release is a public
publication point with its own data set.

## [v2.1] — 2026-04-25

### Added
- README **Validation timeline (post-publication)** section consolidating six
  independent corroborations and one academic theoretical framing that have
  appeared since v1 / v2:
  - [MoE-Spec (arXiv 2602.16052)](https://arxiv.org/abs/2602.16052) names
    the phenomenon ("expert budgeting") and proposes a training-free
    verification-time budget cap.
  - [Alloc-MoE (arXiv 2604.08133)](https://arxiv.org/abs/2604.08133) and
    [XShare (arXiv 2602.07265)](https://arxiv.org/pdf/2602.07265) frame
    the same expert-saturation pressure.
  - [vllm #35387](https://github.com/vllm-project/vllm/issues/35387) —
    H100 + FP8 + Qwen3-Next-80B-A3B with `method=qwen3_next_mtp` reports
    −76.5 % latency regression (different hardware/quant/arch from this
    bench, suspected `mamba_postprocess` CPU sync; same direction).
  - [vllm #38182](https://github.com/vllm-project/vllm/issues/38182) —
    H20-3e + Qwen3.5-35B-A3B + MTP drops prefix-cache hit rate
    ≈92 % → ≈71 %; @Angazenn pinpoints the cause to
    `single_type_kv_cache_manager.py:L457`.
  - [vLLM Qwen3.5/3.6 official Recipes](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen3.5.html)
    now state up-front that "MTP-1 reduces per-token latency but degrades
    text throughput under high concurrency".
- README cross-engine confirmation note in TL;DR + Related reading pointer
  to sibling repo
  [`thc1006/qwen3.6-vllm-2x3090`](https://github.com/thc1006/qwen3.6-vllm-2x3090).
- README applicability note (iv) — batched multi-user serving caveat —
  and (v) — explicit scope: this bench tests `ngram-cache`, `ngram-mod`,
  classic `--model-draft` in llama.cpp and `mtp k=1` in vLLM. **EAGLE-3**
  with CUDA graphs (vLLM Model Runner V2) is not evaluated here.
- README counter-example block: corrected attribution for the +15–45 %
  Qwen3.5-122B-A10B speedup on PR #20075 — that data is from the PR
  author's M3 Max bench plus @0xSero's AMD Strix Halo follow-up, not
  srogmann's bench. Strix Halo also reports up to **+119 %** with the
  REAP-pruned variant on gfx1151.

### Changed
- README applicability note (ii) — `[PR #20075](https://github.com/ggml-org/llama.cpp/pull/20075)`
  was open at v1 publication; on 2026-04-25 a community comment suggested
  it can be closed because its functionality is superseded elsewhere. The
  note now reflects that the hybrid-SSM/MoE checkpoint situation is fluid.

### Older Unreleased entries (carried over from earlier in 2026-04-22 → 2026-04-25)
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
