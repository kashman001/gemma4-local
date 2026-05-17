"""Model id alias table and resolution."""

from time import perf_counter

import mlx.core as mx
from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_sampler

from gemma4_local.session import Metrics, Sampler

ALIASES: dict[str, str] = {
    "31b": "mlx-community/gemma-4-31B-it-OptiQ-4bit",
    "26b": "mlx-community/gemma-4-26b-a4b-it-4bit",
}


def resolve(model_id_or_alias: str) -> str:
    return ALIASES.get(model_id_or_alias, model_id_or_alias)


def run_once(
    model_id: str, prompt: str, system: str | None, sampler: Sampler
) -> Metrics:
    """Load the model, run one generation, return Metrics. Subprocess-safe: holds no module-level state so benchmark.run can fork a fresh process per model (see ADR-0001)."""
    model, tokenizer = load(model_id)
    messages: list[dict[str, str]] = []
    if system is not None:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    rendered = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=False
    )
    mlx_sampler = make_sampler(temp=sampler.temperature, top_p=sampler.top_p)

    mx.reset_peak_memory()
    tokens = 0
    t_first: float | None = None
    t_start = perf_counter()
    for chunk in stream_generate(
        model, tokenizer, rendered, max_tokens=sampler.max_tokens, sampler=mlx_sampler
    ):
        if t_first is None:
            t_first = perf_counter()
        tokens = chunk.generation_tokens
    t_end = perf_counter()
    if t_first is None:
        t_first = t_end

    ttft_ms = (t_first - t_start) * 1000
    total_wall_ms = (t_end - t_start) * 1000
    decode_tps = tokens / max(t_end - t_first, 1e-9)
    peak_mem_gb = mx.get_peak_memory() / (1024**3)

    return Metrics(
        ttft_ms=ttft_ms,
        decode_tps=decode_tps,
        total_wall_ms=total_wall_ms,
        peak_mem_gb=peak_mem_gb,
    )
