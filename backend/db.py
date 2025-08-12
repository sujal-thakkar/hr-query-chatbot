"""
Simple SQLite storage for employees with JSON fallback.

Schema:
  employees(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    skills TEXT NOT NULL,         -- JSON-encoded list[str]
    experience_years INTEGER NOT NULL,
    projects TEXT NOT NULL,       -- JSON-encoded list[str]
    availability TEXT NOT NULL
  )
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # isolation_level=None for autocommit-like behavior when needed
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
        """Initialize database schema (employees + meta)."""
        with _connect(db_path) as conn:
                try:  # concurrency pragmas (best-effort)
                        conn.execute("PRAGMA journal_mode=WAL;")
                        conn.execute("PRAGMA synchronous=NORMAL;")
                except Exception:
                        pass
                conn.execute(
                        """
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    skills TEXT NOT NULL,
    experience_years INTEGER NOT NULL,
    projects TEXT NOT NULL,
    availability TEXT NOT NULL
)
"""
                )
                conn.execute(
                        """
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
)
"""
                )


def _count_employees(conn: sqlite3.Connection) -> int:
    cur = conn.execute("SELECT COUNT(1) AS c FROM employees")
    row = cur.fetchone()
    return int(row[0]) if row else 0


def upsert_employees(db_path: Path, employees: List[Dict[str, Any]]) -> None:
    with _connect(db_path) as conn:
        # Use INSERT OR REPLACE to be idempotent
        conn.executemany(
            """
            INSERT OR REPLACE INTO employees (id, name, skills, experience_years, projects, availability)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    e.get("id"),
                    e.get("name"),
                    json.dumps(e.get("skills", [])),
                    int(e.get("experience_years", 0)),
                    json.dumps(e.get("projects", [])),
                    e.get("availability", "available"),
                )
                for e in employees
            ],
        )


def load_employees_from_db(db_path: Path) -> List[Dict[str, Any]]:
    with _connect(db_path) as conn:
        cur = conn.execute(
            "SELECT id, name, skills, experience_years, projects, availability FROM employees ORDER BY id"
        )
        rows = cur.fetchall()
        result: List[Dict[str, Any]] = []
        for r in rows:
            result.append(
                {
                    "id": r["id"],
                    "name": r["name"],
                    "skills": json.loads(r["skills"]) if r["skills"] else [],
                    "experience_years": int(r["experience_years"]),
                    "projects": json.loads(r["projects"]) if r["projects"] else [],
                    "availability": r["availability"],
                }
            )
        return result


essure_msg = ""  # placeholder for potential use


def ensure_db_with_data(db_path: Path, json_path: Path) -> None:
    """Ensure the SQLite DB exists and is populated; seed from JSON if empty.

    Args:
        db_path: target SQLite database path
        json_path: employees.json file path to seed from when DB is empty
    """
    db_path = Path(db_path)
    init_db(db_path)
    with _connect(db_path) as conn:
        # Sentinel check in meta table to ensure seeding runs only once across workers
        try:
            seeded = conn.execute("SELECT value FROM meta WHERE key='seeded'").fetchone()
        except Exception:
            seeded = None
        if not seeded and _count_employees(conn) == 0 and Path(json_path).exists():
            try:
                conn.execute("BEGIN IMMEDIATE")
            except Exception:
                pass
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                employees = data.get("employees", []) if isinstance(data, dict) else []
                conn.executemany(
                    """
                    INSERT OR IGNORE INTO employees (id, name, skills, experience_years, projects, availability)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            e.get("id"),
                            e.get("name"),
                            json.dumps(e.get("skills", [])),
                            int(e.get("experience_years", 0)),
                            json.dumps(e.get("projects", [])),
                            e.get("availability", "available"),
                        )
                        for e in employees
                    ],
                )
                conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('seeded', '1')")
            finally:
                try:
                    conn.execute("COMMIT")
                except Exception:
                    pass
