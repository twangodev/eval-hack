# Can LLMs Judge Hackathons?

[![HF Collection](https://img.shields.io/badge/Hugging%20Face-Collection-222?logo=huggingface&logoColor=FFD21E)](https://huggingface.co/collections/twangodev/devpost-hacks)

Evaluating whether LLMs can judge hackathons in agreement with human judges.
Scraping lives in a separate repo; this one covers enrichment, pairwise
judging, Bradley-Terry ranking, and dataset publishing.

We compare five judges:

1. **Qwen3.5-27B** — large reasoning teacher
2. **Qwen3.5-4B** — small open-weights reasoning peer
3. **Qwen3-4B-Instruct-2507** — the actual base under our LoRA
4. **twangodev/devpost-hacks-qwen3-4b-judge** — our 4B finetune distilled from the 27B teacher
5. **gpt-oss-20b** — cross-family open-weights baseline

Pairwise verdicts feed a Bradley-Terry model. Primary eval: top-1 agreement
with human winners on Devpost. Secondary: percentile correlation against the
private MadHacks Plackett-Luce ranking.

## Datasets

- [`twangodev/devpost-hacks`](https://huggingface.co/datasets/twangodev/devpost-hacks)
  — 2,222 projects across 9 hackathons + GitHub READMEs
- [`twangodev/devpost-hacks-judgments`](https://huggingface.co/datasets/twangodev/devpost-hacks-judgments)
  — SFT-format pairwise judgments from each of the five judges above; row's
  `model` field disambiguates the source

## Pipeline

```bash
uv sync
devpost enrich -s <hackathon>.json             # GitHub READMEs → projects parquet
devpost pairs  -c <hackathon> --n 500          # sample pairs from the HF dataset
docker compose up -d sglang-qwen3.5-27b        # one of: sglang-qwen3.5-{27b,4b}, sglang-qwen3-4b-{2507,judge}, sglang-gpt-oss-20b
devpost judge  --pairs data/<h>/pairs.jsonl --model Qwen/Qwen3.5-27B    # resumable; matches the running service
devpost rank   -c <hackathon>                  # BT ranking + recall@K to stdout
devpost summary                                # cross-judge eval w/ bootstrap CIs and pairwise stats
devpost export projects | judgments            # stage for HF upload
```

External: `gh` (README fetches), Docker (SGLang).

## Authors

Manas Joshi · Oliver Ohrt · Andrew Lou · Mari Garey · George Sukhotin · Ethan Feiges · Ben Friedl · James Ding
