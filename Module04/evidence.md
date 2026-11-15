# Module 4: Data Integrity, Constraints & Edge Triggers

**Database:** SQLite 3.53.4 (`edge.db`), Windows PowerShell, Python 3.14
**Scenario:** machine-shop telemetry at the edge. The database itself has to refuse bad data, raise alarms and keep an audit trail, because there is no server or DBA to fix it afterwards.

## Learning goals and where they are evidenced

| Learning goal | Evidence |
|---|---|
| 1. Constraint toolkit (`NOT NULL`, `UNIQUE`, `CHECK`, keys, `STRICT`) | Task A, Task 1 |
| 2. Generated columns | Task 1 (`energy_j`) |
| 3. Triggers for domain rules and audit | Task 3 |
| 4. DML with UPSERT for idempotent ingestion | Task 2 |
| 5. Access control (DCL) in an embedded world | Task 4 |

## Files in `Module04/`

| File | Purpose |
|---|---|
| `setup.sql` | Creates `sensor` and `reading` (STRICT, constraints, generated column) |
| `task1.sql`, `task2.sql`, `task3.sql` | Statements for each task |
| `ingest.py`, `readings.csv` | UPSERT-based ingestion script and test data |
| `bench.py` | Trigger cost benchmark |
| `taskA-output.txt` ... `task4-output.txt`, `bench-output.txt` | Raw outputs |
| `integrity-notes.md` | Pod study notes |

---

## Task A: What does an unconstrained table accept?

**Goal:** see which junk an unconstrained table lets through, then repeat the same inserts against a constrained twin.

**Unconstrained table `t`** (no constraints): all 5 inserts were accepted.

| Row stored | Why it is wrong |
|---|---|
| `1, temp_c, 9000.0` | Physically impossible temperature |
| `1, temp_c, hot` | Text stored in a REAL column (SQLite is dynamically typed) |
| `2, bogus, -500.0` | Unknown metric, and below absolute zero |
| `NULL, '', -1.0` | Missing id and empty metric |
| `-5, x, Inf` | Negative id; the text `'1e999'` became infinity |

**Constrained table `t2`** (`STRICT`, `PRIMARY KEY`, `NOT NULL` on metric, two `CHECK`s):

```sql
CREATE TABLE t2(
  sensor_id INTEGER PRIMARY KEY,
  metric TEXT NOT NULL CHECK (metric IN ('temp_c','vib_rms','spindle_load')),
  value REAL CHECK (value BETWEEN -273.15 AND 5000)
) STRICT;
```

| Insert | Result | Layer |
|---|---|---|
| value 9000 | `CHECK constraint failed: value BETWEEN -273.15 AND 5000` | Semantic (domain) |
| value `'hot'` | `cannot store TEXT value in REAL column t2.value` | Semantic (STRICT typing) |
| metric `'bogus'` | `CHECK constraint failed: metric IN ('temp_c','vib_rms','spindle_load')` | Semantic (domain) |
| `sensor_id` 4 a second time | `UNIQUE constraint failed: t2.sensor_id` | Entity |
| value NULL | **Accepted** | none |
| value 400 | **Accepted** | none |

**Follow-up questions**
- **What does `CHECK` do with NULL?** It lets it through. `CHECK` only rejects when the condition is false, and NULL makes it "unknown". Only `NOT NULL` blocks it, so the two constraints do different jobs.
- **Which wrong value still gets in?** 400 degC passes every constraint, even if the machine tops out at 80 degC. Constraints enforce what is *impossible*, not what is *unlikely*. Catching it needs per-sensor limits or a trigger.

---

## Task 1: Prove the constraints reject

Each statement was run against `edge.db` with `PRAGMA foreign_keys = ON`.

| Statement | Exact error | Layer |
|---|---|---|
| Temperature 9000 | `CHECK constraint failed: value >= -273.15 AND value <= 5000` | Semantic (domain) |
| Value `'hot'` | `cannot store TEXT value in REAL column reading.value` | Semantic (STRICT) |
| Sensor 99 (does not exist) | `FOREIGN KEY constraint failed` | Referential |
| Second `cnc-01` + `temp_c` sensor | `UNIQUE constraint failed: sensor.machine_id, sensor.metric` | Entity |

**Generated column:** the valid row (value 41.5, interval 1 s) returned:
```
reading_id | value | interval_s | energy_j
1          | 41.5  | 1          | 41.5
```
`energy_j = value * interval_s` is computed by the database, so no application can compute it wrongly.

**What this proves:** all three integrity layers (entity, referential, semantic) were seen rejecting bad data. Foreign keys only work because the pragma was switched on in that connection; SQLite leaves it off by default.

---

## Task 2: Idempotent ingestion with UPSERT

**Problem:** after a network outage the gateway replays readings. Replays must not create duplicates.

**Solution:** a unique index makes `(sensor_id, ts)` a natural key, so a replayed reading collides with the existing row. `ON CONFLICT ... DO UPDATE` then updates the value instead of failing or inserting a copy.

```sql
CREATE UNIQUE INDEX ux_reading_sensor_ts ON reading(sensor_id, ts);

INSERT INTO reading(sensor_id, ts, value, interval_s)
VALUES (1,'2026-03-01 08:00:00', 41.7, 1)
ON CONFLICT(sensor_id, ts) DO UPDATE SET value = excluded.value;
```

