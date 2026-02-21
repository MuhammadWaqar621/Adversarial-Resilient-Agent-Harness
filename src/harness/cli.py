from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import AgentConfig, ResearchAgent
from .config import load_environment
from .fetcher import HttpFetcher
from .llm import OpenAILLMClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Adversarial-resilient research agent harness")
    parser.add_argument("--goal", required=True, help="Research goal")
    parser.add_argument("--urls", nargs="+", required=True, help="One or more source URLs")
    parser.add_argument(
        "--mode",
        choices=["defended", "vulnerable"],
        default="defended",
        help="Harness mode for comparison",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional JSON output file path",
    )
    return parser.parse_args()


def main() -> None:
    load_environment()
    args = parse_args()
    agent = ResearchAgent(
        fetcher=HttpFetcher(),
        llm=OpenAILLMClient(),
        config=AgentConfig(mode=args.mode),
    )
    result = agent.run(goal=args.goal, urls=args.urls)
    payload = {
        "goal": result.goal,
        "summary": result.summary,
        "key_points": result.key_points,
        "citations": result.citations,
        "blocked_urls": result.blocked_urls,
        "notes": result.notes,
    }
    text = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
