#!/usr/bin/env python3
"""Validate the ontology: every file against its JSON Schema, then the
cross-file rules no single-file schema can express.

    python tools/validate.py            # errors fail, warnings do not
    python tools/validate.py --strict   # warnings fail too

Errors are things that are wrong. Warnings are references to nodes that are
enumerated but not yet written: a decision listed in src/decisions/README.md,
or any metric id without a file. Those are expected while the ontology is
being built, and --strict is the gate for a release.

The rules checked here are the ones stated in the `description` fields of
src/schema/*.json. When a rule changes, change it in both places.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
KINDS = {"entity": "entities", "metric": "metrics", "decision": "decisions"}


class _Loader(yaml.SafeLoader):
    """SafeLoader that keeps dates as strings, as JSON Schema expects."""


_Loader.yaml_implicit_resolvers = {
    ch: [(tag, rx) for tag, rx in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for ch, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


@dataclass
class Report:
    errors: list[tuple[str, str]] = field(default_factory=list)
    warnings: list[tuple[str, str]] = field(default_factory=list)

    def error(self, where: str, msg: str) -> None:
        self.errors.append((where, msg))

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append((where, msg))


@dataclass
class Ontology:
    """Every node keyed by id, plus bindings and the planned decision ids."""

    entities: dict[str, dict] = field(default_factory=dict)
    metrics: dict[str, dict] = field(default_factory=dict)
    decisions: dict[str, dict] = field(default_factory=dict)
    bindings: dict[str, dict] = field(default_factory=dict)
    paths: dict[int, str] = field(default_factory=dict)  # id(doc) -> path
    planned_decisions: set[str] = field(default_factory=set)
    schemas: dict[str, dict] = field(default_factory=dict)

    def where(self, doc: dict) -> str:
        return self.paths.get(id(doc), "?")

    def add(self, kind: str, doc: dict, path: str) -> None:
        self.paths[id(doc)] = path
        key = doc.get("id") if isinstance(doc, dict) else None
        getattr(self, kind if kind == "bindings" else KINDS[kind])[key or path] = doc


# ---------------------------------------------------------------- loading


def load(root: Path = ROOT) -> Ontology:
    ont = Ontology()
    for p in sorted((root / "src" / "schema").glob("*.schema.json")):
        ont.schemas[p.name] = json.loads(p.read_text())
    for kind, folder in KINDS.items():
        for p in sorted((root / "src" / folder).glob("*.yaml")):
            ont.add(kind, yaml.load(p.read_text(), Loader=_Loader), str(p.relative_to(root)))
    for p in sorted((root / "examples").glob("**/*.yaml")):
        ont.add("bindings", yaml.load(p.read_text(), Loader=_Loader), str(p.relative_to(root)))
    readme = root / "src" / "decisions" / "README.md"
    if readme.exists():
        ont.planned_decisions = set(re.findall(r"^\| `(d-[a-z0-9-]+)` \|", readme.read_text(), re.M))
    return ont


# ------------------------------------------------------------- schema pass


def validate_schemas(ont: Ontology, report: Report) -> None:
    """Schema-check every file. Files that fail are dropped from the
    ontology, so the cross-file pass only ever sees well-formed documents."""
    registry = Registry().with_resources(
        [(name, Resource.from_contents(s)) for name, s in ont.schemas.items()]
    )
    for name, schema in ont.schemas.items():
        Draft202012Validator.check_schema(schema)

    def run(kind: str, table: dict[str, dict]) -> None:
        validator = Draft202012Validator(
            ont.schemas[f"{kind}.schema.json"], registry=registry, format_checker=FormatChecker()
        )
        for key, doc in list(table.items()):
            errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))
            for e in errors:
                loc = "/".join(map(str, e.absolute_path)) or "(root)"
                report.error(ont.where(doc), f"schema: {loc}: {_short(e.message)}")
            if errors:
                del table[key]

    for kind, folder in KINDS.items():
        run(kind, getattr(ont, folder))
    run("binding", ont.bindings)


def _short(msg: str, limit: int = 160) -> str:
    return msg if len(msg) <= limit else msg[: limit - 1] + "…"


# ----------------------------------------------------------- reference helpers


class Refs:
    def __init__(self, ont: Ontology, report: Report):
        self.ont, self.report = ont, report
        self.components = {
            c["id"]: m for m in ont.metrics.values() for c in m.get("components", [])
        }

    def decision(self, did: str, where: str) -> dict | None:
        if did in self.ont.decisions:
            return self.ont.decisions[did]
        if did in self.ont.planned_decisions:
            self.report.warn(where, f"decision '{did}' is planned but not yet written")
        else:
            self.report.error(where, f"unknown decision '{did}' (not written, not in src/decisions/README.md)")
        return None

    def metric(self, mid: str, where: str) -> dict | None:
        """Return the metric's file, or None for a component or unwritten metric."""
        if mid in self.ont.metrics:
            return self.ont.metrics[mid]
        if mid not in self.components:
            self.report.warn(where, f"metric '{mid}' is not yet written")
        return None

    def entity(self, eid: str, where: str) -> dict | None:
        if eid in self.ont.entities:
            return self.ont.entities[eid]
        self.report.error(where, f"unknown entity '{eid}'")
        return None


