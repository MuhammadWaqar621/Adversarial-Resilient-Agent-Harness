from __future__ import annotations

import os

from dotenv import load_dotenv


def load_environment() -> None:
    load_dotenv()


def get_model_name(default: str = "gpt-4.1-mini") -> str:
    return os.getenv("OPENAI_MODEL", default)

