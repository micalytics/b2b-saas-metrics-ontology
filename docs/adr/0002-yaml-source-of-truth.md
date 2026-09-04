# ADR-0002: A neutral YAML tree is the single source of truth

**Status:** Accepted — 2026-09-04

## Context

This project ships four distribution formats: OKF markdown bundles, OWL/RDF,
OpenMetadata glossary CSV, and Knowledge Catalog glossary JSON. More will follow
(dbt MetricFlow, Cube, a flat JSON for LLM tool use).

The tempting shortcut is to author directly in one of the target formats —
usually OKF, since it is markdown and pleasant to write, or OWL, since it feels
like "the real ontology". Either choice forces the other three to be maintained
by hand, and by metric twelve they will have silently diverged.

There is a second temptation worth naming: authoring in OWL because RDF *feels*
like the rigorous choice. It is not, for this domain. Nothing here needs
description-logic reasoning, and essentially nobody in the modern data stack
consumes OWL directly.

## Decision

`src/**/*.yaml` is the only source of truth. It is deliberately **format-neutral**
— it borrows nothing from OKF, OWL, or any target — and is validated against
JSON Schema in `src/schema/`.

Every distribution format is produced by an emitter in `tools/`. OWL is a
generated artifact, not the model.

## Consequences

- Adding a target format is writing one emitter, not re-authoring the content.
- The JSON Schema plus CI validation is what makes contributions safe.
- OWL/RDF still ships, and still loads in Protégé, and a reasoner still runs over
  it in CI — it just is not where the thinking happens.
- Reviewers only ever need to read YAML diffs. Generated diffs are noise and
  should be reviewed as such.
