from __future__ import annotations

import asyncio
import json
import re
import time
from pathlib import Path

from openai import AsyncOpenAI

from devpost.pairs import iter_jsonl
from devpost.prompts import JUDGE_SYSTEM, render

VERDICT_RE = re.compile(r"VERDICT\s*:\s*(A|B|TIE)\b", re.IGNORECASE)


def _parse_verdict(text: str) -> str:
    last = None
    for cand in VERDICT_RE.finditer(text):
        last = cand
    if last is None:
        return "invalid"
    v = last.group(1).upper()
    return "tie" if v == "TIE" else v


def _load_done(out: Path) -> set[str]:
    if not out.exists():
        return set()
    done: set[str] = set()
    with out.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                if jid := row.get("judgment_id"):
                    done.add(jid)
            except json.JSONDecodeError:
                continue
    return done


async def _wait_ready(client: AsyncOpenAI, timeout_s: float) -> None:
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            await client.models.list()
            return
        except Exception as e:
            last_err = e
        await asyncio.sleep(2.0)
    raise SystemExit(
        f"openai-compatible server not ready after {timeout_s:.0f}s "
        f"(last error: {last_err})\nstart it with `docker compose up -d sglang`"
    )


async def _judge_one(
    client: AsyncOpenAI,
    sem: asyncio.Semaphore,
    model: str,
    row: dict,
    sampling: dict,
) -> dict:
    messages = [
        {"role": "system", "content": JUDGE_SYSTEM},
        {"role": "user", "content": render(row["project_a"], row["project_b"])},
    ]
    async with sem:
        t0 = time.time()
        resp = await client.chat.completions.create(
            model=model,
            messages=messages,
            extra_body={"chat_template_kwargs": {"enable_thinking": True}},
            **sampling,
        )
        elapsed = time.time() - t0

    choice = resp.choices[0]
    content = choice.message.content or ""
    extra = choice.message.model_extra or {}
    reasoning = extra.get("reasoning_content") or ""
    verdict = _parse_verdict(content)
    usage = resp.usage
    output_text = (
        f"<think>{reasoning}</think>\n{content}" if reasoning else content
    )
    return {
        "judgment_id": row["judgment_id"],
        "pair_id": row["pair_id"],
        "hackathon": row.get("hackathon"),
        "position": row["position"],
        "project_a_id": row["project_a_id"],
        "project_b_id": row["project_b_id"],
        "project_a": row["project_a"],
        "project_b": row["project_b"],
        "prompt": json.dumps(messages, ensure_ascii=False),
        "output_text": output_text,
        "reasoning": reasoning,
        "answer": content.strip(),
        "verdict": verdict,
        "model": model,
        "sampling": sampling,
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "finish_reason": choice.finish_reason,
        "latency_s": elapsed,
        "created_at": time.time(),
    }


async def _run_async(
    client: AsyncOpenAI,
    model: str,
    todo: list[dict],
    sampling: dict,
    concurrency: int,
    out_path: Path,
) -> int:
    sem = asyncio.Semaphore(concurrency)
    written = 0
    completed = 0
    total = len(todo)
    t_start = time.time()
    with out_path.open("a") as f:
        tasks = [
            asyncio.create_task(_judge_one(client, sem, model, row, sampling))
            for row in todo
        ]
        for fut in asyncio.as_completed(tasks):
            try:
                rec = await fut
            except Exception as e:
                print(f"  request failed: {e}")
                completed += 1
                continue
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            written += 1
            completed += 1
            if completed % 5 == 0 or completed == total:
                rate = completed / max(time.time() - t_start, 1e-3)
                print(f"  {completed}/{total} done ({rate:.2f} req/s)")
    return written


def run(
    pairs_path: Path,
    out: Path,
    model: str,
    base_url: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
    seed: int,
    limit: int | None,
    resume: bool,
    concurrency: int,
    wait_ready_s: float,
) -> int:
    todo: list[dict] = list(iter_jsonl(pairs_path))
    if resume:
        done = _load_done(out)
        if done:
            print(f"resume: skipping {len(done)} already-judged rows")
            todo = [r for r in todo if r["judgment_id"] not in done]
    if limit is not None:
        todo = todo[:limit]
    if not todo:
        print("nothing to judge")
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    sampling = {
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }

    async def main() -> int:
        client = AsyncOpenAI(
            base_url=f"{base_url}/v1",
            api_key="EMPTY",
            timeout=600.0,
        )
        try:
            print(f"checking server at {base_url} ...")
            await _wait_ready(client, wait_ready_s)
            print("server ready")
            print(
                f"judging {len(todo)} rows "
                f"(model={model}, concurrency={concurrency})"
            )
            return await _run_async(
                client, model, todo, sampling, concurrency, out
            )
        finally:
            await client.close()

    return asyncio.run(main())
