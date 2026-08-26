#!/usr/bin/env python3
"""Focused counterexamples for the C015 request-admission fence."""

from __future__ import annotations

import ast
import subprocess
import sys
import tempfile
import threading
import types
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[3]
PATCH = ROOT / "upstream/sglang/patches/0002-g1-scripted-forced-demote-c015.patch"
SCRIPTED_TEST = Path(
    "test/registered/scripted_runtime/test_toolgap_g1_forced_demote.py"
)


def applied_test_source() -> str:
    with tempfile.TemporaryDirectory(prefix="g1-c-015-admission-") as directory:
        checkout = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=checkout, check=True)
        subprocess.run(["git", "apply", str(PATCH)], cwd=checkout, check=True)
        return (checkout / SCRIPTED_TEST).read_text(encoding="utf-8")


def load_function(source: str, name: str, *, class_name: str | None = None):
    tree = ast.parse(source)
    body = tree.body
    if class_name is not None:
        owner = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == class_name
        )
        body = owner.body
    function = next(
        node
        for node in body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == name
    )
    function.decorator_list = []
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    namespace = {
        "Any": object,
        "Generator": object,
        "_MAX_NEW_TOKENS": 8,
        "_MAX_STEPS": 400,
        "_PROMPT_LEN": 256,
    }
    exec(compile(module, str(PATCH), "exec"), namespace)
    return namespace[name]


class FakeHandle:
    def __init__(self, *, rid: str, context: object) -> None:
        self.rid = rid
        self.context = context

    @property
    def finished(self) -> bool:
        return self.context.admitted and self.context.scheduler_steps >= 2


class FakeCloseSessionReqInput:
    def __init__(self, *, session_id: str) -> None:
        self.session_id = session_id


def equal_but_distinct(value: str) -> str:
    actual = (" " + value)[1:]
    assert actual == value
    assert actual is not value
    return actual


@contextmanager
def scripted_runtime_modules(*, submit, await_arrival):
    names = (
        "sglang",
        "sglang.srt",
        "sglang.srt.managers",
        "sglang.srt.managers.io_struct",
        "sglang.test",
        "sglang.test.scripted_runtime",
        "sglang.test.scripted_runtime.context",
        "sglang.test.scripted_runtime.context.http_post",
        "sglang.test.scripted_runtime.req_handle",
    )
    previous = {name: sys.modules.get(name) for name in names}
    modules = {name: types.ModuleType(name) for name in names}
    modules["sglang.srt.managers.io_struct"].CloseSessionReqInput = (
        FakeCloseSessionReqInput
    )
    modules[names[-2]]._submit_post = submit
    modules[names[-2]]._http_post_and_await_recv_msg = await_arrival
    modules[names[-1]].ScriptedReqHandle = FakeHandle
    sys.modules.update(modules)
    try:
        yield
    finally:
        for name, module in previous.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


