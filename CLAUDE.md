# CLAUDE.md

Guidance for Claude Code (and other AI assistants) working in this repository.

## What this repo is

This is a **single Claude skill package**, not an application. It distributes one
skill — `llm-council` — that end users install into their own Claude Code or
Claude Cowork setup. There is no build system, no dependencies, no tests, and no
source code in the traditional sense. The entire "product" is two markdown files.

## File structure

```
.
├── README.md   # Human-facing landing page (GitHub-rendered). Install + usage instructions
│               # written for non-technical readers.
└── SKILL.md    # The actual skill definition Claude loads and executes.
```

There is no other code, no package manifest, no CI config. Any new file added to
this repo should have a clear reason to exist — this project is intentionally minimal.

## SKILL.md — the skill definition

`SKILL.md` is a Claude Code / Claude Cowork **Skill** file: YAML frontmatter plus a
markdown body of instructions that Claude follows verbatim when the skill is invoked.

- **Frontmatter** (`name`, `description`): The `description` field is doing double duty —
  it's both a human-readable summary and the **trigger specification** that tells
  Claude when to activate the skill (mandatory trigger phrases vs. strong/contextual
  triggers vs. explicit non-triggers). When editing the description, preserve this
  structure; it directly controls activation behavior.
- **Body**: A step-by-step runbook for a 6-step "council" workflow:
  1. Frame the question (scan workspace for context, e.g. `CLAUDE.md`, `memory/` folder)
  2. Convene 5 advisor sub-agents in parallel (Contrarian, First Principles Thinker,
     Expansionist, Outsider, Executor)
  3. Peer review — advisors anonymously critique each other's responses
  4. Chairman synthesis — one agent produces the final verdict
  5. Present the verdict in chat (markdown, no files/HTML generated)
  6. Optionally save a transcript

The prompt templates embedded in each step (sub-agent prompt, reviewer prompt,
chairman prompt) are the actual instructions an executing Claude will send to
sub-agents — they are executable spec, not documentation. Treat wording changes
here as behavior changes, not copy edits.

## README.md — the landing page

Written for a non-technical audience (explicitly explains "what's GitHub?" and
"what's a skill?"). Two install paths are documented: asking Claude to fetch and
install the skill directly from the GitHub URL, or manually downloading `SKILL.md`
and asking Claude to place it. Keep README.md's "when to use it" examples and
install instructions in sync with SKILL.md if either changes.

## Conventions when editing this repo

- **Keep README.md and SKILL.md in sync.** They duplicate content on purpose
  (e.g. "good/bad council questions," the credit line) — one is the pitch, the
  other is the executable spec. If you change the council's behavior (steps,
  advisors, output format) in `SKILL.md`, check whether README.md's description
  of "what it does" / "how to use it" needs a matching update.
- **Preserve attribution.** Credit to Ole Lehmann (skill author) and Andrej
  Karpathy (original LLM Council methodology) appears in both files — don't
  remove it.
- **No build/test tooling exists or is expected.** Don't add package.json,
  linters, or CI unless the user explicitly asks — this is a plain-markdown
  content repo.
- **Changes to the trigger phrases in SKILL.md's frontmatter `description`
  are high-impact** — they determine when the skill fires in a user's Claude
  session. Be precise and conservative when adjusting them; overly broad
  triggers cause the skill to activate on unrelated questions.
- **The 5-advisor / peer-review / chairman structure is the core mechanic.**
  If asked to modify the workflow, preserve the "important notes" section at
  the end of SKILL.md (parallel spawning, anonymized peer review, chairman may
  override majority, don't council trivial questions) — these are documented
  failure modes the author already identified.

## Git workflow

- Default branch: `main`.
- Commit history so far is small and linear (README rewrites, initial commit).
  No PR template, no CI checks currently configured in this repo.
