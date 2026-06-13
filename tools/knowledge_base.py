"""
Knowledge Base — Foundry IQ layer backed by Azure AI Search.

Uploads synthetic world data documents and performs semantic retrieval
to ground agent responses in campaign-specific lore.
Falls back to local file reads if Azure AI Search is unavailable.
"""

import os
from pathlib import Path
from typing import Any

from config import Config

WORLD_DATA_DIR = Path(__file__).parent.parent / "world_data"


class KnowledgeBase:
    """
    Retrieves lore from Azure AI Search (Foundry IQ equivalent).
    Gracefully falls back to local keyword search if Search is unavailable.
    """

    def __init__(self) -> None:
        self._search_client = None
        self._search_available = False
        self._local_docs: dict[str, str] = {}

        self._load_local_docs()
        if Config.has_search():
            self._init_search()

    def _load_local_docs(self) -> None:
        """Pre-load all world data markdown files for local fallback."""
        for md_file in WORLD_DATA_DIR.glob("*.md"):
            self._local_docs[md_file.stem] = md_file.read_text(encoding="utf-8")

    def _init_search(self) -> None:
        try:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential

            self._search_client = SearchClient(
                endpoint=Config.AZURE_SEARCH_ENDPOINT,
                index_name=Config.AZURE_SEARCH_INDEX_NAME,
                credential=AzureKeyCredential(Config.AZURE_SEARCH_API_KEY),
            )
            self._search_available = True
        except Exception:
            self._search_available = False

    def query(self, query_text: str, top: int = 3) -> list[dict[str, Any]]:
        """
        Retrieve relevant lore documents for the given query.
        Returns list of {source, content, score} dicts.
        """
        if self._search_available:
            return self._search_azure(query_text, top)
        return self._search_local(query_text, top)

    def _search_azure(self, query_text: str, top: int) -> list[dict[str, Any]]:
        try:
            results = self._search_client.search(
                search_text=query_text,
                top=top,
                include_total_count=False,
            )
            return [
                {
                    "source": r.get("source", "unknown"),
                    "content": r.get("content", ""),
                    "score": r.get("@search.score", 0.0),
                }
                for r in results
            ]
        except Exception:
            return self._search_local(query_text, top)

    def _search_local(self, query_text: str, top: int) -> list[dict[str, Any]]:
        """
        Simple keyword relevance scoring over local markdown files.
        Used when Azure AI Search is not available.
        """
        query_terms = set(query_text.lower().split())
        scored: list[tuple[float, str, str]] = []

        for doc_name, content in self._local_docs.items():
            content_lower = content.lower()
            score = sum(1.0 for term in query_terms if term in content_lower)
            if score > 0:
                scored.append((score, doc_name, content))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, doc_name, content in scored[:top]:
            # Return the most relevant excerpt (~1500 chars) rather than full doc
            excerpt = self._extract_excerpt(content, query_terms)
            results.append(
                {
                    "source": f"{doc_name}.md",
                    "content": excerpt,
                    "score": score,
                }
            )
        return results

    def _extract_excerpt(self, content: str, terms: set[str], window: int = 1500) -> str:
        """Find the paragraph most relevant to the query terms."""
        paragraphs = content.split("\n\n")
        best_para = content[:window]
        best_score = 0

        for para in paragraphs:
            score = sum(1 for t in terms if t in para.lower())
            if score > best_score:
                best_score = score
                best_para = para

        return best_para[:window]

    def get_document(self, doc_name: str) -> str:
        """Return the full content of a named world data document."""
        return self._local_docs.get(doc_name, "")

    def format_for_prompt(self, results: list[dict[str, Any]]) -> str:
        """Format retrieval results as a context block for an agent prompt."""
        if not results:
            return "No relevant lore retrieved."
        parts = []
        for r in results:
            parts.append(f"[Source: {r['source']}]\n{r['content']}")
        return "\n\n---\n\n".join(parts)
