# Module 2: Data Contracts & Reading Legacy Schemas (ERD Audits)

[Back to main portfolio](../README.md) | [Reflection 2](../Reflections/ref02.md)

## Summary

I audited a deliberately flawed legacy maintenance database (`legacy.db`). I reconstructed the ER model it should have had, proved its integrity defects with queries, and wrote the corrected schema as an executable data contract in Python.

## Learning Goals

1. <a id="lg1"></a>**LG1, reconstruct:** Reconstruct an ER/EER model (entities, attributes, keys, relationships, cardinalities) from an undocumented SQL schema.
2. <a id="lg2"></a>**LG2, defects:** Identify integrity defects (missing foreign keys, orphan rows, redundant data, normalization violations) with queries, not intuition.
3. <a id="lg3"></a>**LG3, keys:** Distinguish an entity relationship from an attribute, and a surrogate key from a natural key, and justify the choice.
4. <a id="lg4"></a>**LG4, contract:** Express a schema as a code-first data contract (Pydantic / SQLAlchemy) that an application can enforce.
5. <a id="lg5"></a>**LG5, requirements:** Write the requirements the schema forgot: the business rules nobody encoded.

## Pod study (Tasks A to C)

Proves: [LG1](#lg1), [LG3](#lg3)

- **Tasks A and B (study, words to sketch):** done with my pod, [Smit](https://github.com/[username]/[repo]), [Champu](https://github.com/[username]/[repo]) and [Sam Beza](https://github.com/[username]/[repo]). They cover my references, what I googled, LLM Q&A with how I verified each answer, my two best found ER sketches, and four drawn examples (1:1, 1:n, m:n, entity vs. attribute) with one `CREATE TABLE` and `COUNT` proof.
- **Task C (explain and share):** done with the neighbouring pod: [Ian](https://github.com/[username]/[repo]), [Leviscus](https://github.com/[username]/[repo]), [Njeru](https://github.com/[username]/[repo]) and [Sofia](https://github.com/[username]/[repo]). We explained our study logs to each other, agreed on the most important points, and shared one image in Discord. The "Agreed learning (pod discussion)" section is in my study log.
- Files: [study-log.md](study-log.md)

## Task 1: Reconstruct the ER model

Proves: [LG1](#lg1), [LG3](#lg3)

This task was executed by myself.

- Rebuilt the intended entities (Machine, Part, MaintenanceJob, Technician) from the legacy schema.
- Proved the cardinalities by counting, not guessing. Jobs and parts are many-to-many, hidden in a text column.
- Files: [setup.sql](setup.sql) (builds `legacy.db`), [er-audit.md](er-audit.md), [cardinality-proof.txt](cardinality-proof.txt)

![ER diagram](pictures/er-diagram.png)

## Task 2: Find the integrity defects with queries

Proves: [LG2](#lg2)

This task was executed by myself.

- Proved five defects with queries:
  1. an orphan job (machine `cnc-05` does not exist)
  2. a duplicate part (`P-1003` appears twice)
  3. a price stored as text
  4. install dates that are not dates
  5. a comma-separated parts list that silently drops multi-part jobs
- Each defect has a one-line note on what breaks in production, in [er-audit.md](er-audit.md).
- Files: [defects.py](defects.py), [defects-results.txt](defects-results.txt)

## Task 3: Write the data contract in code

Proves: [LG4](#lg4), [LG5](#lg5)

This task was executed by myself.

- Pydantic validates data in the app. SQLAlchemy enforces it in the database (foreign keys, `UNIQUE` serial number, `NUMERIC` price, and a `job_part` junction table that fixes the comma-separated list).
- **Where each rule lives:** the `SN-` serial prefix and the real date type are checked in the Pydantic model, before data reaches the database. Foreign keys, `UNIQUE` and `NOT NULL` are enforced by the database, so they hold even if a different program writes to it.
- Tested that the contract rejects bad data.
- Files: [contract.py](contract.py), [emitted-ddl.txt](emitted-ddl.txt), [check_contract.py](check_contract.py), [contract-rejects-bad-data.txt](contract-rejects-bad-data.txt)

## Stretcher tasks (Tasks 4 and 5)

Proves: [LG3](#lg3)

- **Task 4, inheritance:** I modeled machines that are CNC mills and injection molders in two ways (one table with a type column, and separate tables joined by key), and