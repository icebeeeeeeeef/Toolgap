#!/usr/bin/env bash
# Static contract checks for the independent formal G1-C-020 source bundle.
set -euo pipefail

[[ "$#" == 0 ]] || { printf 'g1-c-020 verifier: arguments are forbidden\n' >&2; exit 2; }
for override in PYTHON BASH_ENV ENV PYTHONHOME PYTHONPATH PYTHONPYCACHEPREFIX CDPATH GLOBIGNORE \
  G1_C_020_VERIFY_RUNNER G1_C_020_VERIFY_BOOTSTRAP G1_C_020_SKIP_ORACLE_MUTATIONS; do
  [[ -z "${!override+x}" ]] || {
    printf 'g1-c-020 verifier: pre-set interpreter/injection variables are forbidden: %s\n' "$override" >&2
    exit 2
  }
done
if export -p | /usr/bin/grep -Eq 'declare -x (BASHOPTS|SHELLOPTS)='; then
  printf 'g1-c-020 verifier: exported shell option injection is forbidden\n' >&2
  exit 2
fi
readonly PYTHON="/usr/bin/python3"
readonly TRUSTED_PATH="/usr/bin:/bin:/usr/sbin:/sbin"
export PATH="$TRUSTED_PATH"
export PYTHONPYCACHEPREFIX="/tmp/toolgap-g1-c020-pycache-$$"
ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/.." && pwd -P)"
SPEC="$ROOT/experiments/g1/SPEC.g1-c-020.md"
TEMPLATE="$ROOT/experiments/g1/manifest.g1-c-020.template.json"
BOOTSTRAP="$ROOT/experiments/g1/commands/00-g1-c-020-bootstrap.sh"
RUNNER="$ROOT/experiments/g1/commands/20-g1-c-020.sh"
BUILDER="$ROOT/experiments/g1/commands/g1_c_020_bundle_manifest.py"
ARM_LAUNCHER="$ROOT/experiments/g1/commands/g1_c_020_arm_launcher.py"
EXTRACTOR="$ROOT/experiments/g1/commands/g1_c_020_extract_records.py"
FINALIZER="$ROOT/experiments/g1/commands/g1_c_020_finalize.py"
TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_finalize.py"
ARM_LAUNCHER_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_arm_launcher.py"
GPU_SAMPLER="$ROOT/experiments/g1/commands/g1_c_020_gpu_sampler.py"
GPU_SAMPLER_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_gpu_sampler.py"
SIGNAL_CLEANUP_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_signal_cleanup.sh"
SOURCE_RESTORE_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_source_restore.sh"
RUNTIME_WHEEL_NAME_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_runtime_wheel_name.sh"
ARM_RUNNER_SPAWN_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_arm_runner_spawn.sh"
ANCHOR_OFFLINE_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_anchor_offline.sh"
REQUEST_ADMISSION_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_request_admission.py"
SHARED_COVERAGE_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_shared_coverage.py"
REJECTION_GUARD_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_rejection_guards.py"
STORAGE_PREFLIGHT_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_storage_preflight.sh"
BUILDER_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_bundle_manifest.py"
PRE_EXECUTION_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_pre_execution.py"
FAILURE_EVIDENCE_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_failure_evidence.sh"
CLEANUP_FAILURE_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_cleanup_failure.sh"
HOST_MISMATCH_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_host_mismatch.sh"
NINJA_BINDING_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_ninja_binding.py"
ORACLE_MUTATION_TESTS="$ROOT/experiments/g1/commands/test_g1_c_020_oracle_mutations.py"
PLAN="$ROOT/worklog/plans/2026-08-25/g1-c-020-venv-ninja-binding.md"
LESSON="$ROOT/worklog/lessons/2026-08-25/g1-c-009-request-admission-race.md"
ANCHOR_LESSON="$ROOT/worklog/lessons/2026-08-25/g1-c-012-load-back-threshold.md"
CONTROL_REVIEW="$ROOT/worklog/reviews/2026-08-25/g1-c-010-final-matrix-review.md"
BASIS_REVIEW="$ROOT/worklog/reviews/2026-08-25/g1-c-013-pending-basis-review.md"
ANCHOR="$ROOT/scripts/anchor-g1-c-020-oss.sh"

for path in "$SPEC" "$TEMPLATE" "$BOOTSTRAP" "$RUNNER" "$BUILDER" "$ARM_LAUNCHER" "$EXTRACTOR" "$FINALIZER" "$TESTS" "$ARM_LAUNCHER_TESTS" "$GPU_SAMPLER" "$GPU_SAMPLER_TESTS" "$SIGNAL_CLEANUP_TESTS" "$SOURCE_RESTORE_TESTS" "$RUNTIME_WHEEL_NAME_TESTS" "$ARM_RUNNER_SPAWN_TESTS" "$ANCHOR_OFFLINE_TESTS" "$REQUEST_ADMISSION_TESTS" "$SHARED_COVERAGE_TESTS" "$REJECTION_GUARD_TESTS" "$STORAGE_PREFLIGHT_TESTS" "$BUILDER_TESTS" "$PRE_EXECUTION_TESTS" "$FAILURE_EVIDENCE_TESTS" "$CLEANUP_FAILURE_TESTS" "$HOST_MISMATCH_TESTS" "$NINJA_BINDING_TESTS" "$ORACLE_MUTATION_TESTS" "$PLAN" "$LESSON" "$ANCHOR_LESSON" "$CONTROL_REVIEW" "$BASIS_REVIEW" "$ANCHOR"; do
  test -f "$path"
