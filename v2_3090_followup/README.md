# v2 follow-up bench (2026-04-22)

Response to [Oleg-dM's comment on HF discussion #14](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/discussions/14).
Fresh bench on a single RTX 3090 covering the commenter's suggested
`--draft-min 2 --draft-max 32`, a control sweep of `--draft-min=5`
defaults, srogmann-style `--draft-min 48 --draft-max 64`, plus a
cross-check on current llama.cpp master `bcb5eeb64`
(post PR #22227 `speculative-simple: add checkpoint support`).

![v2 bench result chart](plot_v2_configs.png)

## Headline numbers (tok/s, N=5 per config, same 3090, stock clocks)

| | mean | vs baseline |
|---|---:|---:|
| **baseline** (no spec-decode) | **139.9** | — |
| `--draft-min 48 --draft-max 64` (srogmann-style) | 85.6 | **−39 %** |
| `--draft-min 2 --draft-max 32` (commenter's suggestion) | 65.0 | −54 % |
| default `--draft-min=5 --draft-max 8/16/32` | 55.3–56.5 | −60 % |

Cross-check on master `bcb5eeb64`: identical within ±0.3 % noise.

## Why it still loses

1. **100 % draft acceptance is genuine** — `common/speculative.cpp`
   increments `n_acc_tokens += n_accepted` post-verify; a `--verbose`
   run confirms `draft acceptance rate = 1.00000 (115 / 115)`. The
   0.8 B vocab-matched draft genuinely matches the 35 B target on
   low-entropy prompts. Accept rate is not the bottleneck.
2. **Verify + KV-management overhead exceeds the savings.** On a
   consumer 3090 bound by memory bandwidth, the union of expert
   slices touched during verification ate the per-token forward-pass
   win even at 100 % acceptance.
3. **Counter-intuitive finding:** larger draft windows (48 / 64) lose
   *less* than shorter ones, because they amortise the verify cost
   across more speculated tokens. The opposite of the "wasted
   compute" intuition.

## File index

| File | Purpose |
|---|---|
| [`SUMMARY.md`](SUMMARY.md) | Full methodology, setup, and result tables |
| [`plot_v2_configs.png`](plot_v2_configs.png) | Headline bar chart (above) |
| [`plot_v2.py`](plot_v2.py) | Chart generator (matplotlib) |
| [`results_v2.json`](results_v2.json) | Machine-readable per-config and per-prompt results |
| [`extract_results.py`](extract_results.py) | Extractor that produces `results_v2.json` from the `.log` files |
| [`bench_3090_oleg.sh`](bench_3090_oleg.sh) | Reproducible bash script (requires the two GGUFs locally) |
| [`v2_oleg_suggestions/`](v2_oleg_suggestions) | 4 configs × 5 prompts + `verbose.log` per-token dump |
| [`v2_controls/`](v2_controls) | 5 control configs × 5 prompts (default `--draft-min=5` sweep + srogmann + bare `-md`) |
| [`v2_master_cross_check/`](v2_master_cross_check) | 3 configs × 5 prompts on master `bcb5eeb64` |

## Reproduce

```bash
# (1) install llama.cpp at 97895129e or current master, build with CUDA arch 86
# (2) download model files
hf download unsloth/Qwen3.6-35B-A3B-GGUF Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf --local-dir ~/models
hf download unsloth/Qwen3.5-0.8B-GGUF --include '*Q4_K_M*' --local-dir ~/models
# (3) run
bash bench_3090_oleg.sh
```

Environment snapshot for this bench is appended to the top-level
[`BENCHMARK_ENV.md`](../BENCHMARK_ENV.md#v2-benchmark-environment-follow-up-bench-2026-04-22).

## Conclusion

**No speculative decoding configuration on a consumer RTX 3090 is a
net win for Qwen3.6-35B-A3B at Q4_K_M**, regardless of commit,
regardless of `--draft-min` / `--draft-max`, regardless of whether
you're measuring the "always-active" regime (this v2 bench, 55–85
tok/s) or the "active-plus-skipped mixture" regime (v1 bench, mean
120 with bimodal tail 59).

H100 / H200 / NVLinked pairs may flip the sign. Dual-3090 with PCIe
crossing between main-GPU and draft-GPU makes it worse (per Oleg's
80 → 25 tok/s observation on his own dual-GPU setup).

---

See also:
- [main repo README](../README.md) — original v1 bench + v2 UPDATE banner
- [CHANGELOG.md](../CHANGELOG.md)
- [HF discussion #14](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/discussions/14)
- original llama.cpp PR: [#19493](https://github.com/ggml-org/llama.cpp/pull/19493)
- current-master spec-decode PR: [#22227](https://github.com/ggml-org/llama.cpp/pull/22227)
