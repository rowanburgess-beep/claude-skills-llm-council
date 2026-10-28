# PipeTech OS: Platform Analysis & System Design

**Prepared for:** Rowan Burgess, Managing Director, PipeTech
**Date:** 28 October 2026
**Status:** Draft v0.1 for discussion. Not an approved specification.
**Working name:** "PipeTech OS". *(Opinion: pick a name crews will actually say out loud. "The Hub" or "Pipeline" both work too.)*

---

## 0. What I could and couldn't see (read this first)

| Item | Status |
|---|---|
| Live app at `https://www.pipetechnz.net/work/default.aspx` | **Not reached.** This cloud session's network policy blocks the host. The app is also very likely behind a login. |
| PipeTech services, brand, standards | **Confirmed** from your Notion: *PipeTech HQ → Operating Context, Oct 2026 Process Capture, Web/App Development*. |
| ASOE / AM-LINER II distribution | **Public source:** Trenchless Australasia (Nov 2023) names PipeTech as sole NZ licensee distributor for AM-LINER II and ASOE FFPP uPVC ranges. |

**So, honest status:** sections 1–2 are what can be *inferred* about the current system, plus a checklist to finish the audit properly. Everything from section 3 onwards is the new design, which doesn't depend on the old screens.

**To complete the current-system audit, I need one of:**
1. `www.pipetechnz.net` added to this environment's **Allowed domains** (environment settings → Network access), plus a test login with read-only access; **or**
2. Screenshots of every main screen, plus a short screen recording of a "typical day" (booking a job → closing it out).

---

## 1. Current system: what we can infer

### 1.1 From the URL alone
- **`default.aspx` = ASP.NET Web Forms.** This is Microsoft's 2002-era web framework. It still runs, but only on .NET Framework 4.8, which Microsoft keeps on life support with security patches only. **Web Forms was never carried forward into modern .NET.** There's no upgrade path: a rebuild is the only way forward.
- **Typical Web Forms side-effects** (to be confirmed once I can see it):
  - Full-page reloads on every click → feels slow, especially on rural 4G.
  - Not responsive → painful on phones, so crews fall back to paper/photos/texts and someone re-keys it later.
  - Heavy hidden "ViewState" → large page sizes.
  - Usually tied to an on-prem or single VM SQL Server database. Backups, patching and security are often "whoever set it up".
  - Hard to hire developers for. Key-person risk if one contractor built it.

> **Risk flag:** If this system holds council asset data, client contacts or staff records, check (a) who hosts it, (b) when the server was last patched, (c) whether there's MFA on logins, and (d) that backups are tested. Councils increasingly send supplier security questionnaires, and "Web Forms on an unpatched VM" is a tender-loser.

### 1.2 Audit checklist (to finish once we have access)

| # | Area | Questions to answer | Score (1–5) |
|---|---|---|---|
| 1 | Modules | What does it do today? (jobs, timesheets, quotes, stock, QA, HSE?) | |
| 2 | Users | Who logs in, how often, on what device? | |
| 3 | Data | Tables, record counts, how many years of history, export options | |
| 4 | Workflow fit | Steps that happen *outside* the system (Excel, paper, MS Project, Notion, texts) | |
| 5 | Speed | Clicks to log a day's work; page load on 4G | |
| 6 | Mobile | Usable on a phone in a gloved hand in the rain? | |
| 7 | Reporting | Can you get margin per job, metres/week, WIP without Excel? | |
| 8 | Integrations | Xero? Email? CCTV software? None? | |
| 9 | Security | MFA, roles, audit log, hosting, backups, patching | |
| 10 | Ownership | Who owns the code? Is there documentation? Who can fix it if it breaks? | |

**Known workarounds already (from Notion):** multi-crew scheduling is in **Microsoft Project**; tenders, crew capacity, HSE, meetings and staff live in **Notion databases**; inspection forms are separate templates. *Each workaround is a module the new platform should absorb.*

---

## 2. Who uses it (personas)

