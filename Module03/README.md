# Module 3 - LLM-Assisted SQL & Query Profiling

## Overview

This folder contains my work for Module 3. I built a small warehouse database, asked an LLM to write an analytics query, and then checked that query for correctness and performance with EXPLAIN QUERY PLAN. The main files are setup.sql, q1.sql, q1-result.md, plan.sql and sql-notes.md. All commands are run from the repository root.

## Setup

setup.sql creates four tables (customer, product, orders and order_line) and fills them with generated data using recursive CTEs. The result is 2,000 customers, 500 products, 60,000 orders and 240,000 order lines. I rebuilt the database with `sqlite3 Module03/warehouse.db ".read Module03/setup.sql"` and confirmed the counts with a COUNT query: 60000 orders and 240000 lines. The database file itself is ignored by git, so setup.sql is the file to use for rebuilding it.

## Task 1: LLM query and plan

I gave the LLM the schema and asked for the number of distinct customers and the total revenue per city for orders placed in 2025, sorted by revenue. The query it produced (q1.sql) joins customer, orders, order_line and product, filters with a half-open date range on the bare ordered_on column, groups by city, and uses COUNT(DISTINCT customer_id). Its result (q1-result.md) lists four cities with (500 customers each), and Bielefeld has the highest revenue (about 11.2 million).

I checked correctness in three ways. COUNT(DISTINCT ...) is needed, because without it the count would be the number of order lines per city (about 40,000) rather than the number of customers. The date range covers 2025 only, and since the data runs into 2026 an open upper bound would include extra orders. Keeping the column bare also lets a future index be used.

The EXPLAIN QUERY PLAN output (plan.sql) shows SCAN ol, followed by SEARCH on o, c and p, each by INTEGER PRIMARY KEY, and (temp B-trees for GROUP BY, count(DISTINCT) and ORDER BY). order_line is the largest table and has no index on order_id, so SQLite starts there and looks up the other tables by primary key. (Compared with my prediction, I was right about ... and wrong about ...)

## Task A: Plan safari on legacy.db

legacy.db has no primary keys, no UNIQUE
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