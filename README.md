# Task Management System - Relational Database Design

A production-grade, 3NF-normalized relational database system built for managing multi-user task hierarchies, priorities, statuses, and performance-optimized querying in **MySQL 8.0+**.

---

## 📁 Repository Structure

```text
├── schema.sql           # MySQL DDL (Tables, Constraints, Indexes)
├── seed.sql             # Sample data (Users, Priorities, Multi-level Tasks, Assignees)
├── queries.sql          # Benchmark & Demonstration queries (Recursive CTEs, Dashboard filtering)
├── docker-compose.yml   # 1-click MySQL 8.0 environment with auto-seeding
├── run_demo.py          # Zero-dependency local demo runner (works immediately via Python)
└── README.md            # Documentation and setup guide
```

---

## 🚀 How to Run the Project

You can run this project using any of the 3 methods below:

### Option 1: Instant Local Demo (Zero Setup)

You can run the full relational logic, test queries, and recursive hierarchy trees immediately using Python:

```bash
python run_demo.py
```

---

### Option 2: Docker Compose (Recommended for MySQL)

If you have Docker Desktop installed, boot MySQL 8.0 pre-loaded with `schema.sql` and `seed.sql`:

```bash
docker compose up -d
```

- **Host**: `localhost`
- **Port**: `3306`
- **Database**: `task_management_db`
- **User**: `appuser` / **Password**: `apppassword`
- **Root Password**: `rootpassword`

To open a MySQL shell inside the container:
```bash
docker exec -it task_mgmt_mysql mysql -u appuser -papppassword task_management_db
```

---

### Option 3: Local MySQL CLI or GUI (Workbench / DBeaver)

If you have a local MySQL server installed:

1. **Import the Schema**:
   ```bash
   mysql -u root -p < schema.sql
   ```

2. **Populate Seed Data**:
   ```bash
   mysql -u root -p task_management_db < seed.sql
   ```

3. **Execute Queries**:
   ```bash
   mysql -u root -p task_management_db < queries.sql
   ```

*Or open [schema.sql](schema.sql), [seed.sql](seed.sql), and [queries.sql](queries.sql) directly in **MySQL Workbench** or **DBeaver** and execute them sequentially.*

---

## 🛠️ Key Features & Implementation Highlights

1. **Self-Referencing Task Hierarchy**: Supports infinite nesting depth (Epics -> Tasks -> Subtasks) using `parent_task_id` with `ON DELETE CASCADE`.
2. **Recursive Common Table Expressions (CTEs)**: Traverses parent/child task trees in a single database round-trip without nested application loops.
3. **Composite B-Tree Indexes**:
   - `(project_id, status_id, due_date)` covers high-frequency dashboard filters.
   - `(user_id, task_id)` on the bridge table optimizes user-specific task retrievals.
4. **Relational Constraints**:
   - `CHECK (parent_task_id <> id)` prevents self-referencing cyclic loops.
   - `CHECK (completed_at >= created_at)` validates logical timestamp integrity.
