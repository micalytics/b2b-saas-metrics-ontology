# ADR-0001: Scope of v0.1

**Status:** Accepted — 2026-09-04. Amended by ADR-0006: retention is four
Tier 1 metrics, bringing Tier 1 to 14.

## Context

"An ontology of SaaS metrics" is unbounded. There are several hundred named SaaS
metrics in circulation, and an attempt to model all of them fully is how this
project would die at 40% completion with no adoption.

At the same time, most of those metrics are not contested. Nobody argues about
what ARPA means. The value of this project lives entirely in the metrics where
reasonable companies disagree — and those are a minority.

## Decision

Scope is split by **depth of treatment**, not by inclusion.

**Tier 1 — full variant treatment (12 metrics).** Variants, assumptions, typed
inputs, time semantics, gating decisions, pitfalls, benchmark ranges:

MRR · ARR · Churned MRR · Expansion MRR · NRR/NDR · GRR · CAC · LTV ·
CAC Payback · Gross Margin · Rule of 40 · Win Rate

**Tier 2 — stub entries (~18 metrics).** Name, aliases, one-line definition, and
a `componentOf` / `derivedFrom` relation to a Tier 1 metric or to a metric
family. No variant tree:

New MRR · Contraction MRR · Reactivation MRR · Net New MRR · Bookings ·
Billings · Logo Retention · Logo Churn · Gross Revenue Churn ·
Net Revenue Churn · LTV:CAC · Magic Number · Burn Multiple · Quick Ratio ·
Stage Conversion Rate · Sales Cycle Length · ACV · ARPA

Tier 2 metrics that have no natural Tier 1 parent attach to a **metric family**:
Revenue Base, Revenue Movement, Retention, Unit Economics, Commercial Efficiency.
Bookings and Billings are siblings of MRR on a revenue-timing axis, not children
of it; Logo Retention is a different axis from GRR. The family node exists so
these do not become orphans.

## Explicitly out of scope for v0.1

**Product and engagement metrics** — activation, DAU/MAU, stickiness, feature
adoption, time-to-value, NPS. Different entity model, different domain, and
[GrowthCues Core](https://github.com/ArvoanDev/growthcues-core) already covers
this ground well. Ceding it deliberately keeps the positioning sharp: this is the
revenue, finance and commercial layer.

**ASC 606 revenue recognition modelling.** Recognized revenue appears as a
concept the entity model references, not as a metric this ontology defines. That
rabbit hole is bottomless and is properly the domain of accounting standards.

## Consequences

- The bundle looks complete to a consumer (~30 metrics) while the deep work is
  done 12 times.
- Component metrics are modelled as `componentOf` their parent, which is more
  faithful than treating New/Expansion/Contraction/Churned MRR as peers.
- Promoting a Tier 2 metric to Tier 1 is a scope change and needs a new ADR.
- Anyone arriving looking for product analytics will bounce. That is intended.
