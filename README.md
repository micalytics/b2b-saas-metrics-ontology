# B2B SaaS Metrics Ontology

**An open reference ontology for B2B SaaS metrics that models all the competing definitions, not just one. Ships as ready-to-import OKF, OWL/RDF, OpenMetadata and Knowledge Catalog bundles.**

> **Status: v0.1 in progress.** The meta-model and scope are settled; metric content is being written. See [`log.md`](log.md) for the running journal and [`docs/adr/`](docs/adr/) for decisions.

---

## The problem

Every B2B SaaS company measures MRR, NRR, GRR, CAC and the Rule of 40. Almost none of them measure them the same way.

- **NRR** can be cohort-based or snapshot-based, and the window can be trailing-12-month or period-over-period.
- **MRR** can be contracted, billed, or recognized — and annual prepay splits them apart immediately.
- **Churn** can be dated at cancellation or at end-of-term, which moves it across period boundaries.
- **CAC** can be blended or paid-only, with or without customer success loaded in.

On the same underlying data, a defensible NRR can land anywhere between ~97% and ~112% depending on which definitions you picked. That gap is not an error — it is the absence of a shared model.

Existing metric glossaries pick one formula and present it as *the* formula. That makes them useless to every company that picked the other one.

## What this is

A machine-readable ontology where **the disagreement is first-class**:

- Every contested metric carries its **variants**, each with explicit assumptions, typed inputs and time semantics.
- **Decision nodes** encode the choices that select variants — pricing model, revenue basis, FX treatment, churn dating.
- A company records its answers in a **binding**, which resolves the ontology down to *their* definitions.
- One YAML source of truth **generates** every distribution format.

## What this is not

- Not a dbt project. See [SOMA-B2B-SaaS](https://github.com/Levers-Labs/SOMA-B2B-SaaS) and [GrowthCues Core](https://github.com/ArvoanDev/growthcues-core) for warehouse implementations — this is the layer above them.
- Not a benchmark dataset.
- Not a product/engagement metrics library. Activation, DAU/MAU, stickiness and feature adoption are deliberately out of scope; see [ADR-0001](docs/adr/0001-scope.md).

## Node types

The ontology has exactly three kinds of node ([ADR-0004](docs/adr/0004-node-types.md)):

| Node | Directory | What it is |
|---|---|---|
| **Entity** | `src/entities/` | Things that exist: Account, Subscription, Contract Line, Invoice, Opportunity, Cost, Period |
| **Metric** | `src/metrics/` | Measures over entities, with variants |
| **Decision** | `src/decisions/` | Choices that gate which metric variants are valid |

Not everything the ontology asks you about is a metric. FX treatment is a Decision plus entity properties, not a metric.

## Scope of v0.1

**Tier 1 — full variant treatment (12):**
MRR · ARR · Churned MRR · Expansion MRR · NRR/NDR · GRR · CAC · LTV · CAC Payback · Gross Margin · Rule of 40 · Win Rate

**Tier 2 — documented as components of their Tier 1 parent or metric family (~18):**
New MRR · Contraction MRR · Reactivation MRR · Net New MRR · Bookings · Billings · Logo Retention · Logo Churn · Gross Revenue Churn · Net Revenue Churn · LTV:CAC · Magic Number · Burn Multiple · Quick Ratio · Stage Conversion Rate · Sales Cycle Length · ACV · ARPA

Full rationale and exclusions in [ADR-0001](docs/adr/0001-scope.md).

## Bundles

Generated into `build/` and committed, so you can import without running the toolchain ([ADR-0003](docs/adr/0003-commit-generated-bundles.md)):

| Format | Path | Target |
|---|---|---|
| OKF v0.2 | `build/okf/` | Google Knowledge Catalog, AI agents, any OKF consumer |
| OWL + SKOS | `build/owl/` | Protégé, RDF triple stores |
| CSV | `build/openmetadata/` | OpenMetadata glossary bulk import |
| JSON | `build/knowledge-catalog/` | Dataplex / Knowledge Catalog glossary import |

## Roadmap

- **v0.1** — meta-model, decision nodes, Tier 1 metrics, all four bundles, worked example
- **v0.2** — a guided Skill that walks you through the decisions and emits your binding
- **v1.0** — interactive web guide, if there is demand for it

## Licence

- **Content** (`src/`, `build/`, `docs/`) — [CC BY 4.0](LICENSE-CONTENT)
- **Code** (`tools/`, CI) — [Apache 2.0](LICENSE)

## Contributing

Variants marked `status: draft` are open questions, not oversights — they are the best place to contribute. If your company defines a metric in a way this ontology cannot express, that is a bug worth an issue.
