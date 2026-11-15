**What I did:** I built an SQLite edge database for machine telemetry and made the database itself enforce the rules: constraints and `STRICT` tables, a generated column, UPSERT for replay-safe ingestion, triggers for alarms and auditing, and read-only access control without a server.

**What I learned:**
- Integrity has three layers (entity, referential, semantic), and I saw each one reject bad data with its own error message.
- `CHECK` lets NULL through, so `NOT NULL` is a separate job. Constraints also only block impossible values: 400 degC on an 80 degC machine passes everything.
- Foreign keys are off by default in SQLite and must be switched on in every connection.
- Timing matters for triggers. In my experiment a `BEFORE INSERT` alarm trigger created a duplicate alarm when a reading was replayed through the UPSERT, while `AFTER INSERT` did not. That is why `AFTER` was the right choice here.
- A trigger costs time: about 25% more on a 10,000-row ingest in my measurement, though one run was an outlier.

**What was hard:** Working in Windows PowerShell, because the module's commands are written for bash (heredocs, `chmod`). I had to translate them, for example using the `IsReadOnly` attribute instead of `chmod 444`.

**What I would do differently / next steps:** Run the benchmark more times to smooth out the outlier, and add per-sensor limits to catch plausible but wrong values.