def options_of(decision: dict) -> list[str]:
    return [o["id"] for o in decision["options"]]


def matching_options(cond: dict, decision: dict) -> set[str]:
    opts = set(options_of(decision))
    if "equals" in cond:
        return opts & {cond["equals"]}
    if "in" in cond:
        return opts & set(cond["in"])
    if "not_equals" in cond:
        return opts - {cond["not_equals"]}
    return opts - set(cond["not_in"])


def condition_holds(cond: dict, answer: str) -> bool:
    if "equals" in cond:
        return answer == cond["equals"]
    if "in" in cond:
        return answer in cond["in"]
    if "not_equals" in cond:
        return answer != cond["not_equals"]
    return answer not in cond["not_in"]


def check_condition(refs: Refs, cond, where: str) -> dict | None:
    """Check a condition's references. Returns the decision when it is written."""
    if cond == "always":
        return None
    decision = refs.decision(cond["decision"], where)
    if decision is None:
        return None
    named = [cond[k] for k in ("equals", "not_equals") if k in cond]
    named += [o for k in ("in", "not_in") if k in cond for o in cond[k]]
    for opt in named:
        if opt not in options_of(decision):
            refs.report.error(where, f"'{opt}' is not an option of {decision['id']}")
    return decision


# --------------------------------------------------------- cross-file checks


def check_ids(ont: Ontology, report: Report) -> None:
    seen: dict[str, str] = {}
    for folder in KINDS.values():
        for nid, doc in getattr(ont, folder).items():
            where = ont.where(doc)
            if Path(where).stem != nid:
                report.error(where, f"filename does not match id '{nid}'")
            if nid in seen:
                report.error(where, f"id '{nid}' also used by {seen[nid]}")
            seen[nid] = where
    for m in ont.metrics.values():
        for c in m.get("components", []):
            if c["id"] in seen:
                report.error(ont.where(m), f"component '{c['id']}' collides with {seen[c['id']]}")
            seen[c["id"]] = ont.where(m)


def check_entities(ont: Ontology, refs: Refs, report: Report) -> None:
    for e in ont.entities.values():
        where = ont.where(e)
        names = [p["name"] for p in e["properties"]]
        for dup in {n for n in names if names.count(n) > 1}:
            report.error(where, f"property '{dup}' declared twice")
        for p in e["properties"]:
            if "references" in p:
                refs.entity(p["references"], where)
            if "required_when" in p:
                check_condition(refs, p["required_when"], where)
        if "resolved_from" in e:
            refs.entity(e["resolved_from"], where)
        for mid in e.get("read_by_metrics", []):
            refs.metric(mid, where)
        for did in e.get("read_by_decisions", []):
            refs.decision(did, where)


def check_reads(ont: Ontology, refs: Refs, node: dict) -> None:
    where = ont.where(node)
    for r in node.get("reads_entities", []):
        entity = refs.entity(r["entity"], where)
        if entity is None:
            continue
        have = {p["name"] for p in entity["properties"]}
        for prop in r.get("properties", []):
            if prop not in have:
                refs.report.error(where, f"entity '{entity['id']}' has no property '{prop}'")


def check_decisions(ont: Ontology, refs: Refs, report: Report) -> None:
    for d in ont.decisions.values():
        where = ont.where(d)
        opts = options_of(d)
        for dup in {o for o in opts if opts.count(o) > 1}:
            report.error(where, f"option '{dup}' declared twice")
        if d["default"] not in opts:
            report.error(where, f"default '{d['default']}' is not an option")
        params = {p["id"] for p in d.get("parameters", [])}
        for o in d["options"]:
            for pid in o.get("parameters", []):
                if pid not in params:
                    report.error(where, f"option '{o['id']}' uses undeclared parameter '{pid}'")
            for mid in o.get("labels", {}):
                refs.metric(mid, where)
        for p in d.get("parameters", []):
            if "required_when" in p:
                check_condition(refs, p["required_when"], where)
        if "applies_when" in d:
            if d["applies_when"]["decision"] == d["id"]:
                report.error(where, "applies_when refers to the decision itself")
            else:
                check_condition(refs, d["applies_when"], where)
        for did in d.get("related_decisions", []):
            refs.decision(did, where)
        for g in d["gates"]:
            metric = refs.metric(g["metric"], where)
            if metric is not None:
                variants = {v["id"] for v in metric.get("variants", [])}
                for vid in g.get("variants", []):
                    if vid not in variants:
                        report.error(where, f"gates variant '{vid}', which {metric['id']} does not have")
        check_reads(ont, refs, d)