| Persona | Their one job | Where they are | What "great" looks like |
|---|---|---|---|
| **MD / GM** (Rowan) | Know the business is healthy | Office, phone | One screen: pipeline, margin, WIP, safety, cash. No Excel. |
| **Project / Ops Manager** | Get jobs done on time, on budget | Office + site | Job board with blockers flagged, not buried |
| **Scheduler** | Right crew + plant + product, right place | Office | Drag-drop crew board that knows leave, competencies and stock |
| **Crew Leader** | Do the job safely, record it once | Site, gloves, bad signal | Offline phone app: pre-start → install log → sign-off in minutes |
| **Technician / Operator** | Know where to be and what to do | Truck, site | Today's job, address, hazards, SOP links |
| **Stores / Logistics** | Right product in the right truck | Yard | Scan QR → done |
| **Accounts / Admin** | Bill fast and correctly | Office | Job closes → claim/invoice draft lands in Xero |
| **HSE Lead** | Nobody gets hurt; prove it | Everywhere | Live view of pre-starts, incidents, expiring tickets, SDS |
| **Council / Client Asset Manager** | Know what was fixed, where, with what, and that it's QA'd | Council office | Portal: map of assets, CCTV before/after, materials traced, QA pack PDF |
| **ASOE Dealer / Installer** (distribution customers) | Order liner, track delivery, register installs | Their office/site | Order, track, and download certs without phoning PipeTech |

---

## 3. Benchmark: borrow from the best

*(Opinion: no single product does trenchless + traceability + distribution well. That gap is your opportunity.)*

| Product | Category | What to steal | Where it falls short for PipeTech |
|---|---|---|---|
| Simpro / AroFlo / Fergus | Trade job management (Fergus is NZ-built) | Quote → job → invoice flow, Xero sync, simple field app | No pipe-segment asset model, no material traceability, no QA hold points |
| Assignar | Civil crew & plant ops | Crew/plant allocation board, pre-starts, competencies | Not built for stock traceability or client portals |
| Procore | Construction PM | Document control, RFIs, permissions | Heavy, expensive, built for vertical construction |
| HammerTech | Construction HSE | Inductions, permits, incidents | HSE only |
| WinCan / ITpipes / POSM | CCTV inspection | Defect coding, inspection reports | Inspection only; integrate, don't replace |
| Flexport / courier trackers | Supply chain | "Where is my stuff" timeline with live ETAs | N/A — pure inspiration for the tracking UX |
| Linear | Software teams | Speed. Keyboard shortcuts, instant search, zero clutter | N/A — inspiration for feel |

**The play:** combine *Fergus-simple* field UX, *Assignar-grade* crew planning, *Flexport-style* product tracking, and a *council-facing portal* nobody else in NZ trenchless offers.

---

## 4. Design principles (the non-negotiables)

1. **Capture once, use everywhere.** A crew leader logs the install once. That record feeds QA, the client portal, the invoice, stock levels and KPIs. No re-keying.
2. **Every pipe has a passport.** The core record is the **asset** (manhole-to-manhole segment, lateral or manhole), not the job. Jobs come and go; the asset history lasts 50+ years.
3. **Every metre is traceable.** Every reel, drum, patch and TopHat gets a QR label on arrival. Scan in, scan out, scan into the pipe.
4. **Status is calculated, never typed.** "Ready to install" turns green when permit + pre-CCTV + product + crew are all in place. Nobody edits a status dropdown.
5. **Hold points block, they don't nag.** You *can't* mark a liner installed without a pre-install CCTV and an approved pre-start. Same principle as a physical hold point on site.
6. **Offline-first in the field.** Assume no signal in a manhole in Stratford. Everything works offline and syncs later.
7. **Three taps, gloved thumbs.** Field actions in ≤3 taps, 48px+ targets, high-contrast, voice notes allowed.
8. **Role-based by default.** Crews see their work; councils see their assets; tender values and margins stay in restricted views.
9. **Own your data and code.** IP ownership, exportable data, documented. No repeat of a black-box legacy app.
10. **Brand-consistent.** PipeTech design system (Green `#65FF00`, Dark Grey `#272422`, Stone, Steam, Switzer), phone-first, dark/light aware, works on a dodgy rural connection.

---

## 5. Platform map (modules)

