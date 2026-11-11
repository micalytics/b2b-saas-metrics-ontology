# Metrics

A **metric** is a measure over entities. Tier 1 metrics carry variants; Tier 2
metrics are stubs nested inside their Tier 1 parent or attached to a family.
See ADR-0001.

## Required shape

```yaml
id: mrr                       # kebab-case, matches filename, stable forever
type: metric
tier: 1                       # 1 = full variant treatment, 2 = stub
family: revenue-base          # revenue-base | revenue-movement | retention
                              # unit-economics | commercial-efficiency
title: Monthly Recurring Revenue
preferred_label: MRR
aliases: [...]                # every name this is known by, for glossary matching
status: stable                # stable | draft | deprecated. A draft needs only
                              # the identity fields and a definition; every
                              # other field is required once it leaves draft.

definition: >                 # prose. What it measures, in one paragraph.
formula: >                    # variant-independent skeleton. Variants refine it.

unit: currency                # currency | ratio | percentage | count | duration
time_semantics:
  basis: point-in-time        # point-in-time | period
  as_of: ...                  # which instant, or which period boundary
  proration: ...              # what happens to mid-period changes
grain: ...                    # the level one value describes

reads_entities:               # every entity and property the formula touches
  - entity: contract-line
    properties: [amount, currency, start_date, end_date, is_recurring]

gated_by: [d-revenue-basis]   # every decision that affects this metric: variant
                              # selection, computation, population or label.
                              # Mirrors the decisions' gates: entries, which
                              # record how. Validation checks both directions.
consumes: []                  # ADR-0005. Named upstream VARIANTS, never bare
                              # metric ids. Empty only if nothing upstream.

variants:
  - id: mrr-committed
    selected_when: {decision: d-revenue-basis, equals: committed}
    formula: >
    assumptions: [...]
    status: stable

decomposable_by: [...]        # dimensions this can legitimately be split by
relations:                    # componentOf | derivedFrom | contrastWith,
                              # metric to metric only. A confusion with
                              # something outside the ontology is contrastWith
                              # a free-text concept instead of a target.
  - {type: contrastWith, target: arr}
  - {type: contrastWith, concept: Recognized revenue}
components: [...]             # Tier 2 stubs belonging to this metric
benchmarks: [...]             # with a source, or omitted entirely
pitfalls: [...]
sources: [...]
```

## Rules

**`consumes` names variants, not metrics.** A derived metric that reads
`gross-margin` without saying which variant is a validation error. This is what
makes the cost double-counting constraint checkable in CI rather than a warning
nobody reads — see ADR-0005. As LTV will declare it:

```yaml
consumes:
  - {metric: gross-margin, variant: gross-margin-unit-economics}
```

**Time semantics are not optional.** A metric that does not pin down
point-in-time versus period, the as-of instant, and proration behaviour is not
finished. Most real-world disagreements that look like formula disputes are
time-semantics disputes wearing a disguise.

**Every `reads_entities` property must exist** on the named entity. Validation
enforces this, and it is what stops a formula from quietly depending on a field
nobody has.

**Benchmarks need a source or they do not appear.** An unsourced range is worse
than no range, because it will be quoted.

**Variants are selected, never computed.** A `selected_when` points at a decision
and one of its option ids. A variant unreachable by any combination of answers is
dead, and validation should say so.

## Tier 2 stubs

Nested under their parent rather than given their own file:

```yaml
components:
  - id: new-mrr
    title: New MRR
    definition: >
    relation: componentOf
    tier: 2
```

Where a Tier 2 metric has no natural Tier 1 parent — Bookings, Billings, Logo
Retention — it attaches to its `family` instead, in that family's index file.
