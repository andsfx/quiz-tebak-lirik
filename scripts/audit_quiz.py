#!/usr/bin/env python3
import json, re, sys
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'songs.json'
data=json.load(open(p))
errs=[]; warn=[]; flat=[]
for gi,g in enumerate(data.get('groups',[]),1):
    songs=g.get('songs',[])
    if len(songs)!=5: errs.append(f'Group {gi} has {len(songs)} songs, expected 5')
    for si,s in enumerate(songs,1):
        name=f'G{gi}S{si} {s.get("title")}'
        flat.append(s)
        for k in ['title','artist','year','bait','answer','lyricsSource','verification','file','audioSource','timestamp']:
            if k not in s: errs.append(f'{name}: missing {k}')
        if s.get('audioSource')!='local': errs.append(f'{name}: audioSource not local')
        file=s.get('file') or ''
        expected_prefix=f'audio/grup{gi}-{si:02d}-'
        if not file.startswith(expected_prefix) or not file.endswith('.mp3'):
            errs.append(f'{name}: invalid local file path {file!r}, expected {expected_prefix}*.mp3')
        if s.get('verification')!='verified': warn.append(f'{name}: lyrics not verified ({s.get("verification")})')
        txt=' '.join([s.get('bait',''),s.get('answer','')]).lower()
        for bad in ['ferguso','cookie','privacy','toggle navigation','outdated browser','back to top','lirik lagu terbaru']:
            if bad in txt: errs.append(f'{name}: bad lyric/chrome text contains {bad}')
        t=s.get('timestamp') or {}
        if t.get('start') is None or t.get('end') is None:
            warn.append(f'{name}: timestamp start/end not marked yet')
        elif float(t.get('end',0))<=float(t.get('start',0)):
            errs.append(f'{name}: invalid timestamp start/end')
        if len(s.get('bait','').splitlines())<1 or len(s.get('answer','').splitlines())<1:
            errs.append(f'{name}: empty bait/answer')
print(f'TOTAL={len(flat)} ERRORS={len(errs)} WARNINGS={len(warn)}')
for e in errs: print('ERROR:',e)
for w in warn[:60]: print('WARN:',w)
sys.exit(1 if errs else 0)