done
bash -n "$BOOTSTRAP"
bash -n "$RUNNER"
bash -n "$ANCHOR"
test ! -e "$ROOT/experiments/g1/commands/19-g1-c-020-project-prereqs.sh"
"$PYTHON" -m py_compile "$BUILDER" "$ARM_LAUNCHER" "$EXTRACTOR" "$FINALIZER" "$TESTS" "$ARM_LAUNCHER_TESTS" "$GPU_SAMPLER" "$GPU_SAMPLER_TESTS" "$BUILDER_TESTS" "$PRE_EXECUTION_TESTS" "$REQUEST_ADMISSION_TESTS" "$SHARED_COVERAGE_TESTS" "$REJECTION_GUARD_TESTS" "$NINJA_BINDING_TESTS" "$ORACLE_MUTATION_TESTS"
"$PYTHON" "$BUILDER_TESTS"
"$PYTHON" "$PRE_EXECUTION_TESTS"
"$PYTHON" "$TESTS"
"$PYTHON" "$ARM_LAUNCHER_TESTS"
"$PYTHON" "$GPU_SAMPLER_TESTS"
bash "$SIGNAL_CLEANUP_TESTS"
bash "$SOURCE_RESTORE_TESTS"
bash "$RUNTIME_WHEEL_NAME_TESTS"
bash "$ARM_RUNNER_SPAWN_TESTS"
bash "$ANCHOR_OFFLINE_TESTS"
"$PYTHON" "$REQUEST_ADMISSION_TESTS"
"$PYTHON" "$SHARED_COVERAGE_TESTS"
"$PYTHON" "$REJECTION_GUARD_TESTS"
"$PYTHON" "$NINJA_BINDING_TESTS"
bash "$STORAGE_PREFLIGHT_TESTS"
bash "$FAILURE_EVIDENCE_TESTS"
bash "$CLEANUP_FAILURE_TESTS"
bash "$HOST_MISMATCH_TESTS"
PREDECESSOR="8417f2cda4bc53c92836d53179d362ff49d9fdf1"
git -C "$ROOT" diff --check "$PREDECESSOR"

# Every path present in frozen C-018 remains byte-identical. C-020 is additive.
FROZEN=()
while IFS= read -r path; do
  [[ -z "$path" ]] || FROZEN+=("$path")
done < <(git -C "$ROOT" ls-tree -r --name-only "$PREDECESSOR" -- experiments/g1 scripts upstream/sglang/patches worklog)
git -C "$ROOT" cat-file -e "$PREDECESSOR^{commit}"
git -C "$ROOT" diff --quiet "$PREDECESSOR" -- "${FROZEN[@]}" || {
  printf 'g1-c-020 verifier: frozen predecessor or external basis differs\n' >&2
  exit 1
}
git -C "$ROOT" apply --check \
  "$ROOT/upstream/sglang/patches/0002-g1-scripted-forced-demote-c020.patch"

readonly INLINE_ORACLE_TOKEN="G1_C_020_INLINE_ORACLE_COMPLETE_C016_EXTERNAL_BASIS"
INLINE_ORACLE_OUTPUT_FILE="$(/usr/bin/mktemp /tmp/g1-c-020-inline-oracle.XXXXXXXX)"
trap '/bin/rm -f "$INLINE_ORACLE_OUTPUT_FILE"' EXIT
"$PYTHON" -I - "$ROOT" "$SPEC" "$TEMPLATE" "$BOOTSTRAP" "$RUNNER" "$BUILDER" "$ARM_LAUNCHER" "$EXTRACTOR" "$FINALIZER" "$GPU_SAMPLER" "$ANCHOR" >"$INLINE_ORACLE_OUTPUT_FILE" <<'PY'
import hashlib
import importlib.util
import json
import pathlib
import re
import sys

root, spec_path, template_path, bootstrap_path, runner_path, builder_path, launcher_path, extractor_path, finalizer_path, sampler_path, anchor_path = map(pathlib.Path, sys.argv[1:])
spec = spec_path.read_text(encoding="utf-8")
bootstrap = bootstrap_path.read_text(encoding="utf-8")
runner = runner_path.read_text(encoding="utf-8")
builder = builder_path.read_text(encoding="utf-8")
launcher = launcher_path.read_text(encoding="utf-8")
extractor = extractor_path.read_text(encoding="utf-8")
finalizer = finalizer_path.read_text(encoding="utf-8")
sampler = sampler_path.read_text(encoding="utf-8")
anchor = anchor_path.read_text(encoding="utf-8")
shared_tests = (root / "experiments/g1/commands/test_g1_c_020_shared_coverage.py").read_text(encoding="utf-8")
request_tests = (root / "experiments/g1/commands/test_g1_c_020_request_admission.py").read_text(encoding="utf-8")
template = json.loads(template_path.read_text(encoding="utf-8"))


def marked_block(source: str, revision: str, name: str) -> str:
    pattern = rf"(?ms)^[^\n]*# BEGIN_{revision}_{name}\n.*?^[^\n]*# END_{revision}_{name}\n"
    matches = re.findall(pattern, source)
    if len(matches) != 1:
        raise AssertionError(f"{revision} marker count differs: {name}: {len(matches)}")
    return matches[0]


def normalize_to_c016(source: str) -> str:
    for current, predecessor in (
        ("G1-C-020", "G1-C-016"), ("G1_C_020", "G1_C_016"),
        ("g1-c-020", "g1-c-016"), ("g1_c_020", "g1_c_016"),
        ("c020", "c016"), ("C020", "C016"),
    ):
        source = source.replace(current, predecessor)
    return source


