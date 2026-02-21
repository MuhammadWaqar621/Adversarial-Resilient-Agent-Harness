from __future__ import annotations

import json

import streamlit as st

from harness.agent import AgentConfig, ResearchAgent
from harness.config import load_environment
from harness.fetcher import HttpFetcher
from harness.llm import OpenAILLMClient


def run_agent(goal: str, urls_text: str, mode: str) -> dict:
    urls = [line.strip() for line in urls_text.splitlines() if line.strip()]
    if not urls:
        raise ValueError("Please provide at least one URL.")
    agent = ResearchAgent(
        fetcher=HttpFetcher(),
        llm=OpenAILLMClient(),
        config=AgentConfig(mode=mode),
    )
    result = agent.run(goal=goal, urls=urls)
    return {
        "goal": result.goal,
        "summary": result.summary,
        "key_points": result.key_points,
        "citations": result.citations,
        "blocked_urls": result.blocked_urls,
        "notes": result.notes,
    }


def main() -> None:
    load_environment()
    st.set_page_config(page_title="Research Agent Harness", layout="wide")
    st.title("Adversarial-Resilient Research Agent")
    st.caption("Interactive frontend for testing defended vs vulnerable behavior")

    with st.sidebar:
        mode = st.selectbox("Mode", ["defended", "vulnerable"], index=0)
        st.markdown("Add one URL per line.")

    goal = st.text_input(
        "Research Goal",
        value="Compare prompt-injection defenses for LLM-powered research agents",
    )
    urls_text = st.text_area(
        "Source URLs",
        value="https://example.com",
        height=180,
    )

    if st.button("Run Research"):
        with st.spinner("Running agent..."):
            try:
                payload = run_agent(goal, urls_text, mode)
            except Exception as exc:
                st.error(str(exc))
                return
        st.subheader("Structured Result")
        st.json(payload, expanded=True)
        st.download_button(
            "Download JSON",
            data=json.dumps(payload, indent=2),
            file_name="research_result.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()

