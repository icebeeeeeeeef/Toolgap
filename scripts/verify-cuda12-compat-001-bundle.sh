#!/usr/bin/env bash
# Static contract checks for the CUDA12-COMPAT-001 source bundle.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/.." && pwd)"
BASE_COMMIT="a48e8d179767da1ef9e2b036835795f4865d94ae"
BASE_SGLANG_COMMIT="92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2"
PATCH_0001="$ROOT/upstream/sglang/patches/0001-atomic-checked-demote.patch"
PATCH_0002="$ROOT/upstream/sglang/patches/0002-g1-scripted-forced-demote.patch"
PATCH_0003="$ROOT/upstream/sglang/patches/0003-cuda12-compat-packaging.patch"
PIN="$ROOT/upstream/sglang/pin.cuda12-compat-001.toml"
TEMPLATE="$ROOT/experiments/g1/manifest.cuda12-compat-001.template.json"
RUNNER="$ROOT/experiments/g1/commands/20-cuda12-compat-001.sh"
BOOTSTRAP="$ROOT/experiments/g1/commands/00-cuda12-compat-001-bootstrap.sh"
PREREQS="$ROOT/experiments/g1/commands/19-cuda12-compat-001-project-prereqs.sh"
BUNDLE_MANIFEST="$ROOT/experiments/g1/commands/cuda12_compat_001_bundle_manifest.py"
FINALIZE="$ROOT/experiments/g1/commands/cuda12_compat_001_finalize.py"
WHEELHOUSE_BUILDER="$ROOT/experiments/g1/commands/cuda12_compat_001_build_wheelhouse.py"
REPACKAGER="$ROOT/experiments/g1/commands/cuda12_compat_001_repackage_wheel.py"
ANCHOR="$ROOT/scripts/anchor-cuda12-compat-001-oss.sh"
STAGER="$ROOT/scripts/stage-cuda12-compat-001-inputs-oss.sh"

if [[ -n "${PYTHON:-}" ]]; then
  PYTHON="$(command -v "$PYTHON")"
else
  PYTHON=""
  for candidate in python3 /opt/homebrew/bin/python3; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import tomllib' >/dev/null 2>&1; then
      PYTHON="$(command -v "$candidate")"
      break
    fi
  done
  test -n "$PYTHON"
fi
"$PYTHON" -c 'import tomllib'

for path in "$PATCH_0001" "$PATCH_0002" "$PATCH_0003" "$PIN" "$TEMPLATE" "$RUNNER" "$BOOTSTRAP" "$PREREQS" "$BUNDLE_MANIFEST" "$FINALIZE" "$WHEELHOUSE_BUILDER" "$REPACKAGER" "$ANCHOR" "$STAGER"; do
  test -f "$path"
done

# The compatibility probe may add successor artifacts only. Its predecessor
# remains byte-for-byte unchanged from the frozen CUDA 13 revision.
ORIGINAL_G1_PATHS=(
  experiments/g1/SPEC.g1-preflight-001.md
  experiments/g1/manifest.g1-preflight-001.template.json
  experiments/g1/commands/00-g1-preflight-001-bootstrap.sh
  experiments/g1/commands/20-g1-preflight-001.sh
  experiments/g1/commands/g1_preflight_001_bundle_manifest.py
  experiments/g1/commands/g1_preflight_001_finalize.py
  upstream/sglang/pin.g1-preflight-001.toml
  upstream/sglang/patches/0001-atomic-checked-demote.patch
  upstream/sglang/patches/0002-g1-scripted-forced-demote.patch
  scripts/verify-g1-preflight-001-bundle.sh
)
git -C "$ROOT" diff --quiet "$BASE_COMMIT" -- "${ORIGINAL_G1_PATHS[@]}"

bash -n "$BOOTSTRAP"
bash -n "$PREREQS"
bash -n "$RUNNER"
bash -n "$ANCHOR"
bash -n "$STAGER"
"$PYTHON" -m py_compile "$BUNDLE_MANIFEST" "$FINALIZE" "$WHEELHOUSE_BUILDER" "$REPACKAGER"

