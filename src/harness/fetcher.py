from __future__ import annotations

from typing import Protocol

import requests
from bs4 import BeautifulSoup

from .models import PageContent
from .security import UrlPolicy, detect_prompt_injection


class Fetcher(Protocol):
    def fetch(self, url: str) -> PageContent:
        ...


class HttpFetcher:
    def __init__(self, url_policy: UrlPolicy | None = None, timeout_seconds: float = 8.0):
        self.url_policy = url_policy or UrlPolicy()
        self.timeout_seconds = timeout_seconds

    def fetch(self, url: str) -> PageContent:
        ok, reason = self.url_policy.validate(url)
        if not ok:
            raise ValueError(f"url rejected: {reason}")
        response = requests.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        text = extract_text(response.text)
        reasons = detect_prompt_injection(text)
        return PageContent(
            url=url,
            text=text,
            suspicious=bool(reasons),
            suspicious_reasons=reasons,
        )


class InMemoryFetcher:
    def __init__(self, pages: dict[str, str], url_policy: UrlPolicy | None = None):
        self.pages = pages
        self.url_policy = url_policy or UrlPolicy()

    def fetch(self, url: str) -> PageContent:
        ok, reason = self.url_policy.validate(url)
        if not ok:
            raise ValueError(f"url rejected: {reason}")
        if url not in self.pages:
            raise KeyError(f"missing test page for {url}")
        text = self.pages[url]
        reasons = detect_prompt_injection(text)
        return PageContent(
            url=url,
            text=text,
            suspicious=bool(reasons),
            suspicious_reasons=reasons,
        )


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script", "style", "noscript"]):
        node.extract()
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())

