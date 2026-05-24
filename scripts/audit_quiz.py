#!/usr/bin/env python3
import json, re, sys
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'songs.json'
data=json.load(open(p))
errs=[]
warn=[]
flat=[]
for gi,g in enumerate(data.get('groups',[]),1):
    songs=g.get('songs',[])
    if len(songs)!=5: errs.append(f'Group {gi} has {len(songs)} songs, expected 5')
    for si,s in enumerate(songs,1):
        name=f'G{gi}S{si} {s.get("title")}'
        flat.append(s)
        for k in ['title','artist','year','bait','answer','lyricsSource','verification','youtube','syncStatus']:
            if k not in s: errs.append(f'{name}: missing {k}')
        if s.get('file') not in ('', None): errs.append(f'{name}: file must be empty for YouTube mode')
        if s.get('audioSource')!='youtube': errs.append(f'{name}: audioSource not youtube')
        if s.get('verification')!='verified': warn.append(f'{name}: lyrics not verified ({s.get("verification")})')
        if s.get('syncStatus')!='synced': warn.append(f'{name}: timestamp not marked synced ({s.get("syncStatus")})')
        txt=' '.join([s.get('bait',''),s.get('answer','')]).lower()
        for bad in ['ferguso','cookie','privacy','toggle navigation','outdated browser','back to top','lirik lagu terbaru']:
            if bad in txt: errs.append(f'{name}: bad lyric/chrome text contains {bad}')
        y=s.get('youtube') or {}
        if not y.get('id'): errs.append(f'{name}: missing YouTube id')
        if y.get('start') is None or y.get('end') is None or float(y.get('end',0))<=float(y.get('start',0)):
            errs.append(f'{name}: invalid youtube start/end')
        if len(s.get('bait','').splitlines())<1 or len(s.get('answer','').splitlines())<1:
            errs.append(f'{name}: empty bait/answer')
print(f'TOTAL={len(flat)} ERRORS={len(errs)} WARNINGS={len(warn)}')
for e in errs: print('ERROR:',e)
for w in warn[:40]: print('WARN:',w)
sys.exit(1 if errs else 0)
