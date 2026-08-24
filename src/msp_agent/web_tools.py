from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlparse
import ipaddress
import socket
import httpx
from bs4 import BeautifulSoup


@dataclass
class SearchResult:
    title: str
    url: str
    content: str


def search_searxng(base, query, timeout=30, limit=5):
    if not base:
        return []
    r = httpx.get(base.rstrip("/") + "/search", params={"q": query, "format": "json"}, timeout=timeout)
    r.raise_for_status()
    return [
        SearchResult(str(x.get("title", "")), str(x.get("url", "")), str(x.get("content", "")))
        for x in r.json().get("results", [])[:limit]
    ]


def private_host(host):
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except Exception:
        pass
    try:
        for info in socket.getaddrinfo(host, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return True
    except Exception:
        pass
    return False


def fetch_url(url, allow_private, timeout=30):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are supported.")
    if private_host(parsed.hostname or "") and not allow_private:
        raise PermissionError("Private/internal URL blocked by policy.")
    r = httpx.get(url, timeout=timeout, follow_redirects=True, headers={"User-Agent": "msp-ai-agent/1.1"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    return soup.get_text("\n", strip=True)[:20000]


def should_use_online(text):
    t = text.lower()
    return any(x in t for x in [
        "latest", "current", "recent", "vendor docs", "official docs",
        "microsoft docs", "cve", "release notes", "look up", "research", "verify online"
    ])


def build_research_context(base, query, allow_private, max_results, fetch_top, timeout):
    results = search_searxng(base, query, timeout, max_results)
    parts = ["ONLINE RESEARCH CONTEXT", f"Query: {query}", ""]
    for i, result in enumerate(results, 1):
        parts.append(f"Result {i}: {result.title}\nURL: {result.url}\nSnippet: {result.content}\n")
    for i, result in enumerate(results[:fetch_top], 1):
        try:
            parts.append(f"--- FETCHED PAGE {i} ---\nURL: {result.url}\n{fetch_url(result.url, allow_private, timeout)[:6000]}")
        except Exception as exc:
            parts.append(f"FETCH FAILED {result.url}: {exc}")
    return "\n".join(parts)
