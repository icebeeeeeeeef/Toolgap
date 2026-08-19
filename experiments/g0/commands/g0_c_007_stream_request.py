#!/usr/bin/env python3
"""Send and retain one bounded native SGLang streaming /generate request."""

from __future__ import annotations

import argparse
import http.client
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit


def write_json(path: Path, document: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--request-json", required=True, type=Path)
    parser.add_argument("--raw-output", required=True, type=Path)
    parser.add_argument("--parsed-output", required=True, type=Path)
    parser.add_argument("--connect-timeout", type=float, default=10.0)
    parser.add_argument("--terminal-timeout", type=float, default=180.0)
    args = parser.parse_args()

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
        "target": target,
        "http_status": None,
        "saw_json_with_text_and_meta_info": False,
        "saw_done": False,
        "parse_error": None,
        "error": None,
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
            headers={
                "Accept": "text/event-stream",
                "Content-Type": "application/json",
            },
        )
        response = connection.getresponse()
        state["http_status"] = response.status
        if response.status != 200:
            state["error"] = f"expected HTTP 200, got {response.status}"
        else:
            while True:
                elapsed = time.monotonic() - start
                remaining = args.terminal_timeout - elapsed
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
                if isinstance(event, dict) and {
                    "text",
                    "meta_info",
                }.issubset(event):
                    state["saw_json_with_text_and_meta_info"] = True
    except Exception as error:  # preserves a concrete failure artifact
        state["error"] = f"{type(error).__name__}: {error}"
    finally:
        if connection is not None:
            connection.close()
        args.raw_output.parent.mkdir(parents=True, exist_ok=True)
        args.raw_output.write_bytes(bytes(raw))

    state["elapsed_seconds"] = time.monotonic() - start
    state["event_count"] = len(events)
    state["passed"] = bool(
        state["http_status"] == 200
        and state["saw_json_with_text_and_meta_info"]
        and state["saw_done"]
        and state["parse_error"] is None
        and state["error"] is None
    )
    state["events"] = events
    write_json(args.parsed_output, state)
    return 0 if state["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
