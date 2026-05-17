"""Default values consumed across the package. CLI flags override these."""

DEFAULTS = {
    "model_id": "mlx-community/gemma-4-31B-it-OptiQ-4bit",
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 2048,
    "sessions_dir": "./sessions",
}
