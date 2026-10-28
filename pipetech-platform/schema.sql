-- PipeTech OS: starter data model (PostgreSQL 16 + PostGIS)
-- Draft v0.1. Covers jobs/assets and the supply-to-install traceability spine.
-- HSE, people, plant and finance modules are stubbed; expand in Phase 2.

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ─────────────────────────────────────────────────────────────
-- Parties
-- ─────────────────────────────────────────────────────────────
CREATE TABLE organisation (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  kind          text NOT NULL CHECK (kind IN ('client','supplier','dealer','forwarder','internal')),
  name          text NOT NULL,
  xero_contact_id text,
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE person (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id uuid REFERENCES organisation(id),
  full_name     text NOT NULL,
  email         text,
  role          text NOT NULL,  -- md, ops, scheduler, crew_leader, technician, stores, accounts, hse, client, dealer
  active        boolean NOT NULL DEFAULT true
);

CREATE TABLE competency (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  person_id     uuid NOT NULL REFERENCES person(id),
  name          text NOT NULL,      -- e.g. Confined space entry, TTM, First aid, KRE cutter operator
  evidence_doc  text,
  expires_on    date
);

CREATE TABLE crew (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name          text NOT NULL,
  leader_id     uuid REFERENCES person(id)
);

-- ─────────────────────────────────────────────────────────────
-- Work: contracts, jobs, assets
-- ─────────────────────────────────────────────────────────────
CREATE TABLE contract (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     uuid NOT NULL REFERENCES organisation(id),
  reference     text NOT NULL,       -- client contract number
  title         text NOT NULL,
  value_nzd     numeric(14,2),       -- restricted view
  starts_on     date,
  ends_on       date
);

CREATE TABLE asset (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     uuid NOT NULL REFERENCES organisation(id),
  client_asset_ref text,             -- council's own asset ID
  kind          text NOT NULL CHECK (kind IN ('gravity_main','pressure_main','lateral','manhole')),
  upstream_node text,                -- e.g. MH-0231
  downstream_node text,
  dn_mm         integer,
  host_material text,                -- e.g. AC, VC, concrete, PVC
  length_m      numeric(8,2),
  depth_m       numeric(6,2),
  geom          geometry(LineString, 2193),  -- NZTM2000
  UNIQUE (client_id, client_asset_ref)
);

CREATE TABLE job (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id   uuid REFERENCES contract(id),
  number        text UNIQUE NOT NULL,   -- e.g. J26-0142
  title         text NOT NULL,
  method        text NOT NULL,          -- fold_and_form, cipp_patch, uv_tophat, robotic_cutting, cctv, jetting, mh_rehab, pressure_relining
  site_address  text,
  planned_start date,
  planned_end   date,
  crew_id       uuid REFERENCES crew(id),
  created_at    timestamptz NOT NULL DEFAULT now()
  -- NB: no status column. Status is derived (see v_job_readiness).
);

CREATE TABLE job_asset (
  job_id        uuid NOT NULL REFERENCES job(id),
  asset_id      uuid NOT NULL REFERENCES asset(id),
  planned_m     numeric(8,2),
  PRIMARY KEY (job_id, asset_id)
);

-- ─────────────────────────────────────────────────────────────
-- Product & supply chain
-- ─────────────────────────────────────────────────────────────
CREATE TABLE product (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  supplier_id   uuid NOT NULL REFERENCES organisation(id),
  sku           text UNIQUE NOT NULL,
  name          text NOT NULL,          -- e.g. ASOE FFPP uPVC liner DN150
  family        text NOT NULL,          -- liner, resin, patch_kit, tophat, consumable
  dn_mm         integer,
  uom           text NOT NULL CHECK (uom IN ('m','kg','l','each')),
  has_expiry    boolean NOT NULL DEFAULT false,
  install_checklist jsonb               -- product-specific fields, sourced from the current manufacturer manual
);

CREATE TABLE purchase_order (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  number        text UNIQUE NOT NULL,
  supplier_id   uuid NOT NULL REFERENCES organisation(id),
  currency      char(3) NOT NULL DEFAULT 'NZD',
  required_by   date,
  xero_po_id    text,
  raised_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE po_line (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  po_id         uuid NOT NULL REFERENCES purchase_order(id),
  product_id    uuid NOT NULL REFERENCES product(id),
  qty           numeric(12,2) NOT NULL,
  unit_price    numeric(12,4) NOT NULL
);

CREATE TABLE batch (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id    uuid NOT NULL REFERENCES product(id),
  manufacturer_lot text NOT NULL,
  produced_on   date,
  expires_on    date,
  certificate_doc text,               -- test certificate / CoC
  UNIQUE (product_id, manufacturer_lot)
);

CREATE TABLE shipment (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  po_id         uuid NOT NULL REFERENCES purchase_order(id),
  forwarder_id  uuid REFERENCES organisation(id),
  container_no  text,
  vessel        text,
  etd           date,
  eta           date,
  cleared_at    timestamptz,          -- customs + biosecurity
  landed_cost_nzd numeric(14,2)       -- freight + duty + charges, apportioned to units on receipt
);

CREATE TABLE stock_location (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name          text NOT NULL,        -- Yard bay A3, Container 2, Truck PT-07, Site J26-0142
  kind          text NOT NULL CHECK (kind IN ('yard','container','vehicle','site','dealer'))
);

-- One physical unit: a reel, coil, drum, kit or TopHat. Carries the QR label.
CREATE TABLE stock_unit (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  label         text UNIQUE NOT NULL, -- e.g. PT-R-26-00417 (printed as QR)
  batch_id      uuid NOT NULL REFERENCES batch(id),
  shipment_id   uuid REFERENCES shipment(id),
  parent_id     uuid REFERENCES stock_unit(id),  -- offcuts become children
  qty_initial   numeric(12,2) NOT NULL,
  landed_unit_cost_nzd numeric(12,4)
);

-- Append-only ledger. Current position/quantity of any unit is derived from its events.
CREATE TABLE stock_event (
  id            bigserial PRIMARY KEY,
  stock_unit_id uuid NOT NULL REFERENCES stock_unit(id),
  kind          text NOT NULL CHECK (kind IN
                  ('received','inspected','moved','allocated','deallocated','dispatched',
                   'on_site','installed','offcut','returned','scrapped','adjusted')),
  qty_delta     numeric(12,2) NOT NULL DEFAULT 0,  -- negative when consumed
  location_id   uuid REFERENCES stock_location(id),
  job_id        uuid REFERENCES job(id),
  asset_id      uuid REFERENCES asset(id),
  actor_id      uuid REFERENCES person(id),
  geo           geometry(Point, 4326),
  note          text,
  occurred_at   timestamptz NOT NULL,              -- device time (offline capture)
  recorded_at   timestamptz NOT NULL DEFAULT now() -- server time on sync
);
CREATE INDEX ON stock_event (stock_unit_id, occurred_at);
CREATE INDEX ON stock_event (asset_id);

-- ─────────────────────────────────────────────────────────────
-- Field execution & QA
-- ─────────────────────────────────────────────────────────────
CREATE TABLE inspection (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id      uuid NOT NULL REFERENCES asset(id),
  job_id        uuid REFERENCES job(id),
  stage         text NOT NULL CHECK (stage IN ('pre','post','audit')),
  inspected_at  timestamptz NOT NULL,
  video_uri     text,
  report_uri    text,                 -- export from CCTV software
  grade         text                  -- per NZ Pipe Inspection Manual coding
);

CREATE TABLE installation (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id        uuid NOT NULL REFERENCES job(id),
  asset_id      uuid NOT NULL REFERENCES asset(id),
  crew_id       uuid REFERENCES crew(id),
  started_at    timestamptz,
  finished_at   timestamptz,
  metres_installed numeric(8,2),
  laterals_reinstated integer DEFAULT 0,
  params        jsonb,                -- readings per product install_checklist (temps, pressures, times)
  sample_ref    text,
  signed_by     uuid REFERENCES person(id),
  signed_at     timestamptz           -- once signed, row is locked (enforce via trigger/policy)
);

CREATE TABLE installation_unit (
  installation_id uuid NOT NULL REFERENCES installation(id),
  stock_unit_id uuid NOT NULL REFERENCES stock_unit(id),
  start_mark_m  numeric(8,2),
  end_mark_m    numeric(8,2),
  qty_used      numeric(12,2) NOT NULL,
  PRIMARY KEY (installation_id, stock_unit_id)
);

CREATE TABLE hold_point (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id        uuid NOT NULL REFERENCES job(id),
  asset_id      uuid REFERENCES asset(id),
  kind          text NOT NULL,        -- permit, prestart, pre_cctv, product_allocated, post_cctv, qa_review, client_signoff
  cleared_by    uuid REFERENCES person(id),
  cleared_at    timestamptz,
  evidence_uri  text
);

CREATE TABLE prestart (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id        uuid NOT NULL REFERENCES job(id),
  crew_id       uuid REFERENCES crew(id),
  answers       jsonb NOT NULL,
  hazards_noted text,
  submitted_at  timestamptz NOT NULL
);

-- ─────────────────────────────────────────────────────────────
-- Audit
-- ─────────────────────────────────────────────────────────────
CREATE TABLE audit_log (
  id            bigserial PRIMARY KEY,
  actor_id      uuid REFERENCES person(id),
  entity        text NOT NULL,
  entity_id     uuid NOT NULL,
  action        text NOT NULL,
  diff          jsonb,
  at            timestamptz NOT NULL DEFAULT now()
);

-- ─────────────────────────────────────────────────────────────
-- Derived views
-- ─────────────────────────────────────────────────────────────

-- Quantity on hand per unit, from the ledger
CREATE VIEW v_stock_on_hand AS
SELECT su.id, su.label, su.batch_id,
       su.qty_initial + COALESCE(SUM(e.qty_delta), 0) AS qty_on_hand
FROM stock_unit su
LEFT JOIN stock_event e ON e.stock_unit_id = su.id
GROUP BY su.id;

-- Recall query: every asset containing product from a given manufacturer lot
CREATE VIEW v_batch_trace AS
SELECT b.manufacturer_lot, p.name AS product, su.label AS unit,
       a.client_asset_ref, a.upstream_node, a.downstream_node,
       iu.qty_used, i.signed_at AS installed_at, j.number AS job_number
FROM batch b
JOIN product p           ON p.id = b.product_id
JOIN stock_unit su       ON su.batch_id = b.id
JOIN installation_unit iu ON iu.stock_unit_id = su.id
JOIN installation i      ON i.id = iu.installation_id
JOIN asset a             ON a.id = i.asset_id
JOIN job j               ON j.id = i.job_id;

-- Job readiness: status is computed from hold points, never typed
CREATE VIEW v_job_readiness AS
SELECT j.id, j.number,
       COUNT(h.*)                                   AS hold_points_total,
       COUNT(h.*) FILTER (WHERE h.cleared_at IS NOT NULL) AS hold_points_cleared,
       CASE
         WHEN COUNT(h.*) = 0 THEN 'not_planned'
         WHEN COUNT(h.*) FILTER (WHERE h.cleared_at IS NULL) = 0 THEN 'complete'
         WHEN COUNT(h.*) FILTER (WHERE h.cleared_at IS NULL AND h.kind IN ('permit','prestart','pre_cctv','product_allocated')) = 0
           THEN 'ready_or_in_progress'
         ELSE 'blocked'
       END AS readiness
FROM job j
LEFT JOIN hold_point h ON h.job_id = j.id
GROUP BY j.id;
