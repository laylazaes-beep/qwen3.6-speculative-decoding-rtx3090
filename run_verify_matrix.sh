#!/usr/bin/env bash
# Verification matrix — isolate cause of ngram-cache RTX 3090 regression.
# Hypotheses under test:
#   H1: -fa on interacts badly with spec-decode on SM 8.6
#   H2: -ctk q8_0 -ctv q8_0 KV quant interacts with draft verification
#   H3: 300 max_tokens too short — spec needs longer runway
#   H4: ngram-mod benefits from different N  (srogmann's 24 may not be optimal for 3090)
#
# Runs ngram-cache (worst regression in original matrix) under each hypothesis flip.

set -euo pipefail

OUT=${OUT:-"$(dirname "$0")/results/verify"}
RUNNER="$(dirname "$0")/bench_runner.py"
PY=${PY:-/home/reachym/dev/reachy-agent/robot/.venv/bin/python}
mkdir -p "$OUT"

echo "=== CONTROLS: repeat baseline + ngram-cache to confirm stability ==="
"$PY" "$RUNNER" --config baseline-rerun --gpu 1 --output "$OUT/baseline-rerun.json"
"$PY" "$RUNNER" --config ngcache-rerun  --gpu 1 --output "$OUT/ngcache-rerun.json"  --server-args '--spec-type ngram-cache'

echo "=== H1: disable flash attention ==="
"$PY" "$RUNNER" --config ngcache-nofa --gpu 1 --output "$OUT/ngcache-nofa.json" \
    --no-fa --server-args '--spec-type ngram-cache'

echo "=== H2: fp16 KV cache ==="
"$PY" "$RUNNER" --config ngcache-kv-fp16 --gpu 1 --output "$OUT/ngcache-kv-fp16.json" \
    --kv-fp16 --server-args '--spec-type ngram-cache'

echo "=== H3: longer output (1000 tok) ==="
"$PY" "$RUNNER" --config ngcache-1000tok --gpu 1 --output "$OUT/ngcache-1000tok.json" \
    --max-tokens 1000 --server-args '--spec-type ngram-cache'

echo "=== H4: ngram-mod N sweep {12, 16, 32} ==="
for N in 12 16 32; do
    "$PY" "$RUNNER" --config "ngmod-n$N" --gpu 1 --output "$OUT/ngmod-n$N.json" \
        --server-args "--spec-type ngram-mod --spec-ngram-size-n $N --draft-min 48 --draft-max 64"
done

echo ""
echo "=== VERIFY MATRIX COMPLETE ==="
ls -la "$OUT"