runtime_executables = {
    "bootstrap": bootstrap,
    "runner": runner,
    "builder": builder,
    "launcher": launcher,
    "extractor": extractor,
    "finalizer": finalizer,
    "sampler": sampler,
    "anchor": anchor,
}
canonical_runner = (root / "experiments/g1/commands/20-g1-c-016.sh").read_text(encoding="utf-8")
canonical_finalizer = (
    root / "experiments/g1/commands/g1_c_016_finalize.py"
).read_text(encoding="utf-8")
forbidden_privilege = re.compile(
    r"(?i)(?<![A-Za-z0-9_.-])(?:apt(?:-get)?|sudo|pkexec|doas|su|ubuntu-drivers|"
    r"dnf|yum|zypper|pacman|snap|dpkg(?:-query)?|rpm|systemctl|modprobe|insmod|"
    r"rmmod|mount|umount|chroot|nsenter|unshare|setcap|chown|sysctl)"
    r"(?![A-Za-z0-9_.-])"
)
system_pip = re.compile(
    r"(?im)^[ \t]*(?:(?:env|command)[^\n]*[ \t])?"
    r"(?:/usr/(?:local/)?bin/(?:python(?:3(?:\.\d+)?)?|pip3?)|python(?:3(?:\.\d+)?)?|pip3?)"
    r"[ \t]+(?:-m[ \t]+pip[ \t]+)?install\b"
)
raw_pip_install = re.compile(r"(?m)^.*?-m[ \t]+pip[ \t]+install\b.*$")
allowed_pip_installs = raw_pip_install.findall(canonical_runner)
assert len(allowed_pip_installs) == 4, "frozen C016 pip-install allowance differs"
for name, source in runtime_executables.items():
    privilege = forbidden_privilege.search(source)
    assert privilege is None, (
        f"forbidden package/privilege command in {name}: "
        f"{privilege.group(0) if privilege else ''}"
    )
    assert "--break-system-packages" not in source, f"system pip escape in {name}"
    assert "uv pip install --system" not in source, f"uv system install escape in {name}"
    assert system_pip.search(source) is None, f"system interpreter pip install in {name}"
    observed_pip_installs = raw_pip_install.findall(source)
    expected_pip_installs = allowed_pip_installs if name == "runner" else []
    assert observed_pip_installs == expected_pip_installs, (
        f"raw runtime pip-install surface differs: {name}"
    )

runner_ninja_blocks = (
    "NINJA_BINDING_HELPER", "NINJA_BINDING", "NINJA_RUNTIME_ENV", "FORMAL_ARM_PATH",
)
finalizer_ninja_blocks = (
    "NINJA_FINALIZER", "NINJA_RUNTIME_REPLAY", "NINJA_RUNTIME_ENV_EXPECTED",
    "NINJA_DISTRIBUTION_BINDING",
)
for name in runner_ninja_blocks:
    observed = normalize_to_c016(marked_block(runner, "C020", name))
    expected = marked_block(canonical_runner, "C016", name)
    assert observed == expected, f"runner Ninja block differs from frozen C016: {name}"
for name in finalizer_ninja_blocks:
    observed = normalize_to_c016(marked_block(finalizer, "C020", name))
    expected = marked_block(canonical_finalizer, "C016", name)
    assert observed == expected, f"finalizer Ninja block differs from frozen C016: {name}"

normalized_builder = builder.replace(
    '    "experiments/g1/commands/test_g1_c_020_oracle_mutations.py",\n', "", 1
)
assert normalized_builder != builder, "C020 builder oracle input is absent"
for name, current_source, predecessor in (
    ("bootstrap", bootstrap, "experiments/g1/commands/00-g1-c-016-bootstrap.sh"),
    ("builder", normalized_builder, "experiments/g1/commands/g1_c_016_bundle_manifest.py"),
    ("launcher", launcher, "experiments/g1/commands/g1_c_016_arm_launcher.py"),
    ("extractor", extractor, "experiments/g1/commands/g1_c_016_extract_records.py"),
    ("sampler", sampler, "experiments/g1/commands/g1_c_016_gpu_sampler.py"),
    ("anchor", anchor, "scripts/anchor-g1-c-016-oss.sh"),
):
    assert normalize_to_c016(current_source) == (root / predecessor).read_text(encoding="utf-8"), (
        f"runtime identity differs: {name}"
    )
assert (
    root / "upstream/sglang/patches/0002-g1-scripted-forced-demote-c020.patch"
).read_bytes() == (
    root / "upstream/sglang/patches/0002-g1-scripted-forced-demote-c014.patch"
).read_bytes()
assert (
    root / "upstream/sglang/patches/0002-g1-scripted-forced-demote-c020.patch"
).read_bytes() == (
    root / "upstream/sglang/patches/0002-g1-scripted-forced-demote-c016.patch"
).read_bytes()


def assert_ninja_contract(runner_source: str, finalizer_source: str) -> None:
    runner_requirements = (
        'local arm_path="$runtime_venv/bin:$cuda_home/bin:/usr/bin:/bin"',
        'command_resolution="$(PATH="$arm_path" command -v ninja)"',
        'shutil.which("ninja")',
        '[[ "$command_resolution" == "$ninja_path" ]]',
        '[[ "$python_resolution" == "$ninja_path" ]]',
        'ninja_sha256="$(sha256sum "$ninja_path"',
        '"arm_path": arm_path', '"ninja_path": ninja_path',
        '"command_resolution": command_resolution',
        '"python_resolution": python_resolution', '"sha256": sha256',
        '"version": version', 'PATH="$ARM_PATH"',
    )
    finalizer_requirements = (
        "def validate_ninja_runtime(", 'ninja = validate_ninja_runtime(run_dir, context)',
        'document["command_resolution"] != ninja_path',
        'document["python_resolution"] != ninja_path',
        'not valid_digest(document["sha256"])',
        '"ARM_PATH": ninja["arm_path"]', '"NINJA_SHA256": ninja["sha256"]',
        '"ninja"}.issubset(names)',
    )
    if any(item not in runner_source for item in runner_requirements):
        raise AssertionError("runner Ninja contract differs")
    if any(item not in finalizer_source for item in finalizer_requirements):
        raise AssertionError("finalizer Ninja replay differs")


assert_ninja_contract(runner, finalizer)
assert "/usr/bin/ninja" not in runner

def block_bounds(source: str, revision: str, name: str):
    block = marked_block(source, revision, name)
    start = source.index(block)
    return start, start + len(block)


