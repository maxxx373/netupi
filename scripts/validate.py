#!/usr/bin/env python3
"""Проверяет все записи в data/institutions по data/schema.json.

Запуск: python3 scripts/validate.py   (нужен пакет jsonschema)
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
schema = json.loads((ROOT / "data/schema.json").read_text(encoding="utf-8"))
validator = Draft202012Validator(schema, format_checker=FormatChecker())

files = sorted((ROOT / "data/institutions").rglob("*.json"))
errors = 0
ids = {}
for f in files:
    rel = f.relative_to(ROOT)
    try:
        rec = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"✗ {rel}: битый JSON — {e}")
        errors += 1
        continue
    problems = [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in validator.iter_errors(rec)]
    if rec.get("id") and f.stem != rec["id"]:
        problems.append(f"имя файла должно быть {rec['id']}.json")
    for ph in rec.get("photos", []):
        photo_file = ph.get("file", "")
        if photo_file.startswith(("https://", "http://")):
            continue
        p = ROOT / "data" / photo_file
        if not p.is_file():
            problems.append(f"фото не найдено: {ph.get('file')}")
        elif not (p.read_bytes()[:3] == b"\xff\xd8\xff" or p.read_bytes()[:4] == b"\x89PNG"):
            problems.append(f"фото не похоже на JPEG/PNG (возможно, страница ошибки): {ph.get('file')}")
    if rec.get("id") in ids:
        problems.append(f"id повторяется, уже есть в {ids[rec['id']]}")
    ids[rec.get("id")] = rel
    if problems:
        errors += 1
        print(f"✗ {rel}")
        for p in problems:
            print(f"    {p}")

print(f"\nЗаписей: {len(files)}, с ошибками: {errors}")
sys.exit(1 if errors else 0)
