# Module 3: LLM-Assisted SQL & Query Profiling

## Overview

In this module I built a warehouse database, asked an LLM to write SQL, and then checked that SQL for correctness, performance and safety. The main evidence is `EXPLAIN QUERY PLAN` output, because a plan shows what the engine actually did, while a timing only shows how long it took. All commands are run from the repository root.

| Learning goal | Where it is covered |
|---|---|
| Write complex queries (joins, aggregation, subqueries, windows) | Tasks 1 and 5 |
| Read `EXPLAIN QUERY PLAN` as evidence | Tasks 1, A and 2 |
| Benchmark an index and explain when it is ignored | Tasks A and 2 |
| Generate with an LLM, then verify | Task 1 and `Reflections/ref03.md` |
| Prevent SQL injection | Task 3 |

## Files

| File | Purpose |
|---|---|
| `setup.sql` | Builds `warehouse.db` (2,000 customers, 500 products, 60,000 orders, 240,000 order lines) |
| `q1.sql`, `q1-result.md` | Task 1: the LLM query and its result |
| `plan.sql`, `plan-output.txt` | Task 1: `EXPLAIN QUERY PLAN` of the dashboard query |
| `taskA-before.sql`, `taskA-before.txt`, `taskA-after.txt` | Task A: queries and plans before and after `ix_job_tech` |
| `bench.py`, `bench-output.txt`, `bench-output-run2.txt` | Task 2: benchmark script and the output of two runs |
| `injection_demo.py`, `injection-output.txt` | Task 3: injection drill and its output |
| `task5_bench.py`, `task5-output.txt` | Task 5: three versions of one report, with plans and timings |
| `sql-notes.md` | Notes, curiosities with sources, and the pod comparison |

`warehouse.db` is generated and git-ignored, so it is not in the repository.

## Setup

`setup.sql` creates four tables (`customer`, `product`, `orders`, `order_line`) and fills them with generated data using recursive CTEs.

```powershell
sqlite3 Module03/warehouse.db ".read Module03/setup.sql"
sqlite3 Module03/warehouse.db "SELECT 'orders', COUNT(*) FROM orders UNION ALL SELECT 'lines', COUNT(*) FROM order_line;"
```

Expected: 60,000 orders and 240,000 lines. If the numbers are lower, the script stopped early: delete `warehouse.db` and run it again from the repository root. Scripts run with `uv run Module03/<script>.py`.

## Task 1: LLM query and plan

**Prompt:** I gave the LLM the schema and asked for the number of distinct customers and the total revenue per city for orders placed in 2025, sorted by revenue.

**Result:** the query (`q1.sql`) joins `customer`, `orders`, `order_line` and `product`, filters with a half-open date range, groups by city and uses `COUNT(DISTINCT customer_id)`. The result (`q1-result.md`) has four cities with 500 customers each. Bielefeld has the highest revenue (about 11.2 million).

**Correctness checks:**
- `COUNT(DISTINCT customer_id)` is needed. Without it the count would be the number of order lines per city (about 40,000), not the number of customers.
- The date range is `>= '2025-01-01' AND < '2026-01-01'`. The data runs into 2026, so an open upper bound would include extra orders.
- The `ordered_on` column is left bare, so an index can be used.

**Plan (`plan-output.txt`):** `SCAN ol`, then `SEARCH` on `o`, `c` and `p`, each by `INTEGER PRIMARY KEY`, plus temp B-trees for `GROUP BY`, `count(DISTINCT)` and `ORDER BY`. `order_line` is the largest table and has no index on `order_id`, so SQLite reads it first and looks up the other tables by primary key.

**Prediction vs. reality:** [fill in: what I predicted, and where I was right and wrong]

## Task A: Plan safari on `legacy.db`

`legacy.db` has no primary keys, no unique columns and no indexes, so I predicted `SCAN` for all three queries. That was confirmed.

