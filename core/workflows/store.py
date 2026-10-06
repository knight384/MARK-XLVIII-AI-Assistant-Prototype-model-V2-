import json
import sqlite3
import threading
from typing import List, Optional, Dict, Any
from pathlib import Path
from core.workflows.models import (
    WorkflowDefinition, WorkflowRun, WorkflowStepRun, WorkflowEvent,
    WorkflowState, StepState, EventType
)
from core.observability import registry
import time
import asyncio
import contextlib

@contextlib.contextmanager
def track_sqlite(operation: str):
    start = time.perf_counter()
    try:
        yield
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e).lower() or "busy" in str(e).lower():
            # Fire and forget update
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(registry.inc("sqlite_contention_errors"))
            except RuntimeError:
                pass
        raise
    finally:
        duration = time.perf_counter() - start
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(registry.observe(f"sqlite_duration_{operation}", duration))
        except RuntimeError:
            pass

class WorkflowStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(
                self.db_path,
                timeout=10.0,
                isolation_level=None  # We handle transactions explicitly
            )
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self):
        conn = self._get_conn()
        conn.execute("BEGIN")
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS workflow_defs (
                    workflow_id TEXT PRIMARY KEY,
                    version INTEGER,
                    name TEXT,
                    enabled BOOLEAN,
                    data TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS workflow_runs (
                    run_id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    state TEXT,
                    created_at REAL,
                    data TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS workflow_step_runs (
                    step_run_id TEXT PRIMARY KEY,
                    workflow_run_id TEXT,
                    step_id TEXT,
                    state TEXT,
                    created_at REAL,
                    data TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS outbox_events (
                    event_id TEXT PRIMARY KEY,
                    run_id TEXT,
                    event_type TEXT,
                    created_at REAL,
                    data TEXT
                )
            ''')
            # Indexes for faster recovery/lookup
            conn.execute("CREATE INDEX IF NOT EXISTS idx_wruns_state ON workflow_runs(state)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_wsteps_run_id ON workflow_step_runs(workflow_run_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_wsteps_state ON workflow_step_runs(state)")
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

    # Defs
    def save_workflow_def(self, wf: WorkflowDefinition):
        with track_sqlite("write"):
            conn = self._get_conn()
            conn.execute("BEGIN")
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO workflow_defs (workflow_id, version, name, enabled, data) VALUES (?, ?, ?, ?, ?)",
                    (wf.workflow_id, wf.version, wf.name, wf.enabled, wf.model_dump_json())
                )
                conn.execute("COMMIT")
            except:
                conn.execute("ROLLBACK")
                raise

    def get_workflow_def(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        with track_sqlite("read"):
            row = self._get_conn().execute("SELECT data FROM workflow_defs WHERE workflow_id = ?", (workflow_id,)).fetchone()
            return WorkflowDefinition.model_validate_json(row["data"]) if row else None

    # Runs
    def save_run(self, run: WorkflowRun, outbox_events: List[WorkflowEvent] = None):
        with track_sqlite("write"):
            conn = self._get_conn()
            conn.execute("BEGIN")
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO workflow_runs (run_id, workflow_id, state, created_at, data) VALUES (?, ?, ?, ?, ?)",
                    (run.run_id, run.workflow_id, run.state.value, run.created_at, run.model_dump_json())
                )
                if outbox_events:
                    for ev in outbox_events:
                        conn.execute(
                            "INSERT INTO outbox_events (event_id, run_id, event_type, created_at, data) VALUES (?, ?, ?, ?, ?)",
                            (ev.event_id, ev.workflow_run_id, ev.event_type.value, ev.timestamp, ev.model_dump_json())
                        )
                conn.execute("COMMIT")
            except:
                conn.execute("ROLLBACK")
                raise

    def get_run(self, run_id: str) -> Optional[WorkflowRun]:
        with track_sqlite("read"):
            row = self._get_conn().execute("SELECT data FROM workflow_runs WHERE run_id = ?", (run_id,)).fetchone()
            return WorkflowRun.model_validate_json(row["data"]) if row else None

    def get_runs_by_state(self, states: List[WorkflowState]) -> List[WorkflowRun]:
        with track_sqlite("read"):
            state_vals = [s.value for s in states]
            placeholders = ",".join("?" * len(state_vals))
            rows = self._get_conn().execute(f"SELECT data FROM workflow_runs WHERE state IN ({placeholders})", state_vals).fetchall()
            return [WorkflowRun.model_validate_json(row["data"]) for row in rows]

    # Step Runs
    def save_step_run(self, step_run: WorkflowStepRun, outbox_events: List[WorkflowEvent] = None):
        with track_sqlite("write"):
            conn = self._get_conn()
            conn.execute("BEGIN")
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO workflow_step_runs (step_run_id, workflow_run_id, step_id, state, created_at, data) VALUES (?, ?, ?, ?, ?, ?)",
                    (step_run.step_run_id, step_run.workflow_run_id, step_run.step_id, step_run.state.value, step_run.created_at, step_run.model_dump_json())
                )
                if outbox_events:
                    for ev in outbox_events:
                        conn.execute(
                            "INSERT INTO outbox_events (event_id, run_id, event_type, created_at, data) VALUES (?, ?, ?, ?, ?)",
                            (ev.event_id, ev.workflow_run_id, ev.event_type.value, ev.timestamp, ev.model_dump_json())
                        )
                conn.execute("COMMIT")
            except:
                conn.execute("ROLLBACK")
                raise

    def get_step_run(self, step_run_id: str) -> Optional[WorkflowStepRun]:
        with track_sqlite("read"):
            row = self._get_conn().execute("SELECT data FROM workflow_step_runs WHERE step_run_id = ?", (step_run_id,)).fetchone()
            return WorkflowStepRun.model_validate_json(row["data"]) if row else None

    def get_step_runs(self, run_id: str) -> List[WorkflowStepRun]:
        with track_sqlite("read"):
            rows = self._get_conn().execute("SELECT data FROM workflow_step_runs WHERE workflow_run_id = ?", (run_id,)).fetchall()
            return [WorkflowStepRun.model_validate_json(row["data"]) for row in rows]

    def get_step_runs_by_state(self, states: List[StepState]) -> List[WorkflowStepRun]:
        with track_sqlite("read"):
            state_vals = [s.value for s in states]
            placeholders = ",".join("?" * len(state_vals))
            rows = self._get_conn().execute(f"SELECT data FROM workflow_step_runs WHERE state IN ({placeholders})", state_vals).fetchall()
            return [WorkflowStepRun.model_validate_json(row["data"]) for row in rows]

    # Outbox
    def pop_outbox_events(self) -> List[WorkflowEvent]:
        """Fetch and delete outbox events atomically."""
        with track_sqlite("outbox_pop"):
            conn = self._get_conn()
            conn.execute("BEGIN")
            try:
                rows = conn.execute("SELECT event_id, data FROM outbox_events ORDER BY created_at ASC").fetchall()
                events = [WorkflowEvent.model_validate_json(row["data"]) for row in rows]
                if rows:
                    event_ids = [row["event_id"] for row in rows]
                    placeholders = ",".join("?" * len(event_ids))
                    conn.execute(f"DELETE FROM outbox_events WHERE event_id IN ({placeholders})", event_ids)
                conn.execute("COMMIT")
                return events
            except:
                conn.execute("ROLLBACK")
                raise

    def close(self):
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            del self._local.conn
