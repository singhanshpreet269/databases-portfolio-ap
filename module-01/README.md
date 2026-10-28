# Module 1: Introduction & Local-First Foundations

[Back to main portfolio](../README.md) | [Reflection 1](../Reflections/ref01.md)

## Summary

I built a local-first monitoring database for the Wittkamp machine-shop scenario. The data is simulated: 172,800 telemetry readings from three CNC machines, stored in a single SQLite file (about 10.5 MB). I queried it from Python and the shell, and I checked an LLM-generated query before trusting it.

## Learning Goals

1. <a id="lg1"></a>**LG1, class:** Explain how this class works (learning goals as the contract, portfolio-based assessment).
2. <a id="lg2"></a>**LG2, portfolio:** Set up my GitHub portfolio from the course template with a clean `.gitignore`.
3. <a id="lg3"></a>**LG3, uv:** Set up the toolchain reproducibly with `uv`.
4. <a id="lg4"></a>**LG4, embedded:** Explain, with a measurement, embedded vs. client/server databases.
5. <a id="lg5"></a>**LG5, load and query:** Load rows into SQLite and query them from Python.
6. <a id="lg6"></a>**LG6, verify:** Verify an LLM-generated query before trusting it.

## Task Inspirations

Proves: [LG1](#lg1)

- **Inspiration 1:** Detect a wearing bearing early. In my simulation, the vibration of `cnc-02` slowly rises over two days. I want to store readings locally and query the trend with SQL, so a machine can warn about wear without a cloud connection.
- **Inspiration 2:** Keep an alarm log on the device itself. A query for `vib_rms > 2.0` found 11,675 alarm rows on `cnc-02` and only 21 and 18 on the other two machines. I want to log such events locally, so nothing is lost when the network is down.

## Task Personal Profile

Proves: [LG1](#lg1)

I am an undergraduate student at HSBI.

- **Programming experience:**   I have learned c++ ,  python 
- **Creative qualities:**  very socialable , love to connect with people
- **Expectations:** I want to understand how databases are structured, learn SQL, and learn how to create and manage databases locally, with reliable, offline-capable data storage.

## Task What is IoT

Proves: [LG1](#lg1)

IoT means physical devices with sensors that collect data and exchange it over a network.

**Domains:** industrial IoT (machine monitoring, predictive maintenance, digital twins), smart home and buildings, smart cities, healthcare and wearables.

**Common protocols:**
- **MQTT:** lightweight publish-subscribe messaging for small devices and weak networks.
- **HTTP/HTTPS and REST:** web communication for dashboards, configuration and cloud services.
- **CoAP:** a lightweight web protocol for low-power devices.
- **Modbus and OPC UA:** industrial protocols for PLCs, sensors and factory equipment.

**Typical devices:** microcontrollers and single-board computers (ESP32, Arduino, Raspberry Pi, STM32), industrial hardware (PLCs, sensors, CNC machines, 3D printers), consumer devices (thermostats, cameras, fitness trackers).

**Challenges:**
- **Unreliable networks:** a device must keep its data when the connection drops. A local database helps here.
- **Storage:** high-frequency sensor data must be stored and queried efficiently on small devices.
- **Security:** small devices are hard to protect against attacks.
- **Limited resources:** little CPU, memory and battery.

**Link to my work:** my simulated telemetry shows how a local database handles the storage and network challenges.

## Evidence

**Goals 2 and 3: Portfolio and toolchain** (Proves: [LG2](#lg2), [LG3](#lg3))
- Repository created from the course template, instructor added as collaborator, `.gitignore` keeps `.venv/`, `*.db`, `*.duckdb`, `*.parquet`, `.env` and `__pycache__/` out of Git.
- `uv` environment: `pyproject.toml`, `uv.lock`, `.python-version`, `uv-check.py` (in the repo root).

**Goal 4: Embedded vs. client/server** (Proves: [LG4](#lg4))
- Database size and row count: [db-size.txt](db-size.txt). `telemetry.db` is about 10.5 MB and holds 172,800 rows.
- Cloud cost (Task 6): this dataset is only about 10.5 MB, read by one dashboard and one weekly report. In the cloud it would need a small server plus a database instance, which means a monthly fee, and Wittkamp (the machine shop) would pay for it, plus someone to run it. A local SQLite file needs none of that.

**Goal 5: Loading and querying** (Proves: [LG5](#lg5))
- Generator (simulated data, fixed seed): [generate_telemetry.py](generate_telemetry.py)
- Loader: [load_telemetry.py](load_telemetry.py)
- Queries: [run_queries.py](run_queries.py), results in [query-results.txt](query-results.txt)
- Stretcher, Task 8 (Datasette): [datasette-task8.md](datasette-task8.md). Filtering `cnc-02` with `vib_rms > 2.0` gave 11,675 rows. Alarm readings: cnc-01 has 21, cnc-02 has 11,675, cnc-03 has 18, so almost all alarms come from the machine with the built-in bearing wear.

**Goal 6: Verify before you trust** (Proves: [LG6](#lg6))
- Task 7: [llm-sql-verification.md](llm-sql-verification.md), [task7.py](task7.py), [task7-output.txt](task7-output.txt)
- The generated query ran, but `EXPLAIN QUERY PLAN` showed a full table scan, and it kept only 43,200 of the 86,400 overnight rows because "overnight" crosses midnight. A sloppy `LIKE '%18%'` version was also wrong (18,102 rows).

**Shell and tools**
- Shell tour: [shell-tour.txt](shell-tour.txt) and [tour.sql](tour.sql)
- Most useful dot-command: `.schema`, because it shows how a table was built without needing the original code.

**SQL Island**
- Answers: [sql-island.md](sql-island.md)

![SQL Island progress](pictures/sql-island-progress.png)

## What I learned

- A database does not need a server. SQLite runs inside my script and keeps all the data in one file.
- Measuring beats guessing: 172,800 rows are only about 10.5 MB, so a cloud setup would be extra cost for no benefit.
- AI-written SQL can look right and still be wrong. Checking row counts and query plans caught mistakes the model did not mention.
- Reproducibility matters: scripts and `uv.lock` let anyone rebuild my results, so the `.db` files stay out of Git.

## Reflection

[Reflection 1](../Reflections/ref01.md)