```
                         ┌───────────────────────────────┐
                         │      INSIGHTS & KPIs          │
                         └──────────────▲────────────────┘
  WIN WORK          PLAN            DO              PROVE           GET PAID
┌─────────┐   ┌──────────────┐  ┌───────────┐  ┌──────────────┐  ┌──────────┐
│Tenders &│──▶│ Jobs & Assets│─▶│ Field App │─▶│ QA & Close-  │─▶│ Claims & │
│ Quotes  │   │ Scheduling   │  │ (offline) │  │ out Packs    │  │ Xero sync│
└─────────┘   └──────┬───────┘  └─────┬─────┘  └──────┬───────┘  └──────────┘
                     │                │               │
              ┌──────▼────────────────▼───────────────▼──────┐
              │  SUPPLY CHAIN & TRACEABILITY (product spine) │
              └──────▲────────────────────────────────▲──────┘
                     │                                │
              ┌──────┴──────┐                  ┌──────┴────────┐
              │ Suppliers & │                  │ ASOE Dealer   │
              │ Imports     │                  │ Portal        │
              └─────────────┘                  └───────────────┘
   Cross-cutting: HSE · People & Competencies · Plant & Fleet · Documents · Client Portal
```

### 5.1 Module detail

| Module | Key features | Replaces |
|---|---|---|
| **Tenders & Quotes** | Tender register, go/no-go scoring, rate library (per metre by DN, per TopHat, per MH), quote builder, win/loss | Notion Tender Tracker, Excel pricing |
| **Jobs & Assets** | Job → sites → assets (MH-MH segments with DN, material, length, depth, council asset ID); map view; import council asset lists (CSV/GIS) | Current app, spreadsheets |
| **Scheduling** | Multi-crew board (week/month), drag-drop, non-working days, leave, competencies, plant & stock availability checks, clash warnings | MS Project Gantt, Notion Crew Capacity |
| **Field App** | Today's jobs, navigation, pre-start/JSA, TMP check, permits (confined space), install logs, photos, voice notes, client sign-off. Fully offline | Paper, texts, photo rolls |
| **Supply Chain & Traceability** | See section 6. The spine of the whole system | Spreadsheets, memory |
| **QA & Close-out** | Hold points, test results, CCTV links, auto-built as-built / QA pack PDF per asset or job | Manual Word/PDF packs |
| **Claims & Finance** | Progress claims from completed metres, Xero invoices/bills/POs, job costing (labour + plant + landed material cost), WIP | Manual invoicing |
| **HSE** | Incidents & near-misses, hazards, SDS register (e.g. BlueLine Part A/B), corrective actions, toolbox talks, audits | Separate forms, Notion HSE db |
| **People** | Competencies & tickets with expiry alerts (confined space, TTM, first aid, KRE cutter), inductions, training records | Spreadsheets |
| **Plant & Fleet** | KRE robotic cutter & other plant: hours, service schedules, pre-use checks; vehicles: WoF/CoF, rego, RUC, TSL display | Ad hoc |
| **Documents** | Controlled SOPs with version/owner/approval (Robotic Cutting SOP v2 etc.), linked into field steps | Shared drives |
| **Client Portal** | Councils see their assets, progress, CCTV before/after, materials traced, QA packs, claims | Emails with attachments |
| **ASOE Dealer Portal** | Dealers order, track shipments, download certs, register installs → warranty | Phone + email |
| **Insights** | KPI dashboards (section 9) | Excel |

### 5.2 Additions from the Procore / Simpro analysis (v0.2)

See [`COMPETITOR-ANALYSIS.md`](./COMPETITOR-ANALYSIS.md) for the full comparison. Added to scope:

| Feature | Module | Phase |
|---|---|---|
| Native pre-start/JSA, permits, plant pre-use (offline, prefilled) | HSE / Field App | 1 |
| Competency matrix with hard scheduling block | People / Scheduling | 1 |
| Incidents & observations with WorkSafe notifiable-event flag | HSE | 1 |
| Auto-built daily site diary + voice notes | Field App | 1 |
| Progress claims from verified metres, retentions, Construction Contracts Act compliant | Claims & Finance | 2 |
| Early-warning variations from the field → client approval | Jobs / Client Portal | 2 |
| Council submittals register and Technical Queries (TQs) | Documents | 2 |
| Plant maintenance (KRE cutter, heat units, CCTV, jetters) | Plant & Fleet | 2 |
| Defects list per asset | QA | 2 |
| Subcontractor register + portal | Suppliers | 3 |
| AI photo validation, AI scheduling, "Ask PipeTech" assistant | Insights / AI | 3–4 |

**Performance budget** (non-negotiable, learned from competitor reviews): app opens in under 2 s on a mid-range Android; every field flow works 100% offline; photos upload in a background queue; a new technician completes a pre-start unaided within 5 minutes.

