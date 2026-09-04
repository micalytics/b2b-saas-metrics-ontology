# Decisions

A **decision** is a choice that gates which metric variants are valid. Answering
all of them produces a *binding* — one company's resolved set of definitions.

This directory is what the guided Skill (v0.2) traverses. Every node here must be
answerable by a competent RevOps or finance person **without reading the ontology
first**. A decision that needs a tutorial is badly framed and should be reworked.

## Not everything is a decision

Enumerating these surfaced a distinction the meta-model needs. Three different
things were initially conflated:

| Kind | What it is | Where it lives |
|---|---|---|
| **Decision** | A branching choice that selects between named metric variants | `src/decisions/` |
| **Parameter** | A numeric knob with no branching — same model, different number | `parameters:` block on the binding |
| **Convention** | A default nobody argues about, overridable by those who do | `defaults:` block, not asked in the guided flow |

Promoting a parameter to a decision is how a 13-question flow becomes a
40-question flow that nobody finishes. Demote aggressively.

## The decisions (14)

| ID | Question in one line | Gates |
|---|---|---|
| `d-revenue-basis` | Committed, billed, or recognised? | MRR, ARR, everything downstream |
| `d-pricing-model` | Subscription, usage-based, or hybrid? | Asked first; gates `d-usage-recurring-basis` |
| `d-usage-recurring-basis` | How is the recurring floor derived from consumption? | MRR, ARR, Expansion MRR, Churned MRR |
| `d-contract-normalisation` | How do annual and multi-year contracts become MRR? | MRR, ARR |
| `d-non-recurring-revenue` | Do setup fees, services and hardware count? | MRR, ARR, Gross Margin, Rule of 40 |
| `d-churn-dating` | Dated at notice, at end of term, or at last payment? | Churned MRR, GRR, NRR, Logo Churn |
| `d-retention-naming` | Do you distinguish NDR from NRR, or treat them as synonyms? | Labels on the four retention metrics |
| `d-fx-treatment` | Which rate, at which moment, and does history restate? | Every revenue metric |
| `d-customer-grain` | Billing account, legal entity, or parent group? | Logo metrics, NRR denominator, ARPA, CAC |
| `d-cac-scope` | Which costs, and acquiring which customers? | CAC, CAC Payback, LTV:CAC, Magic Number |
| `d-cogs-scope` | What sits in COGS for a software business? | Gross Margin, LTV, CAC Payback |
| `d-ltv-method` | Formulaic, cohort-observed, or discounted? | LTV, LTV:CAC |
| `d-rule-of-40-composition` | Which growth measure, which profitability measure? | Rule of 40 |
| `d-win-rate-denominator` | Closed-lost only, or everything created? | Win Rate |

**Health check: 14 decisions.** Target was 10–14. If this climbs past ~20 the
guided flow stops being usable, and the correct response is to prune variants
rather than ship a longer questionnaire. See ADR-0004.

## The traversal is stateful

`d-pricing-model` must be asked first, because `d-usage-recurring-basis` only
appears for usage-based and hybrid businesses. A subscription-only company
answers 13 questions, not 14. Decisions therefore carry an optional
`applies_when` block referencing an earlier answer, and the guided flow is a
traversal rather than a flat list.

## Cohort and period retention are separate metrics, not variants

Cohort-based retention (what happened to the customers who were here at T0) and
period-over-period retention (what happened between two balance dates) answer
different questions with different denominators. They are four metric nodes —
`gross-retention-cohort`, `net-retention-cohort`, `gross-retention-period`,
`net-retention-period` — not two metrics with a basis variant.

The naming is a separate matter and genuinely contested, so it is its own
decision. See `d-retention-naming`.

## Parameters (not asked as decisions)

`dormancy_window_days` · `fiscal_year_start_month` · `ltv_discount_rate` ·
`cac_payback_threshold_months`

## Conventions (defaults, overridable)

Period grain is the calendar month · MRR is net of discounts · Snapshot date is
the last day of the period · Amounts are exclusive of tax