helper_start, helper_end = block_bounds(runner, "C020", "NINJA_BINDING_HELPER")
binding_start, binding_end = block_bounds(runner, "C020", "NINJA_BINDING")
runtime_env_start, runtime_env_end = block_bounds(runner, "C020", "NINJA_RUNTIME_ENV")
formal_path_start, formal_path_end = block_bounds(runner, "C020", "FORMAL_ARM_PATH")
positions = {
    "die_helper": runner.index("die() {"),
    "ordinary_helper": runner.index("# BEGIN_RUNTIME_WHEEL_COPY_HELPERS"),
    "resolver_venv": runner.index('RUNTIME_VENV="$WORK_ROOT/runtime-venv"'),
    "ordinary_resolver": runner.index('"$RUNTIME_VENV/bin/python" -m pip install --only-binary=:all: --index-url'),
    "installed_distributions": runner.index('chmod 0444 "$RUN_DIR/installed-distributions.json"'),
    "runtime_validation": runner.index('"$PYTHON" - "$RUN_DIR/runtime-wheel-validation.json"'),
    "arm_plan": runner.index('"$PYTHON" - "$RUN_DIR/arm-plan.json"'),
    "arm_runner": runner.index('cat >"$RUN_DIR/arm-runner.py"'),
    "arm_runner_ready": runner.index('chmod 0444 "$RUN_DIR/arm-runner.py"'),
    "runtime_env_open": runner.index("  printf 'ORDINARY_PYPI_INDEX=%q\\n'"),
    "runtime_env_close": runner.index('} >"$RUN_DIR/runtime.env"'),
    "formal_phase": runner.index('PHASE="formal_arms"'),
    "run_arm_definition": runner.index("run_arm() {"),
    "arm_artifact": runner.index('printf \'%s\\n\' "$selector" >"$arm_dir/$arm.command.txt"'),
    "formal_launch": runner.index('exec "$PYTHON" "$ARM_LAUNCHER"'),
    "timeout": runner.index('timeout --signal=TERM --kill-after=30s "${LONG_TIMEOUT_SECONDS}s"'),
    "child_background": runner.index(') >"$arm_dir/$arm.log" 2>&1 &'),
    "run_arm_calls": runner.index('for arm in "${ARMS[@]}"; do run_arm'),
}
assert positions["die_helper"] < helper_start < helper_end <= positions["ordinary_helper"], (
    "C020 Ninja helper ordering differs"
)
assert positions["resolver_venv"] < positions["ordinary_resolver"]
assert positions["installed_distributions"] < binding_start < binding_end <= min(
    positions["runtime_validation"], positions["arm_plan"], positions["arm_runner"],
    positions["formal_phase"], positions["run_arm_definition"], positions["formal_launch"],
    positions["run_arm_calls"],
), "C020 Ninja binding ordering differs"
assert positions["arm_runner_ready"] < positions["runtime_env_open"] < runtime_env_start
assert runtime_env_start < runtime_env_end <= positions["runtime_env_close"] < positions["formal_phase"], (
    "C020 Ninja runtime environment ordering differs"
)
assert positions["formal_phase"] < positions["run_arm_definition"] < positions["arm_artifact"]
assert positions["formal_launch"] < positions["timeout"] < formal_path_start < formal_path_end
assert formal_path_end <= positions["child_background"] < positions["run_arm_calls"], (
    "C020 formal arm PATH ordering differs"
)

finalizer_bounds = {
    name: block_bounds(finalizer, "C020", name) for name in finalizer_ninja_blocks
}
validate_environment = finalizer.index("def validate_runtime_environment(")
expected_environment = finalizer.index("    expected = {", validate_environment)
validate_resolver = finalizer.index("def validate_resolver_milestone(")
installed_names = finalizer.index("    names = {", validate_resolver)
resolver_exception = finalizer.index("    exception = load_json(", validate_resolver)
assert finalizer_bounds["NINJA_FINALIZER"][1] <= validate_environment
assert validate_environment < finalizer_bounds["NINJA_RUNTIME_REPLAY"][0]
assert finalizer_bounds["NINJA_RUNTIME_REPLAY"][1] <= expected_environment
assert expected_environment < finalizer_bounds["NINJA_RUNTIME_ENV_EXPECTED"][0]
assert finalizer_bounds["NINJA_RUNTIME_ENV_EXPECTED"][1] < validate_resolver
assert installed_names < finalizer_bounds["NINJA_DISTRIBUTION_BINDING"][0]
assert finalizer_bounds["NINJA_DISTRIBUTION_BINDING"][1] < resolver_exception, (
    "C020 finalizer Ninja block ordering differs"
)
assert normalize_to_c016(runner) == canonical_runner, "runtime identity differs: runner"
assert normalize_to_c016(finalizer) == canonical_finalizer, "runtime identity differs: finalizer"
assert runner.count('readonly LONG_TIMEOUT_SECONDS=2400') == 1
assert runner.count('timeout --signal=TERM --kill-after=30s "${LONG_TIMEOUT_SECONDS}s"') == 1
runner_mutations = (
    'PATH="$ARM_PATH"',
    '[[ "$command_resolution" == "$ninja_path" ]]',
    '[[ "$python_resolution" == "$ninja_path" ]]',
    '"arm_path": arm_path', '"ninja_path": ninja_path',
    '"command_resolution": command_resolution',
    '"python_resolution": python_resolution', '"sha256": sha256',
    '"version": version', 'ninja_sha256="$(sha256sum "$ninja_path"',
)
for mutation in runner_mutations:
    assert runner.count(mutation) == 1, mutation
    try:
        assert_ninja_contract(runner.replace(mutation, "", 1), finalizer)
    except AssertionError:
        pass
    else:
        raise AssertionError(f"runner mutation stayed green: {mutation}")
for mutation in (
    'ninja = validate_ninja_runtime(run_dir, context)',
    'document["command_resolution"] != ninja_path',
    'document["python_resolution"] != ninja_path',
    'not valid_digest(document["sha256"])',
    '"ARM_PATH": ninja["arm_path"]',
    '"NINJA_SHA256": ninja["sha256"]',
):
    assert finalizer.count(mutation) == 1, mutation
    try:
        assert_ninja_contract(runner, finalizer.replace(mutation, "", 1))
    except AssertionError:
        pass
    else:
        raise AssertionError(f"finalizer mutation stayed green: {mutation}")

