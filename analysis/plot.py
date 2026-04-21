"""Plot spec-decode bench results.

Reads every *.json under results/ and results/verify/ produced by bench_runner.py,
and emits:
    analysis/plot_mean_by_config.png    — mean tok/s per config (sorted)
    analysis/plot_per_prompt.png        — per-prompt heatmap
    analysis/plot_accept_vs_speed.png   — draft accept rate vs decode rate scatter
    analysis/summary.csv                — all numbers, for the repo

Run: python analysis/plot.py  (from repo root)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULT_DIRS = [ROOT / "results", ROOT / "results/verify"]
OUT_DIR = ROOT / "analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_all() -> pd.DataFrame:
    rows = []
    for d in RESULT_DIRS:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            try:
                obj = json.loads(f.read_text())
            except Exception as e:
                print(f"  skip {f}: {e}", file=sys.stderr)
                continue
            config = obj.get("config", f.stem)
            meta = obj.get("meta", {}) or {}
            for r in obj.get("rows", []):
                rows.append({
                    "config":        config,
                    "source_file":   f.name,
                    "prompt":        r.get("tag"),
                    "tok_s":         r.get("predicted_per_second", 0),
                    "wall_ms":       r.get("wall_ms", 0),
                    "predicted_ms":  r.get("predicted_ms", 0),
                    "predicted_n":   r.get("predicted_n", 0),
                    "prompt_n":      r.get("prompt_tokens", 0),
                    "draft_n":       r.get("draft_n", 0),
                    "draft_acc":     r.get("draft_n_accepted", 0),
                    "max_tokens":    meta.get("max_tokens", 300),
                    "fa":            meta.get("fa", True),
                    "kv_q8":         meta.get("kv_q8", True),
                    "commit":        obj.get("llama_cpp_commit", "?"),
                })
    return pd.DataFrame(rows)


def plot_mean_by_config(df: pd.DataFrame):
    if df.empty: return
    agg = (df.groupby("config")["tok_s"]
             .agg(["mean", "min", "max", "std", "count"])
             .sort_values("mean", ascending=True))
    fig, ax = plt.subplots(figsize=(10, max(4, 0.4 * len(agg))))
    colors = ["#d62728" if m < 130 else "#ff7f0e" if m < 140 else "#2ca02c"
              for m in agg["mean"]]
    ax.barh(agg.index, agg["mean"], xerr=agg["std"], color=colors, alpha=0.85)
    for i, (cfg, row) in enumerate(agg.iterrows()):
        ax.text(row["mean"] + 2, i, f"{row['mean']:.1f} (±{row['std']:.1f})",
                va="center", fontsize=9)
    ax.axvline(x=107, color="gray", linestyle="--", linewidth=1, label="Ollama Q4_K_M (107 tok/s)")
    ax.set_xlabel("Decode speed (tokens / second)")
    ax.set_title("Qwen3.6-35B-A3B UD-Q4_K_XL on RTX 3090 (single GPU, batch=1)")
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "plot_mean_by_config.png", dpi=140)
    plt.close()
    print(f"  wrote {OUT_DIR / 'plot_mean_by_config.png'}")


def plot_per_prompt_heatmap(df: pd.DataFrame):
    if df.empty: return
    pivot = df.pivot_table(index="config", columns="prompt", values="tok_s", aggfunc="mean")
    # order prompts consistently
    preferred = ["short_greet", "short_q", "medium_chat", "medium_rec",
                 "reasoning", "long_explain", "code_small",
                 "multi_turn_1", "multi_turn_2", "zh_cn"]
    cols = [c for c in preferred if c in pivot.columns] + \
           [c for c in pivot.columns if c not in preferred]
    pivot = pivot[cols]
    fig, ax = plt.subplots(figsize=(max(8, 0.8 * len(cols)), max(4, 0.3 * len(pivot))))
    im = ax.imshow(pivot.values, cmap="RdYlGn", vmin=60, vmax=145, aspect="auto")
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=30, ha="right")
    ax.set_yticks(range(len(pivot.index))); ax.set_yticklabels(pivot.index)
    for i in range(len(pivot.index)):
        for j in range(len(cols)):
            v = pivot.values[i, j]
            if np.isnan(v): continue
            ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                    color="black" if v > 100 else "white", fontsize=8)
    plt.colorbar(im, ax=ax, label="tok / s")
    ax.set_title("Decode speed per prompt × config")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "plot_per_prompt.png", dpi=140)
    plt.close()
    print(f"  wrote {OUT_DIR / 'plot_per_prompt.png'}")


def plot_accept_vs_speed(df: pd.DataFrame):
    with_draft = df[df["draft_n"] > 0].copy()
    if with_draft.empty:
        print("  no draft stats, skip accept-vs-speed plot")
        return
    with_draft["accept_rate"] = with_draft["draft_acc"] / with_draft["draft_n"].clip(lower=1)
    fig, ax = plt.subplots(figsize=(8, 6))
    for cfg, sub in with_draft.groupby("config"):
        ax.scatter(sub["accept_rate"] * 100, sub["tok_s"], label=cfg, s=60, alpha=0.7)
    ax.axhline(y=135.7, color="gray", linestyle="--", label="baseline 135.7 tok/s")
    ax.set_xlabel("Draft acceptance rate (%)")
    ax.set_ylabel("Decode speed (tok / s)")
    ax.set_title("Anomaly: 100% acceptance does not imply speedup on MoE")
    ax.legend(fontsize=8, loc="lower left")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "plot_accept_vs_speed.png", dpi=140)
    plt.close()
    print(f"  wrote {OUT_DIR / 'plot_accept_vs_speed.png'}")


def write_summary_csv(df: pd.DataFrame):
    if df.empty: return
    df.to_csv(OUT_DIR / "summary.csv", index=False)
    print(f"  wrote {OUT_DIR / 'summary.csv'}")
    # Aggregated
    agg = (df.groupby("config")
             .agg(mean_tok_s=("tok_s", "mean"),
                  min_tok_s=("tok_s", "min"),
                  max_tok_s=("tok_s", "max"),
                  std_tok_s=("tok_s", "std"),
                  runs=("tok_s", "count"),
                  total_draft=("draft_n", "sum"),
                  total_accept=("draft_acc", "sum"))
             .sort_values("mean_tok_s", ascending=False))
    agg["accept_rate_pct"] = np.where(agg["total_draft"] > 0,
                                       100 * agg["total_accept"] / agg["total_draft"].clip(lower=1),
                                       np.nan)
    agg.to_csv(OUT_DIR / "summary_by_config.csv")
    print(f"  wrote {OUT_DIR / 'summary_by_config.csv'}")
    print("\n=== SUMMARY BY CONFIG ===")
    print(agg.to_string(float_format=lambda x: f"{x:.1f}" if not np.isnan(x) else "-"))


if __name__ == "__main__":
    df = load_all()
    print(f"loaded {len(df)} rows from {df['config'].nunique()} configs")
    plot_mean_by_config(df)
    plot_per_prompt_heatmap(df)
    plot_accept_vs_speed(df)
    write_summary_csv(df)
