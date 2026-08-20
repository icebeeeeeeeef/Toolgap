#!/usr/bin/env python3
"""Create the one-way, pre-arm admission manifest for G0-C-ATOMIC-008."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(checkout: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(checkout), *args], text=True
    ).strip()


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    return path.resolve()


def require_executable(path: Path, label: str) -> Path:
    absolute = Path(os.path.abspath(path))
    if not absolute.is_file() or not os.access(absolute, os.X_OK):
        raise ValueError(f"missing executable {label}: {absolute}")
    return absolute


def require_clean(checkout: Path, label: str) -> None:
    dirty = git(checkout, "status", "--porcelain", "--untracked-files=no")
    if dirty:
        raise ValueError(f"{label} has tracked changes:\n{dirty}")


def relative_to(path: Path, root: Path, label: str) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"{label} must live under {root}: {path}") from error


def no_placeholders(value: object) -> bool:
    if isinstance(value, dict):
        return all(no_placeholders(item) for item in value.values())
    if isinstance(value, list):
        return all(no_placeholders(item) for item in value)
    return not (isinstance(value, str) and value.startswith("__"))


def parse_passed_json(path: Path, label: str) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("passed") is not True:
        raise ValueError(f"{label} did not pass: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--stock-checkout", required=True, type=Path)
    parser.add_argument("--treatment-checkout", required=True, type=Path)
    parser.add_argument("--patch", required=True, type=Path)
    parser.add_argument("--stock-wheel", required=True, type=Path)
    parser.add_argument("--treatment-wheel", required=True, type=Path)
    parser.add_argument("--dependency-lock", required=True, type=Path)
    parser.add_argument("--environment-readback", required=True, type=Path)
    parser.add_argument("--runtime-env", required=True, type=Path)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--model-snapshot", required=True, type=Path)
    parser.add_argument("--stock-install-report", required=True, type=Path)
    parser.add_argument("--treatment-install-report", required=True, type=Path)
    parser.add_argument("--stock-provenance", required=True, type=Path)
    parser.add_argument("--treatment-provenance", required=True, type=Path)
    parser.add_argument("--stock-interpreter", required=True, type=Path)
    parser.add_argument("--treatment-interpreter", required=True, type=Path)
    args = parser.parse_args()

    if args.output.exists():
        raise ValueError(f"refusing to replace sealed manifest: {args.output}")
    repo_root = args.repo_root.resolve()
    run_dir = args.output.resolve().parent
    template = require_file(args.template, "template")
    spec = require_file(args.spec, "SPEC")
    patch = require_file(args.patch, "patch")
    request = require_file(args.request, "request")
    stock = args.stock_checkout.resolve()
    treatment = args.treatment_checkout.resolve()
    require_clean(repo_root, "ToolGap repository")
    require_clean(stock, "stock checkout")
    require_clean(treatment, "treatment checkout")

    inputs = {
        "stock_wheel": require_file(args.stock_wheel, "stock wheel"),
        "treatment_wheel": require_file(args.treatment_wheel, "treatment wheel"),
        "dependency_lock": require_file(args.dependency_lock, "dependency lock"),
        "environment_readback": require_file(
            args.environment_readback, "environment readback"
        ),
        "runtime_env": require_file(args.runtime_env, "runtime environment"),
        "model_snapshot": require_file(args.model_snapshot, "model snapshot"),
        "stock_install_report": require_file(
            args.stock_install_report, "stock install report"
        ),
        "treatment_install_report": require_file(
            args.treatment_install_report, "treatment install report"
        ),
        "stock_provenance": require_file(args.stock_provenance, "stock provenance"),
        "treatment_provenance": require_file(
            args.treatment_provenance, "treatment provenance"
        ),
        "stock_interpreter": require_executable(
            args.stock_interpreter, "stock interpreter"
        ),
        "treatment_interpreter": require_executable(
            args.treatment_interpreter, "treatment interpreter"
        ),
    }
    if inputs["stock_interpreter"] == inputs["treatment_interpreter"]:
        raise ValueError("stock and treatment must use distinct interpreters")
    for key in (
        "stock_wheel",
        "treatment_wheel",
        "dependency_lock",
        "environment_readback",
        "runtime_env",
        "model_snapshot",
        "stock_install_report",
        "treatment_install_report",
        "stock_provenance",
        "treatment_provenance",
    ):
        relative_to(inputs[key], run_dir, key)
    parse_passed_json(inputs["stock_provenance"], "stock provenance")
    parse_passed_json(inputs["treatment_provenance"], "treatment provenance")
    json.loads(inputs["stock_install_report"].read_text(encoding="utf-8"))
    json.loads(inputs["treatment_install_report"].read_text(encoding="utf-8"))
    json.loads(inputs["model_snapshot"].read_text(encoding="utf-8"))

    document = json.loads(template.read_text(encoding="utf-8"))
    identity = document["identity"]
    source = document["source"]
    runtime = document["runtime"]
    environment = document["environment"]
    expected_spec = (repo_root / identity["spec_path"]).resolve()
    expected_patch = (repo_root / source["patch_path"]).resolve()
    expected_request = (repo_root / runtime["request_path"]).resolve()
    if spec != expected_spec or patch != expected_patch or request != expected_request:
        raise ValueError("SPEC, patch, or request path differs from the template")
    if git(stock, "rev-parse", "HEAD") != source["base_commit"]:
        raise ValueError("stock checkout does not match the fixed base commit")
    if git(stock, "rev-parse", "HEAD^{tree}") != source["base_tree"]:
        raise ValueError("stock checkout does not match the fixed base tree")
    if git(treatment, "rev-parse", "HEAD^") != source["base_commit"]:
        raise ValueError("treatment parent does not match the fixed base commit")
    if sha256(patch) != source["patch_sha256"]:
        raise ValueError("patch hash differs from the fixed template")

    identity.update(
        {
            "attempt_id": args.attempt_id,
            "spec_sha256": sha256(spec),
            "toolgap_commit": git(repo_root, "rev-parse", "HEAD"),
            "toolgap_repository": str(repo_root),
            "toolgap_tracked_clean": True,
            "toolgap_tree": git(repo_root, "rev-parse", "HEAD^{tree}"),
        }
    )
    source.update(
        {
            "stock_checkout": str(stock),
            "stock_commit": git(stock, "rev-parse", "HEAD"),
            "stock_tree": git(stock, "rev-parse", "HEAD^{tree}"),
            "stock_wheel_path": relative_to(
                inputs["stock_wheel"], run_dir, "stock wheel"
            ),
            "stock_wheel_sha256": sha256(inputs["stock_wheel"]),
            "treatment_checkout": str(treatment),
            "treatment_commit": git(treatment, "rev-parse", "HEAD"),
            "treatment_tree": git(treatment, "rev-parse", "HEAD^{tree}"),
            "treatment_wheel_path": relative_to(
                inputs["treatment_wheel"], run_dir, "treatment wheel"
            ),
            "treatment_wheel_sha256": sha256(inputs["treatment_wheel"]),
        }
    )
    environment.update(
        {
            "observed_readback_path": relative_to(
                inputs["environment_readback"], run_dir, "environment readback"
            ),
            "observed_readback_sha256": sha256(inputs["environment_readback"]),
            "stock_interpreter": str(inputs["stock_interpreter"]),
            "treatment_interpreter": str(inputs["treatment_interpreter"]),
        }
    )
    runtime.update(
        {
            "dependency_lock_path": relative_to(
                inputs["dependency_lock"], run_dir, "dependency lock"
            ),
            "dependency_lock_sha256": sha256(inputs["dependency_lock"]),
            "model_snapshot_path": relative_to(
                inputs["model_snapshot"], run_dir, "model snapshot"
            ),
            "model_snapshot_sha256": sha256(inputs["model_snapshot"]),
            "request_sha256": sha256(request),
            "runtime_env_path": relative_to(
                inputs["runtime_env"], run_dir, "runtime environment"
            ),
            "runtime_env_sha256": sha256(inputs["runtime_env"]),
            "stock_install_report_path": relative_to(
                inputs["stock_install_report"], run_dir, "stock install report"
            ),
            "stock_install_report_sha256": sha256(inputs["stock_install_report"]),
            "stock_provenance_path": relative_to(
                inputs["stock_provenance"], run_dir, "stock provenance"
            ),
            "stock_provenance_sha256": sha256(inputs["stock_provenance"]),
            "treatment_install_report_path": relative_to(
                inputs["treatment_install_report"], run_dir, "treatment install report"
            ),
            "treatment_install_report_sha256": sha256(
                inputs["treatment_install_report"]
            ),
            "treatment_provenance_path": relative_to(
                inputs["treatment_provenance"], run_dir, "treatment provenance"
            ),
            "treatment_provenance_sha256": sha256(inputs["treatment_provenance"]),
        }
    )
    if not no_placeholders(document):
        raise ValueError("admission manifest still has generated placeholders")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(document, indent=2, sort_keys=True) + "\n"
    descriptor = os.open(
        args.output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode=0o444
    )
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(encoded)
    args.output.chmod(0o444)
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
