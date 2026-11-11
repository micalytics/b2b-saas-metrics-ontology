# Log

Change history, newest first. Structural decisions get an ADR in `docs/adr/`;
this file is the running journal and the list of open questions.

## TODO

- Add `.gitattributes` marking `build/` as `linguist-generated` (ADR-0003).
- Delete the leftover `.gitkeep` files in `src/entities`, `src/metrics`,
  `src/schema`, `tools`, `build/*` and `examples/*` (`git rm` them; the sandbox
  cannot).
- Write `tools/validate.py` and wire up CI. The cross-file checks it owns are
  listed in the `description` fields of `src/schema/*.json`. References to the
  enumerated-but-unwritten decisions and metrics are warnings, not errors.
- When `cac` is written, add it to `d-fx-treatment.gates`: it reads `cost`,
  which carries FX properties.
- Move the parameters typed provisionally in `binding.schema.json`
  (`max_pause_days`, `dormancy_window_days`, `usage_floor_recompute_months`,
  `opportunity_max_age_months`, `fiscal_year_start_month`, `ltv_discount_rate`,
  `cac_payback_threshold_months`) onto their owning nodes as those are written.
- Replace the illustrative "97% to 112%" NRR range in the README with the real
  figure once the worked example computes it. Now that cohort and
  period-over-period are separate metrics, that example is the cleanest possible
  demonstration: the same data, two bases, two defensible answers.

## Open questions

- How many decision nodes are there really? Target is 10–14 for Tier 1. If it
  lands above ~20 the guided flow becomes unusable and the variant model needs
  pruning. **This count is the project's health check.**
- Do pure usage-based pricing companies have a meaningful MRR at all, or does
  the ontology need a parallel "recurring-equivalent revenue" concept?
- Does Bookings belong in Tier 1? TCV vs ACV vs new-only is a real disagreement.
- Should Gross Margin drop to Tier 2?
- Is `usage_floor_percentile: 10` the right value, or 25? Needs testing against
  real consumption data before v0.1 ships. (Only applies when a user selects
  trailing-percentile; it is no longer the default.)
- Fixture inconsistencies found while writing the schemas, left unedited
  pending review (the schemas accept all of them as written):
- Tier 2 metrics without a parent live in a "family index file" whose format is
  not yet defined, so it has no schema.

## 2026-09-24

- **JSON Schemas written** in `src/schema/`: `common`, `entity`, `metric`,
  `decision`, `binding` (draft 2020-12, closed objects). All 13 fixtures
  validate unchanged. `consumes` entries must be `{metric, variant}` objects, so
  a bare metric id fails at schema level (ADR-0005). `selected_when` and
  `applies_when` share one condition shape (`decision` + exactly one of
  `equals`/`in`). A non-draft variant must carry `selected_when`.
- **Binding shape agreed**: `answers` (option + whether the default was
  accepted), `parameters`, `defaults` (conventions). Resolved variants are not
  stored. Conventions agreed in review:
  - no restriction to one variant per metric: `consumes` accepts a single
    variant id, a set of ids, or `selected` (which may resolve to a set)
  - `subscription.yaml` updated: pause-to-churn now reads `max_pause_days`;
    new `pause_start_date` property and a pitfall on backdated churn
- **Stale references fixed.** `invoice` → `invoice-line` in `d-revenue-basis`,
  `d-usage-recurring-basis` and `d-fx-treatment`. `d-fx-treatment` now gates
  the four retention metrics instead of `nrr`/`grr`, and no longer relates to
  the removed `d-retention-basis`. `cost` and `d-fx-treatment` now reference
  each other, since `cost` already carried FX properties gated on it.
- **ADR-0006: retention is four Tier 1 metrics**, amending ADR-0001. Tier 1 is
  now 14. Churned MRR and Expansion MRR moved out of `mrr.yaml` components into
  their own files, as ADR-0001 always specified; both are `draft`, carrying only
  their existing definition, gates and `componentOf: mrr`. The metric schema
  now requires only identity fields and a definition for a `draft` metric.
- **`selected_when: always`** added for a variant no decision selects.
  `net-retention-cohort-all` uses it instead of a condition on every option of
  the labels-only `d-retention-naming`.
- **Labels follow the naming default.** `net-retention-cohort` is now
  `NRR (cohort)`, the `synonymous` default's label, not `NDR`. Where
  `label_decided_by` is set, the validator will require `preferred_label` to
  match the default option's label.
- **`gated_by` means "affects this metric"**, matching how the fixtures use it:
  variant selection, computation, population or label. The how lives on the
  decision's `gates` entry. The validator will check the two are symmetric.
  To settle with `d-churn-dating`: `mrr` lists it in `gated_by`, but the
  decisions README table does not list MRR among what it gates.
- **One condition syntax.** `required_when` on parameters and entity
  properties now uses the structured condition, which gains `not_equals` and
  `not_in`. A parameter names its own decision explicitly.
- **`requires_entities` and `requires_entity_properties` merged** into
  `reads_entities` on decisions, mirroring metrics; `properties` optional.
- **`decimal` vs `number` kept deliberately**: entity properties are stored
  amounts, parameters are settings. Documented on the parameter definition.
