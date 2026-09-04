# Entities

Entities are the things that exist. Metrics are measures over them. Without this
layer the formulas are prose — "expansion MRR is the increase in MRR from
existing customers" says nothing a query can act on.

The rule for this directory: **model only what a Tier 1 metric or a decision
actually needs.** This is not an attempt at a canonical SaaS billing schema.
Every property here should be traceable to something that reads it.

## The model

```
        Party ──┐ (self-referencing hierarchy)
                │
             Customer          resolved from Party at the grain
                │              chosen in d-customer-grain
       ┌────────┼────────┐
       │        │        │
  Subscription  │   Opportunity
       │        │
  ContractLine  │
       │        │
  InvoiceLine ──┘

  Cost — attaches to a period and a category, not to a customer
```

## Why Party and Customer are separate

`d-customer-grain` asks whether a customer is a billing account, a legal entity,
or a parent group. That choice cannot be baked into the data model, because the
same underlying records must support all three answers.

So the ontology models **Party** — a node with an optional `parent_party_id` —
and treats **Customer** as a *resolved view* over that hierarchy at whichever
grain the binding selected. Logo counts, NRR denominators and CAC all read
Customer, and all move when the grain changes. That is correct behaviour, not a
bug, and it is the cleanest demonstration of why bindings exist.

## Grain

| Entity | Grain | Notes |
|---|---|---|
| `party` | One row per organisation or billing account | Self-referencing |
| `customer` | Resolved view over `party` | Grain set by `d-customer-grain` |
| `subscription` | One row per subscription lifecycle | Carries the churn dates |
| `contract-line` | One row per priced line per term | The grain for committed revenue |
| `invoice-line` | One row per billed line per period | The grain for billed revenue |
| `opportunity` | One row per sales opportunity | Win rate, sales cycle |
| `cost` | One row per cost category per period | CAC and COGS scopes |

## Period is a convention, not an entity

Periods are generated from `fiscal_year_start_month` and the period-grain
convention. Modelling them as an entity adds a table and answers no question the
convention does not already answer.

## Usage records are not a separate entity

`d-usage-recurring-basis` needs a consumption history per customer. That is
derivable from `invoice-line` rows flagged `is_usage`, so no separate usage
entity is introduced. If a business bills usage in arrears at a different grain
than it meters it, that is a mapping problem on the way in, not an ontology
problem.

## Cost has no customer relationship, by design

Acquisition cost is not measurable per customer in practice. Modelling a link
between `cost` and `customer` would let allocation assumptions pass themselves
off as facts, so the relationship does not exist. CAC is a portfolio metric over
a cohort acquired in a period, and the ontology can only express it that way.

`cost.attribution` exists to separate new-business from expansion spend where a
business genuinely tracks it, and defaults to `unattributed` because most rows
honestly are. What `d-cac-scope` does with unattributed cost is an assumption,
and that node has to say so out loud.

## Status

All seven entities are written. Two open questions remain:

- Does `contract-line` need an explicit amendment or version chain, or is a
  start/end date per line sufficient to reconstruct history? Sufficient for the
  Tier 1 metrics as currently scoped, but expansion attribution may force it.
- When customers merge or are acquired, is history restated under the new parent
  or left under the old one? Changes retention; recorded in the binding rather
  than decided here.
