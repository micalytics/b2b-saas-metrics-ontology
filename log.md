# Log

Change history, newest first. Structural decisions get an ADR in `docs/adr/`;
this file is the running journal and the list of open questions.

## TODO

- Add `.gitattributes` marking `build/` as `linguist-generated` (ADR-0003).
- Delete the leftover `.gitkeep` files in directories that now have content.
- Write the JSON Schema for decisions in `src/schema/` and wire up CI validation.
- Replace the illustrative "97% to 112%" NRR range in the README with the real
  figure once the Phase 4 worked example computes it.

## Open questions

- How many decision nodes are there really? Target is 10–14 for Tier 1. If it
  lands above ~20 the guided flow becomes unusable and the variant model needs
  pruning. **This count is the project's health check.**
- Do pure usage-based pricing companies have a meaningful MRR at all, or does
  the ontology need a parallel "recurring-equivalent revenue" concept?
- Does Bookings belong in Tier 1? TCV vs ACV vs new-only is a real disagreement.
- Should Gross Margin drop to Tier 2?
- Is `usage_floor_percentile: 10` the right default, or should it be 25? Needs
  testing against real consumption data before v0.1 ships.
- Does the trailing floor recompute every month, or reset only on contract
  events? Monthly recomputation is assumed but not yet stated in the model.

## 2026-09-04 (later)

- **Retention restructured.** Cohort and period-over-period retention are four
  separate metrics, not one metric with a basis variant — different denominators,
  different questions. `d-retention-basis` removed as a decision.
- **Naming made a decision.** Checked the market position before encoding one:
  the prevailing view is that NRR and NDR are synonyms, a terminological rather
  than mathematical split. Encoding the cohort/period naming distinction as
  canonical would reproduce the failure this project exists to correct, so
  `d-retention-naming` carries it as a labelling choice over stable metric IDs.
- **Usage-based MRR resolved.** `d-usage-recurring-basis` with five options
  grounded in public company filings: committed-minimum-only (Elastic, Cloudera),
  trailing-minimum, trailing-percentile, trailing-average (MongoDB),
  last-period-annualised (Datadog, DigitalOcean, HashiCorp, Sumo Logic).
  Default is trailing-percentile.
- **The traversal is stateful.** `d-pricing-model` is asked first and gates
  `d-usage-recurring-basis`; decisions carry `applies_when`.
- Count now **14**. Health check still passes.

## 2026-09-04

- **Phase 1 started.** Decisions enumerated before variants, deliberately: the
  question list is what determines which variants are load-bearing.
- **13 decisions** for the 12 Tier 1 metrics. Health check passes (target 10-14).
- Meta-model refined: *decision* vs *parameter* vs *convention*. Enumerating
  surfaced that several candidates were numeric knobs or uncontested defaults
  rather than branching choices. Demoting them is what kept the count at 13
  instead of ~20. See `src/decisions/README.md`.
- `d-revenue-basis` and `d-fx-treatment` written as the format template. The FX
  node carries `emits: false` on its single-currency option, which is the
  mechanism for excluding machinery a company does not need.
- Repository created, pushed, Apache-2.0 + CC BY 4.0 in place.
- Scaffold, licences and ADR-0001 through ADR-0004 written.
- Scope settled: 12 Tier 1 metrics with full variant treatment, ~18 Tier 2
  metrics as stubs. Product/engagement metrics explicitly out of scope.
- Meta-model settled on three node types: Entity, Metric, Decision.
