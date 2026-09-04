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
- Should `d-pricing-model` be asked *first* and used to skip whole branches, or
  asked in sequence like the rest? Asking it first shortens the flow for
  subscription-only companies but makes the traversal stateful.
- Is `d-retention-basis` really one decision, or two (cohort-vs-snapshot, and
  the window)? Splitting it would take the count to 14.

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
