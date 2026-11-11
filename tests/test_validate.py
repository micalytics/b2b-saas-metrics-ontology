"""Each test breaks one rule on a freshly loaded copy of the real ontology
and checks the validator reports it. The repo itself must stay error-free."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import validate  # noqa: E402


@pytest.fixture
def ont():
    return validate.load()


def errors(ont):
    return [msg for _, msg in validate.check(ont).errors]


def warnings(ont):
    return [msg for _, msg in validate.check(ont).warnings]


def assert_error(ont, fragment):
    found = errors(ont)
    assert any(fragment in e for e in found), f"no error containing {fragment!r} in {found}"


def binding(**answers):
    return {
        "id": "test-binding",
        "type": "binding",
        "title": "Test binding",
        "answers": {d: {"option": o, "source": "explicit"} for d, o in answers.items()},
    }


def add_binding(ont, doc):
    ont.add("bindings", doc, "examples/test/binding.yaml")
    return doc


# ---------------------------------------------------------------- the repo


def test_repo_has_no_errors(ont):
    assert errors(ont) == []


def test_planned_decisions_are_read_from_the_readme(ont):
    assert "d-pricing-model" in ont.planned_decisions
    assert len(ont.planned_decisions) == 14


# ------------------------------------------------------------ schema pass


def test_schema_error_is_reported_and_file_skipped(ont):
    ont.metrics["mrr"]["consumes"] = ["gross-margin"]
    found = errors(ont)
    assert any(e.startswith("schema: consumes/0") for e in found)


# ------------------------------------------------------------------- ids


def test_component_colliding_with_a_metric_file(ont):
    ont.metrics["mrr"]["components"].append(
        {"id": "churned-mrr", "title": "Churned MRR", "tier": 2, "relation": "componentOf", "definition": "x"}
    )
    assert_error(ont, "component 'churned-mrr' collides")


def test_variant_id_prefix(ont):
    ont.metrics["mrr"]["variants"][0]["id"] = "committed-mrr"
    assert_error(ont, "must start with 'mrr-'")


# ------------------------------------------------------------- references


def test_unknown_decision_is_an_error_planned_one_a_warning(ont):
    ont.metrics["mrr"]["gated_by"].append("d-made-up")
    assert_error(ont, "unknown decision 'd-made-up'")
    assert any("'d-pricing-model' is planned" in w for w in warnings(ont))


def test_unknown_entity_property(ont):
    ont.metrics["mrr"]["reads_entities"][0]["properties"].append("no_such_field")
    assert_error(ont, "has no property 'no_such_field'")


def test_condition_option_must_belong_to_its_decision(ont):
    ont.metrics["mrr"]["variants"][0]["selected_when"]["equals"] = "booked"
    assert_error(ont, "'booked' is not an option of d-revenue-basis")


def test_default_must_be_an_option(ont):
    ont.decisions["d-revenue-basis"]["default"] = "booked"
    assert_error(ont, "default 'booked' is not an option")


def test_option_parameters_must_be_declared(ont):
    ont.decisions["d-usage-recurring-basis"]["options"][1]["parameters"].append("made_up")
    assert_error(ont, "undeclared parameter 'made_up'")


# ------------------------------------------------------- variants and gates


def test_selected_when_decision_must_be_in_gated_by(ont):
    ont.metrics["mrr"]["gated_by"].remove("d-revenue-basis")
    assert_error(ont, "missing from gated_by")


def test_unreachable_variant(ont):
    ont.metrics["mrr"]["variants"][0]["selected_when"] = {"decision": "d-revenue-basis", "in": ["committed"]}
    ont.decisions["d-revenue-basis"]["options"] = [
        o for o in ont.decisions["d-revenue-basis"]["options"] if o["id"] != "committed"
    ]
    ont.decisions["d-revenue-basis"]["default"] = "billed"
    assert_error(ont, "unreachable")


def test_gated_by_and_gates_are_symmetric(ont):
    ont.decisions["d-fx-treatment"]["gates"] = [
        g for g in ont.decisions["d-fx-treatment"]["gates"] if g["metric"] != "mrr"
    ]
    assert_error(ont, "lists this decision in gated_by but gates does not list mrr")


def test_gates_variant_must_exist(ont):
    ont.decisions["d-revenue-basis"]["gates"][0]["variants"].append("mrr-booked")
    assert_error(ont, "gates variant 'mrr-booked'")


def test_reads_entities_and_read_by_decisions_are_symmetric(ont):
    ont.entities["cost"]["read_by_decisions"].remove("d-fx-treatment")
    assert_error(ont, "reads this entity but read_by_decisions does not list it")


# --------------------------------------------------------------- consumes


def test_consumes_named_variant_must_exist(ont):
    ont.metrics["net-retention-cohort"]["consumes"] = [{"metric": "mrr", "variant": "mrr-booked"}]
    assert_error(ont, "consumes 'mrr-booked'")


def test_consumes_accepts_a_set_of_variants(ont):
    ont.metrics["net-retention-cohort"]["consumes"] = [
        {"metric": "mrr", "variant": ["mrr-committed", "mrr-usage-floor"]}
    ]
    assert errors(ont) == []


def test_consumes_cannot_name_a_variant_of_a_component(ont):
    ont.metrics["net-retention-cohort"]["consumes"].append({"metric": "new-mrr", "variant": "new-mrr-x"})
    assert_error(ont, "Tier 2 component")


# ------------------------------------------------------------------ labels


def test_preferred_label_must_match_naming_default(ont):
    ont.metrics["net-retention-cohort"]["preferred_label"] = "NDR"
    assert_error(ont, "differs from the label 'NRR (cohort)'")


# ------------------------------------------------------------- traversal


def test_applies_when_cycle(ont):
    ont.decisions["d-revenue-basis"]["applies_when"] = {"decision": "d-fx-treatment", "equals": "spot-at-transaction"}
    ont.decisions["d-fx-treatment"]["applies_when"] = {"decision": "d-revenue-basis", "equals": "committed"}
    assert_error(ont, "applies_when cycle")


def test_applies_when_self_reference(ont):
    ont.decisions["d-fx-treatment"]["applies_when"] = {"decision": "d-fx-treatment", "equals": "single-currency"}
    assert_error(ont, "refers to the decision itself")


def test_parameter_declared_twice(ont):
    ont.metrics["mrr"]["parameters"] = [{"id": "reporting_currency", "type": "string"}]
    assert_error(ont, "parameter 'reporting_currency' also declared")


# ---------------------------------------------------------------- bindings


ALL_WRITTEN = {
    "d-revenue-basis": "committed",
    "d-fx-treatment": "single-currency",
    "d-retention-naming": "synonymous",
}


def test_valid_binding(ont):
    add_binding(ont, binding(**ALL_WRITTEN))
    assert errors(ont) == []


def test_binding_missing_an_answer(ont):
    answers = dict(ALL_WRITTEN)
    del answers["d-fx-treatment"]
    add_binding(ont, binding(**answers))
    assert_error(ont, "d-fx-treatment applies but is not answered")


def test_binding_answers_a_decision_that_does_not_apply(ont):
    ont.decisions["d-fx-treatment"]["applies_when"] = {"decision": "d-revenue-basis", "equals": "billed"}
    add_binding(ont, binding(**ALL_WRITTEN))
    assert_error(ont, "d-fx-treatment is answered but does not apply")


def test_binding_default_source_must_match_default(ont):
    b = add_binding(ont, binding(**ALL_WRITTEN))
    b["answers"]["d-revenue-basis"] = {"option": "billed", "source": "default"}
    assert_error(ont, "source is 'default' but the default is 'committed'")


def test_binding_required_parameter(ont):
    add_binding(ont, binding(**{**ALL_WRITTEN, "d-fx-treatment": "spot-at-transaction"}))
    assert_error(ont, "parameter 'reporting_currency' is required")


def test_binding_undeclared_parameter(ont):
    b = add_binding(ont, binding(**ALL_WRITTEN))
    b["parameters"] = {"made_up_days": 3}
    assert_error(ont, "parameter 'made_up_days' is not declared")


def test_binding_parameter_type(ont):
    b = add_binding(ont, binding(**ALL_WRITTEN))
    b["parameters"] = {"usage_floor_window_months": "twelve"}
    assert_error(ont, "should be integer")


def test_binding_provisional_parameter_is_accepted(ont):
    b = add_binding(ont, binding(**ALL_WRITTEN))
    b["parameters"] = {"max_pause_days": 90}
    assert errors(ont) == []
