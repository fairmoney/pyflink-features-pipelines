import os


def run_slow_tests() -> bool:
    return os.getenv("ENV_VAR", "False").lower() in ("true", "1", "t")