"$PYTHON" - "$ROOT" "$PIN" "$TEMPLATE" "$PATCH_0001" "$PATCH_0002" "$PATCH_0003" "$RUNNER" "$BOOTSTRAP" "$PREREQS" "$BUNDLE_MANIFEST" "$FINALIZE" "$WHEELHOUSE_BUILDER" "$REPACKAGER" "$ANCHOR" "$STAGER" <<'PY'
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import tarfile
import tempfile
import tomllib

root, pin_path, template_path, patch_one, patch_two, patch_three, runner_path, bootstrap_path, prereqs_path, builder_path, finalizer_path, wheelhouse_builder_path, repackager_path, anchor_path, stager_path = map(pathlib.Path, sys.argv[1:])

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

pin = tomllib.loads(pin_path.read_text(encoding="utf-8"))
assert pin["schema_version"] == 1
assert pin["bundle"] == {
    "id": "CUDA12-COMPAT-001",
    "kind": "preformal_cuda12_compatibility_probe",
    "claim_state": "roadmap",
    "gate_decision": "N/A: this bundle cannot produce a G1 Gate result",
}
sglang = pin["sglang"]
assert sglang["base_commit"] == "92b1d382c7f4d1c82ed3a76345d6f625f1fc54a2"
assert sglang["base_tree"] == "25e9bf86d04c27fe380024d9c8c421c3b5b51f3c"
assert sglang["source_seed_sha256"] == "2d40db92ff1a21cb78e95f4da98352f1fa17086e1a16a82e95070f05e1460400"
patches = sglang["patches"]
assert [item["path"] for item in patches] == [
    "upstream/sglang/patches/0001-atomic-checked-demote.patch",
    "upstream/sglang/patches/0002-g1-scripted-forced-demote.patch",
    "upstream/sglang/patches/0003-cuda12-compat-packaging.patch",
]
assert [item["changed_paths"] for item in patches] == [
    [
        "python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py",
        "python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py",
        "python/sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py",
        "python/sglang/srt/mem_cache/unified_radix_cache.py",
    ],
    ["test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py"],
    ["python/pyproject.toml"],
]
for declared, actual in zip(patches, (patch_one, patch_two, patch_three)):
    assert declared["sha256"] == sha256(actual)

model = pin["model"]
assert model == {
    "repository": "Qwen/Qwen3-0.6B",
    "revision": "c1899de289a04d12100db370d81485cdf75e47ca",
    "inventory": "experiments/g1/artifacts/model-files.g1-preflight-001.json",
    "local_only": True,
    "supports_swa": False,
}
inventory = json.loads((root / model["inventory"]).read_text(encoding="utf-8"))
assert inventory["repository"] == model["repository"]
assert inventory["revision"] == model["revision"]
spec = (root / "experiments/g1/SPEC.cuda12-compat-001.md").read_text(encoding="utf-8")
assert spec.index("19-cuda12-compat-001-project-prereqs.sh") < spec.index(
    "00-cuda12-compat-001-bootstrap.sh"
) < spec.index("20-cuda12-compat-001.sh")
assert "must not install, replace, or alter the NVIDIA driver, CUDA,\ncuDNN, or NCCL substrate" in spec
assert "current-tree source rebuild" in spec and "G0 prebuilt wheel payload" in spec
assert "patch 0002 adds only the named test file" in spec
assert "patch 0003 changes only package metadata" in spec
assert "must not install `$TREATMENT/python`" in spec
required_input_objects = (
    "generated input manifest", "ToolGap source seed", "SGLang source seed", "model snapshot", "runtime wheel",
    "runtime wheel provenance", "CUDA wheelhouse archive",
    "19-cuda12-compat-001-project-prereqs.sh", "00-cuda12-compat-001-bootstrap.sh",
    "input-oss-receipt.json", "stage-cuda12-compat-001-inputs-oss.sh",
)
for required_input_object in required_input_objects:
    assert required_input_object in spec, required_input_object
