#!/usr/bin/env python3
"""Build chuanxilu-jing.json from yangming-jing.json (传习录 only, no 大学问)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets/data/yangming-jing.json"
OUT = ROOT / "assets/data/chuanxilu-jing.json"


def main() -> None:
    entries = json.loads(SRC.read_text(encoding="utf-8"))
    chuanxilu = [e for e in entries if e["volume"] != "大学问"]
    if len(chuanxilu) != 254:
        raise SystemExit(f"expected 254 传习录 entries, got {len(chuanxilu)}")
    OUT.write_text(json.dumps(chuanxilu, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT} ({len(chuanxilu)} entries)")


if __name__ == "__main__":
    main()
