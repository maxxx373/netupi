#!/usr/bin/env python3
"""Полнота карточек по чек-листу data/FILLING.md. Запуск: python3 scripts/completeness.py"""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
rows=[]
for f in sorted((ROOT/'data/institutions').rglob('*.json')):
    r=json.loads(f.read_text())
    abroad='abroad' in f.parts
    college=r.get('type')=='college'
    progs=r.get('programs',[])
    req=r.get('requirements',{})
    checks={
     'ru_name': bool(r.get('name',{}).get('ru')) and r['name']['ru']!=r['name'].get('en'),
     'basics': all(r.get(k) for k in ['city_size','ownership','founded']),
     'summary': bool(r.get('summary')),
     'highlights': len(r.get('highlights',[]))>=3,
     'programs3': len(progs)>=3,
     'prog_price': sum(1 for p in progs if p.get('tuition'))>=2,
     'prog_score': sum(1 for p in progs if p.get('passing_score'))>=2,
     'cost': bool(r.get('cost',{}).get('tuition_min')),
     'living': bool(r.get('cost',{}).get('living_month_estimate')),
     'funding': bool(r.get('funding')),
     'requirements': len(req)>=4,
     'documents': bool(req.get('documents')),
     'deadlines': bool(r.get('deadlines')),
     'dorm': bool(r.get('dorm')),
     'rankings': bool(r.get('rankings')) or college,
     'perks': bool(r.get('perks')),
     'prep': bool(r.get('prep')),
     'photo': bool(r.get('photos')),
     'sources3': len(r.get('sources',[]))>=3,
    }
    if abroad: checks['visa']=bool(r.get('visa',{}).get('notes'))
    miss=[k for k,v in checks.items() if not v]
    score=round(100*(1-len(miss)/len(checks)))
    rows.append((score,'abroad' if abroad else 'ru',r['id'],r.get('type'),r.get('confidence'),r['name']['ru'],r.get('country'),len(r.get('todo',[])),miss))
rows.sort()
if '--json' in sys.argv: print(json.dumps(rows,ensure_ascii=False)); sys.exit()
for s in rows: print(f"{s[0]:3d} {s[1]:6} {s[2]:20} {s[3]:10} {s[4]:6} todo={s[7]} {s[6]} | {s[5][:40]} | miss: {','.join(s[8])}")
import collections
print(collections.Counter(r[4] for r in rows))
print('full(>=90):',sum(r[0]>=90 for r in rows),' mid(50-89):',sum(50<=r[0]<90 for r in rows),' low(<50):',sum(r[0]<50 for r in rows))