---

## 6. Supply-to-install tracking system (the centrepiece)

### 6.1 The idea in one line
**Every physical unit of product (reel, coil, drum, patch kit, TopHat) gets a unique ID at receipt, and every movement is an event, from purchase order to "it's in pipe SW-1042 at chainage 0–62.4 m".**

*Analogy:* it's a courier tracking number, except the parcel ends up buried under a road for 50 years and the council can still look it up.

### 6.2 Lifecycle stages

| # | Stage | Trigger / who | Data captured |
|---|---|---|---|
| 1 | **Forecast** | Auto from won work & backlog | Metres by DN needed, by month |
| 2 | **Ordered** | PO raised (synced to Xero) | Supplier, product, DN, qty, price, currency, required-by date |
| 3 | **Confirmed / In production** | Supplier confirms | Batch/lot no., production date, test certificate / CoC |
| 4 | **Shipped** | Supplier / forwarder | Container no., vessel, ETD/ETA, freight forwarder ref |
| 5 | **In port / Clearing** | Broker | Customs entry, biosecurity clearance, duty/GST, landed cost |
| 6 | **Received** | Stores scan at yard | Inspection pass/fail, photos, **QR label printed per unit**, actual qty |
| 7 | **In stock** | Auto | Location (yard bay/container), storage conditions, expiry (resins) |
| 8 | **Allocated** | Scheduler | Job + assets it's reserved for |
| 9 | **Dispatched** | Stores scan onto truck | Vehicle, crew, date |
| 10 | **On site** | Crew scan | GPS, time |
| 11 | **Installed** | Crew install log | Asset ID, metres used (start/end marks), install parameters, crew, photos |
| 12 | **Verified** | QA | Post-install CCTV, test results, hold points cleared |
| 13 | **Handed over** | Close-out | QA pack issued, warranty start date |
| 14 | **Remainder** | Crew/stores | Offcut back to stock (new child ID) / scrap with reason |

### 6.3 Identifiers
- **Unit ID** (e.g. `PT-R-26-00417`): printed as a QR label (thermal printer, weatherproof labels) at receipt. Phones scan it. No special hardware needed to start.
- **Manufacturer batch/lot**: links to test certificates. Many units can share one batch.
- **Parent/child**: cutting 62.4 m off a 150 m reel creates a child record for the remainder. Full genealogy preserved.
- **Asset ID**: PipeTech ID + the council's own asset ID, so their asset system can match it.

### 6.4 Install record (what the crew captures)
Kept generic on purpose: **exact parameters must come from the current manufacturer installation manual for each product.** The system stores whatever the manual requires as a configurable checklist per product.

- Asset, DN, host pipe material, length, upstream/downstream MH
- Unit ID(s) scanned + metres used
- Pre-install CCTV ref (hold point), cleaning/jetting done
- Process log: temperature/pressure readings and times (manual entry first; heater data-logger import later)
- Ambient conditions
- Lateral reinstatements (count, positions; robotic cutter used)
- Samples taken (ID) for lab testing, where specified
- Photos (start, during, end), voice notes
- Post-install CCTV ref (hold point), defects noted
- Crew, start/finish time, client rep sign-off

### 6.5 What this unlocks
- **Recall in one click:** "Which council assets contain batch X?" Answer in seconds, not weeks.
- **Yield / shrinkage:** metres received = installed + offcuts + scrap + on hand. Variance over threshold → alert. *(Fresh money hiding here: a 3% yield improvement on liner spend drops straight to margin.)*
- **True job margin:** landed cost per metre (product + freight + duty + FX) flows into job costing automatically.
- **Stock-outs prevented:** forecast vs on-hand vs inbound by DN, with lead-time alerts.
- **Expiry control:** resin and kit expiry alerts; first-expiry-first-out picking.
- **Tender weapon:** "Every metre we install is traceable to its batch and test certificate, visible in your portal." Very few NZ competitors can say that.
- **ASOE distribution:** the same spine powers the dealer portal. Dealers see their orders move through stages 2–9 and register their installs for warranty.

### 6.6 Tracking hardware: crawl, walk, run
| Stage | Tech | Cost |
|---|---|---|
| Crawl (MVP) | Phone camera QR scanning + thermal label printer | Low (printer + labels) |
| Walk | Rugged Android scanners for stores; GPS stamps on scans | Moderate |
| Run | Data-logger import from heat/cure units; BLE tags on high-value reels; truck telematics | Higher; only if ROI proven |

