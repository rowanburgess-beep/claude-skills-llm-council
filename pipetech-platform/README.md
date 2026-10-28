# PipeTech OS: platform redesign

Analysis and design for replacing PipeTech's legacy web app (`pipetechnz.net/work`) with a modern operations platform, including full product traceability from purchase order to installed pipe.

| File | What it is |
|---|---|
| [`DESIGN.md`](./DESIGN.md) | The blueprint: current-system findings, personas, benchmarks, modules, supply-to-install tracking, architecture, KPIs, roadmap, budget, risks |
| [`schema.sql`](./schema.sql) | Starter PostgreSQL/PostGIS data model for jobs, assets and the traceability ledger |
| [`prototype/index.html`](./prototype/index.html) | Clickable concept: Today dashboard, job board, product tracking, pipe passport, field app, council portal. Sample data only |

**Status:** Draft v0.1 for discussion. The live legacy app could not be reached from the build environment, so the current-system audit (DESIGN.md §1) needs finishing once access or screenshots are available.

Changelog: v0.1 (28 Oct 2026) first blueprint, schema and prototype.