assert template["identity"] == {
    "attempt_id": "__GENERATED__", "bundle_id": "G1-C-020",
    "claim_state": "roadmap", "gate": "G1", "gate_decision": "__GENERATED__",
    "kind": "formal_checked_demote_runtime",
    "spec_path": "experiments/g1/SPEC.g1-c-020.md",
    "spec_sha256": "__GENERATED__", "toolgap_commit": "__GENERATED__",
    "toolgap_tree": "__GENERATED__",
}
assert template["outcome"] == {"claim_state": "roadmap", "terminals": ["PASS", "STOP", "INVALID"]}
for fragment in (
    "private Full KV tail", "committed host copy", "G2/G3",
    "public pause/cancel/resume API", "second physical KV data plane",
    "G0_prebuilt_runtime_payload_plus_CUDA12_metadata_rewrite",
    "current-tree wheel build", "six special wheels", "fresh SGLang",
    "six rejection cases", "is permitted only", "external anchor",
    "2026-08-25T01:32:28Z", "formal_arms", "_check_not_importing_main",
    "cleanup evidence was clean", "ENOSPC", "25769803776",
    "storage_preflight.minimum_free_bytes", "14922854400",
    "33479200768", "0ad49f1afdf5c59285a2828afbfe36d3409caa68",
    "529866d7fb10c88fbbfd174a320089b5ca0f8ab8",
    "g1-c-007-a1-20260825T042407Z", "2026-08-25 12:30:51 CST",
    "ModuleNotFoundError: No module named 'g1_c_007_scripted'",
    "frozen 2400-second timeout", "premature C-007 terminal state or receipt",
    "g1-c-008-a1-20260825T053604Z", "sealed `pre_execution INVALID`",
    "after three complete arm records", "((21,), (24,))",
    "DEFERRED/DEFERRED", "WRITE_THROUGH_PENDING",
    "REJECTED/STALE_GENERATION", "source-backed rejection-oracle mapping",
    "same nonempty unique sequence", "eligible and completed IDs must be empty",
    "non-boolean supplied and current generations differ", "empty target",
    "fixed `FULL`, `SWA`, and `MAMBA` slots", "exactly three",
    "Enabled binds requested, eligible", "scheduled, completed", "globally",
    "flatten exactly to the aggregate freed indices",
    "Within each before or after snapshot", "recomputed from before observations",
    "demote count, ID count, and cache-drain count agree",
    "does not assert the PASS-side", "before causal `STOP` is considered",
    "exact unchanged prepared device shape", "demoted host-only shape",
    "tombstones, host loss, and", "`checked_backend` to equal",
    "stock-victim record whose `after`", "frees cannot be reassigned across nodes",
    "all-unchanged", "capacity is unchanged",
    "reason must also be replayable", "all locks are zero", "from `1` to `0`",
    "Allocator device indices are", "Malformed or contradictory IDs are `INVALID`",
    "causal missing-reclaim `STOP` case",
    "pre-execution-failure.json", "real filename stem", "inherits this `sys.path`",
    "28a094182905fb4b8a8bc52182fb0314490baf08",
    "g1-c-009-a1-20260825T082527Z", "400 scheduler steps",
    "eventual HTTP 200", "_http_post_and_await_recv_msg", "exact request `rid`",
    "close-session control admission fences", "CloseSessionReqInput",
    "exact `session_id`", "No bare", "`_submit_post` remains",
    "g1-c-010-a1-20260825T095119Z", "seven-arm", "final independent matrix review",
    "LOAD_BACK_PENDING", "settled Host-copy guards", "all nine exactly once",
    "host_value_present == false", "available_before_reservation == logical_size",
    "available_after_release == logical_size", "no scheduler yield",
    "g1-c-011-a1-20260825T113123Z", "sealed `INVALID`", "`input_len - 1`",
    "new parent", "original child NodeId", "g1-c-012-a1-20260825T123410Z",
    "eight Full-KV tokens", "ten-token `load_back_threshold`",
    "without creating pending state", "Host-tail qualification",
    "6347aae14a98b5a2eda68d6fcf7bb92c1c3baada",
    "rejected before execution", "positive basis check",
    "whole scripted module", "byte-equivalent", "basis mutation oracle",
    "Relative to C-012 patch 0002", "`load_back_threshold + 2`",
    "at least `load_back_threshold` tokens", "appended token `7`",
    "exact pending",
):
    assert fragment in spec, fragment

module_spec = importlib.util.spec_from_file_location("g1_c_020_finalize", finalizer_path)
assert module_spec and module_spec.loader
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)
selected_test_path = pathlib.PurePosixPath(
    "test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py"
)
assert module.SCRIPTED_TEST_PATH == str(selected_test_path)
assert module.SELECTOR_MODULE == selected_test_path.stem
assert f'SCRIPTED_TEST="$TREATMENT/{selected_test_path}"' in runner
assert '"selector_module": scripted_test.stem' in runner
assert tuple(module.ARMS) == (
    "enabled", "bypass", "reject_write_through_pending",
    "reject_non_target_session_coverage", "reject_device_locked",
    "reject_stale_generation", "stock_eviction_liveness",
    "reject_load_back_pending", "reject_host_copy_not_committed",
)
assert set(module.SELECTORS) == set(module.ARMS)
for arm, selector in module.SELECTORS.items():
    assert selector in runner
