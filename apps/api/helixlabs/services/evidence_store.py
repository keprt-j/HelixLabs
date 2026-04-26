from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class EvidenceStore:
    def __init__(self, store_dir: Path | None = None) -> None:
        self._store_dir = store_dir or (Path(__file__).resolve().parents[4] / "data" / "runtime" / "evidence")
        self._store_dir.mkdir(parents=True, exist_ok=True)

    def ingest(self, run_id: str, studies: list[dict[str, Any]], user_goal: str) -> dict[str, Any]:
        docs: list[dict[str, Any]] = []
        chunks: list[dict[str, Any]] = []
        chunk_counter = 0
        for idx, study in enumerate(studies):
            doc_id = f"doc_{idx + 1}"
            text = str(study.get("_evidence_text") or study.get("abstract") or "").strip()
            if not text:
                continue
            title = str(study.get("title", "")).strip()
            doi = str(study.get("doi", "")).strip()
            source_url = str(study.get("url", "")).strip()
            evidence_level = str(study.get("evidence_level", "abstract"))
            doc = {
                "doc_id": doc_id,
                "title": title,
                "doi": doi,
                "url": source_url,
                "evidence_level": evidence_level,
                "year": study.get("year"),
            }
            docs.append(doc)
            for chunk_text in self._chunk_text(text):
                chunk_counter += 1
                chunk_id = f"chunk_{chunk_counter}"
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "doc_id": doc_id,
                        "text": chunk_text,
                        "tokens": sorted(self._tokens(chunk_text)),
                    }
                )

        payload = {
            "run_id": run_id,
            "goal": user_goal,
            "docs": docs,
            "chunks": chunks,
        }
        persisted = True
        try:
            self._path(run_id).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError:
            persisted = False
        return {
            "doc_count": len(docs),
            "chunk_count": len(chunks),
            "path": str(self._path(run_id)),
            "persisted": persisted,
        }

    def retrieve(self, run_id: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        payload = self._load(run_id)
        if payload is None:
            return []
        query_tokens = self._tokens(query)
        if not query_tokens:
            return []
        doc_by_id = {d.get("doc_id"): d for d in payload.get("docs", [])}
        scored: list[dict[str, Any]] = []
        for chunk in payload.get("chunks", []):
            chunk_tokens = set(chunk.get("tokens") or [])
            if not chunk_tokens:
                continue
            overlap = len(query_tokens & chunk_tokens)
            if overlap <= 0:
                continue
            score = overlap / max(3, min(20, len(query_tokens)))
            score += 0.08 if "fulltext" in str((doc_by_id.get(chunk.get("doc_id")) or {}).get("evidence_level", "")) else 0.0
            doc = doc_by_id.get(chunk.get("doc_id")) or {}
            scored.append(
                {
                    "score": round(score, 4),
                    "doc_id": chunk.get("doc_id"),
                    "chunk_id": chunk.get("chunk_id"),
                    "title": doc.get("title"),
                    "doi": doc.get("doi"),
                    "url": doc.get("url"),
                    "evidence_level": doc.get("evidence_level"),
                    "text": str(chunk.get("text", ""))[:400],
                }
            )
        scored.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)
        limit = max(1, min(20, top_k))
        if scored:
            return scored[:limit]
        # Fallback retrieval when lexical overlap is weak: return recent chunks
        fallback: list[dict[str, Any]] = []
        for chunk in payload.get("chunks", [])[:limit]:
            doc = doc_by_id.get(chunk.get("doc_id")) or {}
            fallback.append(
                {
                    "score": 0.01,
                    "doc_id": chunk.get("doc_id"),
                    "chunk_id": chunk.get("chunk_id"),
                    "title": doc.get("title"),
                    "doi": doc.get("doi"),
                    "url": doc.get("url"),
                    "evidence_level": doc.get("evidence_level"),
                    "text": str(chunk.get("text", ""))[:400],
                }
            )
        return fallback

    def claim_citations(self, run_id: str, claims: dict[str, str], top_k: int = 2) -> dict[str, list[dict[str, Any]]]:
        out: dict[str, list[dict[str, Any]]] = {}
        for key, claim in claims.items():
            refs = self.retrieve(run_id=run_id, query=claim, top_k=top_k)
            out[key] = [
                {
                    "doc_id": r.get("doc_id"),
                    "chunk_id": r.get("chunk_id"),
                    "title": r.get("title"),
                    "doi": r.get("doi"),
                    "score": r.get("score"),
                    "evidence_level": r.get("evidence_level"),
                }
                for r in refs
            ]
        return out

    def _path(self, run_id: str) -> Path:
        return self._store_dir / f"{run_id}.json"

    def _load(self, run_id: str) -> dict[str, Any] | None:
        p = self._path(run_id)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None

    @staticmethod
    def _tokens(text: str) -> set[str]:
        tokens = set(re.findall(r"[a-zA-Z0-9]{3,}", text.lower()))
        stop = {"with", "from", "that", "this", "were", "have", "their", "into", "using", "study", "based"}
        return {t for t in tokens if t not in stop}

    @staticmethod
    def _chunk_text(text: str, max_chars: int = 500) -> list[str]:
        clean = re.sub(r"\s+", " ", text).strip()
        if not clean:
            return []
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean) if s.strip()]
        if not sentences:
            return [clean[:max_chars]]
        chunks: list[str] = []
        current = ""
        for sent in sentences:
            if len(current) + len(sent) + 1 <= max_chars:
                current = f"{current} {sent}".strip()
                continue
            if current:
                chunks.append(current)
            current = sent
        if current:
            chunks.append(current)
        return chunks
