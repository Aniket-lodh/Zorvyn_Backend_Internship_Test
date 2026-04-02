# Finance Data Processing & Access Control Backend

A backend system designed to manage financial records with strict role-based access control and structured data processing.

This project focuses on:

- Clean backend architecture (routes → services → data layer)
- Explicit access control enforcement using database-backed roles
- Data handling with validation and error management
- Aggregation-focused APIs for dashboard analytics

The goal of this project is not just to implement APIs, but to demonstrate clear backend system design, data modeling, and access control logic.

---

## Key Highlights

- **Database-backed RBAC** — no trust on client role input; role is derived from the database
- **Clean separation of concerns** — route → service → data layer
- **Structured validation and error handling** — proper 422 / 403 / 404 / 401 responses with descriptive messages
- **Aggregation-focused dashboard APIs** — summary and trends with date range filtering and empty-dataset handling
- **Pagination support** — record retrieval with `limit`/`offset`
- **Indexed database design** — optimized queries on filtered and aggregated columns

---

## How to Evaluate This Project

To review this backend effectively:

1. **Start the server** and access Swagger UI:

   ```bash
   http://localhost:8065/docs
   ```

2. **Run the bootstrap command** to create the initial admin:

   ```bash
   uv run task seed
   ```

3. **Use the generated UUID** as the `X-User-Id` header in Swagger

4. **Test role-based behavior** by creating users with different roles:

   - **Viewer** → can only access `GET /dashboard/summary`
   - **Analyst** → can read records + view analytics
   - **Admin** → full CRUD on users and records

5. **Review these behaviors:**
   - Access control enforcement (try a Viewer UUID on `POST /records` → expect `403`)
   - Validation behavior (submit `amount: -5` or a future date → expect `422`)
   - Dashboard aggregation responses (check totals, category breakdowns, and trends)

---

## Setup / Bootstrapping

### Prerequisites

- Python 3.11+
- PostgreSQL running at `127.0.0.1:5432`
- Database `finance_db` created
- `uv` package manager installed

### Installation

```bash
# Clone and enter the project
cd Zorvyn_Backend_Internship_Test

# Copy environment file
cp .env.example .env

# Install dependencies
uv sync

# Run database migrations
uv run task upgrade

# Seed the initial admin user (required before first use)
uv run task seed

# Start development server
uv run task dev
```

The server will be available at `http://localhost:8065`.
Swagger UI is at `http://localhost:8065/docs`.

### Why Bootstrapping Is Required

This system enforces role-based access control by verifying every request against the database. The `X-User-Id` header must contain a UUID that maps to a real, active user in the `users` table. This means you **cannot create the first user through the API** — it's a chicken-and-egg problem.

The `uv run task seed` command solves this by:

- Checking if any admin user already exists
- If none exists, creating an initial admin user (`admin@zorvyn.test`)
- Printing the generated UUID to the terminal (Copy this UUID and use it as the `X-User-Id` header in Swagger)`

**Idempotent:** Running the seed script multiple times is safe — it skips if an admin already exists.

### Available Tasks

All tasks are run via `uv run task <name>`:

| Task        | Command                 | Description                                  |
| ----------- | ----------------------- | -------------------------------------------- |
| `dev`       | `uv run task dev`       | Start dev server with hot reload (port 8065) |
| `start`     | `uv run task start`     | Start production server (port 8000)          |
| `upgrade`   | `uv run task upgrade`   | Apply all pending Alembic migrations         |
| `downgrade` | `uv run task downgrade` | Rollback one Alembic migration               |
| `seed`      | `uv run task seed`      | Bootstrap initial admin user                 |

---

## API Reference

### Access Control

Every request must include the `X-User-Id` header with a valid UUID.

```
Request → Extract X-User-Id → Fetch User from DB → Validate is_active → Check Role → Allow/Deny
```

| Condition            | HTTP Status | Response                                      |
| -------------------- | ----------- | --------------------------------------------- |
| Invalid UUID format  | `400`       | Bad Request                                   |
| User not found in DB | `401`       | Unauthorized                                  |
| User is inactive     | `403`       | Forbidden ("Inactive user")                   |
| Role not permitted   | `403`       | Forbidden ("Role '...' does not have access") |

### Role Permissions

| Role        | Manage Users | Write Records | Read Records | Dashboard Summary | Dashboard Trends |
| ----------- | ------------ | ------------- | ------------ | ----------------- | ---------------- |
| **Admin**   | ✅           | ✅            | ✅           | ✅                | ✅               |
| **Analyst** | ❌           | ❌            | ✅           | ✅                | ✅               |
| **Viewer**  | ❌           | ❌            | ❌           | ✅                | ❌               |

### Users

| Method  | Endpoint      | Role  | Description       |
| ------- | ------------- | ----- | ----------------- |
| `POST`  | `/users`      | Admin | Create a new user |
| `GET`   | `/users`      | Admin | List all users    |
| `GET`   | `/users/{id}` | Admin | Get user by ID    |
| `PATCH` | `/users/{id}` | Admin | Update a user     |

### Financial Records

| Method   | Endpoint        | Role           | Description                              |
| -------- | --------------- | -------------- | ---------------------------------------- |
| `POST`   | `/records`      | Admin          | Create a financial record                |
| `GET`    | `/records`      | Analyst, Admin | List records (with filters + pagination) |
| `GET`    | `/records/{id}` | Analyst, Admin | Get record by ID                         |
| `PATCH`  | `/records/{id}` | Admin          | Update a record                          |
| `DELETE` | `/records/{id}` | Admin          | Delete a record                          |

#### GET /records — Query Parameters

| Parameter    | Type                  | Default | Description                           |
| ------------ | --------------------- | ------- | ------------------------------------- |
| `type`       | `income` \| `expense` | —       | Filter by record type                 |
| `category`   | string                | —       | Filter by category (case-insensitive) |
| `start_date` | `YYYY-MM-DD`          | —       | Records on or after this date         |
| `end_date`   | `YYYY-MM-DD`          | —       | Records on or before this date        |
| `limit`      | int (1–100)           | `20`    | Max number of records to return       |
| `offset`     | int (≥ 0)             | `0`     | Number of records to skip             |

Pagination is applied _after_ all filters. Returns a subset of matching results ordered by date (descending).

### Dashboard

| Method | Endpoint             | Role           | Description                  |
| ------ | -------------------- | -------------- | ---------------------------- |
| `GET`  | `/dashboard/summary` | All roles      | Aggregated financial summary |
| `GET`  | `/dashboard/trends`  | Analyst, Admin | Income vs expense trends     |

#### GET /dashboard/summary — Query Parameters

| Parameter    | Type         | Default | Description                    |
| ------------ | ------------ | ------- | ------------------------------ |
| `start_date` | `YYYY-MM-DD` | —       | Filter summary from this date  |
| `end_date`   | `YYYY-MM-DD` | —       | Filter summary up to this date |

If no date range is provided, the summary includes all records.

---

## Validation Rules

### Financial Records

| Field      | Rule                              | Error                                    |
| ---------- | --------------------------------- | ---------------------------------------- |
| `amount`   | Must be > 0                       | `422` — "Input should be greater than 0" |
| `type`     | Must be `"income"` or `"expense"` | `422` — Invalid enum value               |
| `category` | 1–100 characters                  | `422` — String constraint violation      |
| `date`     | Cannot be in the future           | `422` — "Date cannot be in the future"   |
| `notes`    | Max 500 characters (optional)     | `422` — String constraint violation      |

### Users

| Field   | Rule                                          | Error                                      |
| ------- | --------------------------------------------- | ------------------------------------------ |
| `email` | Must be a valid email format                  | `422` — Value is not a valid email address |
| `name`  | Required, non-empty                           | `422` — Field required                     |
| `role`  | Must be `"viewer"`, `"analyst"`, or `"admin"` | `422` — Invalid enum value                 |

---

## Performance Considerations

### Database Indexing

The following indexes are applied on the `financial_records` table to optimize query performance:

| Column       | Purpose                                                           |
| ------------ | ----------------------------------------------------------------- |
| `date`       | Accelerates date range filtering and dashboard date aggregation   |
| `type`       | Speeds up income/expense type filtering                           |
| `category`   | Improves category-based filtering and dashboard breakdown queries |
| `created_by` | Optimizes foreign key lookups and potential per-user queries      |

## Design Tradeoffs

| Decision                                               | Rationale                                                                                                                                                   |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Header-based identity (`X-User-Id`) instead of JWT** | Simpler implementation for assignment scope. Role and active status are verified via DB lookup, but the header itself is not cryptographically signed.      |
| **Async SQLAlchemy**                                   | Chosen for scalability and non-blocking I/O. Adds setup complexity (asyncpg, async sessions) but aligns with FastAPI's async-first architecture.            |
| **Pagination**                                         | Balances initial simplicity with production readiness. Default limit of 20 prevents unbounded queries.                                                      |
| **No caching**                                         | Avoided premature optimization. Dashboard queries use indexed columns, making raw SQL performance sufficient at this scale.                                 |
| **No authentication layer (JWT/OAuth)**                | The system validates identity against the database but does not verify that the requester owns the `X-User-Id`. Which Is not important for this assignment. |

---

## Project Structure

```
├── app/
│   ├── main.py                  # FastAPI app, router registration, exception handlers
│   ├── core/
│   │   ├── config.py            # Settings via pydantic-settings
│   │   └── database.py          # Async engine, session factory, Base
│   ├── models/
│   │   ├── user.py              # User ORM model
│   │   └── financial_record.py  # FinancialRecord ORM model
│   ├── schemas/
│   │   ├── user.py              # User request/response schemas
│   │   ├── financial_record.py  # Record schemas
│   │   └── dashboard.py         # Dashboard response schemas
│   ├── routes/
│   │   ├── users.py             # /users endpoints
│   │   ├── records.py           # /records endpoints
│   │   └── dashboard.py         # /dashboard endpoints
│   ├── services/
│   │   ├── user_service.py      # User business logic
│   │   ├── record_service.py    # Record business logic
│   │   └── dashboard_service.py # Dashboard aggregation logic
│   ├── dependencies/
│   │   └── access_control.py    # DB-backed RBAC dependency
│   └── utils/
│       └── exceptions.py        # Custom exceptions + global handlers
├── scripts/
│   └── seed_admin.py            # Bootstrap script for initial admin
├── pyproject.toml               # Dependencies + taskipy tasks
└── alembic.ini                  # Migration configuration
```