assert "fresh_process_per_arm" in runner
assert 'exec "$PYTHON" "$ARM_LAUNCHER"' in runner
assert "wait_for_arm_handshake" in runner and "launcher-handshake.json" in runner
assert "os.setsid()" in launcher and "os.O_EXCL" in launcher and "wait_for_ack" in launcher
assert "G1_C_020_INPUT_OSS_RECEIPT" in runner
assert "--find-links" in runner and "mirrors.cloud.aliyuncs.com" in runner
assert "pip install --upgrade pip" not in runner
assert "g1_c_020_gpu_sampler.py" in runner
assert "--poll-seconds 0.25" in runner
assert "gpu-samples.json" in runner and "gpu-during.txt" in runner and "gpu-attributable.txt" in runner
assert "cleanup_active_processes" in runner and "CURRENT_ARM_PGID" in runner
assert "cleanup could not prove process-group exit; attempt remains unsealed" in runner
assert 'wait_for_runtime_group_exit "$pgid" || return 1' in runner
assert "os.getpgid(pid)" in runner and "launcher-ack.json" in runner
assert "trap 'seal_invalid \"$?\"' EXIT" in runner
assert "PATCHES=(" in runner
assert "apply_frozen_patches" in runner
assert "000{1-3}" not in runner
assert "storage_preflight" in runner
assert "24 * 1024 * 1024 * 1024" in runner
assert "storage-preflight-source-restore.json" in runner
assert "storage-preflight-resolver.json" in runner
assert "available disk is below manifest bound before source restore" in runner
assert "available disk is below manifest bound before dependency install" in runner
assert runner.index('storage-preflight-source-restore.json') < runner.index('tar --no-same-owner')
assert runner.index('storage-preflight-resolver.json') < runner.index('"$PYTHON" -m venv')
assert runner.index('record_failure_evidence "$code"') < runner.index('"$PYTHON" "$FINALIZER" invalid')
assert '"work_root": str(work_root)' in runner
assert runner.index("capture_environment") < runner.index("requires Linux x86_64")
assert runner.rindex('PHASE="seal"') > runner.index('sha256sum manifest.json')
assert runner.rindex('PHASE="render"') > runner.index('scope=clean')
assert runner.rindex('PHASE="render"') < runner.index('sha256sum manifest.json')
assert "def main() -> int:" in runner
assert 'if __name__ == "__main__":' in runner
assert "raise SystemExit(main())" in runner
assert "sys.path.insert(0, str(path.parent))" in runner
assert "importlib.import_module(path.stem)" in runner
assert 'getattr(module, "__file__", None)' in runner
assert 'pathlib.Path(module_file).resolve() != path' in runner
assert "g1_c_020_scripted" not in runner
assert "importlib.util, pathlib, sys, unittest" not in runner
assert "runtime_wheel_filename" in runner
assert "EXPECTED_RUNTIME_WHEEL_FILENAME" in runner
assert '"$RUNTIME_WHEEL_FILENAME" == "$EXPECTED_RUNTIME_WHEEL_FILENAME"' in runner
assert '"$RUN_DIR/$RUNTIME_WHEEL_FILENAME"' in runner
assert '"runtime-wheel.whl"' not in runner
assert "changed_regular_paths" in runner
assert '"diff", "--name-only"' in runner
assert '"ls-files", "--others", "--exclude-standard"' in runner
assert "candidate.is_symlink()" in runner
assert "candidate.is_file()" in runner
assert "resolved.relative_to(root)" in runner
assert "CHANGED_OUTPUT" in runner
assert "test_toolgap_g1_forced_demote.py" in runner
for patch_name in (
    "0001-atomic-checked-demote.patch",
    "0002-g1-scripted-forced-demote-c020.patch",
    "0003-cuda12-compat-packaging.patch",
):
    assert patch_name in runner
assert "scope scan requires every formal arm log" in runner
assert "unapproved_index" in runner and "source_build" in runner
for forbidden in (
    "cargo ", "rustc ", "maturin ", "pip install \"$TREATMENT/python\"",
    "download.pytorch.org", "docs.sglang.ai", "github.com/sgl-project",
):
    assert forbidden not in runner, forbidden
assert "G1_C_020_EXTERNAL_OSS_ANCHOR" in anchor
assert "ossutil ls --all-versions" in anchor
assert "python3 \"$FINALIZER\" verify" in anchor
assert "CONTEXT_ATTEMPT_ID" in anchor and "CONTEXT_SHA256" in anchor
assert 'not in ("PASS", "STOP", "INVALID")' in anchor
assert 'r"[A-Za-z0-9][A-Za-z0-9._+/-]*"' in anchor
assert 'not in {"PASS", "STOP", "INVALID"}' not in anchor

# Builder independently binds patch bytes, immutable runtime provenance, the
# six-wheel index, and every static formal script.
for required in (
    "RUNTIME_PROVENANCE", "validate_runtime_provenance", "validate_wheelhouse",
    "safe_seed", "STATIC_PATHS", "tracked ToolGap files must be clean",
):
    assert required in builder, required
for label in ("patch_one", "patch_two", "patch_three"):
    assert label in builder and label in finalizer
for relative in (
    "experiments/g1/SPEC.g1-c-020.md",
    "experiments/g1/commands/20-g1-c-020.sh",
    "experiments/g1/commands/g1_c_020_arm_launcher.py",
    "experiments/g1/commands/g1_c_020_finalize.py",
    "experiments/g1/commands/g1_c_020_gpu_sampler.py",
    "experiments/g1/commands/test_g1_c_020_runtime_wheel_name.sh",
    "experiments/g1/commands/test_g1_c_020_arm_launcher.py",
    "experiments/g1/commands/test_g1_c_020_arm_runner_spawn.sh",
    "experiments/g1/commands/test_g1_c_020_anchor_offline.sh",
    "experiments/g1/commands/test_g1_c_020_request_admission.py",
    "experiments/g1/commands/test_g1_c_020_shared_coverage.py",
    "experiments/g1/commands/test_g1_c_020_rejection_guards.py",
    "experiments/g1/commands/test_g1_c_020_storage_preflight.sh",
    "experiments/g1/commands/test_g1_c_020_bundle_manifest.py",
    "experiments/g1/commands/test_g1_c_020_pre_execution.py",
    "experiments/g1/commands/test_g1_c_020_failure_evidence.sh",
    "experiments/g1/commands/test_g1_c_020_cleanup_failure.sh",
    "experiments/g1/commands/test_g1_c_020_host_mismatch.sh",
    "scripts/anchor-g1-c-020-oss.sh",
):
    assert relative in builder
for patch in (
    root / "upstream/sglang/patches/0001-atomic-checked-demote.patch",
    root / "upstream/sglang/patches/0002-g1-scripted-forced-demote-c020.patch",
    root / "upstream/sglang/patches/0003-cuda12-compat-packaging.patch",
):
    assert re.fullmatch(r"[0-9a-f]{64}", hashlib.sha256(patch.read_bytes()).hexdigest())

