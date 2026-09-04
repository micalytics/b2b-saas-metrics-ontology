# ADR-0005: Cost double-counting is resolved at composition, not by mutual exclusion

**Status:** Accepted — 2026-09-04

## Context

`d-cac-scope` asks which costs count toward acquisition. `d-cogs-scope` asks what
sits in COGS. Customer success can legitimately be selected by both, and a
business that does so double-counts:

- CS in COGS lowers gross margin, which lowers LTV.
- CS in CAC raises CAC.
- LTV:CAC is therefore penalised twice by the same dollar. CAC payback, which is
  gross-margin-adjusted, has the same defect.

The obvious fix is to forbid the overlap — declare the two decisions mutually
exclusive over shared categories. That fix is wrong, because in isolation both
choices are defensible:

- Reported gross margin **should** include customer success in COGS where the P&L
  puts it there. That is the accounting convention and what a board expects.
- CAC **may** legitimately include customer success where that team owns renewal
  and expansion, which is common in B2B.

Neither answer is an error on its own. The error appears only where a derived
metric consumes both.

## Decision

The constraint lives on the derived metric, not between the decisions. The two
decisions stay independent, and `gross-margin` carries two variants:

| Variant | Contents | Consumed by |
|---|---|---|
| `gross-margin-reported` | Follows the P&L, including customer success in COGS where it sits there | Reporting, Rule of 40 |
| `gross-margin-unit-economics` | Excludes every cost category also selected by `d-cac-scope` | LTV, CAC Payback, LTV:CAC |

Where `d-cac-scope` selects no category that `d-cogs-scope` also selects, the two
variants are numerically identical and the distinction is invisible.

Metric definitions therefore gain a `consumes` field naming which upstream
variant they read, so a bundle is checkable without running the guided flow. A
derived metric that reads `gross-margin` without qualifying which variant is a
validation error.

## Consequences

- No decision is forbidden, and no user is told their accounting is wrong.
- The double-count becomes structurally impossible rather than a documented
  warning nobody reads.
- Two margin figures will differ for businesses that put CS in CAC, and both are
  correct. Outputs must label which is which.
- This is the first cross-decision constraint in the model. Others are likely —
  capitalised commissions and professional services revenue are the next
  candidates — and they follow the same pattern: resolve at composition, express
  it as a variant, never as a prohibition.
