# Reflection 02

## Take-away
Don't trust a schema just because it works. Prove its cardinalities and defects with queries, and write the rules as a contract that code can enforce. A join that silently drops rows is more dangerous than an error: in the legacy database, the join on `parts_used` reported success while losing every multi-part job.

**My advice:** draw the ER diagram first, because it makes the problems visible.

## What was good?
- **The ER diagram** was the fun part. Turning a messy set of text columns into a clear picture of machines, parts, jobs and technicians made the structure easy to see.
- **Explaining it to others.** Helping a pod mate understand the diagram forced me to say it simply: an entity is a "thing", a relationship links things, and cardinality tells you how many on each side. That made me understand it better myself.

## What was difficult?
Understanding why the parts list had to become a junction table (`job_part`). The root cause was that I first treated the text column `parts_used` as one value instead of a hidden list of parts, which is a many-to-many relationship. [Add one more thing if you had it, for example deciding whether the technician is an entity or just a name.]

## Exploration and show stoppers
I experimented with the ER diagram in [tool, e.g. Mermaid or diagrams.net] and checked whether the diagram really matched the data, using `COUNT` queries. [Add one thing that got stuck and who you asked, or write "nothing blocked me".]

## Interaction with peers and instructors
I worked on the study tasks with my pod (Smit and Champu). For the exchange in Task C we explained our study logs to a neighbouring pod (Ian, Leviscus, Njeru and Sofia), agreed on the most important points, and shared one image in Discord. [Add one sentence on what they asked or what you learned from them.]

## How did you verify AI suggestions?
I asked an LLM to [sketch the ER model / explain keys, state which]. I did not trust the drawing. I checked it against the data with `COUNT` queries, because a model can draw a relationship the schema never declared. [Add where it was wrong or vague, for example a cardinality it drew that the data did not support.]

## Help and extra work
me and rest guys understand the ER diagram and the many-to-many junction table. it was fun to work with my pod memeber and other with this actuvuty