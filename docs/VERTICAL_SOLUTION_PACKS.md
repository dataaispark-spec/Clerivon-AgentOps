# Six vertical solution packs

## 1. BFSI — KYC & AML Investigation Copilot
**Flow:** document intake/extraction → entity and record reconciliation → risk-signal triage → evidence verification → analyst packet.

- Inputs: synthetic KYC forms, customer records, watchlist match summaries, transaction summaries and policy rules.
- Outputs: normalized facts, source-linked discrepancies, explained risk indicators, missing-evidence checklist and case packet.
- Controls: no autonomous AML determination, account freeze, rejection or regulatory filing.
- Pilot KPIs: case preparation time, evidence completeness, analyst rework and false-positive review rate.

## 2. Retail — Inventory & Demand Orchestration
**Flow:** demand/POS signals → stock and purchase-order reconciliation → forecast review → replenishment recommendation → approval → read-after-write verification.

- Inputs: synthetic POS history, stock-on-hand, open POs, lead times and promotion metadata.
- Outputs: demand summary, stock-mismatch report, forecast range and recommended reorder.
- Controls: no unapproved purchase-order or pricing changes; expose forecast uncertainty.
- Pilot KPIs: stockouts, excess inventory, forecast error and recommendation acceptance.

## 3. Logistics — Shipment Exception Resolution
**Flow:** carrier events → freshness/SLA checks → exception classification → draft escalation → approval → mock execution → outcome verification.

- Seeded case: `SHP-10482` has a 43-hour-old tracking observation against a six-hour freshness threshold.
- Controls: observation time differs from retrieval time; stale tracking cannot confirm ETA; carrier/customer contact requires approval.
- Pilot KPIs: exception detection latency, fresh-evidence rate and SLA response time.

## 4. Healthcare — Prior Authorization Assistant
**Flow:** document intake → approved guideline retrieval → completeness checks → coding suggestions → packet assembly → authorized review.

- Inputs: synthetic clinical notes, coverage criteria, authorization forms and procedure codes.
- Outputs: missing-document checklist, source-linked criteria map, coding suggestions and draft packet.
- Controls: no autonomous diagnosis/treatment decision or submission.
- Pilot KPIs: packet completeness, preparation time and payer rework.

## 5. Marketing — Creative Intelligence & Optimization
**Flow:** creative analysis → objective mapping → brand/legal compliance → experiment design → approval → performance evaluation.

- Inputs: synthetic creative metadata, brand rules, campaign goals and aggregate performance.
- Outputs: creative analysis, compliance flags, variant briefs and test plan.
- Controls: predictions are hypotheses; publishing and budget changes require approval.
- Pilot KPIs: review time, experiment velocity and qualified conversion lift.

## 6. MSME — AI Digital Workforce
**Flow:** lead intake → qualification → invoice extraction → follow-up drafts → operations coordination → owner approval/reporting.

- Inputs: synthetic leads, invoices, orders and task lists.
- Outputs: lead priority with rationale, extracted invoice fields, drafts and owner summaries.
- Controls: no autonomous payments, tax filing, binding quotation or unapproved bulk message.
- Pilot KPIs: lead response time, invoice processing time, follow-up completion and hours saved.