| Query | Before the index | After `ix_job_tech` |
|---|---|---|
| `maint_job WHERE technician = 'Beier'` | `SCAN maint_job` | `SEARCH maint_job USING INDEX ix_job_tech (technician=?)` |
| `machine WHERE machine_name = 'cnc-02'` | `SCAN machine` | `SCAN machine` |
| `maint_job WHERE technician LIKE '%ei%'` | `SCAN maint_job` | `SCAN maint_job` |

- I added `ix_job_tech` on `maint_job(technician)`. Only the first query changed.
- The `machine` query reads a different table, so this index cannot help it.
- A leading `%` in `LIKE` cannot use an index, because the index is sorted by the start of the value.
- **Break it on purpose:** `WHERE lower(technician) = 'beier'` went back to `SCAN`, because the function hides the stored values from the index.
- **Takeaway:** an index only helps when the query matches how the index is stored. Two of three queries got nothing from it, and those negatives taught me the most.

## Task B: Algebra check

**Query:** `SELECT * FROM maint_job WHERE technician = 'Beier'`

**Algebra:** σ_{technician = 'Beier'}(maint_job). The σ comes from `WHERE` and the relation from `FROM`. There is no π, because `SELECT *` keeps all columns.

**My version vs. the LLM's:** [fill in: same, or different in this way]

**Link to Task A:** σ is the step an index speeds up. Without one SQLite scans the whole table; with one it searches directly (`SCAN` to `SEARCH`).

## Task 2: Index benchmark

**Method:** `bench.py` (SQLite 3.53.4) tests three indexes, each alone and then cumulatively. For every setup it records the `EXPLAIN QUERY PLAN` and the median of 5 runs. Queries too fast to time once are amortised over 200 executions. I ran the benchmark twice.

| Setup | dashboard | single_day | product_filter | function_wrapped |
|---|---|---|---|---|
| baseline | 165.0 ms | 4.07 ms | 13.2 ms | 10.5 ms |
| only `ordered_on` | 276.3 ms | 0.64 ms | 23.1 ms | 8.1 ms |
| only `orderline_order` | 163.6 ms | 4.12 ms | 13.1 ms | 8.0 ms |
| only `orderline_product` | 161.0 ms | 3.99 ms | 0.084 ms | 8.0 ms |
| + `ordered_on` | 163.3 ms | 0.34 ms | 13.2 ms | 8.0 ms |
| + `orderline_order` | 1624.0 ms | 0.21 ms | 14.0 ms | 7.9 ms |
| + `orderline_product` | 1785.9 ms | 0.29 ms | 0.094 ms | 9.1 ms |

**Plan evidence:**
- `single_day`: `SCAN o` became `SEARCH o USING INDEX ix_orders_ordered_on (ordered_on=?)`.
- `product_filter`: `SCAN order_line` became `SEARCH order_line USING COVERING INDEX ix_orderline_product (product_id=?)`.
- `function_wrapped` (`date(ordered_on) = …`): `SCAN o` with every index.
- `dashboard`: the plan is unchanged with `ix_orders_ordered_on`. With `ix_orderline_order` it becomes `SEARCH o USING INDEX ix_orders_ordered_on (…)` followed by `SEARCH ol USING INDEX ix_orderline_order (order_id=?)`.

**Findings:**
1. **Plan and time are different questions.** `ix_orders_ordered_on` leaves the dashboard plan unchanged but makes the single-day lookup about 6 to 20× faster. Dashboard rows with an unchanged plan but different times (276 ms against 165 ms) moved around between my two runs, so I treat them as noise.
2. **Negative result.** Adding `ix_orderline_order` changed the dashboard plan and made it about 10× slower in both runs. The year filter keeps about two thirds of the orders, so the index-driven join did tens of thousands of lookups where one sequential scan was cheaper. An index changes the plan; it does not guarantee a speedup.
3. **Useless for one query, useful for another.** The dashboard never uses `ix_orderline_product`, because it reaches `product` through its primary key. The same index makes `WHERE product_id = 42` about 150× faster, using a covering index.
4. **A function around the column defeats the index.** `date(ordered_on) = …` stays a `SCAN`; `ordered_on = …` uses the index.

**Limits:** timings come from one laptop and vary between runs, so I trust plan changes and large effects more than small millisecond differences.

