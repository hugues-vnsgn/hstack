#!/usr/bin/env python3
"""Install a pilot APK and retain UI evidence for the shipping threshold cases."""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

PACKAGE = "com.hstack.gatef.pilot"


class Pilot:
    def __init__(self, serial, evidence):
        self.serial = serial
        self.evidence = evidence
        self.remote_xml = f"/sdcard/gate-f-{uuid.uuid4().hex}.xml"
        self.last_xml = b""

    def adb(self, *args, timeout=30):
        result = subprocess.run(
            ["adb", "-s", self.serial, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                f"adb {' '.join(args)} failed: "
                f"{result.stderr.decode(errors='replace')}"
                f"{result.stdout.decode(errors='replace')}"
            )
        return result.stdout

    def dump(self, deadline):
        def remaining():
            seconds = deadline - time.monotonic()
            if seconds <= 0:
                raise TimeoutError("UI readiness deadline expired")
            return seconds

        self.adb("shell", "uiautomator", "dump", self.remote_xml,
                 timeout=remaining())
        self.last_xml = self.adb("exec-out", "cat", self.remote_xml,
                                 timeout=remaining())
        return ET.fromstring(self.last_xml)

    @staticmethod
    def control(root, name):
        resource_id = f"{PACKAGE}:id/{name}"
        for node in root.iter("node"):
            if node.get("resource-id") == resource_id:
                return node
        return None

    def wait_control(self, name, text=None):
        deadline = time.monotonic() + 10
        last_error = "control absent"
        while time.monotonic() < deadline:
            try:
                node = self.control(self.dump(deadline), name)
                if node is not None:
                    observed = node.get("text", "")
                    if text is None or observed == text:
                        return node
                    last_error = f"expected {text!r}, observed {observed!r}"
            except (ET.ParseError, subprocess.TimeoutExpired, TimeoutError) as error:
                last_error = str(error)
            remaining = deadline - time.monotonic()
            if remaining > 0:
                time.sleep(min(0.2, remaining))
        raise RuntimeError(f"{name} was not ready within 10 seconds: {last_error}")

    def tap(self, node):
        match = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]",
                             node.get("bounds", ""))
        if not match:
            raise RuntimeError("Control has invalid bounds")
        left, top, right, bottom = map(int, match.groups())
        if right <= left or bottom <= top:
            raise RuntimeError("Control has no visible area")
        self.adb("shell", "input", "tap", str((left + right) // 2),
                 str((top + bottom) // 2))

    def capture(self, subtotal):
        prefix = self.evidence / f"subtotal-{subtotal}"
        prefix.with_suffix(".xml").write_bytes(self.last_xml)
        png = self.adb("exec-out", "screencap", "-p")
        if not png.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError("Device screenshot was not PNG")
        prefix.with_suffix(".png").write_bytes(png)

    def check_subtotal(self, subtotal, expected):
        field = self.wait_control("subtotal_input")
        self.tap(field)
        self.adb("shell", "input", "keyevent", "KEYCODE_MOVE_END")
        # Delete the observed field text; deleting hint length is harmless.
        count = max(1, len(field.get("text", "")))
        self.adb("shell", "input", "keyevent", *(["KEYCODE_DEL"] * count))
        self.adb("shell", "input", "text", str(subtotal))
        self.wait_control("subtotal_input", str(subtotal))
        keyboard = self.adb("shell", "dumpsys", "input_method").decode(
            errors="replace")
        if re.search(r"(?:mInputShown|mIsInputViewShown|isInputViewShown)=true\b",
                     keyboard):
            self.adb("shell", "input", "keyevent", "KEYCODE_BACK")
        self.tap(self.wait_control("calculate_button"))
        try:
            self.wait_control("shipping_result", expected)
        finally:
            self.capture(subtotal)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--apk", required=True, type=Path)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    args = parser.parse_args()
    apk = args.apk.resolve(strict=True)
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    if any(args.evidence_dir.iterdir()):
        parser.error("--evidence-dir must be empty to preserve earlier evidence")
    pilot = Pilot(args.serial, args.evidence_dir)
    report = {
        "serial": args.serial,
        "apk": str(apk),
        "apk_sha256": hashlib.sha256(apk.read_bytes()).hexdigest(),
        "cases": [],
        "passed": False,
    }
    try:
        properties = pilot.adb("shell", "getprop")
        (args.evidence_dir / "device-properties.txt").write_bytes(properties)
        install = pilot.adb("install", "-r", str(apk), timeout=120)
        (args.evidence_dir / "install.txt").write_bytes(install)
        launch = pilot.adb("shell", "am", "start", "-W", "-n",
                           f"{PACKAGE}/.MainActivity")
        (args.evidence_dir / "launch.txt").write_bytes(launch)
        for subtotal, expected_fee in ((4999, 500), (5000, 0), (5001, 0)):
            case = {"subtotal_cents": subtotal, "expected_shipping_cents": expected_fee,
                    "passed": False}
            report["cases"].append(case)
            pilot.check_subtotal(subtotal, f"Shipping: {expected_fee} cents")
            case["passed"] = True
        report["passed"] = True
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        report["error"] = str(error)
        print(f"FAIL: {error}", file=sys.stderr)
    finally:
        (args.evidence_dir / "result.json").write_text(
            json.dumps(report, indent=2) + "\n")
        try:
            pilot.adb("shell", "rm", "-f", pilot.remote_xml, timeout=10)
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            pass
    if report["passed"]:
        print(f"PASS: three Android UI cases; evidence: {args.evidence_dir}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