assert "operator downloads and runs\n`19`, then `00`" in spec
assert "`20` is taken only from the exact\ncheckout restored by `00`" in spec
assert "Each script validates its own\ndownloaded bytes" in spec
assert "BLOCKED_DEPENDENCY_TRANSPORT" in spec
assert "BLOCKED_DEPENDENCY_RESOLUTION" in spec
assert "anchor-cuda12-compat-001-oss.sh" in spec
assert "external JSON anchor" in spec
assert "six top-level CUDA wheels" in spec
assert "cuda-tile==1.6.0rc5" in spec
assert pin["capability_envelope"] == {
    "os": "Linux x86_64",
    "provider_image": "Alibaba Cloud official Ubuntu 24.04 NVIDIA GPU image",
    "gpu": "one NVIDIA A10 with 22-25 GiB",
    "nvidia_driver": "580.126.09",
    "system_cuda": "12.8",
    "cuda_home": "/usr/local/cuda-12.8",
    "python": "3.12.x",
    "runtime": "patched SGLang restricted startup; local model path only",
}
assert pin["runtime_wheel"] == {
    "provenance_identity": "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite",
    "source_rebuild": False,
    "payload": "prebuilt G0 treatment runtime payload; only CUDA12 wheel METADATA and RECORD are rewritten",
    "base_wheel_attempt": "G0-C-011 attempt 005 treatment",
    "base_wheel_filename": "sglang-0.0.0.dev2+g734a8e921-cp312-cp312-linux_x86_64.whl",
    "base_wheel_sha256": "0874acca7b27e45ae39606eb12ee24a5f4cb17cd3791bb60fdccb95c332bf59e",
}
assert pin["ordinary_dependency_transport"] == {
    "index_url": "http://mirrors.cloud.aliyuncs.com/pypi/simple/",
    "trusted_host": "mirrors.cloud.aliyuncs.com",
    "evidence": "G0-C-011 attempt 005 resolved ordinary dependencies through this provider-internal mirror",
}
packaging = pin["cuda12_packaging"]
assert packaging["torch_version"] == "2.13.0"
assert packaging["torchvision_version"] == "0.28.0"
assert packaging["torchaudio_version"] == "2.11.0"
assert packaging["torch_index_url"] == "https://download.pytorch.org/whl/cu129"
assert packaging["deep_ep_version"] == "0.1.0"
assert packaging["deep_ep_index_url"] == "https://docs.sglang.ai/whl/cu129/"
assert packaging["sglang_kernel_version"] == "0.4.6.post1"
assert packaging["sglang_kernel_wheel_template"] == (
    "https://github.com/sgl-project/whl/releases/download/v{version}/"
    "sglang_kernel-{version}+cu129-cp310-abi3-manylinux2014_{arch}.whl"
)
assert packaging["deep_gemm_version"] == "0.1.5.post2"
assert "+cu129" in packaging["deep_gemm_wheel_template"]
assert packaging["full_docker_reproduction"] is False
assert "12.6.3 and 12.9.2" in packaging["source_evidence"]

patch_text = patch_three.read_text(encoding="utf-8")
assert patch_text.count("diff --git ") == 1
assert "diff --git a/python/pyproject.toml b/python/pyproject.toml" in patch_text
assert patch_text.count("cuda-python>=13.0") == 1
assert patch_text.count("cuda-python>=12,<13") == 1
assert patch_text.count("flashinfer_python[cu13]") == 1
assert patch_text.count("flashinfer_python[cu12]") == 1
assert patch_text.count("humming-kernels[cu13]") == 1
assert patch_text.count("humming-kernels[cu12]") == 1
assert patch_text.count("nvidia-cutlass-dsl[cu13]") == 1
assert patch_text.count("nvidia-cutlass-dsl==4.6.2") == 1