## Task 3: Injection drill

`injection_demo.py` runs the same lookup with string formatting (vulnerable) and with a bound parameter (safe).

| Input | Vulnerable | Safe (bound parameter) |
|---|---|---|
| `Customer 1` | `[(1, 'Customer 1')]` | n/a |
| `O'Brien` | crashed: `near "Brien": syntax error` | `[]` |
| `' OR '1'='1` | 2,000 rows leaked | `[]` |
| `x' UNION SELECT product_id, sku FROM product WHERE '1'='1` | rows from `product` | `[]` |

The apostrophe crash is the support agent's bug from the module story. The payload `' OR '1'='1` makes the condition true for every row, and the `UNION` payload reads a different table through the same hole.

**Why escaping or filtering `'` by hand is not a real fix:**
- **Context:** quotes only matter inside a string literal. In a numeric context (`WHERE id = 1 OR 1=1`) there is nothing to escape, and table or column names cannot be bound as values at all, so they need an allow-list.
- **Encodings:** escaping depends on how the database and driver decode bytes, and edge cases can turn escaped input back into a working quote.
- **Blacklists lose:** filtering `'`, `--` or `UNION` has to anticipate every trick, and an attacker needs only one miss.
- **Responsibility:** with escaping, every developer must remember it on every query. With bound parameters, the SQL and the values are sent separately, so the value is never parsed as SQL.

## Task 4: Relational algebra of the dashboard query

I wrote the query as one nested expression, translating clause by clause:

τ_{revenue DESC}( π_{city, customers, revenue}( γ_{city; COUNT(DISTINCT customer_id) → customers, SUM(qty·price) → revenue}( σ_{ordered_on ≥ '2025-01-01' ∧ ordered_on < '2026-01-01'}( customer ⋈ orders ⋈ order_line ⋈ product ) ) ) )

Each ⋈ uses its `ON` condition. The mapping is `JOIN … ON` to ⋈, `WHERE` to σ, `GROUP BY` with the aggregates to γ, `SELECT` to π and `ORDER BY` to τ.

The LLM's version differs in form but not in meaning. It applies σ to `orders` before the joins (pushdown), leaves out π because γ already outputs exactly those three columns, and splits the expression into numbered steps. The two forms are equivalent because the filter uses only `ordered_on`, a column that exists only in `orders`.

The algebra describes what the result is, not how to compute it. SQLite's plan (`SCAN ol` first, then primary-key `SEARCH`) reaches the same rows by a different route. τ is an extension to classic relational algebra, because relations are unordered.

## Task 5 (stretcher): Late orders per customer

I rewrote the `GROUP BY` report as a correlated subquery and as a window function. `task5_bench.py` runs all three (median of 3 runs); all three return the same 400 rows.

| Version | No extra index | With `orders(customer_id, status)` |
|---|---|---|
| GROUP BY | 9.6 ms | 7.5 ms |
| Correlated subquery | 1248.1 ms | 1.6 ms |
| Window function | 20.0 ms | 18.3 ms |

- **Correlated subquery, no index:** the select-list subquery shows `SCAN o`, so `orders` is rescanned for each customer. It is about 130× slower than `GROUP BY`.
- **With the index:** both subquery lookups become `SEARCH o USING COVERING INDEX (customer_id=? AND status=?)`, and the time drops to 1.6 ms, about 780× faster.
- **Window function:** it produces one row per late order, so it needs `DISTINCT` to collapse the rows to one per customer. It is no faster than `GROUP BY` and harder to read for this report. The index changes its plan, but not its time beyond noise.
- **Readability:** `GROUP BY` is clearest here. A window function pays off when each row needs its own detail next to the aggregate.
- **What the LLM produced by default:** [fill in after asking it]

## Task C: Comparison with another pod

[fill in: SQLite versions compared, whether plans matched, the plan that surprised us most, and what we swapped]

## Status

- [x] Setup, Task 1
- [x] Task A, Task B
- [x] Tasks 2, 3, 4
- [x] Task 5 (stretcher)
- [ ] Task C
- [ ] `Reflections/ref03.md`