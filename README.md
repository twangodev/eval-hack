# Canh we do n LLMs Judge Hackathons?

Evaluating whether LLMs can judge hackathons in agreement with human judges.
Scraping lives in a separate repo; this one covers enrichment, pairwise
judging, Bradley-Terry ranking, and dataset publishing.

We compare three judges:

1. A large reasoning model
2. A small open-weights reasoning model
3. The small model finetuned to match the large model's preferences

Pairwise verdicts feed a Bradley-Terry model. Primary eval: top-1 agreement
with human winners on Devpost. Secondary: percentile correlation against the
private MadHacks Plackett-Luce ranking.

## Datasets

- [`twangodev/devpost-hacks`](https://huggingface.co/datasets/twangodev/devpost-hacks)
  — 2,222 projects across 9 hackathons + GitHub READMEs
- [`twangodev/devpost-hacks-judgments`](https://huggingface.co/datasets/twangodev/devpost-hacks-judgments)
  — 31,522 SFT-format pairwise judgments from Qwen3.5-27B

## Pipeline

```bash
uv sync
devpost enrich -s <hackathon>.json             # GitHub READMEs → projects parquet
devpost pairs  -c <hackathon> --n 500          # sample pairs from the HF dataset
docker compose up -d sglang-large              # Qwen3.5-27B,        port 30000
docker compose up -d sglang-small              # Qwen3-4B-Thinking,  port 30001
devpost judge  --pairs data/<h>/pairs.jsonl    # → judgments.jsonl (resumable; --base-url to pick a judge)
devpost rank   -c <hackathon>                  # → ranking.parquet + eval.json
devpost export projects | judgments            # stage for HF upload
```

External: `gh` (README fetches), Docker (SGLang).

## Authors

Manas Joshi · Oliver Ohrt · Andrew Lou · Mari Garey · George Sukhotin · Ethan Feiges · Ben Friedl · James Ding