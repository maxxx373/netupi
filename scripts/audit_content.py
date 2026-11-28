#!/usr/bin/env python3
"""Содержательный аудит карточек: объём, специфика для россиян, непереведённый текст, свежесть.
Запуск: python3 scripts/audit_content.py [--md data/AUDIT.md]
"""
import json, re, sys, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
LAT = re.compile(r'[A-Za-z]')
CYR = re.compile(r'[А-Яа-яЁё]')

def eng_share(s):
    l = len(LAT.findall(s)); c = len(CYR.findall(s))
    return l / max(1, l + c)

def walk_strings(o, path=''):
    if isinstance(o, str): yield path, o
    elif isinstance(o, dict):
        for k, v in o.items():
            if k in ('url', 'website', 'admissions_url', 'intl_students_url', 'sources', 'photos', 'name', 'id', 'extra_links', 'source'): continue
            yield from walk_strings(v, path + '.' + k)
    elif isinstance(o, list):
        for v in o: yield from walk_strings(v, path)

rows = []
for f in sorted((ROOT / 'data/institutions').rglob('*.json')):
    r = json.loads(f.read_text())
    ab = r['country'] != 'RU'
    col = r.get('type') == 'college'
    req = r.get('requirements', {}) or {}
    progs = r.get('programs', []) or []
    visa = r.get('visa', {}) or {}
    issues = []
    # volume
    if len(progs) < 3: issues.append(f'программ {len(progs)}')
    np = sum(1 for p in progs if p.get('tuition')); ns = sum(1 for p in progs if p.get('passing_score'))
    if progs and np < len(progs) / 2: issues.append(f'цена у {np}/{len(progs)} программ')
    if progs and ns < len(progs) / 2: issues.append(f'балл у {ns}/{len(progs)} программ')
    if len(r.get('summary', '')) < 200: issues.append('короткое summary')
    if len(r.get('highlights', [])) < 3: issues.append('highlights<3')
    if len(req.get('documents', [])) < 4: issues.append(f'документов {len(req.get("documents", []))}')
    if len(r.get('deadlines', [])) < 2: issues.append(f'сроков {len(r.get("deadlines", []))}')
    if not (r.get('cost', {}) or {}).get('tuition_min'): issues.append('нет цены')
    if not (r.get('cost', {}) or {}).get('living_month_estimate'): issues.append('нет расходов на жизнь')
    if not r.get('funding'): issues.append('нет funding')
    d = r.get('dorm') or {}
    if not d: issues.append('нет dorm')
    elif d.get('available') and not d.get('cost_month'): issues.append('dorm без цены')
    if not r.get('rankings') and not col: issues.append('нет рейтингов')
    if not r.get('photos'): issues.append('нет фото')
    if len(r.get('sources', [])) < 4: issues.append(f'источников {len(r.get("sources", []))}')
    if r['name'].get('ru') == r['name'].get('en'): issues.append('нет русского названия')
    for k in ('city_size', 'ownership', 'founded'):
        if not r.get(k): issues.append('нет ' + k)
    prep = r.get('prep') or {}
    if not prep.get('must'): issues.append('нет prep.must')
    # Russia-specific
    alltext = json.dumps(r, ensure_ascii=False).lower()
    if ab:
        if 'needed_for_ru' not in visa: issues.append('виза: needed_for_ru не указан')
        vn = visa.get('notes', '')
        if len(vn) < 250: issues.append(f'виза: короткий текст ({len(vn)} симв.)')
        if not re.search(r'росси', vn.lower()): issues.append('виза: нет специфики для россиян')
        if not visa.get('url'): issues.append('виза: нет ссылки')
        rq = json.dumps(req, ensure_ascii=False).lower()
        if not re.search(r'аттестат|российск\w+ школ|11 класс|foundation|подготовительн|первого курса|1 курс', rq):
            issues.append('нет про признание российского аттестата')
        if not req.get('intl_exams') and not req.get('language_level'): issues.append('нет языковых требований')
        if not re.search(r'санкц|swift|перевод денег|оплат\w+ из росс|банк', alltext):
            issues.append('нет про оплату/банки из РФ')
    else:
        if not col:
            if not any(p.get('ege_subjects') for p in progs): issues.append('нет предметов ЕГЭ')
            if not req.get('olympiad_benefits'): issues.append('нет олимпиад/БВИ')
            if not req.get('ege_min_per_subject'): issues.append('нет мин. баллов ЕГЭ')
        else:
            if not re.search(r'средн\w+ балл|аттестат', alltext): issues.append('нет про средний балл аттестата')
    # language quality
    eng = [(p, s) for p, s in walk_strings(r) if len(s) > 40 and eng_share(s) > 0.6]
    if eng: issues.append(f'англ. текст без перевода: {len(eng)} полей')
    # freshness
    if (r.get('data_year') or 0) < 2025: issues.append(f'data_year={r.get("data_year")}')
    yrs = [p['passing_score'].get('year') for p in progs if p.get('passing_score') and p['passing_score'].get('year')]
    if yrs and max(yrs) < 2025: issues.append(f'баллы за {max(yrs)}')
    todo = r.get('todo', [])
    rows.append(dict(id=r['id'], ab=ab, col=col, conf=r.get('confidence'), name=r['name']['ru'], country=r['country'],
                     size=len(json.dumps(r, ensure_ascii=False)), n_issues=len(issues), issues=issues, todo=todo,
                     verified=r.get('verified_at')))
rows.sort(key=lambda x: (-x['n_issues'], x['size']))
for x in rows:
    print(f"{x['n_issues']:2d} {x['size']:6d} {x['conf']:6} {'COL' if x['col'] else ('ABR' if x['ab'] else 'RU ')} {x['id']:18} {x['name'][:30]:30} | {'; '.join(x['issues'])}")
c = collections.Counter(i.split(':')[0] if i.startswith('виза') else re.sub(r'\d+', 'N', i) for x in rows for i in x['issues'])
print(); [print(f'{v:3d}  {k}') for k, v in c.most_common()]

if '--md' in sys.argv:
    out = Path(sys.argv[sys.argv.index('--md') + 1])
    tiers = [('Слабые — нужна серьёзная доработка', 9, 99), ('Средние — заметные пробелы', 5, 8),
             ('Почти готовы — точечные правки', 3, 4), ('Готовы — 0–2 замечания', 0, 2)]
    L = ['# Аудит наполнения базы', '', 'Сгенерировано `scripts/audit_content.py`. Число — количество замечаний.', '']
    for title, lo, hi in tiers:
        g = sorted([x for x in rows if lo <= x['n_issues'] <= hi], key=lambda x: -x['n_issues'])
        L += [f'## {title} ({len(g)})', '', '| # | id | Заведение | Страна | confidence | Что не так |', '|---|---|---|---|---|---|']
        L += [f"| {x['n_issues']} | {x['id']} | {x['name']} | {x['country']} | {x['conf']} | {'; '.join(x['issues'])} |" for x in g]
        L.append('')
    out.write_text('\n'.join(L))
