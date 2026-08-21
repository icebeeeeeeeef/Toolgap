#!/usr/bin/env python3
"""Verify all pre-seal success evidence for one G0-C-ATOMIC-016 attempt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def require_receipt(run_dir: Path, name: str, status: str, manifest_sha: str) -> None:
    receipt = load_json(run_dir / name)
    if receipt.get("status") != status or receipt.get("manifest_sha256") != manifest_sha:
        raise ValueError(f"invalid phase receipt: {name}")


def require_provenance(path: Path, expected_interpreter: str) -> None:
    document = load_json(path)
    if document.get("passed") is not True:
        raise ValueError(f"provenance did not pass: {path}")
    if document.get("interpreter_matches") is not True:
        raise ValueError(f"provenance interpreter mismatch: {path}")
    if Path(os.path.abspath(document["interpreter"])) != Path(
        os.path.abspath(expected_interpreter)
    ):
        raise ValueError(f"provenance used an unexpected interpreter: {path}")
    if document.get("package_under_install_root") is not True:
        raise ValueError(f"package escaped the admitted install root: {path}")
    modules = document.get("modules", {})
    if len(modules) != 4:
        raise ValueError(f"provenance did not cover four modules: {path}")
    for module in modules.values():
        if not (
            module.get("hash_matches_source") is True
            and module.get("installed_under_root") is True
            and module.get("outside_source_checkout") is True
        ):
            raise ValueError(f"module provenance mismatch: {path}")


def install_report_identity(
    path: Path, expected_sglang_sha256: str
) -> list[tuple[str, str, str, str]]:
    document = load_json(path)
    dependencies: list[tuple[str, str, str, str]] = []
    saw_sglang = False
    for item in document.get("install", []):
        metadata = item.get("metadata", {})
        name = str(metadata.get("name", "")).lower().replace("_", "-")
        version = str(metadata.get("version", ""))
        download = item.get("download_info", {})
        url = str(download.get("url", ""))
        archive = download.get("archive_info", {})
        hashes = archive.get("hashes", {})
        archive_sha = str(hashes.get("sha256", ""))
        if not archive_sha and str(archive.get("hash", "")).startswith("sha256="):
            archive_sha = str(archive["hash"]).split("=", 1)[1]
        if name == "sglang":
            if saw_sglang or archive_sha != expected_sglang_sha256:
                raise ValueError(f"installed SGLang wheel mismatch: {path}")
            saw_sglang = True
        else:
            dependencies.append((name, version, url, archive_sha))
    if not saw_sglang:
        raise ValueError(f"install report lacks the retained SGLang wheel: {path}")
    return sorted(dependencies)


def raw_sse_has_required_events(raw: bytes) -> bool:
    saw_payload = False
    saw_done = False
    for line in raw.splitlines():
        if not line.startswith(b"data:"):
            continue
        data = line[5:].strip()
        if data == b"[DONE]":
            saw_done = True
            continue
        try:
            event = json.loads(data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False
        if isinstance(event, dict) and {"text", "meta_info"}.issubset(event):
            saw_payload = True
    return saw_payload and saw_done


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    manifest_path = run_dir / "manifest.json"
    manifest = load_json(manifest_path)
    manifest_sha = sha256(manifest_path)
    environment = manifest["environment"]
    source = manifest["source"]
    runtime = manifest["runtime"]

    for relative in manifest["planned_success_artifacts"]:
        if not (run_dir / relative).is_file():
            raise ValueError(f"missing planned success artifact: {relative}")
    report_identities = {}
    for prefix in ("stock", "treatment"):
        wheel = run_dir / source[f"{prefix}_wheel_path"]
        if sha256(wheel) != source[f"{prefix}_wheel_sha256"]:
            raise ValueError(f"{prefix} wheel hash mismatch")
        report_identities[prefix] = install_report_identity(
            run_dir / runtime[f"{prefix}_install_report_path"],
            source[f"{prefix}_wheel_sha256"],
        )
    if report_identities["stock"] != report_identities["treatment"]:
        raise ValueError("stock and treatment dependency install reports differ")
    load_json(run_dir / runtime["model_snapshot_path"])

    require_receipt(run_dir, "preflight-status.json", "ADMITTED_PRE_ARM", manifest_sha)
    require_receipt(run_dir, "controls-passed.json", "CONTROLS_PASSED", manifest_sha)
    require_receipt(run_dir, "serving-passed.json", "SERVING_PASSED", manifest_sha)
    for prefix in ("stock", "treatment"):
        expected = environment[f"{prefix}_interpreter"]
        require_provenance(run_dir / f"{prefix}-provenance.json", expected)
        require_provenance(run_dir / f"{prefix}-serving-provenance.json", expected)

    stock_oracle = (run_dir / "stock-oracle.txt").read_text(encoding="utf-8")
    treatment_oracle = (run_dir / "treatment-oracle.txt").read_text(
        encoding="utf-8"
    )
    seam = (run_dir / "installed-seam.txt").read_text(encoding="utf-8")
    if "Ran 27 tests" not in stock_oracle or "FAILED (failures=27)" not in stock_oracle:
        raise ValueError("stock RED control terminal mismatch")
    if "Ran 27 tests" not in treatment_oracle or "\nOK\n" not in f"\n{treatment_oracle}\n":
        raise ValueError("treatment GREEN control terminal mismatch")
    if "\nOK\n" not in f"\n{seam}\n":
        raise ValueError("installed seam terminal mismatch")
    if load_json(run_dir / "static-inventory.json").get("passed") is not True:
        raise ValueError("static inventory did not pass")
    if int((run_dir / "request-input-token-count.txt").read_text()) < 32:
        raise ValueError("request does not span at least two pages")
    if sha256(run_dir / "request.json") != runtime["request_sha256"]:
        raise ValueError("executed request differs from the frozen request")

    for arm in ("stock", "treatment"):
        for request_number in (1, 2):
            result = load_json(run_dir / f"{arm}-request-{request_number}.json")
            raw = (run_dir / f"{arm}-request-{request_number}.sse").read_bytes()
            content_type = result.get("content_type")
            if not (
                result.get("passed") is True
                and isinstance(content_type, str)
                and content_type.split(";", 1)[0].strip().lower()
                == "text/event-stream"
                and raw_sse_has_required_events(raw)
            ):
                raise ValueError(f"invalid HTTP/SSE terminal: {arm} request {request_number}")
        cleanup = load_json(run_dir / f"{arm}-cleanup-status.json")
        if not (
            cleanup.get("passed") is True
            and cleanup.get("process_group_survivors") == []
            and cleanup.get("attributable_gpu_pid_survivors") == []
            and cleanup.get("server_wait_status") in {0, 137, 143}
        ):
            raise ValueError(f"cleanup did not quiesce the {arm} arm")
        if (run_dir / f"{arm}-process-group-after.txt").stat().st_size != 0:
            raise ValueError(f"process-group evidence is not empty: {arm}")
        if (run_dir / f"{arm}-gpu-pids-leaked.txt").stat().st_size != 0:
            raise ValueError(f"attributable GPU PID evidence is not empty: {arm}")
        listeners = (run_dir / f"{arm}-listeners-after-term.txt").read_text(
            encoding="utf-8"
        )
        port = 30000 if arm == "stock" else 30001
        if f":{port} " in listeners or f":{port}\n" in listeners:
            raise ValueError(f"listener evidence still contains the {arm} port")
        pid = int((run_dir / f"{arm}-server.pid").read_text())
        if pid_alive(pid):
            raise ValueError(f"server PID still alive: {arm} {pid}")
    print(f"SUCCESS_EVIDENCE_VERIFIED: {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
