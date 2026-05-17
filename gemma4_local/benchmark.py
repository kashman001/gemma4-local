"""Benchmark orchestration: one subprocess per model (see ADR-0001)."""

import multiprocessing as mp
import queue as _queue
from pathlib import Path

from gemma4_local.model import run_once
from gemma4_local.session import Metrics, Sampler


def _worker(
    model_id: str,
    prompt: str,
    system: str | None,
    sampler: Sampler,
    result_queue: mp.Queue,
) -> None:
    try:
        metrics = run_once(model_id, prompt, system, sampler)
        result_queue.put(("ok", metrics))
    except BaseException as e:
        result_queue.put(("error", f"{type(e).__name__}: {e}"))


def _format_table(results: list[tuple[str, str, Metrics | str]]) -> str:
    successes = [(mid, m) for mid, status, m in results if status == "ok"]
    failures = [(mid, msg) for mid, status, msg in results if status == "error"]

    lines = [
        "| model | TTFT (ms) | decode (tok/s) | total (ms) | peak mem (GB) |",
        "|---|---|---|---|---|",
    ]
    for mid, m in successes:
        lines.append(
            f"| {mid} | {m.ttft_ms:.1f} | {m.decode_tps:.1f} | {m.total_wall_ms:.1f} | {m.peak_mem_gb:.2f} |"
        )

    if failures:
        lines.append("")
        lines.append("failed:")
        for mid, msg in failures:
            lines.append(f"- {mid}: {msg}")

    return "\n".join(lines) + "\n"


def run(
    prompt: str,
    model_ids: list[str],
    system: str | None,
    sampler: Sampler,
    out_path: Path | None,
) -> None:
    ctx = mp.get_context("spawn")
    results: list[tuple[str, str, Metrics | str]] = []

    for model_id in model_ids:
        result_queue = ctx.Queue()
        process = ctx.Process(
            target=_worker, args=(model_id, prompt, system, sampler, result_queue)
        )
        print(f"[bench] running {model_id} ...", flush=True)
        process.start()
        process.join()
        try:
            status, payload = result_queue.get(timeout=0.5)
            results.append((model_id, status, payload))
        except _queue.Empty:
            results.append(
                (model_id, "error", f"subprocess died (exitcode={process.exitcode})")
            )

    table = _format_table(results)
    print(table, end="")
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(table)
        print(f"[bench] wrote {out_path}", flush=True)
