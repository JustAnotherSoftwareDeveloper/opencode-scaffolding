# Native Qwen shadow evaluation

This package is opt-in and outside normal tests. Run it detached with bounded
resources, dedicated logs, and an output directory, for example:

```sh
timeout --signal=TERM 30m uv run --directory scripts/python python \
  evaluation/qwen3_ollama_skill_ranking_eval.py \
  --project-root . --config-dir ~/.config/opencode \
  --model-profile q8 --output /tmp/qwen-eval/q8.json \
  > /tmp/qwen-eval/q8.log 2>&1
```

Run Q4 separately by changing only the explicit profile and output paths. Preserve
logs and JSON reports; cleanup is `rm -rf /tmp/qwen-eval` after evidence is copied.
The harness imports the production manifest, prompt, tokenizer preflight,
transport, parser, and selection policy. It does not pull models, change
application files, or run in pytest.

Reports include model/version metadata, hashes, quality, clipping, token counts,
cold load, warm mean/p95, complete-task mean/p95, and independent VRAM status.
Copy complete Q8/Q4 JSON reports into `analysis/evaluation/` before updating the
summary decision record.
The current NVML mismatch leaves independent VRAM blocked. A real shadow corpus
also requires a privacy-reviewed format, owner-written numeric quality/latency/
memory gates, named reviewers, and adjudicated labels before it can support
cutover. Until all are present, the decision is **DEFER** and lexical rollback
must remain available.
