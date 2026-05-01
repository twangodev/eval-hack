from __future__ import annotations

import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from devpost.pairs import iter_jsonl
from devpost.prompts import JUDGE_SYSTEM, render


def _ground_truth(project: dict | None) -> str:
    return ((project or {}).get("results")) or "Unknown"


def _assistant_content(reasoning: str, answer: str) -> str:
    if reasoning:
        return f"<think>{reasoning}</think>\n{answer}".rstrip()
    return answer.rstrip()


def _build_row(j: dict) -> dict:
    user_msg = render(j["project_a"], j["project_b"])
    messages = [
        {"role": "system", "content": JUDGE_SYSTEM},
        {"role": "user", "content": user_msg},
        {
            "role": "assistant",
            "content": _assistant_content(
                j.get("reasoning") or "", j.get("answer") or ""
            ),
        },
    ]
    return {
        "messages": messages,
        "judgment_id": j["judgment_id"],
        "pair_id": j["pair_id"],
        "hackathon": j.get("hackathon"),
        "position": j["position"],
        "project_a_id": j["project_a_id"],
        "project_b_id": j["project_b_id"],
        "verdict": j["verdict"],
        "gt_a_result": _ground_truth(j.get("project_a")),
        "gt_b_result": _ground_truth(j.get("project_b")),
        "model": j["model"],
        "prompt_tokens": j.get("prompt_tokens"),
        "completion_tokens": j.get("completion_tokens"),
        "finish_reason": j.get("finish_reason"),
        "latency_s": j.get("latency_s"),
        "sampling": json.dumps(j.get("sampling") or {}, ensure_ascii=False),
    }


def run(judgments_path: Path, out_dir: Path) -> int:
    judgments = list(iter_jsonl(judgments_path))
    if not judgments:
        raise SystemExit(f"no judgments in {judgments_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [_build_row(j) for j in judgments]

    schema = pa.schema(
        [
            (
                "messages",
                pa.list_(
                    pa.struct(
                        [
                            ("role", pa.string()),
                            ("content", pa.string()),
                        ]
                    )
                ),
            ),
            ("judgment_id", pa.string()),
            ("pair_id", pa.string()),
            ("hackathon", pa.string()),
            ("position", pa.string()),
            ("project_a_id", pa.string()),
            ("project_b_id", pa.string()),
            ("verdict", pa.string()),
            ("gt_a_result", pa.string()),
            ("gt_b_result", pa.string()),
            ("model", pa.string()),
            ("prompt_tokens", pa.int64()),
            ("completion_tokens", pa.int64()),
            ("finish_reason", pa.string()),
            ("latency_s", pa.float64()),
            ("sampling", pa.string()),
        ]
    )
    table = pa.Table.from_pylist(rows, schema=schema)
    pq.write_table(table, out_dir / "train.parquet", compression="zstd")
    return len(rows)
