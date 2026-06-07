from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from backend.app.models import Article, Briefing, BriefingProfile, BriefingProfileInput


SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    published_at TEXT,
    description TEXT,
    topic TEXT,
    priority_score INTEGER DEFAULT 0,
    priority_label TEXT,
    priority_reason TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS briefings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sources TEXT NOT NULL,
    topics TEXT NOT NULL,
    date_range TEXT NOT NULL,
    result_json TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS briefing_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sources TEXT NOT NULL,
    topics TEXT NOT NULL,
    custom_keywords TEXT NOT NULL,
    exclude_keywords TEXT NOT NULL,
    date_range TEXT NOT NULL,
    limit_count INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


class Repository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def init(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)
            self._ensure_article_columns(connection)

    def _ensure_article_columns(self, connection: sqlite3.Connection) -> None:
        rows = connection.execute("PRAGMA table_info(articles)").fetchall()
        existing_columns = {row["name"] for row in rows}
        migrations = {
            "priority_score": "ALTER TABLE articles ADD COLUMN priority_score INTEGER DEFAULT 0",
            "priority_label": "ALTER TABLE articles ADD COLUMN priority_label TEXT",
            "priority_reason": "ALTER TABLE articles ADD COLUMN priority_reason TEXT",
        }
        for column_name, statement in migrations.items():
            if column_name not in existing_columns:
                connection.execute(statement)

    def save_articles(self, articles: list[Article]) -> None:
        with self.connect() as connection:
            connection.executemany(
                """
                INSERT OR IGNORE INTO articles
                    (title, source, url, published_at, description, topic, priority_score, priority_label, priority_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        article.title,
                        article.source,
                        str(article.url),
                        article.published_at,
                        article.description,
                        article.topic,
                        article.priority_score,
                        article.priority_label,
                        article.priority_reason,
                    )
                    for article in articles
                ],
            )

    def save_briefing(
        self,
        *,
        sources: list[str],
        topics: list[str],
        date_range: str,
        briefing: Briefing,
    ) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO briefings (sources, topics, date_range, result_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    json.dumps(sources, ensure_ascii=False),
                    json.dumps(topics, ensure_ascii=False),
                    date_range,
                    briefing.model_dump_json(),
                ),
            )

    def log_api(self, provider: str, status: str, message: str | None = None) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO api_logs (provider, status, message) VALUES (?, ?, ?)",
                (provider, status, message),
            )

    def latest_briefings(self, limit: int = 5) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, sources, topics, date_range, result_json, created_at
                FROM briefings
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_briefing(self, briefing_id: int) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT id, sources, topics, date_range, result_json, created_at
                FROM briefings
                WHERE id = ?
                """,
                (briefing_id,),
            ).fetchone()
        return dict(row) if row else None

    def save_profile(self, profile: BriefingProfileInput) -> BriefingProfile:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO briefing_profiles
                    (name, sources, topics, custom_keywords, exclude_keywords, date_range, limit_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.name.strip(),
                    json.dumps(profile.sources, ensure_ascii=False),
                    json.dumps(profile.topics, ensure_ascii=False),
                    json.dumps(profile.custom_keywords, ensure_ascii=False),
                    json.dumps(profile.exclude_keywords, ensure_ascii=False),
                    profile.date_range,
                    profile.limit,
                ),
            )
            row = connection.execute(
                "SELECT * FROM briefing_profiles WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return self._profile_from_row(row)

    def list_profiles(self) -> list[BriefingProfile]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM briefing_profiles
                ORDER BY id DESC
                """
            ).fetchall()
        return [self._profile_from_row(row) for row in rows]

    def delete_profile(self, profile_id: int) -> bool:
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM briefing_profiles WHERE id = ?", (profile_id,))
        return cursor.rowcount > 0

    def _profile_from_row(self, row: sqlite3.Row) -> BriefingProfile:
        return BriefingProfile(
            id=row["id"],
            name=row["name"],
            sources=json.loads(row["sources"]),
            topics=json.loads(row["topics"]),
            custom_keywords=json.loads(row["custom_keywords"]),
            exclude_keywords=json.loads(row["exclude_keywords"]),
            date_range=row["date_range"],
            limit=row["limit_count"],
            created_at=row["created_at"],
        )
