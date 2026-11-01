# PipeTech OS: platform redesign

Analysis and design for replacing PipeTech's legacy web app (`pipetechnz.net/work`) with a modern operations platform, including full product traceability from purchase order to installed pipe.

| File | What it is |
|---|---|
| [`DESIGN.md`](./DESIGN.md) | The blueprint: current-system findings, personas, benchmarks, modules, supply-to-install tracking, architecture, KPIs, roadmap, budget, risks |
| [`COMPETITOR-ANALYSIS.md`](./COMPETITOR-ANALYSIS.md) | Procore vs Simpro across project management, HR, HSE, documents, performance and options, plus the steal list for PipeTech OS |
| [`HANDOFF-PROMPT.md`](./HANDOFF-PROMPT.md) | Brief to paste into another AI assistant or give a developer, with the files to attach |
| [`schema.sql`](./schema.sql) | Starter PostgreSQL/PostGIS data model for jobs, assets and the traceability ledger |
| [`prototype/index.html`](./prototype/index.html) | Clickable concept: Today dashboard, job board, product tracking, pipe passport, field app, council portal. Sample data only |

**Status:** Draft v0.1 for discussion. The live legacy app could not be reached from the build environment, so the current-system audit (DESIGN.md §1) needs finishing once access or screenshots are available.

Changelog:
- v0.3 (30 Oct 2026): prototype adds Safety (reporting with notifiable-event prompt, corrective actions, competency matrix, SDS), Variations (register, approval flow, pricing calculator), Release 1 planner (Must / Next / Later), field-app quick actions, and toasts on demo-only buttons.
- v0.2 (28 Oct 2026): Procore/Simpro competitor analysis; blueprint scope updated (HSE, claims, variations, submittals, plant, performance budget).
- v0.1 (28 Oct 2026): first blueprint, schema and prototype.
