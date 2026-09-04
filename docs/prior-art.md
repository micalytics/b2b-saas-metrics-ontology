# Prior art

Surveyed 2026-09-04, before writing any content. This is the honest map of what
already exists and where this project's gap actually is.

## Warehouse implementations (dbt-shaped)

**[Levers-Labs/SOMA-B2B-SaaS](https://github.com/Levers-Labs/SOMA-B2B-SaaS)** —
"Standard Operating Metrics & Analytics". ~386 stars, YAML metric definitions
plus dbt models and semantic-layer templates. The nearest thing to this project
in intent, but it is an *implementation* for one stack rather than a portable
ontology, and it commits to single definitions. No licence file visible at time
of survey.

**[GrowthCues Core](https://github.com/ArvoanDev/growthcues-core)** — open-source
dbt semantic layer for B2B SaaS. Strong on product/engagement (stickiness,
lifecycle states, volumetric churn), thin on finance. Same dbt coupling.
This project deliberately cedes the product-metrics ground to it — see ADR-0001.

**[dbt MetricFlow](https://www.getdbt.com/blog/open-source-metricflow-governed-metrics)**
— now open source. Mechanism, not content. A natural emitter target.

## Definition authorities

**[SaaS Metrics Standards Board](https://www.saasmetricsboard.com/)** — a
membership organisation publishing standard definitions (ARR, NRR, GRR, CAC
variants, logo retention, Rule of 40) as **PDFs**. Roughly ten metrics, no
machine-readable format, no stated open licence.

Positioning: complement, not competitor. This project is the machine-readable
layer. **Check their terms before quoting any formula verbatim.**

## Ontology work

- Academic KPI ontologies exist —
  [Ontology-driven KPI meta-modelling](https://www.sciencedirect.com/science/article/abs/pii/S026840121930581X),
  [Collaborative Building of an Ontology of KPIs](https://www.researchgate.net/publication/267508100_Collaborative_Building_of_an_Ontology_of_Key_Performance_Indicators).
  Abstract meta-models, no SaaS content, no industry adoption. Useful for rigour,
  not for reuse.
- [Magnowlia Business Ontology](https://magnowlia.com/ontology) — commercial, closed.
- FIBO covers financial instruments, not SaaS operating metrics. No meaningful overlap.

## The OKF ecosystem

[OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
(v0.2) launched mid-2026: a directory of markdown files with YAML frontmatter.
Required frontmatter is just `type`. Provenance via `sources` / `generated` /
`verified`; lifecycle via `status` and `stale_after`; relationships via ordinary
markdown links. Bundles distribute as git repositories.

Public directories index a few hundred bundles. Visible categories are SEO,
e-commerce ops, API docs and agent-memory tooling. **The "Analytics and Metrics"
category is effectively empty.** Existing tooling: okf-conformance, a Go parser,
OKF Skill Toolkit, Open Knowledge CLI — and **no RDF/OWL converter anywhere in
the ecosystem.**

Two unclaimed slots. The second is arguably more differentiating than the first.

### Worth knowing: `Attested Computation`

OKF defines a concept type where a value must derive from a sanctioned
computation — `runtime: bigquery`, typed parameters, an executor with a receipt
(`job_id`, `executed_sql`, `result`). Agents may supply parameter values but
never author the computation. Almost nobody is using it yet, and it is close to
purpose-built for binding a metric definition to an executable query.

## Import formats of the target platforms

| Platform | Format | Reference |
|---|---|---|
| Google Knowledge Catalog (ex-Dataplex) | JSON | [docs](https://docs.cloud.google.com/dataplex/docs/import-glossaries-entrylinks-json) |
| OpenMetadata | CSV | [docs](https://docs.open-metadata.org/latest/how-to-guides/data-governance/glossary/import) |
| Protégé | OWL / Turtle | — |
| OKF consumers | markdown + YAML frontmatter | [spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) |

Three of the four are cheap serialisations. That is the argument for ADR-0002.
