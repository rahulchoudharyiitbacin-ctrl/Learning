# Fable coordinator + Opus workers

A Claude Code setup where **Fable 5.2** plans and verifies, and hands the work to cheaper subagents.

```
.claude/agents/research-worker.md   Opus 5.5 worker: reasoning, coding, experiments
.claude/agents/reader.md            Sonnet 5.5 worker: reading and extraction
CLAUDE.md                           Coordinator instructions (loaded automatically)
```

## How to use it

1. Start a new Claude Code session in this folder.
2. Set the session's model to **Fable 5.2** in the model picker. That makes it the coordinator; the workers run on their own models whatever you pick.
3. Give it a problem that splits into parts. For example:

   > Investigate whether every even number up to 10 million is a sum of two primes in at least N ways, find how N grows, and compare with what the literature predicts. Delegate the parts.

4. Watch it plan in `notes/plan.md`, send tasks to the workers, check their reports, and write `notes/findings.md`.

You can also name a worker directly, for example: "Have the reader find the three most cited papers on X."

## Changing the team

- To change a worker's model, edit `model:` in its file (`opus`, `sonnet`, `haiku`, or `inherit` to match the session).
- To add a specialist (such as a Lean proof checker or a reviewer), add another `.md` file in `.claude/agents/` with a clear `description`. The coordinator picks workers from their descriptions.
- Run `/agents` in a Claude Code terminal to list and edit them.

## Cost

Fable 5.2 costs $8/$40 per million input/output tokens, Opus 5.5 $4/$20 and Sonnet 5.5 $2/$10. The savings come from workers doing the bulk reading and grinding while Fable spends its tokens on planning and checking.
