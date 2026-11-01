# Handoff brief for another AI assistant or developer

Paste this first, then attach the files listed below.

---

You're picking up a software design project for **PipeTech**, a New Zealand trenchless pipeline rehabilitation contractor (fold-and-form uPVC lining, CIPP patches, UV TopHat lateral junctions, robotic cutting, CCTV, jetting, manhole rehab, pressure pipe relining). PipeTech is also the NZ distributor for ASOE / AM-LINER II fold-and-form liner. Clients are councils, water entities and civil contractors.

**Goal:** replace PipeTech's legacy ASP.NET Web Forms job system with "PipeTech OS": a phone-first operations platform with full product traceability from purchase order to the exact pipe a product was installed in.

**Attached files:**
1. `DESIGN.md`: the blueprint (personas, modules, supply-to-install tracking, architecture, KPIs, roadmap, budget, risks)
2. `COMPETITOR-ANALYSIS.md`: Procore vs Simpro, and what to adopt or avoid
3. `schema.sql`: starter PostgreSQL/PostGIS data model
4. `prototype/index.html`: single-file clickable prototype (open in a browser). Sample data only

**Decisions already made (don't relitigate without a reason):**
- Hybrid approach: custom-build the core (assets, traceability, QA/hold points, field app, portals); integrate commodity systems (Xero, Microsoft 365, payroll, CCTV software).
- The core record is the **pipe asset** (manhole-to-manhole segment), not the job.
- Status is **derived from hold points**, never typed by hand.
- Field app must work **fully offline**.
- Brand: Green `#65FF00`, Dark Grey `#272422`, Stone `#A8A39D`, Steam `#F2F1EF`, font Switzer. Phone-first, dark/light aware, works on slow rural connections.
- Performance budget: app opens in under 2 s on a mid-range Android; a new technician can finish a pre-start unaided within 5 minutes.

**Still open:**
- Current legacy system not yet audited (no access yet). See DESIGN.md §1 for the checklist.
- Release 1 scope (Must / Next / Later) awaiting the MD's sign-off. The recommendation is in the prototype's "Release 1 plan" page.
- Construction Contracts Act 2002 payment-claim and retention rules to be confirmed by an accountant or lawyer before building claims.
- Manufacturer install parameters must come from current controlled manufacturer manuals. Don't invent temperatures, pressures or times.

**Rules for anyone continuing this:**
- Keep HSE content (SOPs, PPE, notifiable events under HSWA 2015) as drafts until PipeTech's HSE lead approves them.
- No real client, staff, tender or pricing data in demo builds.
- Flag compliance, privacy and security risks as soon as you spot them.
- Keep the same file names and add a changelog line for every change, so versions don't fork.
