-- ========================================================
-- Seed Data for Task Management System
-- ========================================================

USE task_management_db;

-- 1. Insert Priorities
INSERT INTO task_priorities (code, rank_order, description) VALUES
('CRITICAL', 1, 'Immediate resolution required; blocks production/release'),
('HIGH',     2, 'Important feature or major bugfix needed soon'),
('MEDIUM',   3, 'Normal priority item scheduled in regular sprint'),
('LOW',      4, 'Cosmetic or minor enhancement; handle when bandwidth permits');

-- 2. Insert Statuses
INSERT INTO task_statuses (code, is_closed, display_order) VALUES
('BACKLOG',     FALSE, 1),
('TODO',        FALSE, 2),
('IN_PROGRESS', FALSE, 3),
('IN_REVIEW',   FALSE, 4),
('COMPLETED',   TRUE,  5),
('CANCELLED',   TRUE,  6);

-- 3. Insert Users
INSERT INTO users (username, email, password_hash) VALUES
('alex_dev',     'alex@example.com',     '$2b$12$e80yvY6.7N41rJ9t2U3YEu5y29f8f2'),
('sarah_lead',   'sarah@example.com',    '$2b$12$e80yvY6.7N41rJ9t2U3YEu5y29f8f3'),
('david_qa',     'david@example.com',    '$2b$12$e80yvY6.7N41rJ9t2U3YEu5y29f8f4'),
('emily_pm',     'emily@example.com',    '$2b$12$e80yvY6.7N41rJ9t2U3YEu5y29f8f5');

-- 4. Insert Project
INSERT INTO projects (owner_id, title, description) VALUES
(2, 'E-Commerce Platform Redesign', 'Revamp customer checkout and payment processing pipeline.');

-- 5. Insert Tasks (with 3 levels of hierarchy)
-- Level 1: Root epic
INSERT INTO tasks (id, project_id, parent_task_id, creator_id, status_id, priority_id, title, description, due_date) VALUES
(1, 1, NULL, 4, 3, 2, 'Redesign Checkout Flow', 'Complete overhaul of checkout journey to reduce drop-offs.', DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 14 DAY));

-- Level 2: Subtasks under task 1
INSERT INTO tasks (id, project_id, parent_task_id, creator_id, status_id, priority_id, title, description, due_date) VALUES
(2, 1, 1, 2, 3, 1, 'Implement Stripe Payment Gateway', 'Integrate Stripe Elements and 3D Secure verification.', DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 5 DAY)),
(3, 1, 1, 2, 2, 3, 'Create Address Validation Component', 'Google Places autocomplete integration for shipping address.', DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 8 DAY));

-- Level 3: Sub-subtasks under task 2
INSERT INTO tasks (id, project_id, parent_task_id, creator_id, status_id, priority_id, title, description, due_date) VALUES
(4, 1, 2, 1, 5, 2, 'Configure Stripe Webhook Handlers', 'Handle payment_intent.succeeded and failed events.', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY)),
(5, 1, 2, 1, 3, 1, 'Add Apple Pay / Google Pay Support', 'Wallet button rendering and token exchange handler.', DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 3 DAY));

-- Standalone Task
INSERT INTO tasks (id, project_id, parent_task_id, creator_id, status_id, priority_id, title, description, due_date) VALUES
(6, 1, NULL, 4, 1, 4, 'Update Terms of Service Modal', 'Legal copy update for checkout GDPR compliance.', DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 30 DAY));

-- 6. Assign Users to Tasks
INSERT INTO task_assignees (task_id, user_id) VALUES
(1, 2), -- Sarah leads root task
(2, 1), -- Alex on Stripe
(3, 1), -- Alex on Address validation
(4, 1), -- Alex completed webhooks
(4, 3), -- David QA'd webhooks
(5, 1), -- Alex on Apple Pay
(6, 4); -- Emily on Terms modal

-- 7. Audit Log Sample
INSERT INTO task_activity_logs (task_id, actor_id, field_changed, old_value, new_value) VALUES
(4, 1, 'status_id', 'IN_PROGRESS', 'COMPLETED'),
(2, 2, 'priority_id', 'MEDIUM', 'CRITICAL');
