# Waste Classifier Database

This project uses PostgreSQL running inside Docker. No local PostgreSQL installation is required.

---

## Requirements

- Docker Desktop installed
- Docker running

---

## Project Structure

```
database/
│
├── docker-compose.yml
│
└── init/
    ├── 01_create_tables.sql
    ├── 02_insert_reference_data.sql
    ├── 03_insert_category_bins.sql
    └── 04_insert_disposal_instructions.sql
```

---

## Starting the Database

Open Command Prompt inside the `database` folder.

Run:

```bash
docker compose up -d
```

The first startup may take a few minutes because Docker downloads the PostgreSQL image.

---

## Verify the Container is Running

```bash
docker ps
```

You should see:

```
waste_app_postgres
```

---

## Connect to PostgreSQL

Run:

```bash
docker exec -it waste_app_postgres psql -U admin -d waste_app
```

You should see:

```
waste_app=#
```

---

## Useful Commands

### Show all tables

```sql
\dt
```

### Show the structure of a table

```sql
\d categories
```

Example:

```sql
\d bins
```

### Display all rows

```sql
SELECT * FROM bins;
```

Example:

```sql
SELECT * FROM categories;
```

### Display only a few rows

```sql
SELECT * FROM categories LIMIT 5;
```

### Count rows

```sql
SELECT COUNT(*) FROM categories;
```

### Exit PostgreSQL

```sql
\q
```

---

## Stopping the Database

```bash
docker compose down
```

This stops the database **without deleting any data**.

---

## Resetting the Database

If the SQL files inside `init/` are modified, recreate the database by running:

```bash
docker compose down -v
docker compose up -d
```

**Warning:** This deletes all data stored in the database and recreates it from the SQL scripts.

---

## PostgreSQL Configuration

| Setting | Value |
|---------|-------|
| Database | waste_app |
| Username | admin |
| Password | password |
| Port | 5432 |

---

## Notes

- The SQL files inside the `init/` folder are executed **only the first time** the database is created.
- If you modify any SQL file in `init/`, you must run:

```bash
docker compose down -v
docker compose up -d
```

to recreate the database with the updated schema or seed data.