# Module 4: Error log (LLM-assisted work)

I used Claude to work through this module and **ran every command myself to verify it**. These are the mistakes that happened, from the LLM and from me, and what I learned from each.

| # | Whose error | What went wrong | Cause | Fix | Lesson |
|---|---|---|---|---|---|
| 1 | LLM | `mkdir -p`, `touch`, heredocs (`<<'SQL'`) and `chmod` failed in PowerShell | Commands were written for bash, but I work on Windows | Translated: `New-Item`, here-strings piped to `Set-Content`, `IsReadOnly` instead of `chmod 444` | State the operating system and shell up front; the module text assumes Linux |
| 2 | LLM | Predicted that a rejected row might leave a phantom alarm with a `BEFORE` trigger | Assumed trigger effects survive a failed statement | The Task 5 experiment showed no phantom alarm (count stayed 2 to 2); SQLite rolls back the whole statement | An LLM claim is a hypothesis; the experiment settled it |
| 3 | LLM | Long PowerShell commands (here-strings with tables) did not paste or run reliably | Very long pasted blocks break in the terminal | Edited the file by hand in VS Code instead | Prefer short commands or editing files directly |
| 4 | LLM | The Task 3 script cannot be run twice | `CREATE TRIGGER` fails with "already exists" | Drop the triggers or rebuild `edge.db` from `setup.sql` first | Setup scripts should be re-runnable (`DROP ... IF EXISTS`) |
| 5 | Me | Ran `Get-Content Module04/task4-output.txt` before Task 4 had been run | Skipped the step that creates the file | Ran the Task 4 steps in order, then checked the file | Run tasks in order and check that the output file exists |
| 6 | Me | Accidentally cleared `evidence.md`, then had duplicate sections | Overwrote the file and appended twice | Rebuilt it from the saved `*-output.txt` files and committed it | Commit early so git can restore a file |
| 7 | Both | Red `NativeCommandError` text appeared after `sqlite3` errors | PowerShell wraps stderr lines from native commands | Expected behaviour: the real SQLite error is the first line | Read the SQLite message, not the PowerShell wrapper |
| 8 | Both | Copying the terminal table lost the SQL (`...` truncation) | sqlite3 box mode truncates long cells on screen | Saved output with `-list` or `-markdown` through `Tee-Object` | Save output to a file instead of copying it from the screen |

## What I verified myself

- Every rejected statement and its exact error message (Tasks A and 1)
- Row count of 3 after running the ingest twice (Task 2)
- Trigger rows and benchmark numbers, including the outlier run (Task 3)
- Read-only behaviour at connection and file level (Task 4)
- The BEFORE vs AFTER result, which contradicted the LLM's first guess (Task 5)

## Takeaway

The LLM was fast at drafting commands and write-ups, but it was wrong about the shell, and wrong in one prediction. Running each step and keeping the raw output caught every error.