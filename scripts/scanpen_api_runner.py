#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ScanPen serial API validator and pressure-test runner.

This script drives the AP serial shell with commands from scanInfo.json and
uses AP/CP log regexes to determine whether version, translation, and TTS APIs
are still usable.
"""

from __future__ import annotations

import argparse
import base64
import csv
import datetime as dt
import json
import re
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

try:
    import serial
    import serial.tools.list_ports
except ImportError as exc:  # pragma: no cover - exercised on machines without pyserial
    print("ERROR: pyserial is required. Install it with: python -m pip install pyserial", file=sys.stderr)
    raise SystemExit(3) from exc

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = SKILL_DIR / "assets" / "configs" / "default_scanInfo.json"
DEFAULT_ZH_CORPUS = SKILL_DIR / "assets" / "corpus" / "zhxs.txt"
DEFAULT_EN_CORPUS = SKILL_DIR / "assets" / "corpus" / "xwz.txt"
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
FIELDNAMES = [
    "timestamp",
    "iteration",
    "operation",
    "text",
    "ok",
    "fw_version",
    "return_ok",
    "trans_result",
    "tts_end",
    "trans_init_ms",
    "trans_cost_ms",
    "trans_total_ms",
    "tts_init_ms",
    "tts_cost_ms",
    "tts_speed",
    "error",
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as fp:
        return json.load(fp)


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text).replace("\r", "\n")


def clean_text_for_cmd(text: str) -> str:
    return text.replace("\r", " ").replace("\n", " ").replace('"', "'").strip()


def trim_utf8_bytes(text: str, max_bytes: int) -> str:
    if max_bytes <= 0:
        return text
    out: List[str] = []
    total = 0
    for ch in text:
        size = len(ch.encode("utf-8"))
        if total + size > max_bytes:
            break
        out.append(ch)
        total += size
    return "".join(out).strip()


def load_corpus(kind: str, explicit_file: Optional[Path]) -> str:
    if explicit_file:
        path = explicit_file
    elif kind == "english":
        path = DEFAULT_EN_CORPUS
    else:
        path = DEFAULT_ZH_CORPUS
    return path.read_text(encoding="utf-8-sig", errors="ignore")


def snippet_from_corpus(corpus: str, iteration: int, max_bytes: int) -> str:
    compact = re.sub(r"\s+", " ", corpus).strip()
    if not compact:
        return "你好"
    if len(compact) <= 2:
        return compact
    start = (iteration * max(1, max_bytes // 2)) % max(1, len(compact) - 1)
    candidate = compact[start : start + max(8, max_bytes * 2)]
    trimmed = trim_utf8_bytes(candidate, max_bytes)
    return trimmed or compact[:1]


def now_text() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def make_result_dir(base: Path, label: str) -> Path:
    tag = dt.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    safe_label = re.sub(r"[^A-Za-z0-9_.\-\u4e00-\u9fff]+", "_", label).strip("_") or "scanpen"
    path = base / f"{tag}-{safe_label}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def list_ports() -> None:
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return
    print(f"Found {len(ports)} serial ports:")
    for port in ports:
        print(f"- {port.device}\t{port.description}\t{port.hwid}")


@dataclass
class DeviceConfig:
    name: str
    port: str
    baud: int
    regex: Dict[str, str]


class SerialCapture:
    def __init__(self, config: DeviceConfig, read_timeout: float = 0.05):
        self.config = config
        self.read_timeout = read_timeout
        self.ser: Optional[serial.Serial] = None
        self._parts: List[str] = []
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def open(self) -> None:
        self.ser = serial.Serial(self.config.port, self.config.baud, timeout=self.read_timeout)
        self._thread = threading.Thread(target=self._reader, name=f"read-{self.config.name}", daemon=True)
        self._thread.start()

    def _reader(self) -> None:
        assert self.ser is not None
        while not self._stop.is_set():
            try:
                data = self.ser.read(self.ser.in_waiting or 1)
                if not data:
                    continue
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    text = data.decode("utf-8", errors="replace")
                with self._lock:
                    self._parts.append(text)
            except Exception as exc:
                with self._lock:
                    self._parts.append(f"\n[READ_ERROR:{exc}]\n")
                break

    def close(self) -> None:
        self._stop.set()
        time.sleep(0.1)
        if self.ser is not None and self.ser.is_open:
            self.ser.close()

    def mark(self) -> int:
        with self._lock:
            return len(self._parts)

    def snapshot(self, mark: int = 0) -> str:
        with self._lock:
            return strip_ansi("".join(self._parts[mark:]))

    def full_log(self) -> str:
        return self.snapshot(0)

    def send(self, cmd: str, chunk_size: int = 32, chunk_delay: float = 0.01) -> None:
        if self.ser is None or not self.ser.is_open:
            raise RuntimeError(f"Serial port is not open: {self.config.port}")
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        payload = (cmd + "\r\n").encode("utf-8")
        if chunk_size <= 0:
            self.ser.write(payload)
            return
        for idx in range(0, len(payload), chunk_size):
            self.ser.write(payload[idx : idx + chunk_size])
            if chunk_delay > 0:
                time.sleep(chunk_delay)


def build_device_configs(config: dict, args: argparse.Namespace) -> Tuple[DeviceConfig, DeviceConfig]:
    devices = config.get("deviceListInfo", {})
    ap_info = dict(devices.get("cskApLog", {}))
    cp_info = dict(devices.get("cskCpLog", {}))
    if not ap_info or not cp_info:
        raise ValueError("config.deviceListInfo must include cskApLog and cskCpLog")
    if args.ap:
        ap_info["port"] = args.ap
    if args.cp:
        cp_info["port"] = args.cp
    if args.baud:
        ap_info["baudRate"] = args.baud
        cp_info["baudRate"] = args.baud
    return (
        DeviceConfig("cskApLog", str(ap_info["port"]), int(ap_info.get("baudRate", 115200)), ap_info.get("regex", {})),
        DeviceConfig("cskCpLog", str(cp_info["port"]), int(cp_info.get("baudRate", 115200)), cp_info.get("regex", {})),
    )


def wait_regex(capture: SerialCapture, key: str, timeout: float, mark: int = 0) -> Tuple[bool, Optional[str]]:
    pattern = capture.config.regex.get(key)
    if not pattern:
        return False, None
    compiled = re.compile(pattern)
    deadline = time.time() + timeout
    while time.time() < deadline:
        lines = [line for line in capture.snapshot(mark).split("\n") if line.strip()]
        for line in lines:
            match = compiled.match(line)
            if match:
                return True, match.group(1).strip()
        time.sleep(0.1)
    return False, None


def find_metric(capture: SerialCapture, key: str, mark: int = 0) -> Optional[str]:
    pattern = capture.config.regex.get(key)
    if not pattern:
        return None
    compiled = re.compile(pattern)
    for line in capture.snapshot(mark).split("\n"):
        match = compiled.match(line)
        if match:
            return match.group(1).strip()
    return None


def run_version(ap: SerialCapture, args: argparse.Namespace) -> dict:
    mark = ap.mark()
    ap.send("version", args.chunk_size, args.chunk_delay)
    ok, fw_version = wait_regex(ap, "hearCmdRes", args.timeout, mark)
    return_ok, _ = wait_regex(ap, "returnRes", 1.5, mark) if ok else (False, None)
    return {
        "timestamp": now_text(),
        "iteration": 0,
        "operation": "version",
        "text": "version",
        "ok": ok,
        "fw_version": fw_version,
        "return_ok": return_ok,
        "error": "" if ok else "version timeout or regex mismatch",
    }


def run_translation(ap: SerialCapture, cp: SerialCapture, text: str, iteration: int, args: argparse.Namespace) -> dict:
    text = clean_text_for_cmd(text)
    ap.send(" ", args.chunk_size, args.chunk_delay)
    ap.send(" ", args.chunk_size, args.chunk_delay)
    time.sleep(args.settle)
    ap_mark = ap.mark()
    cp_mark = cp.mark()
    cmd = f'trans_start {args.language} "{text}"'
    ap.send(cmd, args.chunk_size, args.chunk_delay)
    ok, trans_result = wait_regex(ap, "transRes", args.timeout, ap_mark)
    return {
        "timestamp": now_text(),
        "iteration": iteration,
        "operation": "trans",
        "text": text,
        "ok": ok,
        "trans_result": trans_result,
        "trans_init_ms": find_metric(cp, "transInit", cp_mark),
        "trans_cost_ms": find_metric(cp, "transCost", cp_mark),
        "trans_total_ms": find_metric(cp, "transTotal", cp_mark),
        "error": "" if ok else "translation timeout or regex mismatch",
    }


def run_tts(ap: SerialCapture, cp: SerialCapture, text: str, iteration: int, args: argparse.Namespace) -> dict:
    text = clean_text_for_cmd(text)
    ap.send("xtts_stop", args.chunk_size, args.chunk_delay)
    time.sleep(max(args.settle, 0.3))
    ap_mark = ap.mark()
    cp_mark = cp.mark()
    cmd = f'xtts_start {args.role} {args.volume} {args.speed} "{text}"'
    ap.send(cmd, args.chunk_size, args.chunk_delay)
    ok, tts_end = wait_regex(ap, "ttsEnd", args.timeout, ap_mark)
    return {
        "timestamp": now_text(),
        "iteration": iteration,
        "operation": "tts",
        "text": text,
        "ok": ok,
        "tts_end": tts_end,
        "tts_init_ms": find_metric(cp, "ttsInit", cp_mark),
        "tts_cost_ms": find_metric(cp, "ttsCost", cp_mark),
        "tts_speed": find_metric(cp, "ttsSpeed", cp_mark),
        "error": "" if ok else "tts timeout or regex mismatch",
    }


def open_captures(ap_cfg: DeviceConfig, cp_cfg: DeviceConfig, args: argparse.Namespace) -> Tuple[SerialCapture, SerialCapture]:
    ap = SerialCapture(ap_cfg, args.read_timeout)
    cp = SerialCapture(cp_cfg, args.read_timeout)
    ap.open()
    cp.open()
    time.sleep(args.settle)
    return ap, cp


def write_rows(path: Path, rows: Iterable[dict]) -> None:
    exists = path.exists()
    with path.open("a", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        for row in rows:
            normalized = {key: row.get(key, "") for key in FIELDNAMES}
            writer.writerow(normalized)


def save_logs(
    result_dir: Path,
    ap: Optional[SerialCapture],
    cp: Optional[SerialCapture],
    rows: List[dict],
    args: argparse.Namespace,
    write_csv: bool = True,
) -> None:
    result_dir.mkdir(parents=True, exist_ok=True)
    if write_csv:
        write_rows(result_dir / "result.csv", rows)
    summary_lines = [
        f"ScanPen API test summary - {now_text()}",
        f"mode={args.mode}",
        f"config={args.config}",
        f"rows={len(rows)}",
        "",
    ]
    for row in rows:
        summary_lines.append(
            f"[{row.get('operation')}] iter={row.get('iteration')} ok={row.get('ok')} "
            f"text={row.get('text')} error={row.get('error', '')}"
        )
    (result_dir / "summary.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    if ap is not None:
        (result_dir / f"scanPen_{ap.config.name}_{ap.config.port}.log").write_text(ap.full_log(), encoding="utf-8", errors="ignore")
    if cp is not None:
        (result_dir / f"scanPen_{cp.config.name}_{cp.config.port}.log").write_text(cp.full_log(), encoding="utf-8", errors="ignore")


def print_rows(rows: List[dict]) -> None:
    for row in rows:
        details = []
        for key in ("fw_version", "trans_result", "tts_end", "trans_init_ms", "trans_cost_ms", "trans_total_ms", "tts_init_ms", "tts_cost_ms", "tts_speed"):
            if row.get(key) not in (None, ""):
                details.append(f"{key}={row.get(key)}")
        suffix = " " + " ".join(details) if details else ""
        print(f"{row.get('operation')} iter={row.get('iteration')} ok={row.get('ok')}{suffix}")
        if row.get("error"):
            print(f"  error: {row['error']}")


def dry_run(config: dict, ap_cfg: DeviceConfig, cp_cfg: DeviceConfig, args: argparse.Namespace) -> int:
    print("DRY RUN: no serial port will be opened.")
    print(f"projectInfo={config.get('projectInfo')}")
    print(f"AP: {ap_cfg.port} baud={ap_cfg.baud}")
    print(f"CP: {cp_cfg.port} baud={cp_cfg.baud}")
    print("Commands that would be sent:")
    print("- version")
    if not args.no_trans:
        print(f'- trans_start {args.language} "{clean_text_for_cmd(args.text)}"')
    if not args.no_tts:
        print("- xtts_stop")
        print(f'- xtts_start {args.role} {args.volume} {args.speed} "{clean_text_for_cmd(args.text)}"')
    return 0


def run_validate(config: dict, ap_cfg: DeviceConfig, cp_cfg: DeviceConfig, args: argparse.Namespace) -> int:
    if args.dry_run:
        return dry_run(config, ap_cfg, cp_cfg, args)
    result_dir = make_result_dir(args.result_base, args.label)
    rows: List[dict] = []
    ap: Optional[SerialCapture] = None
    cp: Optional[SerialCapture] = None
    exit_code = 0
    try:
        ap, cp = open_captures(ap_cfg, cp_cfg, args)
        rows.append(run_version(ap, args))
        if not args.no_trans:
            rows.append(run_translation(ap, cp, args.text, 1, args))
        if not args.no_tts:
            rows.append(run_tts(ap, cp, args.text, 1, args))
        exit_code = 0 if all(bool(row.get("ok")) for row in rows) else 2
    except Exception as exc:
        rows.append({"timestamp": now_text(), "iteration": -1, "operation": "fatal", "ok": False, "error": repr(exc)})
        exit_code = 2
    finally:
        if ap is not None:
            ap.close()
        if cp is not None:
            cp.close()
        save_logs(result_dir, ap, cp, rows, args)
    print_rows(rows)
    print(f"Result directory: {result_dir}")
    return exit_code


def parse_ops(raw_ops: str) -> List[str]:
    ops = [item.strip().lower() for item in raw_ops.split(",") if item.strip()]
    invalid = [op for op in ops if op not in {"trans", "tts", "version"}]
    if invalid:
        raise ValueError(f"Unsupported ops: {', '.join(invalid)}. Use trans,tts,version")
    return ops or ["trans", "tts"]


def run_stress(config: dict, ap_cfg: DeviceConfig, cp_cfg: DeviceConfig, args: argparse.Namespace) -> int:
    if args.dry_run:
        return dry_run(config, ap_cfg, cp_cfg, args)
    ops = parse_ops(args.ops)
    corpus = load_corpus(args.corpus_kind, args.text_file) if not args.text else ""
    result_dir = make_result_dir(args.result_base, args.label)
    rows: List[dict] = []
    ap: Optional[SerialCapture] = None
    cp: Optional[SerialCapture] = None
    exit_code = 0
    try:
        ap, cp = open_captures(ap_cfg, cp_cfg, args)
        if "version" not in ops:
            rows.append(run_version(ap, args))
        for iteration in range(1, args.count + 1):
            text = args.text or snippet_from_corpus(corpus, iteration, args.text_bytes)
            for op in ops:
                if op == "version":
                    row = run_version(ap, args)
                    row["iteration"] = iteration
                elif op == "trans":
                    row = run_translation(ap, cp, text, iteration, args)
                else:
                    row = run_tts(ap, cp, text, iteration, args)
                rows.append(row)
                write_rows(result_dir / "result.csv", [row])
                print_rows([row])
                if args.stop_on_fail and not row.get("ok"):
                    raise RuntimeError(f"stop_on_fail: {op} failed at iteration {iteration}")
                time.sleep(args.interval)
        exit_code = 0 if all(bool(row.get("ok")) for row in rows) else 2
    except KeyboardInterrupt:
        rows.append({"timestamp": now_text(), "iteration": -1, "operation": "interrupt", "ok": False, "error": "KeyboardInterrupt"})
        exit_code = 130
    except Exception as exc:
        rows.append({"timestamp": now_text(), "iteration": -1, "operation": "fatal", "ok": False, "error": repr(exc)})
        exit_code = 2
    finally:
        if ap is not None:
            ap.close()
        if cp is not None:
            cp.close()
        # result.csv is appended during the run; avoid duplicating rows here.
        save_logs(result_dir, ap, cp, rows, args, write_csv=False)
    print(f"Result directory: {result_dir}")
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and pressure-test ScanPen serial APIs.")
    parser.add_argument("--mode", choices=["list-ports", "validate", "stress"], default="validate")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Path to scanInfo.json-style config")
    parser.add_argument("--ap", default="", help="Override AP serial port, e.g. COM6")
    parser.add_argument("--cp", default="", help="Override CP serial port, e.g. COM3")
    parser.add_argument("--baud", type=int, default=0, help="Override baudRate for AP and CP")
    parser.add_argument("--text", default="你好", help="Text used by validate mode or fixed-text stress")
    parser.add_argument("--text-b64", default="", help="UTF-8 base64 text override; useful for .bat files with Chinese text")
    parser.add_argument("--language", type=int, default=1, help="trans_start language argument: 1=Chinese, 2=English")
    parser.add_argument("--role", type=int, default=1, help="xtts_start role argument")
    parser.add_argument("--volume", type=int, default=50, help="xtts_start volume argument")
    parser.add_argument("--speed", type=int, default=50, help="xtts_start speed argument")
    parser.add_argument("--timeout", type=float, default=20.0, help="Seconds to wait for each regex result")
    parser.add_argument("--read-timeout", type=float, default=0.05, help="pyserial read timeout")
    parser.add_argument("--settle", type=float, default=0.5, help="Delay between setup commands")
    parser.add_argument("--chunk-size", type=int, default=32, help="Serial write chunk size; 0 writes once")
    parser.add_argument("--chunk-delay", type=float, default=0.01, help="Delay between serial write chunks")
    parser.add_argument("--result-base", type=Path, default=Path.cwd() / "result", help="Base directory for result folders")
    parser.add_argument("--label", default="scanpen-api-test", help="Result folder label suffix")
    parser.add_argument("--dry-run", action="store_true", help="Parse config and print commands without opening serial ports")
    parser.add_argument("--no-trans", action="store_true", help="Skip translation check in validate mode")
    parser.add_argument("--no-tts", action="store_true", help="Skip TTS check in validate mode")
    parser.add_argument("--count", type=int, default=20, help="Stress iteration count")
    parser.add_argument("--ops", default="trans,tts", help="Stress operations: trans,tts,version")
    parser.add_argument("--interval", type=float, default=1.0, help="Delay between stress operations")
    parser.add_argument("--text-bytes", type=int, default=40, help="Max UTF-8 bytes per generated stress text")
    parser.add_argument("--corpus-kind", choices=["chinese", "english"], default="chinese")
    parser.add_argument("--text-file", type=Path, default=None, help="Optional corpus file for generated stress text")
    parser.add_argument("--stop-on-fail", action="store_true", help="Stop stress run on first failed operation")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.text_b64:
        args.text = base64.b64decode(args.text_b64).decode("utf-8")
    if args.mode == "list-ports":
        list_ports()
        return 0
    try:
        config = load_json(args.config)
        ap_cfg, cp_cfg = build_device_configs(config, args)
        if args.mode == "validate":
            return run_validate(config, ap_cfg, cp_cfg, args)
        if args.mode == "stress":
            return run_stress(config, ap_cfg, cp_cfg, args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
