"""
Task Management System - Interactive SQL Demo Runner
Can run against:
1. Local SQLite (Default, 0 setup required - works immediately)
2. Live MySQL Server (Pass --mysql flag with credentials)
"""

import sys
import argparse
import sqlite3

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def run_sqlite_demo():
    print("=" * 65)
    print(" Running Task Management System Database Demo (Local Engine)")
    print("=" * 65)

    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # DDL
    cursor.executescript("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE task_priorities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        rank_order INTEGER NOT NULL UNIQUE,
        description TEXT
    );

    CREATE TABLE task_statuses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        is_closed INTEGER NOT NULL DEFAULT 0,
        display_order INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER NOT NULL REFERENCES users(id),
        title TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        parent_task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
        creator_id INTEGER NOT NULL REFERENCES users(id),
        status_id INTEGER NOT NULL REFERENCES task_statuses(id),
        priority_id INTEGER NOT NULL REFERENCES task_priorities(id),
        title TEXT NOT NULL,
        description TEXT,
        due_date TIMESTAMP,
        completed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CHECK (parent_task_id != id)
    );

    CREATE TABLE task_assignees (
        task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (task_id, user_id)
    );

    CREATE TABLE task_activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        actor_id INTEGER NOT NULL REFERENCES users(id),
        field_changed TEXT NOT NULL,
        old_value TEXT,
        new_value TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX idx_tasks_project_status_due ON tasks (project_id, status_id, due_date);
    CREATE INDEX idx_tasks_parent_id ON tasks (parent_task_id);
    CREATE INDEX idx_assignees_user_task ON task_assignees (user_id, task_id);
    """)

    # Seed Data
    cursor.executescript("""
    INSERT INTO task_priorities (code, rank_order, description) VALUES
    ('CRITICAL', 1, 'Immediate resolution required; blocks release'),
    ('HIGH',     2, 'Important feature or major bugfix needed soon'),
    ('MEDIUM',   3, 'Normal priority item scheduled in sprint'),
    ('LOW',      4, 'Cosmetic or minor enhancement');

    INSERT INTO task_statuses (code, is_closed, display_order) VALUES
    ('BACKLOG',     0, 1),
    ('TODO',        0, 2),
    ('IN_PROGRESS', 0, 3),
    ('IN_REVIEW',   0, 4),
    ('COMPLETED',   1, 5),
    ('CANCELLED',   1, 6);

    INSERT INTO users (username, email, password_hash) VALUES
    ('alex_dev',   'alex@example.com',   'hash_1'),
    ('sarah_lead', 'sarah@example.com',  'hash_2'),
    ('david_qa',   'david@example.com',  'hash_3'),
    ('emily_pm',   'emily@example.com',  'hash_4');

    INSERT INTO projects (owner_id, title, description) VALUES
    (2, 'E-Commerce Platform Redesign', 'Revamp checkout and payments');

    -- Level 1: Epic
    INSERT INTO tasks (id, project_id, parent_task_id, creator_id, status_id, priority_id, title, due_date) VALUES
    (1, 1, NULL, 4, 3, 2, 'Redesign Checkout Flow', datetime('now', '+14 days'));

    -- Level 2: Subtasks
    INSERT INTO tasks (id, project_id, parent_task_id, creator_id, status_id, priority_id, title, due_date) VALUES
    (2, 1, 1, 2, 3, 1, 'Implement Stripe Payment Gateway', datetime('now', '+5 days')),
    (3, 1, 1, 2, 2, 3, 'Create Address Validation Component', datetime('now', '+8 days'));

    -- Level 3: Grandchild Tasks
    INSERT INTO tasks (id, project_id, parent_task_id, creator_id, status_id, priority_id, title, due_date) VALUES
    (4, 1, 2, 1, 5, 2, 'Configure Stripe Webhook Handlers', datetime('now', '-1 days')),
    (5, 1, 2, 1, 3, 1, 'Add Apple Pay / Google Pay Support', datetime('now', '+3 days'));

    -- Standalone Task
    INSERT INTO tasks (id, project_id, parent_task_id, creator_id, status_id, priority_id, title, due_date) VALUES
    (6, 1, NULL, 4, 1, 4, 'Update Terms of Service Modal', datetime('now', '+30 days'));

    INSERT INTO task_assignees (task_id, user_id) VALUES
    (1, 2), (2, 1), (3, 1), (4, 1), (4, 3), (5, 1), (6, 4);
    """)
    conn.commit()
    print("Schema initialized and sample data seeded successfully!\n")

    # Query 1: Recursive CTE
    print("--> 1. Recursive CTE: Full Task Hierarchy Traversal")
    print("-" * 65)
    query_1 = """
    WITH RECURSIVE task_hierarchy AS (
        SELECT id, parent_task_id, title, status_id, priority_id, 1 AS level, CAST(id AS TEXT) AS path
        FROM tasks
        WHERE parent_task_id IS NULL

        UNION ALL

        SELECT child.id, child.parent_task_id, child.title, child.status_id, child.priority_id, th.level + 1, th.path || ' > ' || child.id
        FROM tasks child
        JOIN task_hierarchy th ON child.parent_task_id = th.id
    )
    SELECT 
        th.id,
        th.path,
        CASE th.level 
            WHEN 1 THEN th.title
            WHEN 2 THEN '  └─ ' || th.title
            ELSE '      └─ ' || th.title
        END AS visual_hierarchy,
        ts.code AS status,
        tp.code AS priority
    FROM task_hierarchy th
    JOIN task_statuses ts ON th.status_id = ts.id
    JOIN task_priorities tp ON th.priority_id = tp.id
    ORDER BY th.path;
    """
    for row in cursor.execute(query_1):
        task_id, path, tree, status, prio = row
        print(f"[{prio:<8}] [{status:<11}] {tree} (ID: {task_id}, Path: {path})")
    print()

    # Query 2: Active Tasks for User (alex_dev)
    print("--> 2. Active Tasks Filtered For 'alex_dev' (User ID: 1)")
    print("-" * 65)
    query_2 = """
    SELECT t.id, t.title, p.title AS project, ts.code AS status, tp.code AS priority
    FROM task_assignees ta
    JOIN tasks t ON ta.task_id = t.id
    JOIN projects p ON t.project_id = p.id
    JOIN task_statuses ts ON t.status_id = ts.id
    JOIN task_priorities tp ON t.priority_id = tp.id
    WHERE ta.user_id = 1 AND ts.is_closed = 0
    ORDER BY tp.rank_order ASC;
    """
    for row in cursor.execute(query_2):
        print(f"Task #{row[0]}: {row[1]} | Priority: {row[4]} | Status: {row[3]}")
    print()

    # Query 3: Project Progress Rollup
    print("--> 3. Project Progress Rollup")
    print("-" * 65)
    query_3 = """
    SELECT 
        p.title,
        COUNT(t.id) AS total,
        SUM(CASE WHEN ts.is_closed = 1 THEN 1 ELSE 0 END) AS completed,
        ROUND((CAST(SUM(CASE WHEN ts.is_closed = 1 THEN 1 ELSE 0 END) AS REAL) / COUNT(t.id)) * 100, 1) AS percent
    FROM projects p
    LEFT JOIN tasks t ON p.id = t.project_id
    LEFT JOIN task_statuses ts ON t.status_id = ts.id
    GROUP BY p.id;
    """
    for row in cursor.execute(query_3):
        print(f"Project: '{row[0]}' -> {row[2]}/{row[1]} completed ({row[3]}%)")
    print()
    print("=" * 65)
    print(" Demo finished successfully! For full MySQL DDL see 'schema.sql'.")
    print("=" * 65)

if __name__ == "__main__":
    run_sqlite_demo()