def check_applies_when_acyclic(ont: Ontology, report: Report) -> None:
    graph = {
        did: d["applies_when"]["decision"]
        for did, d in ont.decisions.items()
        if "applies_when" in d
    }
    for start in graph:
        seen, node = [start], graph[start]
        while node in graph:
            if node in seen:
                cycle = " -> ".join(seen[seen.index(node):] + [node])
                report.error(ont.where(ont.decisions[start]), f"applies_when cycle: {cycle}")
                break
            seen.append(node)
            node = graph[node]


def can_be_asked(ont: Ontology, did: str, _depth: int = 0) -> bool | None:
    """True if some path of answers reaches this decision, False if none
    does, None if that depends on a decision not yet written."""
    d = ont.decisions.get(did)
    if d is None or _depth > len(ont.decisions):
        return None
    cond = d.get("applies_when")
    if cond is None:
        return True
    gate = ont.decisions.get(cond["decision"])
    if gate is None:
        return None
    if not matching_options(cond, gate):
        return False
    return can_be_asked(ont, gate["id"], _depth + 1)


def check_metrics(ont: Ontology, refs: Refs, report: Report) -> None:
    for m in ont.metrics.values():
        where = ont.where(m)
        mid = m["id"]
        gated_by = set(m.get("gated_by", []))
        for did in gated_by:
            refs.decision(did, where)

        vids = [v["id"] for v in m.get("variants", [])]
        for dup in {v for v in vids if vids.count(v) > 1}:
            report.error(where, f"variant '{dup}' declared twice")
        for v in m.get("variants", []):
            vwhere = f"{where} [{v['id']}]"
            if not v["id"].startswith(mid + "-"):
                report.error(vwhere, f"variant id must start with '{mid}-'")
            cond = v.get("selected_when")
            if cond is None or cond == "always":
                continue
            if cond["decision"] not in gated_by:
                report.error(vwhere, f"selected_when uses {cond['decision']}, which is missing from gated_by")
            decision = check_condition(refs, cond, vwhere)
            if decision is None or v["status"] == "draft":
                continue
            if not matching_options(cond, decision) or can_be_asked(ont, decision["id"]) is False:
                report.error(vwhere, "unreachable: no combination of answers selects this variant")

        for c in m.get("consumes", []):
            target = refs.metric(c["metric"], where)
            named = c["variant"] if isinstance(c["variant"], list) else [c["variant"]]
            named = [n for n in named if n != "selected"]
            if c["metric"] in refs.components and named:
                report.error(where, f"consumes a variant of '{c['metric']}', a Tier 2 component with no variants")
            if target is not None:
                have = {v["id"] for v in target.get("variants", [])}
                for n in named:
                    if n not in have:
                        report.error(where, f"consumes '{n}', which {target['id']} does not have")

        if "label_decided_by" in m:
            decision = refs.decision(m["label_decided_by"], where)
            if decision is not None:
                gate = [g for g in decision["gates"] if g["metric"] == mid]
                if not any(g.get("affects") == "preferred_label" for g in gate):
                    report.error(where, f"{decision['id']} does not gate this metric with affects: preferred_label")
                default = next(o for o in decision["options"] if o["id"] == decision["default"])
                label = default.get("labels", {}).get(mid)
                if label is not None and label != m["preferred_label"]:
                    report.error(
                        where,
                        f"preferred_label '{m['preferred_label']}' differs from the label "
                        f"'{label}' given by {decision['id']}'s default",
                    )

        for r in m.get("relations", []):
            if "target" in r:
                refs.metric(r["target"], where)
        check_reads(ont, refs, m)


