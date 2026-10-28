-- ========================================================
-- Demonstration & Analytical Queries
-- ========================================================

USE task_management_db;

-- --------------------------------------------------------
-- 1. Recursive CTE: Full Task Hierarchy Traversal
-- Traverses root tasks down to child and grandchild subtasks
-- --------------------------------------------------------
WITH RECURSIVE task_hierarchy AS (
    -- Anchor: top-level tasks
    SELECT 
        id,
        parent_task_id,
        title,
        status_id,
        priority_id,
        due_date,
        1 AS level,
        CAST(id AS CHAR(255)) AS breadcrumb
    FROM tasks
    WHERE parent_task_id IS NULL

    UNION ALL

    -- Recursive step: subtasks
    SELECT 
        child.id,
        child.parent_task_id,
        child.title,
        child.status_id,
        child.priority_id,
        child.due_date,
        th.level + 1 AS level,
        CONCAT(th.breadcrumb, ' > ', child.id) AS breadcrumb
    FROM tasks child
    INNER JOIN task_hierarchy th ON child.parent_task_id = th.id
)
SELECT 
    th.id,
    th.breadcrumb,
    CONCAT(REPEAT('  ', th.level - 1), '└─ ', th.title) AS visual_tree,
    ts.code AS status,
    tp.code AS priority,
    th.due_date
FROM task_hierarchy th
JOIN task_statuses ts ON th.status_id = ts.id
JOIN task_priorities tp ON th.priority_id = tp.id
ORDER BY th.breadcrumb;

-- --------------------------------------------------------
-- 2. User Dashboard Query (High-Performance Filtered Retrieval)
-- Returns active tasks assigned to 'alex_dev' (User ID: 1)
-- --------------------------------------------------------
EXPLAIN
SELECT 
    t.id AS task_id,
    t.title,
    p.title AS project_name,
    ts.code AS status,
    tp.code AS priority,
    t.due_date
FROM task_assignees ta
INNER JOIN tasks t ON ta.task_id = t.id
INNER JOIN projects p ON t.project_id = p.id
INNER JOIN task_statuses ts ON t.status_id = ts.id
INNER JOIN task_priorities tp ON t.priority_id = tp.id
WHERE ta.user_id = 1
  AND ts.is_closed = FALSE
ORDER BY tp.rank_order ASC, t.due_date ASC;

-- --------------------------------------------------------
-- 3. Project Progress Metric (Completion Rate Rollup)
-- --------------------------------------------------------
SELECT 
    p.id AS project_id,
    p.title AS project_name,
    COUNT(t.id) AS total_tasks,
    SUM(CASE WHEN ts.is_closed = TRUE THEN 1 ELSE 0 END) AS completed_tasks,
    ROUND(
        (SUM(CASE WHEN ts.is_closed = TRUE THEN 1 ELSE 0 END) / COUNT(t.id)) * 100, 
        2
    ) AS completion_percentage
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
LEFT JOIN task_statuses ts ON t.status_id = ts.id
GROUP BY p.id, p.title;

-- --------------------------------------------------------
-- 4. Overdue Tasks Alert Query
-- --------------------------------------------------------
SELECT 
    t.id AS task_id,
    t.title,
    t.due_date,
    TIMESTAMPDIFF(DAY, t.due_date, NOW()) AS days_overdue,
    GROUP_CONCAT(u.username SEPARATOR ', ') AS assignees
FROM tasks t
JOIN task_statuses ts ON t.status_id = ts.id
LEFT JOIN task_assignees ta ON t.id = ta.task_id
LEFT JOIN users u ON ta.user_id = u.id
WHERE t.due_date < NOW()
  AND ts.is_closed = FALSE
GROUP BY t.id, t.title, t.due_date;