template = json.loads(template_path.read_text(encoding="utf-8"))
assert template["identity"] == {
    "attempt_id": "__GENERATED__",
    "bundle_id": "CUDA12-COMPAT-001",
    "claim_state": "roadmap",
    "gate": "G1",
    "gate_decision": "N/A",
    "kind": "preformal_cuda12_compatibility_probe",
    "spec_path": "experiments/g1/SPEC.cuda12-compat-001.md",
    "spec_sha256": "__GENERATED__",
    "toolgap_commit": "__GENERATED__",
    "toolgap_tree": "__GENERATED__",
}
assert template["model"] == {
    "inventory_path": model["inventory"],
    "local_only": True,
    "repository": model["repository"],
    "revision": model["revision"],
}
assert template["outcome"] == {
    "claim_state": "roadmap",
    "gate_decision": "N/A: CUDA 12 compatibility probe only",
}
artifacts = [
    "attempt-context.json", "environment.txt", "source-seed.txt", "input-manifest-verify.log",
    "input-manifest.json", "input-oss-receipt.json", "bootstrap-receipt.json", "runtime-wheel.whl", "runtime-wheel-provenance.json",
    "runtime-wheel-validation.json", "cuda-wheelhouse-index.json", "cuda-wheelhouse-validation.json", "toolgap-seed-verify.log", "source-restore.log",
    "model-seed-prepare.log", "model-snapshot.json", "resolver-install.log", "cu13-distributions-before-removal.txt",
    "cu13-distributions-after-removal.txt", "dependency-lock.txt", "installed-distributions.json",
    "runtime-install-report.json", "cuda-wheelhouse-install-report.json", "ordinary-dependency-requirements.txt", "flashinfer-exception-install-report.json", "omitted-dependency-exception.json", "ordinary-dependency-report.json", "torch-cuda-probe.log", "cuda-sm86.cu", "cuda-sm86-build.log",
    "cuda-sm86-output.log", "sglang-provenance.json", "test-module-provenance.json", "runtime.env",
    "manifest.json", "manifest.sha256", "restricted-startup-command.txt", "restricted-startup.log",
    "startup.pid", "startup.pgid", "startup-gpu-pids-before.txt", "startup-gpu-pids-during.txt",
    "startup-gpu-pids-attributable.txt", "startup-gpu-pids-after.txt", "startup-gpu-pids-leaked.txt",
    "startup-process-group-after.txt", "startup-listeners-after.txt", "shutdown.log", "scope-scan.log",
]
assert template["planned_success_artifacts"] == artifacts
terminals = [
    "BLOCKED_HOST_IDENTITY", "BLOCKED_DEPENDENCY_TRANSPORT", "BLOCKED_DEPENDENCY_RESOLUTION", "RUNTIME_INCOMPATIBLE", "TOOLKIT_COMPILER_FAILED",
    "SGLANG_STARTUP_JIT_FAILED", "SGLANG_STARTUP_FAILED_OTHER", "INVALID_SCOPE",
    "COMPATIBLE_FOR_RESTRICTED_STARTUP_ONLY",
]
assert template["terminals"] == terminals
assert template["source"] == {
    "base_commit": sglang["base_commit"], "base_tree": sglang["base_tree"],
    "patches": [{"path": item["path"], "sha256": item["sha256"]} for item in patches],
    "remote": sglang["remote"], "source_seed_sha256": sglang["source_seed_sha256"],
}