def check_symmetry(ont: Ontology, report: Report) -> None:
    """gated_by mirrors gates; decisions' reads_entities mirror entities'
    read_by_decisions. Checked only where both ends are written."""
    for did, d in ont.decisions.items():
        gated = {g["metric"] for g in d["gates"]}
        for mid, m in ont.metrics.items():
            listed = did in m.get("gated_by", [])
            if mid in gated and not listed:
                report.error(ont.where(m), f"{did} gates this metric but gated_by does not list it")
            if listed and mid not in gated:
                report.error(ont.where(d), f"{mid} lists this decision in gated_by but gates does not list {mid}")
        reads = {r["entity"] for r in d.get("reads_entities", [])}
        for eid, e in ont.entities.items():
            listed = did in e.get("read_by_decisions", [])
            if eid in reads and not listed:
                report.error(ont.where(e), f"{did} reads this entity but read_by_decisions does not list it")
            if listed and eid not in reads:
                report.error(ont.where(d), f"{eid} lists this decision in read_by_decisions but reads_entities does not list {eid}")


def declared_parameters(ont: Ontology) -> dict[str, dict]:
    return {
        p["id"]: p
        for node in [*ont.decisions.values(), *ont.metrics.values()]
        for p in node.get("parameters", [])
    }


def check_parameters_unique(ont: Ontology, report: Report) -> None:
    owner: dict[str, str] = {}
    for node in [*ont.decisions.values(), *ont.metrics.values()]:
        for p in node.get("parameters", []):
            if p["id"] in owner:
                report.error(ont.where(node), f"parameter '{p['id']}' also declared in {owner[p['id']]}")
            owner[p["id"]] = ont.where(node)


def check_bindings(ont: Ontology, refs: Refs, report: Report) -> None:
    provisional = ont.schemas["binding.schema.json"]["properties"]["parameters"]["properties"]
    declared = declared_parameters(ont)
    json_type = {"integer": int, "number": (int, float), "string": str}
    for b in ont.bindings.values():
        where = ont.where(b)
        answers = {did: a["option"] for did, a in b["answers"].items()}
        for did, a in b["answers"].items():
            d = refs.decision(did, where)
            if d is None:
                continue
            if a["option"] not in options_of(d):
                report.error(where, f"{did}: '{a['option']}' is not an option")
            if a["source"] == "default" and a["option"] != d["default"]:
                report.error(where, f"{did}: source is 'default' but the default is '{d['default']}'")
        for did, d in ont.decisions.items():
            cond = d.get("applies_when")
            if cond is None:
                asked = True
            elif cond["decision"] in answers:
                asked = condition_holds(cond, answers[cond["decision"]])
            else:
                continue  # depends on an unanswered or unwritten decision
            if asked and did not in answers:
                report.error(where, f"{did} applies but is not answered")
            if not asked and did in answers:
                report.error(where, f"{did} is answered but does not apply ({cond['decision']} = {answers[cond['decision']]})")

        params = b.get("parameters", {})
        for pid, value in params.items():
            if pid in declared:
                expected = json_type[declared[pid]["type"]]
                if isinstance(value, bool) or not isinstance(value, expected):
                    report.error(where, f"parameter '{pid}' should be {declared[pid]['type']}")
            elif pid not in provisional:
                report.error(where, f"parameter '{pid}' is not declared by any decision or metric")
        for pid, p in declared.items():
            cond = p.get("required_when")
            if cond is None or pid in params or "default" in p:
                continue
            if cond["decision"] in answers and condition_holds(cond, answers[cond["decision"]]):
                report.error(where, f"parameter '{pid}' is required by {cond['decision']} = {answers[cond['decision']]}")


def check(ont: Ontology) -> Report:
    """Run every check. The schema pass drops invalid files from copies of
    the node tables, never from `ont` itself, so callers can reuse it."""
    ont = copy.copy(ont)
    for folder in (*KINDS.values(), "bindings"):
        setattr(ont, folder, dict(getattr(ont, folder)))
    report = Report()
    validate_schemas(ont, report)
    refs = Refs(ont, report)
    check_ids(ont, report)
    check_entities(ont, refs, report)
    check_decisions(ont, refs, report)
    check_applies_when_acyclic(ont, report)
    check_metrics(ont, refs, report)
    check_symmetry(ont, report)
    check_parameters_unique(ont, report)
    check_bindings(ont, refs, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--quiet", action="store_true", help="print errors and the summary only")
    args = parser.parse_args(argv)

    ont = load()
    report = check(ont)
    for where, msg in sorted(set(report.errors)):
        print(f"ERROR  {where}: {msg}")
    if not args.quiet:
        for where, msg in sorted(set(report.warnings)):
            print(f"warn   {where}: {msg}")
    nodes = sum(len(getattr(ont, f)) for f in KINDS.values())
    errors, warnings = len(set(report.errors)), len(set(report.warnings))
    print(f"\n{nodes} nodes, {len(ont.bindings)} bindings: {errors} errors, {warnings} warnings")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
