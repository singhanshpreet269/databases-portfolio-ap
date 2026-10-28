Task A: Plan safari on legacy.db

Legacy DB has no PKs, no unique columns, no indexes, so my prediction was SCAN for all three queries. Confirmed: technician, machine and LIKE '%ei%' all showed SCAN.
Added ix_job_tech on maint_job(technician). Only the technician = 'Beier' query changed, to SEARCH using ix_job_tech.
The machine query uses a different table, and a leading % in LIKE can’t use an index, so both stayed SCAN.
Tried to break it: WHERE lower(technician) = 'beier' went back to SCAN, because the function hides the stored values from the index.
Takeaway: an index only helps when the query matches how the index is stored. Two of three queries got nothing from it, and those negatives taught me the most.

Task B: Algebra check

Query: SELECT * FROM maint_job WHERE technician = 'Beier'
Algebra: σ_{technician = ‘Beier’}(maint_job). σ comes from WHERE, the relation from FROM, and there is no π because SELECT * keeps all columns.
My own version vs. Claude’s: same / different in this way: (fill in)
Link to Task A: σ is the step an index speeds up. Without it SQLite scans the whole table, with it SQLite searches directly (SCAN → SEARCH).
using the table from my last message, plus the upper() plan. A an index helps only when the WHERE matches how the index is built. The wrong table, a function around the column, or a leading % all bring back SCAN.

When we type commands in sqlite3, enter them one at a time and press Enter after each. Pasting several lines at once is what caused the merged line.
## Task 2: Index benchmark (run 2, SQLite 3.53.4, median ms)

| Setup | dashboard | single_day | product_filter | function_wrapped |
|---|---|---|---|---|
| baseline | 165.0 | 4.07 | 13.2 | 10.5 |
| only `ordered_on` | 276.3 | 0.64 | 23.1 | 8.1 |
| only `orderline_order` | 163.6 | 4.12 | 13.1 | 8.0 |
| only `orderline_product` | 161.0 | 3.99 | 0.084 | 8.0 |
| + `ordered_on` | 163.3 | 0.34 | 13.2 | 8.0 |
| + `orderline_order` | 1624.0 | 0.21 | 14.0 | 7.9 |
| + `orderline_product` | 1785.9 | 0.29 | 0.094 | 9.1 |
## Task 5 (stretcher): Late orders per customer

I rewrote the GROUP BY report as a correlated subquery and as a window function (`COUNT(*) OVER (PARTITION BY customer_id)`). `task5_bench.py` runs all three (median of 3 runs, SQLite 3.53.4); all three return identical rows (400 customers).

| Version | No extra index | With `orders(customer_id, status)` |
|---|---|---|
| GROUP BY | 9.6 ms | 7.5 ms |
| Correlated subquery | 1248.1 ms | 1.6 ms |
| Window function | 20.0 ms | 18.3 ms |

- **Correlated subquery, no index:** the select-list subquery shows `SCAN o` under `CORRELATED SCALAR SUBQUERY 1`, so `orders` is rescanned for each customer. It is about 130× slower than GROUP BY. SQLite built a temporary `AUTOMATIC PARTIAL COVERING INDEX` for the `EXISTS` part, but not for the scalar subquery.
- **With `ix_orders_cust_status`:** both subquery lookups become `SEARCH o USING COVERING INDEX (customer_id=? AND status=?)`, and the time drops to 1.6 ms. It becomes the fastest version, about 780× faster than before.
- **GROUP BY and window:** the index changes their plans to a covering scan, but the timing differences (9.6 to 7.5 ms, 20.0 to 18.3 ms) are within noise. These versions read all late orders either way.
- **Window function:** it produces one row per late order, so it needs `DISTINCT` to collapse the rows back to one per customer. It is no faster than GROUP BY and is harder to read for this report.
- **Readability:** GROUP BY is the clearest here. A window function pays off when each row needs its own detail next to the aggregate, for example every late order together with that customer's total.
- **What the LLM produced by default:** [fill in after asking it]
- **Takeaway:** the three queries mean the same thing, but only the plan shows that one of them is about 130× slower. The right index fixed the slow version without changing the SQL, and it did not change the other two in any way I can measure.