**Result:**
```
1|2026-03-01 08:00:00|41.7
1|2026-03-01 08:00:01|42.0
```
The reading at 08:00:00 had value 41.5 and now has 41.7. It appears **once**, so the conflict was resolved as an update, not a duplicate.

**Python ingest (`ingest.py`):** reads the CSV and runs the same UPSERT with `executemany` in one transaction. It was run twice on the same file:
```
rows in reading: 3
rows in reading: 3
```
**What this proves:** the row count is identical after the second run, so the ingest is idempotent.

---

## Task 3: Triggers for alarms and audit

**Goal:** enforce a rule and keep an audit trail inside the database, so no application can forget either.

| Trigger | Timing | Fires when | Action |
|---|---|---|---|
| `trg_vib_alarm` | AFTER INSERT on `reading` | a `vib_rms` value is above 2.0 mm/s | inserts a row into `alarm` |
| `trg_reading_audit` | AFTER UPDATE OF `value` on `reading` | a reading's value changes | inserts old and new value into `audit` |

`AFTER` is the right timing: alarm and audit rows should only describe changes that actually landed in the table.

**Test and result**

| Statement | Effect | Row produced |
|---|---|---|
| Insert vibration reading 2.7 on sensor 2 | alarm trigger fired | `1\|2\|2026-03-01 09:00:00\|2.7\|vibration over 2.0 mm/s` |
| Update that reading to 1.4 | audit trigger fired | `1\|4\|2.7\|1.4\|2026-10-31 14:24:05` |

**What this proves:** both rows appeared without any application code. The audit row keeps the old value (2.7) and the new value (1.4), and the timestamp was filled in by the database.

**Trigger cost:** 10,000 inserts of value 2.5 (worst case: every row fires the alarm), 3 runs each.

| Run | With trigger (s) | Without trigger (s) |
|---|---|---|
| 1 | 0.1323 | 0.0700 |
| 2 | 0.1313 | 0.0929 |
| 3 | 0.1557 | 0.1746 |
| Average | 0.140 | 0.113 |

**Interpretation:** the trigger added about 25% on average, because each insert also looks up the sensor's metric and writes a second row. Run 3 is an outlier (the run without the trigger was slower), probably from caching or background load, so the numbers are indicative only.

**Takeaway:** a trigger on a hot ingest path is a design decision. Here the cost is acceptable and the guarantee (no missed alarms, no unaudited changes) is worth it.

---

## Task 4: Access control without a server

**Goal:** SQLite has no `GRANT`, so show the embedded substitutes: a view that exposes a safe subset, a read-only file, and a read-only connection.

```sql
CREATE VIEW machine_health AS
SELECT s.machine_id, s.metric, MAX(r.value) AS peak, COUNT(*) AS n
FROM sensor s JOIN reading r USING(sensor_id)
GROUP BY s.machine_id, s.metric;
```

| Test | Command | Result |
|---|---|---|
| Read via view | `sqlite3 -readonly Module04/edge.db "SELECT * FROM machine_health;"` | `cnc-01, temp_c, 42.0, 2` and `cnc-01, vib_rms, 1.4, 2` |
| Write, read-only connection | `sqlite3 -readonly Module04/edge.db "DELETE FROM reading;"` | `attempt to write a readonly database` |
| Write, read-only file | `Set-ItemProperty Module04/edge.db -Name IsReadOnly -Value $true`, then `sqlite3 Module04/edge.db "DELETE FROM reading;"` | `attempt to write a readonly database` |
| Data intact | `SELECT COUNT(*) FROM reading;` | 4 |

On Windows the file-level lock is the read-only attribute (`IsReadOnly`), the equivalent of `chmod 444` on Linux. The file was unlocked afterwards with `-Value $false`.

**What this proves:** both writes were blocked and no data was lost. The view lets a report reader see peaks and counts without access to individual readings.

**How this differs from PostgreSQL**

A PostgreSQL server has its own users and roles, so `GRANT` and `REVOKE` can give each person different rights on each table or column, even though everyone connects to the same database. SQLite has no users: whoever can open the file can read everything, so access control moves to the file system permissions, to views that expose only a safe subset, and to read-only connections. That is acceptable on an edge gateway, where the plant owns the machine and only a few trusted programs touch the file. It is not acceptable for a multi-tenant web app, because all tenants' requests would run through one process with the same file rights, so per-user
**Output:**


**Output:**
**Triggers present in `edge.db` after the experiment** (the original `AFTER INSERT` alarm trigger is still in place):

| Name | Timing | On table |
|---|---|---|
| `trg_vib_alarm` | AFTER INSERT | `reading` |
| `trg_reading_audit` | AFTER UPDATE OF `value` | `reading` |

```sql
CREATE TRIGGER trg_vib_alarm
AFTER INSERT ON reading
FOR EACH ROW
WHEN NEW.value > 2.0 AND (SELECT metric FROM sensor WHERE sensor_id = NEW.sensor_id) = 'vib_rms'
BEGIN
    INSERT INTO alarm(sensor_id, ts, value, reason)
    VALUES (NEW.sensor_id, NEW.ts, NEW.value, 'vibration over 2.0 mm/s');
END;

CREATE TRIGGER trg_reading_audit
AFTER UPDATE OF value ON reading
FOR EACH ROW
BEGIN
    INSERT INTO audit(reading_id, old_value, new_value)
    VALUES (NEW.reading_id, OLD.value, NEW.value);
END;
```
