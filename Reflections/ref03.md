# Reflection 03: LLM-Assisted SQL & Query Profiling

## What I did this block

- Pod study on relational algebra, clause order, plan vocabulary (`SCAN`, `SEARCH`, `COVERING INDEX`) and SQL injection.
- Built `warehouse.db` from `Module03/setup.sql` (60,000 orders, 240,000 order lines).
- Task 1: had an LLM write the revenue-per-city query and checked it with `EXPLAIN QUERY PLAN`.
- Pod Task A: predicted plans on `legacy.db`, added `ix_job_tech`, compared before and after, and broke the index on purpose.
- Task 2: benchmarked three indexes with `bench.py` (each alone and cumulatively, median of 5 runs, run twice).
- Task 3: demonstrated SQL injection and fixed it with bound parameters.
- Task 4: wrote the relational algebra of the dashboard query.
- Task 5 (stretcher): compared GROUP BY, a correlated subquery and a window function.
- **Still open:** [fill in, e.g. Task C with another pod]

## The problem I had with the database files

- **What happened:** [fill in: the exact error or behaviour, for example `warehouse.db` shown as untracked or git-ignored, missing after a pull, locked, or wrong row counts]
- **Cause:** `warehouse.db` is generated data, so it is git-ignored and exists only on the machine that built it. [fill in anything else you found]
- **Fix:** I rebuild it from the script instead of copying the file: `sqlite3 Module03/warehouse.db ".read Module03/setup.sql"`, run from the repository root, then check for 60,000 orders and 240,000 lines.
- **What I learned:** the script is the source of truth and the `.db` is a build artifact. The portfolio should contain the recipe (`setup.sql` plus the README), so anyone can reproduce the database.

## AI verification

I used an LLM to write the Task 1 query and to help with scripts and write-ups. I did not accept any of it without testing.

- **Task 1 query:** I checked three things. `COUNT(DISTINCT customer_id)` is needed, otherwise the count would be about 40,000 order lines per city instead of 500 customers. The date filter must be a half-open range, because the data runs into 2026. The `ordered_on` column must stay bare so an index can be used. I also read the plan (`SCAN ol`, then primary-key `SEARCH` on `o`, `c`, `p`).
- **Prediction vs. reality:** [fill in: what I predicted for Task 1 and Task A, and where I was wrong]
- **Scripts:** I ran every script myself and compared the output with the explanation I was given. For example, I saw the injection payload leak all 2,000 customers, and I saw the dashboard become about 10× slower after an index.
- **Where I did not accept a claim at face value:** the first benchmark run showed slow dashboard rows with unchanged plans. I did not accept those as real. I reran the benchmark, and the slow rows moved, so I treated them as noise and trusted the plan changes.
- **Takeaway:** a query that runs and returns a plausible number is not evidence. The plan, the edge cases and my own algebra check are.

## What the plans taught me

- **Plan vs. time:** a changed plan is stronger evidence than a millisecond difference. `ix_orders_ordered_on` leaves the dashboard plan unchanged but makes the single-day lookup about 20× faster (`SCAN` to `SEARCH`).
- **An index does not guarantee a speedup:** adding `ix_orderline_order` changed the dashboard plan and made it about 10× slower. The year filter keeps about two thirds of the orders, so the index-driven join did tens of thousands of lookups where one scan was cheaper.
- **An index is useless only for a particular query:** the dashboard never used `ix_orderline_product`, but the same index made `product_id = 42` about 150× faster.
- **What defeats an index:** a function around the column (`lower(technician)`, `date(ordered_on)`), a leading `%` in `LIKE`, or an index on the wrong table.
- **Task 5:** the correlated subquery took about 1.2 seconds without an index and 1.6 ms with `orders(customer_id, status)`. The three versions return the same rows, and only the plan shows why one is far slower.

## Mistakes and what they taught me

- I pasted several commands into `sqlite3` at once and they merged into one line, so a command did not run. I now type them one at a time, or run one-line commands from PowerShell.
- I accidentally pasted a terminal command (`uv run …`) into the end of `injection_demo.py`. VS Code's Problems tab showed the errors, and removing the line fixed them.
- `CREATE INDEX ix_job_tech` said "already exists", because the index was left from an earlier attempt. I dropped it, recorded a clean "before", and created it again. A before/after only counts if the "before" really is before.

## The portfolio overview from the lecture

[fill in from your lecture notes: how the portfolio should look.] The module's own checklist gives a starting point:
- One folder per module (`Module03/`) with the scripts that reproduce the work (`setup.sql`, `bench.py`, `injection_demo.py`).
- Evidence rather than claims: prompts, generated SQL, raw `EXPLAIN QUERY PLAN` output and before/after benchmark tables.
- `sql-notes.md` with curiosities and sources.
- A README per module that explains how to set up and run it.
- One reflection per block (`Reflections/refNN.md`) that explicitly covers AI verification.
- Generated files (databases) are not committed, but the scripts that build them are.

## What surprised me

[fill in: for example a wrong plan prediction, the index that made the dashboard slower, or something from `sql-notes.md`]

## Next steps

- Finish Task C with another pod and fill in the open markers in `sql-notes.md`.
- Keep `EXPLAIN QUERY PLAN` before every measurement, as the course asks.
- Use the final project's before/after plan as evidence.