from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass
from typing import List
from urllib.parse import urlparse


PROMPT_INJECTION_PATTERNS = [
    r"ignore (all|previous|prior) instructions",
    r"system prompt",
    r"developer message",
    r"call tool",
    r"fetch .*https?://",
    r"exfiltrate",
    r"secret",
    r"api key",
]


@dataclass
class UrlPolicy:
    allowed_schemes: tuple[str, ...] = ("http", "https")
    deny_local_networks: bool = True

    def validate(self, url: str) -> tuple[bool, str]:
        parsed = urlparse(url)
        if parsed.scheme not in self.allowed_schemes:
            return False, f"blocked scheme: {parsed.scheme}"
        if not parsed.netloc:
            return False, "missing host"
        if self.deny_local_networks and self._is_local(parsed.hostname):
            return False, "blocked local/private host"
        return True, "ok"

    def _is_local(self, hostname: str | None) -> bool:
        if not hostname:
            return True
        lowered = hostname.lower()
        if lowered in {"localhost", "127.0.0.1", "::1"}:
            return True
        try:
            ip = ipaddress.ip_address(lowered)
            return ip.is_private or ip.is_loopback or ip.is_link_local
        except ValueError:
            pass
        try:
            infos = socket.getaddrinfo(hostname, None)
        except OSError:
            return False
        for info in infos:
            address = info[4][0]
            ip = ipaddress.ip_address(address)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return True
        return False


def detect_prompt_injection(text: str) -> List[str]:
    found = []
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(pattern)
    return found


def redact_sensitive_text(value: str, goal: str) -> str:
    redacted = value.replace(goal, "[REDACTED_GOAL]")
    redacted = re.sub(r"sk-[A-Za-z0-9_-]{20,}", "[REDACTED_KEY]", redacted)
    return redacted
