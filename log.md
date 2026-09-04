# Log

Change history, newest first. Structural decisions get an ADR in `docs/adr/`;
this file is the running journal and the list of open questions.

## TODO

- Add the Apache-2.0 `LICENSE` file (GitHub: *Add file -> Create new file ->
  name it `LICENSE` -> "Choose a license template" -> Apache 2.0*). Not written
  here because the licence text could not be fetched offline.
- Add `.gitattributes` marking `build/` as `linguist-generated` (ADR-0003).

## Open questions

- How many decision nodes are there really? Target is 10–14 for Tier 1. If it
  lands above ~20 the guided flow becomes unusable and the variant model needs
  pruning. **This count is the project's health check.**
- Do pure usage-based pricing companies have a meaningful MRR at all, or does
  the ontology need a parallel "recurring-equivalent revenue" concept?
- Does Bookings belong in Tier 1? TCV vs ACV vs new-only is a real disagreement.
- Should Gross Margin drop to Tier 2?

## 2026-09-04

- Repository created.
- Scaffold, licences and ADR-0001 through ADR-0004 written.
- Scope settled: 12 Tier 1 metrics with full variant treatment, ~18 Tier 2
  metrics as stubs. Product/engagement metrics explicitly out of scope.
- Meta-model settled on three node types: Entity, Metric, Decision.
