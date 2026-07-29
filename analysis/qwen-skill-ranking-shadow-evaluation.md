# Qwen skill-ranking shadow evaluation

## Evidence package

The stable opt-in harness is `scripts/python/evaluation/qwen3_ollama_skill_ranking_eval.py`.
It imports the production manifest, renderer, tokenizer preflight, transport,
parser, and selection policy. Fresh bounded Q8 and Q4 synthetic runs completed
at version `2026-07-29.4`. Both profiles achieved 1.0 top-one accuracy and 1.0
precision at 0.8. Q8 recall/exact-set were 0.65/0.583, and Q4 were 0.70/0.583.
The machine-readable Q8/Q4 reports retain fixture scores, prompt hashes, token
counts, runtime identity, manifest hash, tokenizer hash, inventory hash, and
latency evidence under `analysis/evaluation/`.

The previous-task-packet smoke transformed three canonical task packets back to
drafts, ran authoritative Q8 assignment for all three, and ran Q4 on the current
backend packet. All four outputs passed schema validation without auto-fix,
retained one diagnostic record per task, preserved non-skill fields, used only
frozen-inventory names, and contained no circular owner or unusable update
factory assignments. The smoke report remains non-cutover evidence because 21
of 49 task results were forced low confidence, including all 13 proposal-format
tasks after deterministic circular-owner protection.

## Decision

**DEFER cutover.** The synthetic smoke evidence is useful for integration, but
the required owner-written numeric gates, named reviewers, independently
adjudicated real-packet corpus, and independent VRAM measurement are unresolved.
NVML remains blocked. Do not remove or bypass lexical rollback, and do not make
Qwen authoritative, until those dependencies are approved and the shadow report
passes every preregistered gate.

## Required release evidence

1. Owner records numeric top-one/exact-set/precision/recall, clipping, latency,
   and memory gates before inspecting real results.
2. Named reviewers independently label a privacy-reviewed real-packet corpus and
   resolve disagreements with recorded adjudication.
3. Q8 and explicitly selected Q4 runs report exact model, tokenizer, prompt,
   fixture/corpus, runtime, and report hashes; cold, warm, p95, and complete
   latency are retained.
4. NVML is repaired and independent peak VRAM corroborates the Ollama report.

Until then, synthetic Q8/Q4 results remain non-cutover evidence only.
