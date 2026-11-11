# ADR-0006: Retention is four Tier 1 metrics, not two

**Status:** Accepted — 2026-09-24. Amends ADR-0001.

## Context

ADR-0001 lists two retention metrics in Tier 1: NRR/NDR and GRR. Modelling them
exposed that each covers two different measures:

- **Cohort basis** — what happened to the customers who were here at T0.
  Membership is fixed at T0 and never revised.
- **Period-over-period basis** — what happened between two balance dates.

These answer different questions with different denominators, and on the same
data they routinely disagree by ten points or more. They are not two ways of
computing one number, so a variant on a single metric misrepresents them: no
decision selects between them, because a business legitimately wants both.

The names are a separate matter and genuinely contested — whether NRR and NDR
are synonyms or name the period and cohort measures respectively.

## Decision

Retention is four Tier 1 metrics, replacing the two in ADR-0001:

| Metric | Basis | Measure |
|---|---|---|
| `gross-retention-cohort` | Cohort | Gross |
| `net-retention-cohort` | Cohort | Net |
| `gross-retention-period` | Period-over-period | Gross |
| `net-retention-period` | Period-over-period | Net |

The IDs describe the measure and are stable. Display labels come from
`d-retention-naming`, which changes names and never formulas.

## Consequences

- Tier 1 is 14 metrics, not 12: MRR · ARR · Churned MRR · Expansion MRR ·
  the four retention metrics · CAC · LTV · CAC Payback · Gross Margin ·
  Rule of 40 · Win Rate.
- The naming dispute is isolated in one decision instead of leaking into IDs,
  so switching conventions can never change a number.
- The planned worked example — cohort and period retention diverging on
  identical data — becomes a comparison of two metrics rather than of two
  variants, which is the more honest framing.