patch_one = (root / "upstream/sglang/patches/0001-atomic-checked-demote.patch").read_text(encoding="utf-8")
patch_two = (root / "upstream/sglang/patches/0002-g1-scripted-forced-demote-c020.patch").read_text(encoding="utf-8")
assert patch_two == (
    root / "upstream/sglang/patches/0002-g1-scripted-forced-demote-c013.patch"
).read_text(encoding="utf-8")
assert 'reason="STALE_GENERATION"' in patch_one
assert 'reason=disposition' in patch_one
session_request = patch_two.split("+def _session_request(", 1)[1].split(
    "+def _session_frontier", 1
)[0]
assert "_http_post_and_await_recv_msg" in session_request
assert 'predicate=lambda obj: getattr(obj, "rid", None) == rid' in session_request
assert 'description=f"request with rid {rid!r}"' in session_request
assert "_submit_post" not in session_request
assert "_MAX_STEPS = 400" in patch_two
stale_script = patch_two.split("+    def _script_stale_generation", 1)[1].split(
    "+class TestG1StockEvictionLiveness", 1
)[0]
assert "CloseSessionReqInput" in stale_script
assert "_http_post_and_await_recv_msg" in stale_script
assert 'path="/close_session"' in stale_script
assert "isinstance(obj, CloseSessionReqInput)" in stale_script
assert "obj.session_id == session_id" in stale_script
assert 'description=f"close session {session_id!r}"' in stale_script
assert "_submit_post" not in patch_two
for regression in (
    "test_delayed_admission_blocks_helper_before_scheduler_budget_starts",
    "test_wrong_rid_does_not_satisfy_admission_fence",
    "test_request_arrival_timeout_propagates_before_handle_or_budget",
    "test_delayed_close_admission_precedes_side_effect_budget",
    "test_close_predicate_rejects_wrong_type_and_session",
    "test_close_arrival_timeout_propagates_before_side_effect_budget",
    "test_completion_steps_begin_after_arrival_and_reach_frontier",
    "test_source_forbids_fire_and_forget_submission_anywhere",
):
    assert regression in request_tests
assert "equal_but_distinct" in request_tests
assert "actual is not value" in request_tests
assert "def _register_non_target_session_coverage(" in patch_two
assert "ensure_session_generation(session_id)" in patch_two
assert "component.register_session_leaf(session_id, node)" in patch_two
assert "assert target_nodes == other_nodes" not in patch_two
assert 'assert outcome.reason == "DEFERRED"' in patch_two
for reason in (
    "WRITE_THROUGH_PENDING", "NON_TARGET_SESSION_COVERAGE", "DEVICE_LOCKED",
    "LOAD_BACK_PENDING", "HOST_COPY_NOT_COMMITTED",
):
    assert f'_assert_deferred_node_reason(outcome, "{reason}")' in patch_two

load_back_script = patch_two.split("+    def _script_load_back_pending", 1)[1].split(
    "+class TestG1HostCopyNotCommitted", 1
)[0]
assert "+            input_ids=target_input_ids + [7]," in load_back_script
assert "+            input_ids=target_input_ids," not in load_back_script
assert "+                node.load_back_pending_id == node.id" in load_back_script
assert "+                and node.id in cache.ongoing_load_back" in load_back_script
assert "+                and cache.ongoing_load_back[node.id].node_id == node.id" in load_back_script
assert "+                max_new_tokens=t.scheduler.tree_cache.load_back_threshold + 2," in load_back_script
assert "+        target_host_tokens = len(target_host_value)" in load_back_script
assert "+        assert target_host_tokens >= cache.load_back_threshold, (" in load_back_script
assert "+        cache.load_back(" not in load_back_script

enabled_script = patch_two.split("+    def _script_enabled", 1)[1].split(
    "+class TestG1BypassArm", 1
)[0]
bypass_script = patch_two.split("+    def _script_bypass", 1)[1].split(
    "+class TestG1WriteThroughPending", 1
)[0]
for arm_script in (enabled_script, bypass_script):
    assert "record = _new_record(" in arm_script
    assert "print(json.dumps(record, sort_keys=True))" in arm_script
for forbidden in (
    "assert _freed_ids(outcome)", "assert counters.cache_owned_drain",
    'assert after["available_size"]', "expected_freed_ids",
):
    assert forbidden not in enabled_script
for forbidden in (
    "assert counters.physical_demote == 0", "assert counters.cache_owned_drain == 0",
    'assert after["available_size"] == before["available_size"]',
    'assert [observation["device_ids"] for observation in target_after]',
):
    assert forbidden not in bypass_script
assert 'and observation["host_committed"]' in patch_two
assert 'and observation["device_leaf"]' in patch_two
assert 'and not any(observation["lock_refs"])' in patch_two
assert 'and observation["session_ref"] == 1' in patch_two

