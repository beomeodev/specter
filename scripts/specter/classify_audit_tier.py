#!/usr/bin/env python3
"""Deterministic SPECTER Feature Audit Tier classifier.

The machine-readable policy owns classification conditions and tier settings.
This runtime parses evidence-bound Feature Map signals, scans later artifacts
using policy-defined rules, writes a monotonic SHA-bound receipt, and manages
receipt-bound T3 WARN acknowledgments. It never calls an LLM.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CONTRACT = "audit-tier-v1"
CLASSIFIER_VERSION = "1.0.0"
TIERS = ("T1", "T2", "T3")
TIER_RANK = {tier: index for index, tier in enumerate(TIERS, start=1)}
PHASES = ("feature-map", "spec", "plan", "pre-implement", "diff")
PLACEHOLDER_RE = re.compile(r"\b(?:TBD|TODO|UNKNOWN)\b|\{\{", re.IGNORECASE)
FEATURE_HEADING_RE = re.compile(r"^## Feature 0*(\d+):", re.MULTILINE)


class AuditTierError(RuntimeError):
    """A deterministic policy, input, or receipt failure."""


@dataclass(frozen=True)
class Policy:
    path: Path
    raw: bytes
    data: dict[str, Any]

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.raw).hexdigest()

    @property
    def version(self) -> str:
        return str(self.data["version"])


@dataclass
class SignalParse:
    values: dict[str, str | int]
    evidence: dict[str, str]
    legacy: bool
    errors: list[str]


def utc_timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def json_dump(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)


def emit(data: dict[str, Any]) -> None:
    print(json_dump(data))


def load_policy(path: Path) -> Policy:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise AuditTierError(f"policy unavailable: {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AuditTierError(f"policy parse failure: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise AuditTierError("policy root must be a JSON object")
    if data.get("contract") != CONTRACT:
        raise AuditTierError(
            f"policy contract mismatch: expected {CONTRACT}, got {data.get('contract')!r}"
        )
    required = {
        "version",
        "default_tier",
        "tiers",
        "signal_schema",
        "t3_hard_risk_signals",
        "t2_floor_signals",
        "t1_eligibility",
        "artifact_scan_rules",
        "warn_promotions",
    }
    missing = sorted(required - data.keys())
    if missing:
        raise AuditTierError(f"policy missing required keys: {', '.join(missing)}")
    if data["default_tier"] != "T2":
        raise AuditTierError("policy default_tier must be T2")
    if set(data["tiers"]) != set(TIERS):
        raise AuditTierError("policy tiers must be exactly T1, T2, and T3")
    for tier in TIERS:
        settings = data["tiers"][tier]
        if not isinstance(settings, dict):
            raise AuditTierError(f"{tier} settings must be an object")
        if settings.get("independent_reviewers") != 2:
            raise AuditTierError(f"{tier} must retain two independent reviewers")
        for invariant in (
            "layer1_required",
            "layer3_required",
            "executable_gates_required",
            "done_criteria_execution_required",
        ):
            if settings.get(invariant) is not True:
                raise AuditTierError(f"{tier} cannot disable {invariant}")
        if not isinstance(settings.get("targeted_checks"), list):
            raise AuditTierError(f"{tier} targeted_checks must be a list")
        rounds = settings.get("max_automatic_rounds")
        if not isinstance(rounds, int) or isinstance(rounds, bool) or rounds < 1:
            raise AuditTierError(
                f"{tier} max_automatic_rounds must be a positive integer"
            )
    schema = data["signal_schema"]
    if not isinstance(schema, dict):
        raise AuditTierError("signal_schema must be an object")
    boolean_signals = schema.get("boolean_signals")
    numeric_signals = schema.get("numeric_signals")
    if not isinstance(boolean_signals, list) or not all(
        isinstance(item, str) for item in boolean_signals
    ):
        raise AuditTierError("signal_schema.boolean_signals must be a string list")
    if not isinstance(numeric_signals, list) or not all(
        isinstance(item, str) for item in numeric_signals
    ):
        raise AuditTierError("signal_schema.numeric_signals must be a string list")
    known_boolean = set(boolean_signals)
    for key in ("t3_hard_risk_signals", "t2_floor_signals"):
        values = data[key]
        if not isinstance(values, list) or not set(values) <= known_boolean:
            raise AuditTierError(f"{key} must contain known boolean signal keys")
    eligibility = data["t1_eligibility"]
    if not isinstance(eligibility, dict):
        raise AuditTierError("t1_eligibility must be an object")
    for key in (
        "estimated_domains_exact",
        "behavioral_fr_count_max",
        "estimated_touched_files_max",
    ):
        value = eligibility.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise AuditTierError(f"t1_eligibility.{key} must be a non-negative integer")
    if set(eligibility.get("required_boolean_values", {})) != known_boolean:
        raise AuditTierError(
            "t1_eligibility.required_boolean_values must cover every boolean signal"
        )
    if not isinstance(data["artifact_scan_rules"], list):
        raise AuditTierError("artifact_scan_rules must be a list")
    for rule in data["artifact_scan_rules"]:
        if not isinstance(rule, dict) or rule.get("tier") not in TIER_RANK:
            raise AuditTierError("every artifact scan rule must have a valid tier")
        if rule.get("signal") not in known_boolean:
            raise AuditTierError("artifact scan rule references an unknown signal")
        if not isinstance(rule.get("phases"), list) or not set(rule["phases"]) <= set(
            PHASES
        ):
            raise AuditTierError("artifact scan rule has invalid phases")
    promotions = data["warn_promotions"]
    if not isinstance(promotions, dict) or set(promotions) != set(TIERS):
        raise AuditTierError("warn_promotions must define exactly T1, T2, and T3")
    if any(not isinstance(promotions[tier], list) for tier in TIERS):
        raise AuditTierError("warn promotion values must be lists")
    return Policy(path=path, raw=raw, data=data)


def normalize_feature(raw: str) -> str:
    if not re.fullmatch(r"\d+", raw):
        raise AuditTierError(f"Feature must be numeric, got {raw!r}")
    return f"{int(raw):03d}"


def extract_feature_section(feature_map: Path, feature: str) -> str:
    try:
        text = feature_map.read_text(encoding="utf-8")
    except OSError as exc:
        raise AuditTierError(f"Feature Map unavailable: {feature_map}: {exc}") from exc
    matches = list(FEATURE_HEADING_RE.finditer(text))
    target = int(feature)
    for index, match in enumerate(matches):
        if int(match.group(1)) != target:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[match.start() : end]
    raise AuditTierError(f"Feature {feature} section not found in {feature_map}")


def parse_audit_signals(section: str, policy: Policy) -> SignalParse:
    schema = policy.data["signal_schema"]
    boolean_signals = list(schema["boolean_signals"])
    numeric_signals = list(schema["numeric_signals"])
    required = set(boolean_signals + numeric_signals)
    allowed_boolean = set(schema["boolean_values"])
    numeric_unknown = str(schema["numeric_unknown_value"])
    errors: list[str] = []
    values: dict[str, str | int] = {}
    evidence: dict[str, str] = {}

    if re.search(r"(?im)^\s*audit_tier\s*:", section):
        errors.append("direct audit_tier assignment is forbidden")

    heading = re.search(r"(?m)^### Audit signals\s*$", section)
    if heading is None:
        return SignalParse(values={}, evidence={}, legacy=True, errors=errors)
    tail = section[heading.end() :]
    next_heading = re.search(r"(?m)^###? ", tail)
    body = tail[: next_heading.start()] if next_heading else tail
    rows: list[tuple[str, str, str]] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 3:
            errors.append(f"Audit signals row must have exactly 3 columns: {line}")
            continue
        if cells[0].lower() == "signal" or set(cells[0]) <= {"-", ":"}:
            continue
        rows.append((cells[0], cells[1].lower(), cells[2]))

    for key, raw_value, row_evidence in rows:
        if key in values:
            errors.append(f"duplicate Audit signal: {key}")
            continue
        if key not in required:
            errors.append(f"unknown Audit signal key: {key}")
            continue
        if key in boolean_signals:
            if raw_value not in allowed_boolean:
                errors.append(
                    f"invalid value for {key}: {raw_value!r}; "
                    f"allowed={sorted(allowed_boolean)}"
                )
                continue
            values[key] = raw_value
        else:
            if raw_value == numeric_unknown:
                values[key] = raw_value
            elif re.fullmatch(r"\d+", raw_value):
                values[key] = int(raw_value)
            else:
                errors.append(
                    f"invalid numeric value for {key}: {raw_value!r}; "
                    f"expected non-negative integer or {numeric_unknown!r}"
                )
                continue
        if schema.get("evidence_required_for_all_values") is True and (
            not row_evidence
            or row_evidence in {"-", "—", "n/a", "N/A"}
            or PLACEHOLDER_RE.search(row_evidence)
        ):
            errors.append(f"missing or placeholder evidence for {key}")
        evidence[key] = row_evidence

    for key in sorted(required - values.keys()):
        errors.append(f"missing Audit signal: {key}")
    return SignalParse(values=values, evidence=evidence, legacy=False, errors=errors)


def rank_max(*tiers: str | None) -> str:
    present = [tier for tier in tiers if tier is not None]
    if not present or any(tier not in TIER_RANK for tier in present):
        raise AuditTierError(f"invalid tier set: {present}")
    return max(present, key=TIER_RANK.__getitem__)


def classify_signals(
    parsed: SignalParse, policy: Policy
) -> tuple[str, list[str], list[str]]:
    if parsed.errors:
        return (
            "T3",
            ["fail-safe: malformed Audit signals"],
            [f"malformed-audit-signals: {error}" for error in parsed.errors],
        )
    if parsed.legacy:
        return "T2", [], ["legacy-unclassified"]

    values = parsed.values
    triggered: list[str] = []
    reasons: list[str] = []
    for key in policy.data["t3_hard_risk_signals"]:
        if values.get(key) == "yes":
            triggered.append(f"T3:{key}")
            reasons.append(f"T3 hard-risk signal: {key}=yes")
    if triggered:
        return "T3", triggered, reasons

    tier = "T1"
    for key in policy.data["t2_floor_signals"]:
        if values.get(key) == "yes":
            tier = "T2"
            triggered.append(f"T2:{key}")
            reasons.append(f"T2 floor signal: {key}=yes")

    eligibility = policy.data["t1_eligibility"]
    for key, expected in eligibility["required_boolean_values"].items():
        actual = values.get(key)
        if actual != expected:
            tier = rank_max(tier, "T2")
            reasons.append(
                f"T1 predicate failed: {key}={actual!r}, expected {expected!r}"
            )
    numeric_checks = (
        ("estimated_domains", "estimated_domains_exact", lambda a, b: a == b),
        ("behavioral_fr_count", "behavioral_fr_count_max", lambda a, b: a <= b),
        ("estimated_touched_files", "estimated_touched_files_max", lambda a, b: a <= b),
    )
    for signal, policy_key, predicate in numeric_checks:
        actual = values.get(signal)
        threshold = int(eligibility[policy_key])
        if not isinstance(actual, int) or not predicate(actual, threshold):
            tier = rank_max(tier, "T2")
            reasons.append(
                f"T1 predicate failed: {signal}={actual!r}, {policy_key}={threshold}"
            )
    if tier == "T1":
        reasons.append("all T1 eligibility predicates affirmatively satisfied")
    elif not triggered:
        reasons.append("T2 default: no T3 floor and not every T1 predicate passed")
    return tier, triggered, reasons


def artifact_record(path: Path, *, root: Path) -> dict[str, str]:
    if not path.is_file():
        raise AuditTierError(f"required classification input missing: {path}")
    try:
        relative = path.resolve().relative_to(root.resolve())
        label = relative.as_posix()
    except ValueError:
        label = str(path.resolve())
    return {"path": label, "sha256": sha256_file(path)}


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        raise AuditTierError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def diff_evidence(root: Path, base: str) -> tuple[str, str, list[str]]:
    git_output(root, "rev-parse", "--verify", base)
    diff = git_output(root, "diff", "--no-ext-diff", "--binary", base, "--")
    names = {
        line.strip()
        for line in git_output(root, "diff", "--name-only", base, "--").splitlines()
        if line.strip()
    }
    status = git_output(root, "status", "--porcelain", "--untracked-files=all")
    untracked: list[str] = []
    for line in status.splitlines():
        if line.startswith("?? "):
            relpath = line[3:]
            untracked.append(relpath)
            names.add(relpath)
    additions: list[str] = []
    for relpath in sorted(untracked):
        path = root / relpath
        if path.is_file():
            additions.append(
                f"\nUNTRACKED {relpath} sha256={sha256_file(path)}\n"
                + path.read_text(encoding="utf-8", errors="replace")
            )
    bundle = diff + "".join(additions)
    return bundle, sha256_bytes(bundle.encode("utf-8")), sorted(names)


def scan_artifacts(
    policy: Policy,
    phase: str,
    text_by_path: dict[str, str],
) -> tuple[str, list[str], list[str], dict[str, str]]:
    tier = "T1"
    triggered: list[str] = []
    reasons: list[str] = []
    observed: dict[str, str] = {}
    for rule in policy.data["artifact_scan_rules"]:
        if phase not in rule["phases"]:
            continue
        path_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in rule["path_patterns"]
        ]
        content_patterns = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for pattern in rule["content_patterns"]
        ]
        matches: list[str] = []
        for path, content in text_by_path.items():
            if any(pattern.search(path) for pattern in path_patterns):
                matches.append(f"path:{path}")
            if any(pattern.search(content) for pattern in content_patterns):
                matches.append(f"content:{path}")
        if not matches:
            continue
        rule_tier = str(rule["tier"])
        tier = rank_max(tier, rule_tier)
        rule_id = str(rule["id"])
        triggered.append(f"{rule_tier}:{rule_id}")
        reasons.append(
            f"{rule_tier} artifact rule {rule_id}: {', '.join(sorted(set(matches)))}"
        )
        observed[str(rule["signal"])] = "yes"
    return tier, triggered, reasons, observed


def receipt_path(root: Path, feature: str) -> Path:
    return root / ".specify" / "audit-tiers" / f"feature-{feature}.json"


def load_prior_state(path: Path) -> tuple[str | None, str | None]:
    if not path.is_file():
        return None, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        return "T3", "T3"
    except json.JSONDecodeError:
        return "T3", "T3"
    tier = data.get("effective_tier")
    override = data.get("manual_upward_override")
    return (
        tier if tier in TIER_RANK else "T3",
        override if override in TIER_RANK else None,
    )


def resolve_input(root: Path, value: str | None, label: str) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    path = path if path.is_absolute() else root / path
    if not path.is_file():
        raise AuditTierError(f"{label} input missing: {path}")
    return path


def validate_phase_artifact_roles(
    feature: str, phase: str, input_artifacts: list[dict[str, Any]]
) -> None:
    if phase in {"feature-map", "diff"}:
        return
    expected_names = {
        "spec": ("spec.md",),
        "plan": ("spec.md", "plan.md"),
        "pre-implement": ("spec.md", "plan.md", "tasks.md"),
    }[phase]
    role_paths = [Path(str(item.get("path", ""))) for item in input_artifacts[1:]]
    if len(role_paths) != len(expected_names):
        raise AuditTierError(f"{phase} classification has an invalid fixed input set")
    expected_prefix = f"{feature}-"
    parent: Path | None = None
    for path, expected_name in zip(role_paths, expected_names, strict=True):
        if path.name != expected_name:
            raise AuditTierError(
                f"{phase} classification expected {expected_name}, got {path}"
            )
        spec_dir = path.parent
        if spec_dir.parent.name != "specs" or not spec_dir.name.startswith(
            expected_prefix
        ):
            raise AuditTierError(
                f"{phase} classification input is outside specs/{feature}-*: {path}"
            )
        if parent is not None and spec_dir != parent:
            raise AuditTierError(f"{phase} classification inputs span spec directories")
        parent = spec_dir


def classify(args: argparse.Namespace, policy: Policy, root: Path) -> dict[str, Any]:
    feature = normalize_feature(args.feature)
    phase = args.phase
    feature_map = resolve_input(root, args.feature_map, "Feature Map")
    assert feature_map is not None
    section = extract_feature_section(feature_map, feature)
    parsed = parse_audit_signals(section, policy)
    signal_tier, signal_floors, reasons = classify_signals(parsed, policy)
    observed_signals = dict(parsed.values)
    triggered_floors = list(signal_floors)
    input_artifacts = [artifact_record(feature_map, root=root)]
    text_by_path: dict[str, str] = {}

    phase_paths = {
        "spec": (("spec", args.spec),),
        "plan": (("spec", args.spec), ("plan", args.plan)),
        "pre-implement": (
            ("spec", args.spec),
            ("plan", args.plan),
            ("tasks", args.tasks),
        ),
    }
    if phase in phase_paths:
        missing_phase_inputs = [
            label for label, value in phase_paths[phase] if value is None
        ]
        if missing_phase_inputs:
            raise AuditTierError(
                f"{phase} classification requires: {', '.join(missing_phase_inputs)}"
            )
        for label, value in phase_paths[phase]:
            path = resolve_input(root, value, label)
            if path is None:
                continue
            record = artifact_record(path, root=root)
            input_artifacts.append(record)
            text_by_path[record["path"]] = path.read_text(
                encoding="utf-8", errors="replace"
            )
    elif phase == "diff":
        bundle, diff_sha, names = diff_evidence(root, args.diff_base)
        input_artifacts.append(
            {
                "path": f"git-diff:{args.diff_base}",
                "sha256": diff_sha,
                "base": args.diff_base,
            }
        )
        for name in names:
            text_by_path[name] = bundle

    validate_phase_artifact_roles(feature, phase, input_artifacts)
    scan_tier, scan_floors, scan_reasons, scanned_signals = scan_artifacts(
        policy, phase, text_by_path
    )
    observed_signals.update(scanned_signals)
    triggered_floors.extend(scan_floors)
    reasons.extend(scan_reasons)
    newly_computed = rank_max(signal_tier, scan_tier)

    path = receipt_path(root, feature)
    prior, prior_manual_override = load_prior_state(path)
    historical_floor = historical_tier_floor(root, feature, policy)
    if historical_floor is not None:
        prior = rank_max(prior, historical_floor) if prior else historical_floor
    requested_manual_override = args.raise_tier
    if requested_manual_override is not None:
        if requested_manual_override not in TIER_RANK:
            raise AuditTierError(
                f"invalid manual upward override: {requested_manual_override}"
            )
        floor = rank_max(newly_computed, prior) if prior else newly_computed
        if TIER_RANK[requested_manual_override] < TIER_RANK[floor]:
            raise AuditTierError(
                "manual override cannot lower audit_tier "
                f"from {floor} to {requested_manual_override}"
            )
        reasons.append(f"manual upward override: {requested_manual_override}")
    manual_override = (
        rank_max(prior_manual_override, requested_manual_override)
        if prior_manual_override and requested_manual_override
        else prior_manual_override or requested_manual_override
    )
    effective = rank_max(newly_computed, prior, manual_override)
    if prior and TIER_RANK[prior] > TIER_RANK[newly_computed]:
        reasons.append(
            f"monotonic floor retained: prior effective tier {prior} > newly computed {newly_computed}"
        )
    status = "fail-safe" if parsed.errors else "classified"
    receipt: dict[str, Any] = {
        "contract": CONTRACT,
        "classifier_version": CLASSIFIER_VERSION,
        "feature": feature,
        "policy_version": policy.version,
        "policy_path": str(policy.path),
        "policy_hash": policy.sha256,
        "classification_phase": phase,
        "classification_status": status,
        "input_artifacts": input_artifacts,
        "observed_signals": observed_signals,
        "signal_evidence": parsed.evidence,
        "triggered_floors": triggered_floors,
        "prior_effective_tier": prior,
        "newly_computed_tier": newly_computed,
        "effective_tier": effective,
        "manual_upward_override": manual_override,
        "manual_override_requested_this_phase": requested_manual_override,
        "tier_settings": policy.data["tiers"][effective],
        "reasons": reasons,
        "timestamp": utc_timestamp(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json_dump(receipt) + "\n", encoding="utf-8")
    receipt["receipt_path"] = str(path)
    if args.ledger:
        ledger_path = root / ".specify" / "specter-run.jsonl"
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        persisted_sha = sha256_file(path)
        entry = {
            "ts": receipt["timestamp"],
            "cycle": "feature",
            "feature": feature,
            "step": "audit-tier",
            "verdict": "PASS" if status == "classified" else "FAIL",
            "classification_phase": phase,
            "audit_tier": effective,
            "tier_receipt": str(path.relative_to(root)),
            "tier_receipt_sha256": persisted_sha,
            "policy_hash": policy.sha256,
            "reasons": reasons,
        }
        with ledger_path.open("a", encoding="utf-8") as ledger:
            ledger.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")
    return receipt


def load_receipt(root: Path, feature: str) -> tuple[Path, dict[str, Any]]:
    path = receipt_path(root, feature)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise AuditTierError(f"tier receipt missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AuditTierError(f"tier receipt malformed: {path}: {exc}") from exc
    return path, data


def historical_tier_floor(root: Path, feature: str, policy: Policy) -> str | None:
    ledger_path = root / ".specify" / "specter-run.jsonl"
    if not ledger_path.is_file():
        return None
    tiers: list[str] = []
    for raw_line in ledger_path.read_text(
        encoding="utf-8", errors="replace"
    ).splitlines():
        try:
            entry = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        tier = entry.get("audit_tier")
        if (
            entry.get("cycle") == "feature"
            and entry.get("feature") == feature
            and entry.get("step") == "audit-tier"
            and entry.get("policy_hash") == policy.sha256
            and tier in TIER_RANK
        ):
            tiers.append(tier)
    return max(tiers, key=TIER_RANK.__getitem__) if tiers else None


def replay_receipt_classification(
    root: Path, feature: str, receipt: dict[str, Any], policy: Policy
) -> dict[str, Any]:
    phase = receipt.get("classification_phase")
    if phase not in PHASES:
        raise AuditTierError(f"tier receipt classification phase invalid: {phase!r}")
    artifacts = receipt.get("input_artifacts")
    expected_counts = {
        "feature-map": 1,
        "spec": 2,
        "plan": 3,
        "pre-implement": 4,
        "diff": 2,
    }
    if not isinstance(artifacts, list) or len(artifacts) != expected_counts[phase]:
        raise AuditTierError(
            f"tier receipt input set invalid for {phase}: "
            f"expected {expected_counts[phase]} fixed inputs"
        )
    first_path = artifacts[0].get("path") if isinstance(artifacts[0], dict) else None
    if not isinstance(first_path, str) or first_path.startswith("git-diff:"):
        raise AuditTierError("tier receipt first input must be the Feature Map")
    validate_phase_artifact_roles(feature, phase, artifacts)
    feature_map = Path(first_path)
    feature_map = feature_map if feature_map.is_absolute() else root / feature_map
    parsed = parse_audit_signals(extract_feature_section(feature_map, feature), policy)
    signal_tier, signal_floors, signal_reasons = classify_signals(parsed, policy)
    observed_signals = dict(parsed.values)
    text_by_path: dict[str, str] = {}

    if phase == "diff":
        diff_item = artifacts[1]
        if not isinstance(diff_item, dict):
            raise AuditTierError("tier receipt diff input is malformed")
        label = diff_item.get("path", "")
        if not isinstance(label, str) or not label.startswith("git-diff:"):
            raise AuditTierError("tier receipt diff input is not git-diff bound")
        base = diff_item.get("base") or label.split(":", 1)[1]
        bundle, _, names = diff_evidence(root, str(base))
        text_by_path = {name: bundle for name in names}
    else:
        for item in artifacts[1:]:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                raise AuditTierError("tier receipt artifact input is malformed")
            artifact_path = Path(item["path"])
            artifact_path = (
                artifact_path if artifact_path.is_absolute() else root / artifact_path
            )
            if not artifact_path.is_file():
                raise AuditTierError(f"tier receipt input missing: {item['path']}")
            text_by_path[item["path"]] = artifact_path.read_text(
                encoding="utf-8", errors="replace"
            )

    scan_tier, scan_floors, scan_reasons, scanned_signals = scan_artifacts(
        policy, phase, text_by_path
    )
    observed_signals.update(scanned_signals)
    return {
        "classification_status": "fail-safe" if parsed.errors else "classified",
        "newly_computed_tier": rank_max(signal_tier, scan_tier),
        "observed_signals": observed_signals,
        "signal_evidence": parsed.evidence,
        "triggered_floors": signal_floors + scan_floors,
        "reasons": signal_reasons + scan_reasons,
    }


def validate_receipt(root: Path, feature: str, policy: Policy) -> dict[str, Any]:
    path, receipt = load_receipt(root, feature)
    reasons: list[str] = []
    if receipt.get("contract") != CONTRACT:
        reasons.append("tier receipt contract mismatch")
    if receipt.get("classifier_version") != CLASSIFIER_VERSION:
        reasons.append("tier receipt classifier version mismatch")
    if receipt.get("feature") != feature:
        reasons.append("tier receipt Feature mismatch")
    if receipt.get("policy_hash") != policy.sha256:
        reasons.append("tier receipt policy hash is stale")
    if receipt.get("policy_version") != policy.version:
        reasons.append("tier receipt policy version mismatch")
    effective_tier = receipt.get("effective_tier")
    if effective_tier not in TIER_RANK:
        reasons.append("tier receipt effective_tier invalid")
    if receipt.get("classification_status") == "fail-safe":
        reasons.append("tier receipt records malformed Audit signals")
    artifacts = receipt.get("input_artifacts")
    if not isinstance(artifacts, list):
        artifacts = []
        reasons.append("tier receipt input_artifacts malformed")
    for item in artifacts:
        if not isinstance(item, dict):
            reasons.append("tier receipt artifact record malformed")
            continue
        label = item.get("path", "")
        expected = item.get("sha256", "")
        if not isinstance(label, str) or not isinstance(expected, str):
            reasons.append("tier receipt artifact path/hash malformed")
            continue
        if label.startswith("git-diff:"):
            base = item.get("base") or label.split(":", 1)[1]
            try:
                _, actual, _ = diff_evidence(root, base)
            except AuditTierError as exc:
                reasons.append(str(exc))
                continue
        else:
            path_item = Path(label)
            path_item = path_item if path_item.is_absolute() else root / path_item
            if not path_item.is_file():
                reasons.append(f"tier receipt input missing: {label}")
                continue
            actual = sha256_file(path_item)
        if actual != expected:
            reasons.append(
                f"tier receipt input stale: {label} "
                f"(recorded={expected or 'none'}, current={actual})"
            )
    try:
        replay = replay_receipt_classification(root, feature, receipt, policy)
    except AuditTierError as exc:
        reasons.append(str(exc))
    else:
        for key in (
            "classification_status",
            "newly_computed_tier",
            "observed_signals",
            "signal_evidence",
            "triggered_floors",
        ):
            if receipt.get(key) != replay[key]:
                reasons.append(
                    f"tier receipt {key} does not match deterministic replay"
                )

        prior = receipt.get("prior_effective_tier")
        manual_override = receipt.get("manual_upward_override")
        if prior is not None and prior not in TIER_RANK:
            reasons.append("tier receipt prior_effective_tier invalid")
        if manual_override is not None and manual_override not in TIER_RANK:
            reasons.append("tier receipt manual_upward_override invalid")
        if effective_tier in TIER_RANK:
            expected_effective = rank_max(
                replay["newly_computed_tier"], prior, manual_override
            )
            if effective_tier != expected_effective:
                reasons.append(
                    "tier receipt effective_tier does not match deterministic monotonic maximum"
                )
            if receipt.get("tier_settings") != policy.data["tiers"][effective_tier]:
                reasons.append("tier receipt settings do not match canonical policy")
            historical_floor = historical_tier_floor(root, feature, policy)
            if (
                historical_floor
                and TIER_RANK[effective_tier] < TIER_RANK[historical_floor]
            ):
                reasons.append(
                    "tier receipt effective_tier is below append-only historical floor "
                    f"{historical_floor}"
                )
    valid = not reasons
    return {
        "valid": valid,
        "feature": feature,
        "receipt_path": str(path),
        "receipt_sha256": sha256_file(path),
        "effective_tier": receipt.get("effective_tier"),
        "classification_phase": receipt.get("classification_phase"),
        "policy_hash": receipt.get("policy_hash"),
        "tier_settings": receipt.get("tier_settings"),
        "reasons": reasons,
    }


def ack_path(root: Path, feature: str, station: str) -> Path:
    safe_station = re.fullmatch(r"[a-z][a-z0-9-]*", station)
    if safe_station is None:
        raise AuditTierError(f"invalid station for WARN acknowledgment: {station!r}")
    return (
        root / ".specify" / "audit-tiers" / f"feature-{feature}.{station}.warn-ack.json"
    )


def station_warn_evidence(
    root: Path, feature: str, station: str, tier_receipt_sha: str
) -> dict[str, Any] | None:
    ledger_path = root / ".specify" / "specter-run.jsonl"
    if not ledger_path.is_file():
        return None
    matches: list[dict[str, Any]] = []
    for raw_line in ledger_path.read_text(
        encoding="utf-8", errors="replace"
    ).splitlines():
        try:
            entry = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        if (
            entry.get("cycle") != "feature"
            or entry.get("feature") != feature
            or entry.get("step") != station
            or entry.get("verdict") != "WARN"
            or entry.get("tier_receipt_sha256") != tier_receipt_sha
            or not isinstance(entry.get("artifacts"), list)
            or not isinstance(entry.get("report_shas"), list)
            or len(entry["artifacts"]) != len(entry["report_shas"])
        ):
            continue
        fresh = True
        for artifact, expected_sha in zip(
            entry["artifacts"], entry["report_shas"], strict=True
        ):
            path = root / str(artifact)
            actual_sha = sha256_file(path) if path.is_file() else ""
            if actual_sha != expected_sha:
                fresh = False
                break
        if fresh:
            matches.append(
                {
                    "sha256": sha256_bytes(raw_line.encode("utf-8")),
                    "report_shas": entry["report_shas"],
                    "cap": entry.get("cap"),
                    "caught": entry.get("caught", []),
                }
            )
    return matches[-1] if matches else None


def ack_status(
    root: Path, feature: str, station: str, policy: Policy
) -> dict[str, Any]:
    receipt_path_value, receipt = load_receipt(root, feature)
    validation = validate_receipt(root, feature, policy)
    required = (
        receipt.get("effective_tier") == "T3"
        and receipt.get("tier_settings", {}).get("warn_handling") == "human-ack"
    )
    receipt_sha = sha256_file(receipt_path_value)
    station_evidence = station_warn_evidence(root, feature, station, receipt_sha)
    path = ack_path(root, feature, station)
    satisfied = False
    if required and validation["valid"] and path.is_file():
        try:
            ack = json.loads(path.read_text(encoding="utf-8"))
        except OSError:
            ack = {}
        except json.JSONDecodeError:
            ack = {}
        satisfied = (
            ack.get("contract") == CONTRACT
            and ack.get("feature") == feature
            and ack.get("station") == station
            and ack.get("actor") == "human"
            and ack.get("tier_receipt_sha256") == receipt_sha
            and station_evidence is not None
            and ack.get("station_evidence_sha256") == station_evidence["sha256"]
            and ack.get("station_report_shas") == station_evidence["report_shas"]
        )
    return {
        "required": required,
        "satisfied": satisfied,
        "feature": feature,
        "station": station,
        "effective_tier": receipt.get("effective_tier"),
        "tier_receipt_sha256": receipt_sha,
        "station_warn_evidence": station_evidence,
        "ack_path": str(path),
        "receipt_valid": validation["valid"],
    }


def acknowledge_warn(
    root: Path, feature: str, station: str, actor: str, policy: Policy
) -> dict[str, Any]:
    if actor != "human":
        raise AuditTierError("T3 WARN acknowledgment actor must be exactly 'human'")
    status = ack_status(root, feature, station, policy)
    if not status["required"]:
        raise AuditTierError("WARN acknowledgment is not required for the current tier")
    if not status["receipt_valid"]:
        raise AuditTierError(
            "cannot acknowledge WARN against a stale or invalid tier receipt"
        )
    station_evidence = status["station_warn_evidence"]
    if station_evidence is None:
        raise AuditTierError(
            "cannot acknowledge WARN before a fresh mechanical station WARN receipt exists"
        )
    path = Path(status["ack_path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "contract": CONTRACT,
        "feature": feature,
        "station": station,
        "actor": actor,
        "effective_tier": status["effective_tier"],
        "tier_receipt_sha256": status["tier_receipt_sha256"],
        "station_evidence_sha256": station_evidence["sha256"],
        "station_report_shas": station_evidence["report_shas"],
        "acknowledged_cap": station_evidence["cap"],
        "acknowledged_caught": station_evidence["caught"],
        "timestamp": utc_timestamp(),
    }
    path.write_text(json_dump(data) + "\n", encoding="utf-8")
    data["ack_path"] = str(path)
    return data


def gate_status(
    root: Path, feature: str, station: str, policy: Policy
) -> dict[str, Any]:
    expected_phases = {
        "verify": "feature-map",
        "analyze": "pre-implement",
        "review": "diff",
    }
    if station not in expected_phases:
        raise AuditTierError(f"audit tier does not apply to station {station!r}")
    _, receipt = load_receipt(root, feature)
    validation = validate_receipt(root, feature, policy)
    reasons = list(validation["reasons"])
    expected_phase = expected_phases[station]
    if receipt.get("classification_phase") != expected_phase:
        reasons.append(
            "tier receipt phase mismatch: "
            f"station {station} requires {expected_phase}, "
            f"got {receipt.get('classification_phase')!r}"
        )
    valid = not reasons
    ack = ack_status(root, feature, station, policy)
    return {
        "valid": valid,
        "feature": feature,
        "station": station,
        "expected_phase": expected_phase,
        "classification_phase": receipt.get("classification_phase"),
        "effective_tier": receipt.get("effective_tier"),
        "tier_settings": receipt.get("tier_settings"),
        "policy_version": receipt.get("policy_version"),
        "policy_hash": receipt.get("policy_hash"),
        "tier_receipt_path": validation["receipt_path"],
        "tier_receipt_sha256": validation["receipt_sha256"],
        "warn_ack_required": ack["required"],
        "warn_ack_satisfied": ack["satisfied"],
        "reasons": reasons,
    }


def validate_map(
    args: argparse.Namespace, policy: Policy, root: Path
) -> dict[str, Any]:
    feature_map = resolve_input(root, args.feature_map, "Feature Map")
    assert feature_map is not None
    text = feature_map.read_text(encoding="utf-8")
    features = [
        normalize_feature(match.group(1)) for match in FEATURE_HEADING_RE.finditer(text)
    ]
    if args.feature:
        features = [normalize_feature(args.feature)]
    if not features:
        raise AuditTierError(f"no Feature sections found in {feature_map}")
    errors: list[str] = []
    legacy: list[str] = []
    for feature in features:
        parsed = parse_audit_signals(
            extract_feature_section(feature_map, feature), policy
        )
        errors.extend(f"Feature {feature}: {error}" for error in parsed.errors)
        if parsed.legacy:
            legacy.append(feature)
    return {
        "valid": not errors,
        "feature_map": str(feature_map),
        "features_checked": features,
        "legacy_unclassified": legacy,
        "errors": errors,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument(
        "--policy",
        default="docs/templates/audit-tier-policy.json",
        help="canonical audit-tier policy JSON",
    )
    result.add_argument("--root", default=".", help="repository root")
    sub = result.add_subparsers(dest="command", required=True)
    sub.add_parser("version")

    validate_map_parser = sub.add_parser("validate-map")
    validate_map_parser.add_argument("--feature")
    validate_map_parser.add_argument("--feature-map", default="docs/prd/feature-map.md")

    classify_parser = sub.add_parser("classify")
    classify_parser.add_argument("--feature", required=True)
    classify_parser.add_argument("--phase", choices=PHASES, required=True)
    classify_parser.add_argument("--feature-map", default="docs/prd/feature-map.md")
    classify_parser.add_argument("--spec")
    classify_parser.add_argument("--plan")
    classify_parser.add_argument("--tasks")
    classify_parser.add_argument("--diff-base", default="HEAD")
    classify_parser.add_argument("--raise-tier", choices=TIERS)
    classify_parser.add_argument("--ledger", action="store_true")

    validate_parser = sub.add_parser("validate-receipt")
    validate_parser.add_argument("--feature", required=True)

    ack_parser = sub.add_parser("acknowledge-warn")
    ack_parser.add_argument("--feature", required=True)
    ack_parser.add_argument("--station", required=True)
    ack_parser.add_argument("--actor", required=True)

    status_parser = sub.add_parser("ack-status")
    status_parser.add_argument("--feature", required=True)
    status_parser.add_argument("--station", required=True)

    gate_status_parser = sub.add_parser("gate-status")
    gate_status_parser.add_argument("--feature", required=True)
    gate_status_parser.add_argument(
        "--station", choices=("verify", "analyze", "review"), required=True
    )
    return result


def main() -> int:
    args = parser().parse_args()
    root = Path(args.root).resolve()
    try:
        policy_path = Path(args.policy)
        policy_path = policy_path if policy_path.is_absolute() else root / policy_path
        policy = load_policy(policy_path)
        if args.command == "version":
            emit(
                {
                    "classifier_version": CLASSIFIER_VERSION,
                    "contract": CONTRACT,
                    "policy_version": policy.version,
                    "policy_hash": policy.sha256,
                    "compatible": True,
                }
            )
            return 0
        if args.command == "validate-map":
            data = validate_map(args, policy, root)
            emit(data)
            return 0 if data["valid"] else 1
        if args.command == "classify":
            emit(classify(args, policy, root))
            return 0
        feature = normalize_feature(args.feature)
        if args.command == "validate-receipt":
            data = validate_receipt(root, feature, policy)
            emit(data)
            return 0 if data["valid"] else 1
        if args.command == "ack-status":
            emit(ack_status(root, feature, args.station, policy))
            return 0
        if args.command == "gate-status":
            data = gate_status(root, feature, args.station, policy)
            emit(data)
            return 0 if data["valid"] else 1
        if args.command == "acknowledge-warn":
            emit(acknowledge_warn(root, feature, args.station, args.actor, policy))
            return 0
        raise AuditTierError(f"unknown command: {args.command}")
    except AuditTierError as exc:
        print(str(exc), file=sys.stderr)
        if args.command in {"validate-receipt", "validate-map"}:
            emit({"valid": False, "reasons": [str(exc)]})
        return 2
    except (KeyError, TypeError, ValueError) as exc:
        print(
            f"audit-tier policy or receipt validation failure: {exc}", file=sys.stderr
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
