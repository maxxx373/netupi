#!/usr/bin/env python3
"""Собирает каталог для прототипа (codex-prototype/institutions.js) из базы data/institutions.

База — единственный источник данных. Файлы каталога прототипа не правим руками,
а пересобираем этой командой:

    python3 scripts/export_prototype.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "codex-prototype"

COUNTRY_RU = {
    "US": "США", "CA": "Канада", "GB": "Великобритания", "NL": "Нидерланды", "CH": "Швейцария",
    "FR": "Франция", "IT": "Италия", "SE": "Швеция", "DK": "Дания", "SG": "Сингапур",
    "HK": "Гонконг", "JP": "Япония", "KR": "Южная Корея", "CN": "Китай", "IN": "Индия",
    "MY": "Малайзия", "ID": "Индонезия", "AU": "Австралия", "NZ": "Новая Зеландия",
    "BR": "Бразилия", "MX": "Мексика", "AR": "Аргентина", "CL": "Чили", "ZA": "ЮАР",
    "EG": "Египет", "IL": "Израиль", "QA": "Катар", "SA": "Саудовская Аравия", "KE": "Кения",
    "DE": "Германия", "CZ": "Чехия", "TR": "Турция",
}
FIELD_TO_AREA = {
    "natural_sciences": "science", "linguistics": "languages", "design_art": "design",
    "international_relations": "international", "it": "it", "engineering": "engineering",
    "medicine": "medicine", "law": "law", "economics": "economics", "media": "media",
    "pedagogy": "pedagogy", "psychology": "psychology", "business": "business",
    "architecture": "architecture", "agriculture": "agriculture",
}


def art_for(rec):
    f = set(rec.get("fields", []))
    if f & {"it", "engineering"}:
        return "tech"
    if "natural_sciences" in f:
        return "science"
    return "classic"


def to_card(rec):
    areas = rec.get("areas") or list(dict.fromkeys(
        FIELD_TO_AREA[f] for f in rec.get("fields", []) if f in FIELD_TO_AREA))
    card = {
        "id": rec["id"],
        "name": rec["name"]["ru"],
        "city": rec["city"],
        "kind": "college" if rec["type"] == "college" else "uni",
        "areas": areas,
        "about": rec.get("about") or rec.get("summary", ""),
        "site": rec["website"],
        "admission": rec.get("admissions_url", rec["website"]),
        "art": rec.get("art") or art_for(rec),
    }
    if rec["country"] != "RU":
        card["country"] = COUNTRY_RU.get(rec["country"], rec["country"])
    if rec.get("prep"):
        card["prep"] = rec["prep"]
    return card


recs = [json.loads(p.read_text(encoding="utf-8"))
        for p in sorted((ROOT / "data/institutions").rglob("*.json"))]
recs.sort(key=lambda r: (r["country"] != "RU", r["type"] == "college", r["id"]))
cards = [to_card(r) for r in recs]

body = ",\n".join("  " + json.dumps(c, ensure_ascii=False) for c in cards)
(OUT / "institutions.js").write_text(
    "/* Сгенерировано из data/institutions командой scripts/export_prototype.py. Не править руками. */\n"
    f"const INSTITUTIONS = [\n{body}\n];\n", encoding="utf-8")
(OUT / "institutions-global.js").write_text(
    "/* Все заведения теперь в institutions.js (собирается из базы). Файл оставлен для совместимости. */\n"
    "const GLOBAL_INSTITUTIONS = [];\nINSTITUTIONS.push(...GLOBAL_INSTITUTIONS);\n", encoding="utf-8")
print(f"Каталог прототипа: {len(cards)} заведений")
