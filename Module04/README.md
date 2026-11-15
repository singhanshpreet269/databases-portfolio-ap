# Module 4: Data Integrity, Constraints & Edge Triggers

Part of my Databases portfolio (HSBI). This module makes an SQLite "edge" database enforce its own rules, so bad data is refused, alarms are raised and changes are audited without any server or application code.

**Scenario:** machine-shop telemetry from CNC machines is written by an edge gateway into a local SQLite file. There is no DBA and no backend to re-validate, so the database itself has to refuse garbage.

## What I built

| Topic | What I did |
|---|---|
| Constraints | `STRICT` tables with `PRIMARY KEY`, `NOT NULL`, `UNIQUE`, `CHECK` and `FOREIGN KEY` |
| Generated column | `energy_j = value * interval_s`, computed by the database |
| UPSERT | Replay-safe ingestion with `ON CONFLICT ... DO UPDATE`, plus a Python ingest script |
| Triggers | An alarm trigger for vibration above 2.0 mm/s and an audit trigger for value changes |
| Access control | A view, a read-only connection and a read-only file instead of `GRANT` |
| Stretcher | `BEFORE` vs `AFTER` trigger comparison |

## Key findings

- An unconstrained table accepted every junk row, including text in a REAL column and `'1e999'` stored as infinity.
- Each integrity layer rejected bad data with its own error: entity (`UNIQUE`), referential (`FOREIGN KEY`) and semantic (`CHECK`, `STRICT`).
- `CHECK` lets NULL through, and a plausible but wrong value (400 degC on an 80 degC machine) passes every constraint.
- The UPSERT kept the row count at 3 after running the ingest script twice on the same file.
- The alarm trigger added about 25% to a 10,000-row ingest in my measurement (one run was an outlier).
- With a `BEFORE INSERT` alarm trigger, a replayed reading created a duplicate alarm; with `AFTER INSERT` it did not.

## Files

| File | Purpose |
|---|---|
| `evidence.md` | Full portfolio evidence for Tasks A to 5 |
| `setup.sql` | Creates `sensor` and `reading` |
| `task1.sql`, `task2.sql`, `task3.sql`, `task5.sql` | Statements for each task |
| `ingest.py`, `readings.csv` | UPSERT-based ingestion script and test data |
| `bench.py` | Trigger cost benchmark |
| `*-output.txt` | Raw terminal output for each task |
| `integrity-notes.md` | Pod study notes |
| `../Reflections/ref04.md` | Reflection for this module |

The `.db` files are not committed. They are rebuilt from the scripts.

## How to reproduce (Windows PowerShell, from the repo root)

```powershell
Get-Content Module04/setup.sql | sqlite3 Module04/edge.db
sqlite3 Module04/edge.db ".read Module04/task1.sql"
sqlite3 Module04/edge.db ".read Module04/task2.sql"
python Module04/ingest.py Module04/edge.db Module04/readings.csv
sqlite3 Module04/edge.db ".read Module04/task3.sql"
python Module04/bench.py
```

Foreign keys are off by default in SQLite, so every session must run `PRAGMA foreign_keys = ON;` first (the scripts do this).

## Requirements

- SQLite 3.37 or newer (`STRICT` tables); I used 3.53.4
- Python 3.14