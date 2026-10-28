# Personal Portfolio for the Databases class at HSBI

Author: Anshpreet Singh, B.Eng. Industrial Engineering, Hochschule Bielefeld (HSBI)

My pod: [Sam Beza](https://github.com/[username]/[repo]), [Smit](https://github.com/[username]/[repo]) and [Champu](https://github.com/[username]/[repo]).

My team for the final project: [add names and portfolio links once teams are formed].

Our team final project repository is [here]([add link when it exists]).

My personal profile and expectations are [here](module-01/README.md#task-personal-profile).

## About this portfolio

This repository is my proof of learning. There are no exams: each module has learning goals, and I show evidence that I reached them with scripts, outputs, measurements and short reflections.

Anyone should be able to rebuild my results from the scripts alone. That is why databases (`*.db`) and secrets are never committed to Git, only the code that creates them.

## Table of Contents

- [Module 1: Introduction and Local-First Foundations](module-01/README.md), [Reflection 1](Reflections/ref01.md)
  - 172,800 simulated machine readings in one 10.5 MB SQLite file, queried from Python and the shell, plus a verified LLM-generated query.
- [Module 2: Data Contracts and Legacy Schemas](Module02/README.md), [Reflection 2](Reflections/ref02.md)
  - Audit of a flawed maintenance database: five integrity defects proved with queries, and the corrected schema as a Pydantic and SQLAlchemy contract.
- [Module 3: LLM-Assisted SQL, Profiling and Security](Module03/README.md), [Reflection 3](Reflections/ref03.md)
  - [In progress: add a one-line description when finished.]

## Key results so far

- **No server needed:** 172,800 readings fit in a 10.5 MB file, so a cloud database would add cost and failure points with no benefit.
- **Verify before you trust:** an AI-written query ran without errors but dropped half of the overnight readings. Only row counts and `EXPLAIN QUERY PLAN` revealed it.
- **Prove, don't describe:** a join on a comma-separated column reported success while silently losing every multi-part job.

## Quick start: rebuild everything

You need [uv](https://docs.astral.sh/uv/) and Git. Run these at the repo root:

```bash
git clone https://github.com/[your-username]/databases-portfolio.git
cd databases-portfolio
uv sync                                          # installs the pinned Python and libraries
uv run uv-check.py                               # checks the environment
uv run python module-01/generate_telemetry.py    # creates the simulated data (CSV)
uv run python module-01/load_telemetry.py        # loads the CSV into SQLite
uv run python module-01/run_queries.py           # runs the queries
```

`uv run` always uses the Python version pinned in `.python-version` and the library versions locked in `uv.lock`, so the results are the same on every machine.

## Tools

| Tool | What it does |
|---|---|
| **uv** | Installs a fixed Python and the libraries, reproducibly |
| **SQLite** | The embedded database (inside Python and the `sqlite3` shell) |
| **Datasette** | Browse a SQLite file in a web browser |
| **Pydantic, SQLAlchemy** | Data validation and database schema in code |
| **VS Code, Git, GitHub** | Editing, commits and hosting the portfolio |

## Miscellaneous

- [Hardware in my/our possession](Hardware/README.md)

