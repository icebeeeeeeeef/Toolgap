#!/usr/bin/env python3
"""Send and retain one bounded native SGLang streaming /generate request."""

from __future__ import annotations

import argparse
import http.client
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit


def is_event_stream(value: str | None) -> bool:
    return bool(value and value.split(";", 1)[0].strip().lower() == "text/event-stream")


def write_json_exclusive(path: Path, document: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode=0o444)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
    path.chmod(0o444)


def write_bytes_exclusive(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode=0o444)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(content)
    path.chmod(0o444)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--request-json", required=True, type=Path)
    parser.add_argument("--raw-output", required=True, type=Path)
    parser.add_argument("--parsed-output", required=True, type=Path)
    parser.add_argument("--connect-timeout", type=float, default=10.0)
    parser.add_argument("--terminal-timeout", type=float, default=180.0)
    args = parser.parse_args()

    if args.raw_output.exists() or args.parsed_output.exists():
        raise ValueError("request output paths must not already exist")
    request = json.loads(args.request_json.read_text(encoding="utf-8"))
    if request.get("stream") is not True:
        raise ValueError("G0 request must be streaming")
    parsed_url = urlsplit(args.base_url)
    if parsed_url.scheme != "http" or not parsed_url.hostname:
        raise ValueError(f"expected http base URL, got {args.base_url!r}")
    port = parsed_url.port or 80
    target = parsed_url.path.rstrip("/") + "/generate"
    payload = json.dumps(request).encode("utf-8")
    raw = bytearray()
    events: list[dict[str, object]] = []
    state: dict[str, object] = {
        "base_url": args.base_url,
        "content_type": None,
        "error": None,
        "http_status": None,
        "parse_error": None,
        "saw_done": False,
        "saw_json_with_text_and_meta_info": False,
        "target": target,
    }
    connection: http.client.HTTPConnection | None = None
    start = time.monotonic()
    try:
        connection = http.client.HTTPConnection(
            parsed_url.hostname, port, timeout=args.connect_timeout
        )
        connection.request(
            "POST",
            target,
            body=payload,
            headers={"Accept": "text/event-stream", "Content-Type": "application/json"},
        )
        response = connection.getresponse()
        state["http_status"] = response.status
        state["content_type"] = response.getheader("Content-Type")
        if response.status != 200:
            state["error"] = f"expected HTTP 200, got {response.status}"
        elif not is_event_stream(state["content_type"]):
            state["error"] = f"expected text/event-stream, got {state['content_type']!r}"
        else:
            while True:
                remaining = args.terminal_timeout - (time.monotonic() - start)
                if remaining <= 0:
                    state["error"] = "terminal deadline exceeded"
                    break
                if connection.sock is not None:
                    connection.sock.settimeout(remaining)
                line = response.readline()
                if not line:
                    break
                raw.extend(line)
                if not line.startswith(b"data:"):
                    continue
                data = line[5:].strip()
                if data == b"[DONE]":
                    state["saw_done"] = True
                    break
                try:
                    event = json.loads(data)
                except json.JSONDecodeError as error:
                    state["parse_error"] = str(error)
                    break
                events.append(event)
                if isinstance(event, dict) and {"text", "meta_info"}.issubset(event):
                    state["saw_json_with_text_and_meta_info"] = True
    except Exception as error:  # retain the concrete network/parser failure
        state["error"] = f"{type(error).__name__}: {error}"
    finally:
        if connection is not None:
            connection.close()
        write_bytes_exclusive(args.raw_output, bytes(raw))

    state["elapsed_seconds"] = time.monotonic() - start
    state["event_count"] = len(events)
    state["events"] = events
    state["passed"] = bool(
        state["http_status"] == 200
        and is_event_stream(state["content_type"])
        and state["saw_json_with_text_and_meta_info"]
        and state["saw_done"]
        and state["parse_error"] is None
        and state["error"] is None
    )
    write_json_exclusive(args.parsed_output, state)
    return 0 if state["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