runner = runner_path.read_text(encoding="utf-8")
assert runner.count("TestG1PreflightStartup.test_local_model_starts_without_runtime_script") == 1
assert "restricted-startup-command.txt" in runner
assert "scope-scan.log" in runner
assert "INVALID_SCOPE" in runner
assert "importlib.util.spec_from_file_location" in runner
assert "toolgap_cuda12_restricted_startup" in runner
assert "selector did not resolve exactly one test" in runner
assert '"$RUNTIME_VENV/bin/python" -m unittest' not in runner
assert "env -u PYTHONPATH" in runner
assert '"$RUN_DIR/restricted-startup-runner.py"' in runner
assert 'if __name__ == "__main__":' in runner
assert '"$RUNTIME_VENV/bin/python" - \\' not in runner
launcher_start = runner.index("source = '''") + len("source = '''")
launcher_end = runner.index("'''\nfd = os.open", launcher_start)
launcher_source = runner[launcher_start:launcher_end]
compile(launcher_source, "restricted-startup-runner.py", "exec")
with tempfile.TemporaryDirectory() as temp_dir:
    temp_root = pathlib.Path(temp_dir)
    launcher = temp_root / "restricted-startup-runner.py"
    test_module = temp_root / "restricted-startup-test.py"
    launcher.write_text(launcher_source, encoding="utf-8")
    test_module.write_text(
        """import multiprocessing\nimport os\nimport unittest\n\n\nclass TestG1PreflightStartup(unittest.TestCase):\n    def test_local_model_starts_without_runtime_script(self):\n        child = multiprocessing.get_context(\"spawn\").Process(target=os.getpid)\n        child.start()\n        child.join(10)\n        self.assertEqual(child.exitcode, 0)\n""",
        encoding="utf-8",
    )
    replay = subprocess.run(
        [
            sys.executable,
            str(launcher),
            str(test_module),
            "test.registered.scripted_runtime.test_toolgap_g1_forced_demote.TestG1PreflightStartup.test_local_model_starts_without_runtime_script",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert replay.returncode == 0, replay.stdout + replay.stderr
assert "0003-cuda12-compat-packaging.patch" not in runner
assert "CUDA12_COMPAT_RUNTIME_WHEEL" in runner
assert "CUDA12_COMPAT_RUNTIME_WHEEL_PROVENANCE" in runner
assert "CUDA12_COMPAT_CUDA_WHEELHOUSE_ARCHIVE" in runner
assert "CUDA12_COMPAT_INPUT_OSS_RECEIPT" in runner
assert "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite" in runner
assert '"$TREATMENT/python"' not in runner
assert "--find-links \"$CUDA_WHEELHOUSE_ROOT\" --index-url \"$PYPI_INDEX_URL\" --trusted-host \"$PYPI_TRUSTED_HOST\"" in runner
assert "--only-binary=:all:" in runner
assert "cuda-wheelhouse-validation.json" in runner
assert "cuda-wheelhouse-install-report.json" in runner
assert "flashinfer-exception-install-report.json" in runner
assert "omitted-dependency-exception.json" in runner
assert '"flashinfer_python[cu12]==0.6.17"' in runner
assert '"cuda-tile==1.6.0rc5"' in runner
assert 'pip list --format=json >"$RUN_DIR/installed-distributions.json"' in runner
assert '"$RUN_DIR/installed-distributions.json"' in runner
assert "http://mirrors.cloud.aliyuncs.com/pypi/simple/" in runner
for blocked_special_index in (
    "github.com/sgl-project/whl", "docs.sglang.ai/whl", "download.pytorch.org/whl",
):
    assert blocked_special_index not in runner, blocked_special_index
assert not re.search(r"(?i)(?:cargo|rustc)\s*(?:--|build|install)", runner)
assert runner.index('PHASE="restore"') < runner.index('PHASE="resolver"') < runner.index('PHASE="torch_cuda"') < runner.index('PHASE="compiler"')
assert "BLOCKED_DEPENDENCY_TRANSPORT" in runner
assert "BLOCKED_DEPENDENCY_RESOLUTION" in runner
assert '[[ "$exit_code" = 124 ]]' not in runner
assert "cu13-distributions-before-removal.txt" in runner
assert "cu13-distributions-after-removal.txt" in runner
assert "test ! -s \"$RUN_DIR/cu13-distributions-after-removal.txt\"" in runner
assert '"humming-kernels[cu12]==0.1.10"' in runner
assert "nvidia-cuda-runtime" in runner
assert "CUDA 13 distribution remains in installed inventory" in runner
assert "capture_environment" in runner
assert runner.index("capture_environment\n\nconfig=") > runner.index("attempt-context.json")
assert 'gpu_driver="$(xargs <<<"$gpu_driver")"' in runner
assert 'tar --no-same-owner -xzf "$TOOLGAP_SEED_ARCHIVE" -C "$TOOLGAP_INPUT"' in runner
assert '"$PYTHON" - "$RUNTIME_WHEEL" "$RUNTIME_WHEEL_PROVENANCE" \\' in runner
assert '--report "$RUN_DIR/runtime-install-report.json" "$RUNTIME_WHEEL"' in runner
assert '"$PYTHON" - "$RUNTIME_WHEEL" "$RUN_DIR/ordinary-dependency-requirements.txt"' in runner
assert "read_startup_listener_port \"$listener_requirement\"" in runner
assert "listener_requirement=optional" in runner
for unsafe_selector in (
    "TestG1RecordSchema", "TestG1EnabledArm", "TestG1BypassArm", "TestG1WriteThroughPending",
    "TestG1LoadBackPending", "TestG1NonTargetCoverage", "TestG1DeviceLocked",
    "TestG1StaleGeneration", "TestG1StockEvictionLiveness",
):
    assert unsafe_selector not in runner, unsafe_selector
prereqs = prereqs_path.read_text(encoding="utf-8")
assert "expected Ubuntu 24.04 x86_64" in prereqs
assert "nvidia-smi" in prereqs
assert "/usr/local/cuda-12.8/bin/nvcc" in prereqs
assert "curl git iproute2 python3-venv" in prereqs
assert "Rust" not in prereqs and "cargo" not in prereqs.lower()
assert re.search(r"(?m)^\\s*(?:nvidia|cuda|cudnn|nccl)[A-Za-z0-9_.+-]*", prereqs) is None
bootstrap = bootstrap_path.read_text(encoding="utf-8")
assert 'expected_path = "experiments/g1/commands/00-cuda12-compat-001-bootstrap.sh"' in bootstrap
assert "bootstrap script differs from the sealed input manifest" in bootstrap
assert 'tar --no-same-owner -xzf "$TOOLGAP_SEED_ARCHIVE" -C "$BOOTSTRAP_ROOT"' in bootstrap
assert 'expected_path = "experiments/g1/commands/19-cuda12-compat-001-project-prereqs.sh"' in prereqs
assert "prerequisite script differs from the sealed input manifest" in prereqs
builder = builder_path.read_text(encoding="utf-8")
for required in (
    "SPEC.cuda12-compat-001.md", "manifest.cuda12-compat-001.template.json",
    "00-cuda12-compat-001-bootstrap.sh", "19-cuda12-compat-001-project-prereqs.sh",
    "20-cuda12-compat-001.sh",
    "cuda12_compat_001_bundle_manifest.py", "cuda12_compat_001_finalize.py", "cuda12_compat_001_build_wheelhouse.py", "cuda12_compat_001_repackage_wheel.py",
    "pin.cuda12-compat-001.toml", "0003-cuda12-compat-packaging.patch",
):
    assert required in builder, required
for required_option in ("--runtime-wheel", "--runtime-wheel-provenance", "--cuda-wheelhouse"):
    assert required_option in builder, required_option
assert "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite" in builder
assert "wheelhouse-index.json" in builder
assert "static inputs must match the frozen ToolGap commit" in builder
assert '"status", "--porcelain"' not in builder
assert 'runtime_wheel.name != runtime["base_wheel_filename"]' in builder
assert "output wheel filename must preserve the pinned base filename" in repackager_path.read_text(encoding="utf-8")
module_spec = importlib.util.spec_from_file_location("cuda12_bundle_manifest", builder_path)
assert module_spec is not None and module_spec.loader is not None
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)
for required_static_input in (
    "experiments/g1/commands/19-cuda12-compat-001-project-prereqs.sh",
    "experiments/g1/commands/00-cuda12-compat-001-bootstrap.sh",
    "experiments/g1/commands/cuda12_compat_001_build_wheelhouse.py",
):
    assert required_static_input in module.STATIC_PATHS, required_static_input
three_archives = {
    name: {"path": f"{name}.tar", "sha256": "0" * 64, "size_bytes": 1}
    for name in ("model_snapshot", "sglang_source_seed", "toolgap_source_seed")
}
try:
    module.validate_manifest_schema({"archives": three_archives})
except ValueError:
    pass
else:
    raise AssertionError("builder accepts missing runtime-wheel inputs")
with tempfile.TemporaryDirectory() as temp_dir:
    bad_seed = pathlib.Path(temp_dir) / "bad-toolgap-seed.tar.gz"
    with tarfile.open(bad_seed, "w:gz") as archive:
        info = tarfile.TarInfo("._toolgap-source.git")
        info.size = 0
        archive.addfile(info)
    try:
        module.validate_toolgap_seed(bad_seed)
    except ValueError as error:
        assert "unsafe ToolGap seed member" in str(error)
    else:
        raise AssertionError("builder accepts an AppleDouble ToolGap seed member")
with tempfile.TemporaryDirectory() as temp_dir:
    staged = pathlib.Path(temp_dir) / "ecs-download" / pin["runtime_wheel"]["base_wheel_filename"]
    staged.parent.mkdir()
    staged.write_bytes(b"runtime wheel copied through OSS")
    staged_digest = sha256(staged)
    provenance = pathlib.Path(temp_dir) / "ecs-download" / "runtime-wheel-provenance.json"
    provenance.write_text(json.dumps({
        "schema_version": 1,
        "identity": pin["runtime_wheel"]["provenance_identity"],
        "source_rebuild": {"performed": False},
        "base_wheel": {
            "filename": pin["runtime_wheel"]["base_wheel_filename"],
            "sha256": pin["runtime_wheel"]["base_wheel_sha256"],
        },
        "output_wheel": {
            "filename": staged.name, "sha256": staged_digest,
            "size_bytes": staged.stat().st_size, "metadata_sha256": "0" * 64,
            "record_sha256": "1" * 64,
        },
        "patches": [
            {"label": f"patch_{word}", "path": f"/builder/{word}.patch", "sha256": patch["sha256"]}
            for word, patch in zip(("one", "two", "three"), patches)
        ],
        "metadata_rewrite": {"exact_substitutions": [
            {"from": before, "to": after, "input_occurrences": 1, "output_occurrences": 1}
            for before, after in module.METADATA_REWRITE
        ]},
    }), encoding="utf-8")
    module.validate_runtime_wheel_provenance(
        module.read_pin(root), staged, provenance
    )
    bad_name = staged.with_name("runtime-wheel.whl")
    bad_name.write_bytes(staged.read_bytes())
    provenance_value = json.loads(provenance.read_text(encoding="utf-8"))
    provenance_value["output_wheel"]["filename"] = bad_name.name
    bad_provenance = provenance.with_name("bad-runtime-wheel-provenance.json")
    bad_provenance.write_text(json.dumps(provenance_value), encoding="utf-8")
    try:
        module.validate_runtime_wheel_provenance(module.read_pin(root), bad_name, bad_provenance)
    except ValueError as error:
        assert "pinned wheel filename" in str(error)
    else:
        raise AssertionError("builder accepts a renamed runtime wheel")
finalizer = finalizer_path.read_text(encoding="utf-8")
for required in ("runtime-wheel.whl", "runtime-wheel-provenance.json", "cuda-wheelhouse-validation.json"):
    assert required in finalizer, required
for terminal in terminals:
    assert terminal in finalizer, terminal
assert "failure terminal requires best-effort environment evidence" in finalizer
assert "successful attempt retains CUDA13 distributions" in finalizer
assert "validate_cuda13_absence" in finalizer
assert "successful installed inventory retains CUDA13 distribution" in finalizer
assert "validate_failure_evidence" in finalizer
assert "dependency resolution terminal contains transport-failure evidence" in finalizer
assert "startup JIT terminal lacks JIT/compiler evidence" in finalizer
assert "invalid-scope terminal lacks scope=invalid evidence" in finalizer
assert "omitted dependency exception differs" in finalizer
assert "installed inventory unexpectedly contains cuda-tile" in finalizer
assert "validate_input_oss_receipt" in finalizer
assert "input OSS receipt objects do not share a prefix" in finalizer
assert 'canonical = lambda value: re.sub(r"[-_.]+", "-", value).lower()' in runner
assert "duplicate normalized distribution in installed inventory" in runner
assert "installed inventory differs for {name}" in runner
assert 'grep -Fxi "sgl-deep-gemm==${' not in runner
finalizer_spec = importlib.util.spec_from_file_location("cuda12_finalizer", finalizer_path)
assert finalizer_spec is not None and finalizer_spec.loader is not None
finalizer_module = importlib.util.module_from_spec(finalizer_spec)
finalizer_spec.loader.exec_module(finalizer_module)
with tempfile.TemporaryDirectory() as temp_dir:
    run_dir = pathlib.Path(temp_dir)
    after_cleanup = run_dir / "cu13-distributions-after-removal.txt"
    inventory = run_dir / "installed-distributions.json"
    after_cleanup.write_text("", encoding="utf-8")
    inventory.write_text('[{"name": "nvidia-cuda-runtime", "version": "13.0.0"}]', encoding="utf-8")
    try:
        finalizer_module.validate_cuda13_absence(run_dir)
    except ValueError as error:
        assert "nvidia-cuda-runtime==13.0.0" in str(error)
    else:
        raise AssertionError("finalizer accepts an unqualified CUDA 13 runtime package")
    inventory.write_text('[{"name": "nvidia-cuda-runtime-cu13", "version": "13.0.0"}]', encoding="utf-8")
    try:
        finalizer_module.validate_cuda13_absence(run_dir)
    except ValueError as error:
        assert "nvidia-cuda-runtime-cu13==13.0.0" in str(error)
    else:
        raise AssertionError("finalizer accepts a CUDA 13 suffixed package")
    inventory.write_text('[{"name": "nvidia-cuda-runtime-cu12", "version": "12.8.0"}]', encoding="utf-8")
    finalizer_module.validate_cuda13_absence(run_dir)
repackager = repackager_path.read_text(encoding="utf-8")
assert "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite" in repackager
assert "This is not a current three-patch source rebuild" in repackager
assert "sglang/_version.py" in repackager
assert "G0_BASE_WHEEL_SHA256" in repackager
assert '"filename": output_wheel.name' in repackager
assert "subprocess" not in repackager
wheelhouse_builder = wheelhouse_builder_path.read_text(encoding="utf-8")
assert "Create the exact CUDA12-COMPAT-001 wheelhouse archive" in wheelhouse_builder
assert "bundle.validate_cuda_wheelhouse" in wheelhouse_builder
assert "wheel identity differs from pinned CUDA12 route" in wheelhouse_builder
assert "path.read_bytes" not in wheelhouse_builder
anchor = anchor_path.read_text(encoding="utf-8")
assert "finalizer verify" not in anchor  # avoid stale prose-only invocation
assert '"$FINALIZER" verify --run-dir "$ATTEMPT_DIR"' in anchor
assert "ossutil ls --all-versions" in anchor
assert "CUDA12_COMPAT_001_EXTERNAL_OSS_ANCHOR" in anchor
assert "raw and anchor prefixes must not overlap" in anchor
assert anchor.count("ossutil -f cp ") == 4
assert anchor.count("</dev/null") == 4
assert 'ossutil cp "$local_path" "$object_uri"' not in anchor
stager = stager_path.read_text(encoding="utf-8")
assert "input-oss-receipt.json" in stager
assert "ossutil ls --all-versions" in stager
assert "refusing to overwrite existing receipt" in stager
assert "version_id" in stager
assert "version_id, latest, delete_marker, uri = fields[-4:]" in stager
assert stager.count("ossutil -f cp ") == 2
assert stager.count("</dev/null") == 2
PY

PATH="$(dirname -- "$PYTHON"):$PATH" bash "$ROOT/scripts/verify-g1-preflight-001-bundle.sh"

if [[ -n "${CUDA12_COMPAT_SGLANG_CHECKOUT:-}" ]]; then
  test -e "$CUDA12_COMPAT_SGLANG_CHECKOUT/.git"
  replay_root="$(mktemp -d "${TMPDIR:-/tmp}/toolgap-cuda12-static-replay.XXXXXX")"
  trap 'rm -rf "$replay_root"' EXIT
  replay_checkout="$replay_root/sglang"
  mkdir "$replay_checkout"
  git -C "$CUDA12_COMPAT_SGLANG_CHECKOUT" cat-file -e "$BASE_SGLANG_COMMIT^{commit}"
  # A partial local clone may lack unrelated blobs. Archive only every file
  # touched by this three-patch sequence, then verify the sequence against
  # those exact base blobs without asking the source remote for network data.
  git -C "$CUDA12_COMPAT_SGLANG_CHECKOUT" archive "$BASE_SGLANG_COMMIT" \
    python/pyproject.toml \
    python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py \
    python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py \
    python/sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py \
    python/sglang/srt/mem_cache/unified_radix_cache.py | tar -x -C "$replay_checkout"
  git -C "$replay_checkout" init --quiet
  git -C "$replay_checkout" add .
  git -C "$replay_checkout" -c user.name=ToolGap -c user.email=toolgap@invalid \
    commit --quiet --no-gpg-sign -m "base fixture"
  for patch in "$PATCH_0001" "$PATCH_0002" "$PATCH_0003"; do
    git -C "$replay_checkout" apply --check "$patch"
    git -C "$replay_checkout" apply "$patch"
  done
  expected_paths="$(printf '%s\n' python/pyproject.toml python/sglang/srt/mem_cache/unified_cache/session_ref_tracker.py python/sglang/srt/mem_cache/unified_cache/unified_tree_core.py python/sglang/srt/mem_cache/unified_cache/unified_tree_core_interface.py python/sglang/srt/mem_cache/unified_radix_cache.py test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py | LC_ALL=C sort)"
  actual_paths="$(
    {
      git -C "$replay_checkout" diff --name-only
      git -C "$replay_checkout" ls-files --others --exclude-standard
    } | LC_ALL=C sort
  )"
  test "$actual_paths" = "$expected_paths"
  "$PYTHON" -m py_compile "$replay_checkout/test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py"
fi

echo "VERIFIED_CUDA12_COMPAT_001_STATIC_BUNDLE"
