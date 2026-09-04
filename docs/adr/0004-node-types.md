# ADR-0004: The ontology has exactly three node types

**Status:** Accepted — 2026-09-04

## Context

The question that surfaced this: *should multi-currency be handled by adding a
"conversion rate" metric to the ontology?*

It should not, and working out why exposed a gap in the meta-model. A conversion
rate has no formula over the entity model, no competing business definitions and
no benchmark range. It is not a metric. But it clearly belongs in the ontology,
because FX treatment materially changes MRR, NRR and churn.

The real contested question about currency is not *what the rate is* — it is
**when you convert, and whether history gets restated**: spot rate at transaction
date, rate at period close, a fixed budget rate for the year, or restatement at
the latest rate. Those four choices produce different numbers on identical data,
and "why did last quarter's MRR change?" is one of the most common real-world
symptoms of never having decided.

Pricing model (subscription / usage-based / hybrid) and revenue basis
(committed / billed / charged) turn out to be the same *species* of thing.

## Decision

The ontology has three node types, and no others are added without an ADR:

- **Entity** (`src/entities/`) — things that exist. Account, Subscription,
  Contract Line, Invoice, Opportunity, Cost, Period. Carries typed properties.
- **Metric** (`src/metrics/`) — a measure over entities. Carries variants.
- **Decision** (`src/decisions/`) — a choice that gates which metric variants are
  valid. References entity properties; versioned; first-class.

FX is therefore a **Decision** (`d-fx-treatment`) plus **properties** on Contract
Line and Invoice (`amount`, `currency`, `fx_rate`, `fx_rate_date`) — never a
metric.

## Consequences

- The guided Skill planned for v0.2 is a traversal of `src/decisions/`. This ADR
  is what makes that possible; without it there is nothing coherent to walk.
- Decisions must be answerable by a competent RevOps or finance person without
  reading the ontology first. A decision that needs a tutorial is badly framed.
- The number of decision nodes is the project's health check. Target 10–14 for
  Tier 1; much above 20 and the guided flow becomes unusable, which is a signal
  to prune variants rather than to ship a long questionnaire.
- Some decisions gate whether whole metrics are emitted at all. A single-currency
  company should not receive FX machinery in their bundle.