class G1C015RequestAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = applied_test_source()
        cls.session_request = staticmethod(
            load_function(cls.source, "_session_request")
        )
        cls.complete_session = staticmethod(
            load_function(
                cls.source,
                "_complete_private_session",
                class_name="_G1ScriptedTestCase",
            )
        )
        cls.stale_script = staticmethod(
            load_function(
                cls.source,
                "_script_stale_generation",
                class_name="TestG1StaleGeneration",
            )
        )

    def test_delayed_admission_blocks_helper_before_scheduler_budget_starts(self) -> None:
        posted = threading.Event()
        release = threading.Event()
        context = SimpleNamespace(admitted=False, scheduler_steps=0)
        result = []

        def submit(*_args, **_kwargs) -> None:
            posted.set()

        def await_arrival(_context, *, path, json, predicate, description) -> None:
            self.assertEqual(path, "/generate")
            self.assertEqual(json["rid"], "delayed-rid")
            self.assertEqual(description, "request with rid 'delayed-rid'")
            posted.set()
            self.assertTrue(release.wait(1.0))
            self.assertTrue(predicate(SimpleNamespace(rid="delayed-rid")))
            _context.admitted = True

        def invoke() -> None:
            result.append(
                self.session_request(
                    context,
                    "delayed-session",
                    "delayed-rid",
                    max_new_tokens=8,
                )
            )

        with scripted_runtime_modules(submit=submit, await_arrival=await_arrival):
            worker = threading.Thread(target=invoke)
            worker.start()
            self.assertTrue(posted.wait(1.0))
            self.assertTrue(worker.is_alive(), "helper returned before exact-rid admission")
            self.assertEqual(context.scheduler_steps, 0)
            release.set()
            worker.join(1.0)

        self.assertFalse(worker.is_alive())
        self.assertEqual(result[0].rid, "delayed-rid")
        self.assertTrue(context.admitted)

    def test_wrong_rid_does_not_satisfy_admission_fence(self) -> None:
        observed = []
        context = SimpleNamespace(admitted=False, scheduler_steps=0)
        expected_rid = "exact-rid"

        def await_arrival(_context, *, predicate, **_kwargs) -> None:
            observed.append(predicate(SimpleNamespace(rid="exact-rid-stale")))
            observed.append(predicate(SimpleNamespace(rid="other-prefix")))
            observed.append(predicate(SimpleNamespace()))
            observed.append(predicate(SimpleNamespace(rid=7)))
            actual_rid = equal_but_distinct(expected_rid)
            observed.append(predicate(SimpleNamespace(rid=actual_rid)))
            _context.admitted = observed == [False, False, False, False, True]

        with scripted_runtime_modules(
            submit=lambda *_args, **_kwargs: None,
            await_arrival=await_arrival,
        ):
            handle = self.session_request(
                context, "exact-session", expected_rid, max_new_tokens=8
            )

        self.assertEqual(observed, [False, False, False, False, True])
        self.assertEqual(handle.rid, expected_rid)
        self.assertTrue(context.admitted)

    def test_request_arrival_timeout_propagates_before_handle_or_budget(self) -> None:
        context = SimpleNamespace(admitted=False, scheduler_steps=0)
        sentinel = TimeoutError("request-admission-timeout")

        def await_arrival(*_args, **_kwargs) -> None:
            raise sentinel

        with scripted_runtime_modules(
            submit=lambda *_args, **_kwargs: None,
            await_arrival=await_arrival,
        ):
            with self.assertRaises(TimeoutError) as caught:
                self.session_request(
                    context, "timeout-session", "timeout-rid", max_new_tokens=8
                )

        self.assertIs(caught.exception, sentinel)
        self.assertEqual(context.scheduler_steps, 0)

    def test_delayed_close_admission_precedes_side_effect_budget(self) -> None:
        session_id = "g1-stale-generation"
        posted = threading.Event()
        release = threading.Event()
        cache = SimpleNamespace(
            session_refs=SimpleNamespace(_session_generations={session_id: 1})
        )
        result = []

        def complete_private_session(_context, _session_id, _rid):
            if False:
                yield
            return cache, 1, (21,)

        def submit(*_args, **_kwargs) -> None:
            posted.set()

        def await_arrival(_context, *, path, json, predicate, description) -> None:
            self.assertEqual(path, "/close_session")
            self.assertEqual(json, {"session_id": session_id})
            self.assertEqual(description, f"close session {session_id!r}")
            posted.set()
            self.assertTrue(release.wait(1.0))
            self.assertTrue(predicate(FakeCloseSessionReqInput(session_id=session_id)))

        owner = SimpleNamespace(_complete_private_session=complete_private_session)
        globals_ = self.stale_script.__globals__
        previous = globals_.get("TestG1StaleGeneration")
        globals_["TestG1StaleGeneration"] = owner
        generator = self.stale_script(SimpleNamespace())

        def advance() -> None:
            result.append(next(generator))

        try:
            with scripted_runtime_modules(submit=submit, await_arrival=await_arrival):
                worker = threading.Thread(target=advance)
                worker.start()
                self.assertTrue(posted.wait(1.0))
                self.assertTrue(worker.is_alive(), "close side-effect budget started early")
                release.set()
                worker.join(1.0)
        finally:
            if previous is None:
                globals_.pop("TestG1StaleGeneration", None)
            else:
                globals_["TestG1StaleGeneration"] = previous

        self.assertFalse(worker.is_alive())
        self.assertEqual(result, [None])

    def test_close_predicate_rejects_wrong_type_and_session(self) -> None:
        session_id = "g1-stale-generation"
        observed = []
        cache = SimpleNamespace(
            session_refs=SimpleNamespace(_session_generations={session_id: 1})
        )

        def complete_private_session(_context, _session_id, _rid):
            if False:
                yield
            return cache, 1, (21,)

        def await_arrival(_context, *, predicate, **_kwargs) -> None:
            observed.append(predicate(SimpleNamespace(session_id=session_id)))
            observed.append(
                predicate(FakeCloseSessionReqInput(session_id="other-session"))
            )
            actual_session_id = equal_but_distinct(session_id)
            observed.append(
                predicate(FakeCloseSessionReqInput(session_id=actual_session_id))
            )

        owner = SimpleNamespace(_complete_private_session=complete_private_session)
        globals_ = self.stale_script.__globals__
        previous = globals_.get("TestG1StaleGeneration")
        globals_["TestG1StaleGeneration"] = owner
        try:
            with scripted_runtime_modules(
                submit=lambda *_args, **_kwargs: None,
                await_arrival=await_arrival,
            ):
                generator = self.stale_script(SimpleNamespace())
                self.assertIsNone(next(generator))
        finally:
            if previous is None:
                globals_.pop("TestG1StaleGeneration", None)
            else:
                globals_["TestG1StaleGeneration"] = previous

        self.assertEqual(observed, [False, False, True])

    def test_close_arrival_timeout_propagates_before_side_effect_budget(self) -> None:
        session_id = "g1-stale-generation"
        sentinel = TimeoutError("close-admission-timeout")

        class CountingGenerations(dict):
            contains_calls = 0

            def __contains__(self, key) -> bool:
                self.contains_calls += 1
                return super().__contains__(key)

        generations = CountingGenerations({session_id: 1})
        cache = SimpleNamespace(
            session_refs=SimpleNamespace(_session_generations=generations)
        )

        def complete_private_session(_context, _session_id, _rid):
            if False:
                yield
            return cache, 1, (21,)

        def await_arrival(*_args, **_kwargs) -> None:
            raise sentinel

        owner = SimpleNamespace(_complete_private_session=complete_private_session)
        globals_ = self.stale_script.__globals__
        previous = globals_.get("TestG1StaleGeneration")
        globals_["TestG1StaleGeneration"] = owner
        try:
            with scripted_runtime_modules(
                submit=lambda *_args, **_kwargs: None,
                await_arrival=await_arrival,
            ):
                generator = self.stale_script(SimpleNamespace())
                with self.assertRaises(TimeoutError) as caught:
                    next(generator)
        finally:
            if previous is None:
                globals_.pop("TestG1StaleGeneration", None)
            else:
                globals_["TestG1StaleGeneration"] = previous

        self.assertIs(caught.exception, sentinel)
        self.assertEqual(generations.contains_calls, 0)

    def test_completion_steps_begin_after_arrival_and_reach_frontier(self) -> None:
        context = SimpleNamespace(admitted=False, scheduler_steps=0)
        sentinel = (object(), 7, (21,))

        def await_arrival(_context, **_kwargs) -> None:
            self.assertEqual(_context.scheduler_steps, 0)
            _context.admitted = True

        def settled_frontier(_context, _session_id):
            yield
            return sentinel

        globals_ = self.complete_session.__globals__
        old_request = globals_.get("_session_request")
        old_frontier = globals_.get("_wait_for_settled_private_frontier")
        globals_["_session_request"] = self.session_request
        globals_["_wait_for_settled_private_frontier"] = settled_frontier
        try:
            with scripted_runtime_modules(
                submit=lambda *_args, **_kwargs: None,
                await_arrival=await_arrival,
            ):
                generator = self.complete_session(context, "session", "rid")
                self.assertIsNone(next(generator))
                context.scheduler_steps = 1
                self.assertIsNone(next(generator))
                context.scheduler_steps = 2
                self.assertIsNone(next(generator))
                with self.assertRaises(StopIteration) as finished:
                    next(generator)
        finally:
            if old_request is None:
                globals_.pop("_session_request", None)
            else:
                globals_["_session_request"] = old_request
            if old_frontier is None:
                globals_.pop("_wait_for_settled_private_frontier", None)
            else:
                globals_["_wait_for_settled_private_frontier"] = old_frontier

        self.assertEqual(finished.exception.value, sentinel)
        self.assertTrue(context.admitted)

    def test_source_forbids_fire_and_forget_submission_anywhere(self) -> None:
        self.assertIn("_http_post_and_await_recv_msg", self.source)
        self.assertNotIn("_submit_post", self.source)


if __name__ == "__main__":
    unittest.main()