---

## 7. Architecture (recommended)

### 7.1 Build vs buy (opinion clearly flagged)

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| A. Buy off-the-shelf (Simpro/AroFlo/Fergus) | Fast, cheap to start, proven | No pipe-asset model, no traceability, no dealer portal; you bend to it | Fine for a generic trades firm. Not "best in the world" for you |
| B. Full custom build | Exactly fits; becomes a differentiator (and maybe a product) | Highest cost and risk; needs a good dev partner | Only if you commit to it long term |
| **C. Hybrid (recommended)** | Custom core where you're unique (assets, traceability, QA, portals, field app); **integrate** commodity stuff (Xero, M365, payroll, CCTV software) | Needs integration discipline | **Best value. Build the 30% that makes you different; plug in the 70% that's commodity.** |

### 7.2 Tech stack (modern, boring, hireable)
- **Database:** PostgreSQL + PostGIS (maps/spatial). Event-ledger tables for traceability.
- **Backend/API:** TypeScript (Node) or .NET 8+. *(Opinion: if your current developer is a .NET person, .NET 8 is a perfectly good choice and eases data migration from SQL Server.)*
- **Web app:** React (Next.js), PipeTech design system.
- **Field app:** React Native (Expo) with a local SQLite database and background sync. Native app needed for reliable offline use, camera scanning and big photo uploads.
- **Files:** Object storage for photos, CCTV video and PDFs.
- **Hosting:** NZ-region cloud (AWS Auckland or Azure NZ North). Council data stays onshore; good for tender security questionnaires.
- **Identity:** Microsoft 365 / Entra ID single sign-on for staff, MFA enforced; separate logins for council and dealer portal users.
- **Integrations:** Xero (POs, bills, invoices, contacts), Microsoft 365 (calendar, email), CCTV software exports, council GIS (ArcGIS feature services / CSV), freight tracking, a mapping provider.
- **AI layer (forward-looking):** draft QA packs and daily diaries from field data; voice-note → structured log; tender pricing assistant from historical jobs; "ask the system" ("what's our average metres/day on DN150 in Taranaki?"). Human approval on anything client-facing.

### 7.3 Security & compliance
- Role-based access (MD, Ops, Scheduler, Crew, Stores, Accounts, HSE, Client, Dealer); tender values and margins restricted.
- Full audit log on every change (who/what/when). Install and QA records are append-only once signed.
- Privacy Act 2020: staff and client personal info minimised, access-controlled, retention rules.
- HSWA 2015 records (incidents, training, plant) kept per retention requirements.
- Backups with tested restores, encryption at rest and in transit, annual penetration test.
- **Contract:** PipeTech owns the code and data; escrow or repo access; documentation as a deliverable.

---

## 8. Data model (summary)

Full starter schema: [`schema.sql`](./schema.sql). Core entities:

```
Client ─< Contract ─< Job ─< JobAsset >─ Asset (pipe segment / lateral / MH)
                         │                  │
                         ├─< Allocation >─ StockUnit (reel/drum/kit) >─ Batch >─ Product
                         │                  │                               │
                         ├─< Installation ──┘ (asset + unit + metres)       └─ Supplier
                         ├─< Inspection (CCTV pre/post)
                         ├─< HoldPoint / QACheck
                         └─< Claim ─> Xero invoice

PurchaseOrder ─< POLine ─< Shipment ─< StockUnit
StockUnit ─< StockEvent  (append-only ledger: received, moved, allocated, dispatched, installed, offcut, scrapped)
Crew ─< CrewMember >─ Person ─< Competency
```

---

## 9. KPIs the system should give you for free

| Area | KPI | Why it matters |
|---|---|---|
| Production | Metres lined per crew-day, by DN | Core productivity and pricing truth |
| Production | Crew utilisation % | Idle crews = burnt margin |
| Quality | First-time-right % (no rework) | Reputation + cost |
| Quality | Days from install → QA pack issued | Faster packs = faster payment |
| Finance | Job margin: estimate vs actual | Tells you what to tender harder for |
| Finance | WIP & days to invoice | Cash flow |
| Supply | Liner yield % (installed / received) | Waste & shrinkage |
| Supply | Supplier on-time-in-full %, stock cover (weeks by DN) | Avoid stand-downs |
| Safety | Pre-start completion %, near-miss reporting rate, TRIFR | Lead + lag indicators |
| People | Tickets expiring in 60 days | No unqualified person on site |
| Client | Portal logins, client satisfaction score | Stickiness + tender evidence |
| ASOE | Dealer orders, installs registered, warranty claims | Distribution growth |

