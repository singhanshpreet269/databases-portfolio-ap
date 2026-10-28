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