# The terminal classifier validates formal arm context before evaluating only
# the two causal STOP predicates; malformed/rejection/liveness faults are INVALID.
assert "return \"STOP\", causal_stop" in finalizer
assert "return \"INVALID\", structural" in finalizer
assert finalizer.index("if failures:") < finalizer.index("causal_stop =")
assert "enabled_context_errors" in finalizer and "bypass_context_errors" in finalizer
assert "validate_full_evidence" in finalizer and "sglang-package-provenance.json" in finalizer
assert "RUNTIME_WHEEL_FILENAME" in finalizer and "runtime_wheel_filename" in finalizer
assert "MINIMUM_FREE_BYTES" in builder and "storage_preflight" in builder
assert "validate_storage_preflight" in finalizer and "storage-preflight-resolver.json" in finalizer
assert "validate_pre_execution_evidence" in finalizer and "pre_execution_failure_reason" in finalizer
assert "PHASE_REQUIRED_MILESTONES" in finalizer and '"work_root"' in finalizer
assert '"render"' in finalizer and "launcher handshake differs" in finalizer
assert "artifact index does not equal the sealed regular-file set" in finalizer
assert "rejection contract" in finalizer and "stock eviction liveness" in finalizer
assert "rejection_nodes_pass" in finalizer
assert "rejection_observations_pass" in finalizer
assert "stale_rejection_context_pass" in finalizer
assert 'set(operation) != {"session_id", "supplied_generation"}' in finalizer
assert 'target["scheduled_node_ids"] != requested' in finalizer
assert 'target["eligible_node_ids"] != []' in finalizer
assert 'target["completed_node_ids"] != []' in finalizer
assert 'record["released_component_leaves"] > 0' in finalizer
assert 'not isinstance(record["priority_release"], str)' in finalizer
assert 'operation["supplied_generation"] != operation["current_generation"]' in finalizer
assert 'before[node_id]["write_through_pending"] is False' in finalizer
assert 'before[node_id]["load_back_pending"] is False' in finalizer
assert 'all(value == 0 for value in before[node_id]["lock_refs"])' in finalizer
assert 'before[node_id]["session_ref"] == 1' in finalizer
assert 'after[node_id]["session_ref"] == 0' in finalizer
assert '{"disposition": "DEFERRED", "reason": "DEFERRED"}' in finalizer
assert '{"disposition": "REJECTED", "reason": reason}' in finalizer
assert "release_session_priority" in shared_tests
assert "session_ids" in shared_tests and "ancestor" in shared_tests
assert 'self.assertEqual(target.component_data["FULL"].session_ref, 1)' in shared_tests
assert 'self.assertEqual(ancestor.component_data["FULL"].session_ref, 1)' in shared_tests
assert 'self.assertEqual(component._session_leaves[second_session], {target})' in shared_tests
assert "arm record aggregate differs from individual evidence" in finalizer
assert "observation_errors" in finalizer and "LIVE_OBSERVATION_FIELDS" in finalizer
assert 'len(lock_refs) != 3' in finalizer
assert 'observation["session_ref"] < 0' in finalizer
assert 'observation["node_id"] < 0' in finalizer
assert 'len(device_ids) != len(set(device_ids))' in finalizer
assert 'len(phase_device_ids) != len(set(phase_device_ids))' in finalizer
assert 'observation_is_eligible(observation)' in finalizer
assert 'def observation_is_prepared(' in finalizer
assert 'observation_is_prepared(item)' in finalizer
assert 'positive_after_shape(before[index], item)' in finalizer
assert 'len(target[key]) != len(set(target[key]))' in finalizer
assert 'target["eligible_node_ids"] != requested' in finalizer
assert 'target["completed_node_ids"] != requested' in finalizer
assert 'counters["physical_demote_node_ids"] != requested' in finalizer
assert 'counters["physical_demote"] != len(requested)' in finalizer
assert 'counters["cache_owned_drain"] != len(requested)' in finalizer
assert 'counters["physical_demote"] != len(physical_ids)' in finalizer
assert 'counters["cache_owned_drain"] != counters["physical_demote"]' in finalizer
assert 'physical_ids != demoted_ids' in finalizer
assert 'counters["checked_backend"] != len(requested)' in finalizer
assert '== (0 if stale else len(record["target"]["requested_node_ids"]))' in finalizer
assert 'node["disposition"] != "COMPLETED" or node["reason"] != "DEMOTED"' in finalizer
assert 'len(original_device_ids) != len(set(original_device_ids))' in finalizer
assert 'node_freed_device_ids != record["freed_device_ids"]' in finalizer
assert 'expected_node_frees' in finalizer and 'expected_freed_device_ids' in finalizer
assert 'all(shape == "unchanged" for shape in after_shapes)' in finalizer
assert 'def liveness_target_after_passes(' in finalizer
assert 'victim_after.get(after["node_id"]) != after' in finalizer
assert 'any(type(node_id) is not int or node_id < 0 for node_id in candidates)' in finalizer
assert '[data.lock_ref for data in node.component_data]' in patch_two
assert '[1, 0, 0]' in (root / "experiments/g1/commands/test_g1_c_020_finalize.py").read_text(encoding="utf-8")
tests = (root / "experiments/g1/commands/test_g1_c_020_finalize.py").read_text(encoding="utf-8")
assert "test_patch_records_causal_outcomes_before_final_classification" in tests
assert "test_noncausal_failure_precedes_enabled_causal_stop" in tests
assert "test_target_phase_device_ids_are_globally_unique" in tests
assert "test_enabled_after_requires_a_coherent_live_source_shape" in tests
assert "test_bypass_after_requires_unchanged_or_instrumented_demoted_shape" in tests
assert "test_liveness_before_requires_a_prepared_device_tail" in tests
assert "test_enabled_tombstone_preparation_is_invalid_without_exception" in tests
assert "test_checked_backend_count_matches_requested_nodes" in tests
assert "test_enabled_after_shape_binds_frees_and_capacity" in tests
assert "test_enabled_frees_cannot_be_attributed_to_another_node" in tests
assert "test_liveness_after_requires_preserved_state_or_matching_victim" in tests
assert "test_liveness_target_eviction_is_replayed_from_matching_victim" in tests
assert "test_priority_release_unhashable_json_is_invalid_without_exception" in tests
rejection_tests = (root / "experiments/g1/commands/test_g1_c_020_rejection_guards.py").read_text(encoding="utf-8")
assert "test_deleting_either_guard_is_red" in rejection_tests
assert "test_deleting_the_suffix_restores_the_c011_split_parent_counterexample" in rejection_tests
assert "test_lowering_the_specialized_tail_to_eight_tokens_is_red" in rejection_tests
assert "test_deleting_threshold_qualification_is_red" in rejection_tests
assert "test_threshold_revision_has_exact_c012_basis" in rejection_tests
assert "test_indirect_pending_id_fabrication_is_red" in rejection_tests
assert "test_mapping_update_pending_fabrication_is_red" in rejection_tests
assert "threshold_basis_errors" in rejection_tests and "PATCH_BASIS" in rejection_tests
assert "load_back_fixture_contract_errors" in rejection_tests
assert "validate_gpu_samples" in finalizer and "GPU sampler union differs" in finalizer
assert "stock_eviction_errors" in finalizer and "no_allocator_reclaim" in finalizer
print("G1_C_020_INLINE_ORACLE_COMPLETE_C016_EXTERNAL_BASIS")
PY
if ! printf '%s\n' "$INLINE_ORACLE_TOKEN" | /usr/bin/cmp -s - "$INLINE_ORACLE_OUTPUT_FILE"; then
  printf 'g1-c-020 verifier: inline oracle completion token differs\n' >&2
  exit 1
fi
/bin/cat "$INLINE_ORACLE_OUTPUT_FILE"
/bin/rm -f "$INLINE_ORACLE_OUTPUT_FILE"
trap - EXIT
"$PYTHON" "$ORACLE_MUTATION_TESTS"