---

## 10. Roadmap

| Phase | Timing (indicative) | Scope | Outcome |
|---|---|---|---|
| **0. Discovery** | 3–4 weeks | Finish current-system audit; export data; map processes with crews, stores, accounts; confirm product install parameters with manufacturer docs; clickable prototype tested with 2 crew leaders | Signed-off scope + backlog |
| **1. MVP: "Track & Prove"** | ~3–4 months | Jobs & assets, field app (offline pre-start + install log + photos), QR stock receipt/allocation/install, hold points, QA pack PDF | Every metre traced; packs in days, not weeks |
| **2. "Plan & Bill"** | ~2–3 months | Crew scheduling board, Xero sync, progress claims, job costing, HSE & competencies | Retire MS Project + legacy app |
| **3. "Open the doors"** | ~2–3 months | Council client portal, ASOE dealer portal, supplier/shipment tracking, KPI dashboards | Tender differentiator + distribution channel |
| **4. "Smart"** | Ongoing | AI drafting, data-logger import, GIS sync, predictive stock, telematics | Best-in-class |

**Migration approach:** parallel-run the legacy app for one month per module, then read-only archive for history. Don't "big bang" it.

### 10.1 Budget ballpark (estimate, NZD, excl. GST)
*Assumptions: NZ/AU dev partner, hybrid approach, ~25–40 internal users, design system already exists. Treat as ±40% until discovery is done.*

| Item | Range |
|---|---|
| Phase 0 Discovery + prototype | $20k – $40k |
| Phase 1 MVP | $120k – $220k |
| Phases 2–3 | $150k – $300k |
| Run cost (hosting, monitoring, licences, support retainer) | $2k – $6k / month |

**Alternative:** off-the-shelf job management software typically runs per-user per-month subscriptions, plus custom work anyway for traceability. Get 2–3 quotes in Phase 0 to compare properly.

**Funding angle:** check Callaghan Innovation's successor programmes / R&D Tax Incentive eligibility for the traceability and AI components. *(Flag: confirm current eligibility with your accountant; rules have shifted.)*

---

## 11. Risks & how to handle them

| Risk | Likelihood | Mitigation |
|---|---|---|
| Crews don't adopt the app | High if ignored | Co-design with 2 crew leaders; ≤3 taps; train in toolbox talks; paper fallback for first month |
| Scope creep (six-month build becomes eighteen) | High | Phase gates; MVP = "Track & Prove" only |
| Data migration from legacy app is messy | Medium | Export early in Phase 0; clean before migrating, not after |
| Install parameters entered wrong / inconsistent with manufacturer manual | Medium | Product-specific checklists pulled from controlled manufacturer docs; HSE/QA sign-off before use |
| Vendor lock-in / key-person risk (again) | Medium | IP ownership clause, repo access, documentation, mainstream stack |
| Council data privacy / security questionnaires | Medium | NZ hosting, MFA, audit log, pen test, written security summary |
| Tender/commercial data exposure | Low–Med | Role-restricted views; no margins in client/dealer portals |

---

## 12. Next steps

1. **You:** allow `www.pipetechnz.net` in this environment's network settings and set up a read-only test login, **or** send screenshots/screen recording. I'll finish section 1 properly.
2. **You:** list the 5 most annoying things about the current system (ask a crew leader, stores and accounts too; their answers will differ, and that's the point).
3. **Me (can do now):** turn this into a Word/PDF pack or slide deck for the board, and a Phase 0 RFP for dev partners.
4. **Together:** run the clickable prototype past two crew leaders. Watch them use it on site. Fix what confuses them.
5. **Decide:** hybrid build (recommended) vs buy. Get 2–3 dev partner quotes off the RFP.

**Reminders while this runs:** keep HSE sign-off on any SOP that gets digitised (the KRE cutter SOP and BlueLine PPE are still drafts per Notion), plan staff training time into Phase 1, and set the KPIs in section 9 as baselines *before* go-live so you can prove the ROI later. Marketing will love the council portal; get a case study from the first council that uses it.
