# Reflection 01

## Take-away
A database does not always need a server. For small, local data, a single SQLite file is simpler, cheaper and has fewer things that can break. My 172,800 simulated readings fit in a 10.5 MB file, with no administrator and no monthly bill.

**My advice:** measure first, and add a server only when a real requirement (many concurrent writers, several locations) forces it.

## What was good?
- **SQL Island** was fun and made SQL feel natural before I wrote any queries myself.
- The whole pipeline (generate data, load it, query it) was small enough to understand completely.
- **`uv`** made the setup reproducible: one fixed Python and locked library versions.

## What was difficult?
Getting the tools to work on Windows. The VS Code Code Runner play button used the wrong Python, so my scripts ran outside the `uv` environment. The root cause was that I did not run everything through `uv run`. Now I always start scripts from the terminal with `uv run`.

## Exploration and show stoppers
In the sqlite3 shell I explored the dot-commands. `.schema` became my favourite, because it shows how a table was built without needing the original code. [Add one thing that got you stuck, and how you solved it or who you asked.]

## Interaction with peers and instructors
We formed our pod by comparing skills and expectations, and we discussed the embedded vs. client/server question together. [Add one sentence on how your pod worked, or what feedback you got from the instructor.]

## How did you verify AI suggestions?
I asked an LLM for a query that returns the average spindle load per machine for overnight readings. I did not trust the answer. I did three checks:

1. **Run it:** it executed without errors.
2. **Profile it:** `EXPLAIN QUERY PLAN` showed `SCAN readings`, a full table scan of all 172,800 rows.
3. **Break it:** I compared it with a sloppy `LIKE '%18%'` version and a whole-night version, and counted the rows each one used.

**What it got right:** the query structure (`GROUP BY`, `AVG`, `ORDER BY ... DESC`) and the time filter on my text timestamps.
**What it got wrong:** "overnight" crosses midnight, but the query only kept readings after 18:00, so it used 43,200 of the 86,400 overnight rows. The machine ranking changed because of this. The `LIKE` version was worse (18,102 rows), since it matched "18" in minutes and seconds too.
**How I checked:** by comparing row counts and results in Python, not by trusting how correct the query looked.

Details: [llm-sql-verification.md](../Module01/llm-sql-verification.md)

## Help and extra work
I helped other pod meme,bers set up GitHub and VS Code, including cloning their own repository from the template instead of the template itself. [Add who helped you and whether it was useful.]