- **Relations are metric to metric.** `mrr` drops `derivedFrom: contract-line`
  (already covered, more completely, by `reads_entities`). Recognized revenue
  becomes `contrastWith` a free-text `concept`, since ADR-0001 keeps it out of
  the ontology.
- Open: `net-retention-cohort-segmented` may be a decomposition (it overlaps
  `decomposable_by`) rather than a variant. Settle when retention is written.
  - customer M&A restates history by default (unsourced; see rationale)
  - a pause becomes churn after `max_pause_days`, dated at the pause start
  - `dormancy_window_days` now only separates reactivation from new
  - the usage floor recomputes every 3 months over the 12-month window
  - opportunities go stale after 3 months; treatment left to
    `d-win-rate-denominator`
  - grain fallback is a policy flag (`allow_grain_fallback`, default true),
    not a recorded count
  - capitalised commissions left untyped pending `d-cac-scope`

- **Meta-model closed.** Metric shape defined in `src/metrics/README.md`:
  tier, family, definition, formula, unit, time_semantics, reads_entities,
  gated_by, consumes, variants with `selected_when`, decomposable_by, relations,
  components, benchmarks, pitfalls, sources.
- `mrr` written with four variants (committed, billed, recognised, usage-floor)
  and all five movement components nested as Tier 2 stubs.
- **The movement identity is the correctness test.** Closing MRR minus opening
  MRR must equal Net New MRR exactly. A residual means a component is missing or
  double-counted, and it is the fastest available check that an implementation
  is right before anything is built on top.
- `net-retention-cohort` written as the second worked example; the three
  retention siblings follow the same shape. Carries `label_decided_by:
  d-retention-naming` so the emitted label follows the binding.
- `consumes: [{metric: mrr, variant: selected}]` introduced for the case where a
  metric takes whichever variant the binding chose, as against a named one.
- **CLAUDE.md rewritten** as the handoff document: all rules learned since the
  scaffold, plus a "what not to automate" section and an ordered next-steps list.
- Recreated `src/metrics`, `src/schema`, `tools` and `build/*`, which git had
  dropped when the `.gitkeep` files were removed. README licence link repointed
  at `LICENSE`.
- **Handoff point.** Everything after this is mechanical enough for Claude Code,
  with the emitters and synthetic-data work suited to an autonomous loop. Metric
  and decision content stays interactive.

## 2026-09-04 (cross-decision constraints)

- **First cross-decision constraint solved.** Customer success selected by both
  `d-cac-scope` and `d-cogs-scope` double-counts: one dollar lowers LTV through
  margin and raises CAC at the same time.
- Rejected the obvious fix. Mutual exclusion between the two decisions would
  forbid two individually defensible answers — reported gross margin *should*
  carry CS in COGS, and CAC *may* legitimately carry CS where that team owns
  renewal. The error exists only at composition.
- **Resolution: two gross-margin variants.** `gross-margin-reported` for the P&L
  and Rule of 40; `gross-margin-unit-economics`, excluding anything selected by
  `d-cac-scope`, for LTV and CAC Payback. Identical when there is no overlap.
- Metrics gain a `consumes` field naming which upstream variant they read, so a
  bundle validates without running the guided flow. See ADR-0005.
- Pattern for future constraints: resolve at composition, express as a variant,
  never as a prohibition. Capitalised commissions and professional services
  revenue are the next likely candidates.

## 2026-09-04 (entities complete)

- All seven entities written: `party`, `customer`, `subscription`,
  `contract-line`, `invoice-line`, `cost`, `opportunity`.
- **Cost has no customer relationship, confirmed as deliberate.** CAC is not
  measurable per customer, so the link does not exist and allocation assumptions
  cannot masquerade as facts. `cost.attribution` defaults to `unattributed`.
- `party.hierarchy_level` added so `d-customer-grain` resolves without walking
  the tree by hand.
- `subscription` carries all three candidate churn dates side by side
  (`cancellation_notice_date`, `service_end_date`, `last_paid_period_end`) so
  `d-churn-dating` selects rather than derives.
- `opportunity.outcome` separates `disqualified` from `lost`, which is what makes
  `d-win-rate-denominator` a real choice.

## 2026-09-04 (entities)

- **Entity model started.** `src/entities/README.md` with the model, the grain
  table, and the reasoning; `contract-line` and `invoice-line` written as the
  first two, since between them they are read by five of the fourteen decisions.
- **Party vs Customer split.** `d-customer-grain` cannot be baked into the data
  model, so the ontology models `party` with a self-referencing hierarchy and
  treats `customer` as a resolved view at the chosen grain. Logo counts, NRR
  denominators and CAC all move when the grain changes — correct behaviour, and
  the clearest demonstration of why bindings exist.
- **Period is a convention, not an entity.** Generated from
  `fiscal_year_start_month` plus the period-grain convention.
- **No usage entity.** Consumption history derives from `invoice-line` rows
  flagged `is_usage`.
- Usage default switched to last-period-annualised per the defaults rule.

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
  Default is last-period-annualised — the market-practice rule below.
- **Defaults rule established.** A default follows prevailing market practice,
  not the strongest option, with `default_rationale` where the two diverge. The
  usage node is the first case: last-period-annualised is more inflationary than
  the trailing methods, and is still the default because it is what most
  usage-based public companies do.
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
