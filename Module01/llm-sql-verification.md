# Task 7: LLM-Assisted SQL Profiling

**Learning goal:** Goal 6, verify an LLM-generated query before trusting it. The code is in [task7.py](task7.py) and the raw output is in [task7-output.txt](task7-output.txt).

## 1. Prompt

> Here is my SQLite table: readings(ts TEXT, machine TEXT, temp_c REAL, vib_rms REAL, spindle_load REAL). Write a query that returns, for each machine, the average spindle load for readings taken overnight (after 18:00), ordered by average load descending.

## 2. Generated SQL

```sql
SELECT machine, AVG(spindle_load) AS avg_spindle_load
FROM readings
WHERE TIME(ts) > '18:00:00'
GROUP BY machine
ORDER BY avg_spindle_load DESC;
```

## 3. Run it

The query runs without errors:

| machine | avg spindle load |
|---|---|
| cnc-03 | 60.433 |
| cnc-01 | 60.367 |
| cnc-02 | 60.356 |

## 4. Profile it (`EXPLAIN QUERY PLAN`)

```text
SCAN readings
USE TEMP B-TREE FOR GROUP BY
USE TEMP B-TREE FOR ORDER BY
```

`SCAN readings` means a full table scan of all 172,800 rows. There is no index on `ts`, so a scan is expected here. Because the filter wraps the column in `TIME(ts)`, even an index on `ts` could not be used for it.

## 5. Break it

I compared the generated query with two other versions:

| Version | Rows used | Result (highest to lowest) |
|---|---|---|
| Generated: `TIME(ts) > '18:00:00'` | 43,200 | cnc-03 60.43, cnc-01 60.37, cnc-02 60.36 |
| Sloppy: `ts LIKE '%18%'` | 18,102 | cnc-03 61.12, cnc-02 61.02, cnc-01 61.00 |
| Whole night (18:00 to 06:00, across midnight) | [add count] | cnc-02 60.21, cnc-03 60.20, cnc-01 60.18 |

Total rows: 172,800, so the generated query keeps 25% of the data.

- **The LIKE version is wrong.** `'%18%'` matches "18" anywhere in the timestamp string, including minutes and seconds (for example `06:18:03`). That is why it gets only 18,102 rows and a wrong average.
- **The generated query is correct only for the literal wording.** The prompt said "after 18:00", and the query does exactly that. But "overnight" runs past midnight, so readings from 00:00 to 06:00 are missing.
- **The missing hours change the answer.** In the whole-night version, the order of the machines is different (cnc-02 is first, not last).

## 6. Verification paragraph

The model wrote a syntactically correct query with `GROUP BY`, `AVG` and `ORDER BY ... DESC`, and the `TIME(ts)` comparison works on my text timestamps. What it got wrong was the meaning of "overnight": it only keeps 18:00 to 23:59 and drops the hours after midnight, so it used 43,200 of the rows a whole night would use, and the machine ranking changed. It also forces a full table scan because `TIME(ts)` wraps the column. I verified this in Python ([task7.py](task7.py)) by running the query, reading `EXPLAIN QUERY PLAN`, comparing the row counts (172,800 total, 43,200 after 18:00, 18,102 for the sloppy `LIKE`), and writing my own whole-night version to compare the results. One more observation: the averages for the three machines differ by less than 0.1, and the generator adds only random noise to spindle load per machine, so the ranking itself is not very meaningful. The row counts are the more reliable check.