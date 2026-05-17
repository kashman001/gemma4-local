# Subprocess-per-model in benchmark mode

`benchmark.run` spawns one subprocess per model (via `multiprocessing` with the `spawn` start method) rather than loading both models in the same process and switching between them. Each subprocess loads its model, runs the prompt, prints a JSON line of Metrics to stdout, and exits.

## Why

`mlx.metal.get_peak_memory()` is a process-wide high-water mark. If models A and B are loaded in the same process, the reported peak for B is `max(peak_A, peak_B)` — the metric becomes meaningless as a comparison. The same applies to `get_active_memory()`. Calling `reset_peak_memory()` between models doesn't fully isolate them either, because allocator fragmentation and cache state from the prior model persists.

A fresh subprocess gives each model a clean Metal allocator and a meaningful peak-memory number.

## Trade-off accepted

~30s of additional load time per model in a comparison run (one full cold model load instead of an in-process swap). For a 4-model run that's ~2 minutes of pure loading. A benchmark that produces wrong numbers faster is worse than a slower benchmark that produces right ones.

## Consequence for the package API

`gemma4_local.model.run_once(model_id, prompt, system, sampler) -> Metrics` must be subprocess-safe: no module-level mutable state, no shared loaded model, no caching of tokenizers across calls. The function is allowed to assume it owns the process.
