"""Local SQLite memory for explicitly saved agent notes.

This module does not automatically ingest conversations, execute retrieved
content, or provide semantic/vector search.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3
import time


@dataclass(frozen=True)
class MemoryEntry:
    id: int
    namespace: str
    content: str
    created_at: int


class LocalMemory:
    """Persistent, explicit note storage with namespace isolation.

    Do not store secrets. SQLite files are not encrypted by this module.
    """

    def __init__(self, path: str | Path, *, max_chars: int = 10000):
        if not 1 <= max_chars <= 100000:
            raise ValueError("max_chars must be between 1 and 100000")
        self.max_chars = max_chars
        self.connection = sqlite3.connect(str(path))
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS memories ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "namespace TEXT NOT NULL, content TEXT NOT NULL, "
            "created_at INTEGER NOT NULL)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_memories_namespace "
            "ON memories(namespace, id)"
        )
        self.connection.commit()

    def __enter__(self) -> "LocalMemory":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        self.connection.close()

    @staticmethod
    def _validate_namespace(namespace: str) -> None:
        if not isinstance(namespace, str) or not namespace or len(namespace) > 128:
            raise ValueError("namespace must be 1-128 characters")

    def add(self, namespace: str, content: str) -> int:
        self._validate_namespace(namespace)
        if not isinstance(content, str) or not content.strip() or len(content) > self.max_chars:
            raise ValueError("content must be nonblank and within max_chars")
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO memories(namespace, content, created_at) VALUES (?, ?, ?)",
                (namespace, content, int(time.time())),
            )
        return int(cursor.lastrowid)

    def search(self, namespace: str, query: str = "", *, limit: int = 20) -> list[MemoryEntry]:
        self._validate_namespace(namespace)
        if not isinstance(query, str) or len(query) > self.max_chars:
            raise ValueError("invalid query")
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        # instr performs literal substring matching; '%' and '_' are not wildcards.
        rows = self.connection.execute(
            "SELECT id, namespace, content, created_at FROM memories "
            "WHERE namespace = ? AND instr(lower(content), lower(?)) > 0 "
            "ORDER BY id DESC LIMIT ?",
            (namespace, query, limit),
        ).fetchall() if query else self.connection.execute(
            "SELECT id, namespace, content, created_at FROM memories "
            "WHERE namespace = ? ORDER BY id DESC LIMIT ?",
            (namespace, limit),
        ).fetchall()
        return [MemoryEntry(*row) for row in rows]

    def delete(self, namespace: str, memory_id: int) -> bool:
        self._validate_namespace(namespace)
        if not isinstance(memory_id, int) or isinstance(memory_id, bool) or memory_id <= 0:
            raise ValueError("memory_id must be a positive integer")
        with self.connection:
            cursor = self.connection.execute(
                "DELETE FROM memories WHERE namespace = ? AND id = ?",
                (namespace, memory_id),
            )
        return cursor.rowcount > 0
