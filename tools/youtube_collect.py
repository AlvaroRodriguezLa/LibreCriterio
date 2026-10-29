"""Reanudable, local y sin API de pago. Metadatos y subtítulos públicos de YouTube."""
from __future__ import annotations
import argparse, html, json, re, time, hashlib, sys, os, uuid, shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_OUT=ROOT/'knowledge'/'youtube'
VIDEO_ID=re.compile(r'^[A-Za-z0-9_-]{11}$')

def now(): return datetime.now(timezone.utc).isoformat()
def load(path,default=None):
    try: return json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except FileNotFoundError: return default

def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.'+str(os.getpid())+'.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for attempt in range(6):
        try:tmp.replace(path);return
        except PermissionError:
            if attempt==5:raise
            time.sleep(.05*(2**attempt))

def update_row(out,row,fields=None):
    """Actualiza un vídeo sin borrar avances de otros procesos o de la revisión."""
    from filelock import FileLock
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with FileLock(str(out/'catalog.lock'),timeout=30):
        catalog=load(out/'catalog.json',[])
        index=next((i for i,r in enumerate(catalog) if r['id']==row['id']),None)
        previous={} if index is None else catalog[index]
        changes=row if fields is None else {key:row[key] for key in fields if key in row}
        merged={**previous,**changes}
        if fields is None and previous.get('analysisStatus')=='reviewed_transcript' and row.get('analysisStatus')=='pending':
            merged['analysisStatus']=previous['analysisStatus'];merged['analysis']=previous.get('analysis')
        if index is None:catalog.append(merged)
        else:catalog[index]=merged
        save(out/'catalog.json',catalog)
    return catalog

def clock(seconds):
    seconds=max(0,int(seconds));return f'{seconds//3600:02}:{seconds%3600//60:02}:{seconds%60:02}'

def normalize_segments(raw):
    """Conserva números y palabras. Solo quita solapamiento de ventanas automáticas."""
    clean=[]
    for item in raw:
        text=html.unescape(str(item.get('text',''))).replace('\n',' ').strip()
        text=re.sub(r'\s+',' ',text)
        if not text: continue
        start=max(0,float(item.get('start',0)));duration=max(0,float(item.get('duration',0)))
        end=start+duration
        if clean and start<clean[-1]['end']:
            a=clean[-1]['text'].split();b=text.split()
            overlap=0
            for n in range(min(len(a),len(b)),1,-1):
                if a[-n:]==b[:n]:overlap=n;break
            if overlap:
                text=' '.join(b[overlap:])
                if not text: continue
        clean.append({'id':f's{len(clean)+1:05}', 'start':start,'end':end,'text':text,'speaker':None,'attribution':'unreviewed'})
    return clean

def metadata(entry,source):
    vid=entry.get('id')
    if not isinstance(vid,str) or not VIDEO_ID.fullmatch(vid):return None
    channel_id=entry.get('channel_id')
    return {'id':vid,'url':f'https://www.youtube.com/watch?v={vid}','title':entry.get('title'),
        'channel':{'id':channel_id,'name':entry.get('channel') or entry.get('uploader'),'url':entry.get('channel_url')},
        'duration':entry.get('duration'),'availability':entry.get('availability'),
        'metadata':{'status':'verified_from_source','source':source,'retrievedAt':now()},
        'topicsRequested':[],'requestContexts':[],'priority':'normal','transcriptStatus':'pending','analysisStatus':'pending','speakers':[]}

def merge_catalog(entries,seeds,previous=None):
    old={v['id']:v for v in previous or []};catalog={}
    for entry in entries:
        row=metadata(entry,'yt-dlp:playlist')
        if row:
            row={**row,**old.get(row['id'],{})};catalog[row['id']]=row
    for seed in seeds:
        vid=seed['id']
        if not VIDEO_ID.fullmatch(vid):raise ValueError('ID de vídeo inválido')
        row=catalog.setdefault(vid,old.get(vid) or {'id':vid,'url':f'https://www.youtube.com/watch?v={vid}',
            'title':None,'channel':{'id':None,'name':None,'url':None},'duration':None,
            'metadata':{'status':'pending'},'transcriptStatus':'pending','analysisStatus':'pending','speakers':[]})
        row['topicsRequested']=list(dict.fromkeys(row.get('topicsRequested',[])+seed.get('topics',[])))
        row['requestContexts']=list(dict.fromkeys(row.get('requestContexts',[])+seed.get('contexts',[])))
        row['priority']=seed.get('priority','normal')
    return list(catalog.values())

def enable_tls():
    try:
        import truststore
        truststore.inject_into_ssl()
    except ImportError:pass

def youtube_options():
    options={'quiet':True,'skip_download':True,'socket_timeout':25,'retries':1,'extractor_retries':1,
        'http_headers':{'Accept-Language':'es-ES,es;q=0.9,en;q=0.5'},'extractor_args':{'youtube':{'lang':['es']}}}
    bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
    node_path=str(bundled) if bundled.exists() else shutil.which('node')
    if node_path:options['js_runtimes']={'node':{'path':node_path}}
    return options

def inventory(args):
    enable_tls();config=load(args.config);out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    if args.inventory_json:info=load(args.inventory_json)
    else:
        import yt_dlp
        with yt_dlp.YoutubeDL({**youtube_options(),'extract_flat':'in_playlist'}) as y:
            info=y.extract_info(args.playlist or config['playlist'],download=False)
        save(out/'playlist-raw.json',info)
    entries=info.get('entries',[])
    catalog=merge_catalog(entries,config.get('videos',[]),load(out/'catalog.json',[]))
    for i,row in enumerate(catalog,1):row['position']=i
    save(out/'catalog.json',catalog)
    save(out/'playlist.json',{'id':info.get('id'),'title':info.get('title'),'url':config['playlist'],
        'retrievedAt':now(),'playlistVideos':len(entries),'uniqueVideosIncludingSeeds':len(catalog)})
    report(out,catalog)
    print(json.dumps({'playlist':info.get('title'),'playlistVideos':len(entries),'uniqueVideos':len(catalog)},ensure_ascii=False))

def choose_track(tracks):
    available=list(tracks)
    def rank(t):
        lang=t.language_code.split('-')[0]
        return ({'es':0,'en':2}.get(lang,4)+(1 if t.is_generated else 0),t.language_code)
    preferred=sorted(available,key=rank)
    if not preferred:raise ValueError('No hay pistas disponibles')
    # Nunca traducir una pista sin registrar el original.
    return preferred[0]

def store_transcript(out,row,raw,language,generated,method):
    folder=out/'videos'/row['id'];folder.mkdir(parents=True,exist_ok=True)
    save(folder/'metadata.json',row)
    original={'videoId':row['id'],'retrievedAt':now(),'method':method,'language':language,
        'isGenerated':generated,'segments':raw,'speakerNamesVerified':False}
    save(folder/'transcript.original.json',original)
    segments=normalize_segments(raw)
    transcript={'videoId':row['id'],'language':language,'isGenerated':generated,'method':method,
        'sha256Original':hashlib.sha256(json.dumps(raw,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
        'segments':segments,'normalization':'HTML y espacios; deduplicación solo entre ventanas solapadas. Original conservado.',
        'wordCount':sum(len(s['text'].split()) for s in segments),'speakerNamesVerified':False}
    save(folder/'transcript.json',transcript)
    (folder/'transcript.txt').write_text('\n'.join(f"[{s['id']} | {clock(s['start'])}] {s['text']}" for s in segments)+'\n',encoding='utf-8')
    row['transcriptStatus']='downloaded';row['transcript']={'path':f"videos/{row['id']}/transcript.json",
        'language':language,'isGenerated':generated,'method':method,'wordCount':transcript['wordCount'],'segments':len(segments)}
    row['analysisStatus']='pending'
    save(folder/'metadata.json',row)
    return transcript

def fetch(args):
    enable_tls()
    from youtube_transcript_api import YouTubeTranscriptApi
    from requests import Session
    class TimeoutSession(Session):
        def request(self,*a,**kw):kw.setdefault('timeout',25);return super().request(*a,**kw)
    api=YouTubeTranscriptApi(http_client=TimeoutSession())
    out=Path(args.output);catalog=load(out/'catalog.json',[])
    rows=sorted(catalog,key=lambda r:(r.get('priority')!='high',r.get('position',9999)))
    if args.ids:rows=[r for r in rows if r['id'] in args.ids.split(',')]
    processed=0;blocked=False
    for row in rows:
        if row.get('transcriptStatus')=='downloaded' and not args.force:continue
        if row.get('transcriptStatus') not in {'pending','error',None} and not (args.force or args.retry_failed or args.ids):continue
        if args.limit and processed>=args.limit:break
        processed+=1;vid=row['id']
        try:
            track=choose_track(api.list(vid));raw=track.fetch().to_raw_data()
            trans=store_transcript(out,row,raw,track.language_code,track.is_generated,'youtube-transcript-api')
            row.pop('error',None);print(json.dumps({'id':vid,'status':'downloaded','words':trans['wordCount']},ensure_ascii=False),flush=True)
        except Exception as exc:
            name=type(exc).__name__
            blocked=name in {'RequestBlocked','IpBlocked'} or 'captcha' in str(exc).lower()
            row['transcriptStatus']='blocked' if blocked else ('unavailable' if name in {'TranscriptsDisabled','NoTranscriptFound','VideoUnavailable','VideoUnplayable'} else 'error')
            row['error']={'type':name,'message':str(exc)[:700],'at':now()}
            print(json.dumps({'id':vid,'status':row['transcriptStatus'],'error':name},ensure_ascii=False),flush=True)
        catalog=update_row(out,row,['transcriptStatus','transcript','error','metadata','title','channel','duration','description','uploadDate'])
        report(out,catalog)
        if blocked:
            print('Descarga pausada por bloqueo de YouTube; no se usa proxy, CAPTCHA ni credenciales.',flush=True);break
        if args.delay:time.sleep(args.delay)
    report(out,catalog)
    return 2 if blocked else 0

def reconcile(out):
    catalog=load(out/'catalog.json',[]);recovered=0
    for row in catalog:
        folder=Path(out)/'videos'/row['id'];trans=load(folder/'transcript.json');original=load(folder/'transcript.original.json')
        if not trans or not original or not trans.get('segments'):continue
        checksum=hashlib.sha256(json.dumps(original['segments'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        if checksum!=trans.get('sha256Original'):continue
        row['transcriptStatus']='downloaded'
        row['transcript']={'path':f"videos/{row['id']}/transcript.json",'language':trans['language'],'isGenerated':trans['isGenerated'],
            'method':trans['method'],'wordCount':trans['wordCount'],'segments':len(trans['segments'])}
        if trans['method']=='local_asr':row['asrStatus']='completed';row['asr']=trans.get('asr')
        if row.get('error'):row['previousCollectionError']=row.pop('error')
        if row.get('asrError'):row['previousAsrError']=row.pop('asrError')
        update_row(out,row);recovered+=1
    catalog=load(Path(out)/'catalog.json',[]);report(Path(out),catalog);return recovered

def report(out,catalog):
    counts=Counter(r.get('transcriptStatus','pending') for r in catalog)
    channels={}
    for row in catalog:
        ch=row.get('channel') or {};key=ch.get('id') or 'unverified'
        channels.setdefault(key,{'id':ch.get('id'),'name':ch.get('name'),'url':ch.get('url'),'videoIds':[]})['videoIds'].append(row['id'])
    save(out/'channels.json',list(channels.values()))
    save(out/'status.json',{'updatedAt':now(),'videos':len(catalog),'transcripts':dict(counts),
        'analysis':dict(Counter(r.get('analysisStatus','pending') for r in catalog)),
        'words':sum((r.get('transcript') or {}).get('wordCount',0) for r in catalog),'channels':len(channels)})
    lines=['# Base audiovisual local','',f"Actualizada: {now()}",'',
        'Los temas solicitados no se presentan como ideas comprobadas. El canal no identifica al hablante. Las transcripciones automáticas necesitan revisión de cifras y nombres.','',
        '| Canal | Vídeo | Duración | Transcripción | Análisis |','| --- | --- | ---: | --- | --- |']
    for row in sorted(catalog,key=lambda r:((r.get('channel') or {}).get('name') or '',r.get('position',0))):
        title=(row.get('title') or row['id']).replace('|','/');channel=((row.get('channel') or {}).get('name') or 'Por verificar').replace('|','/')
        status=row.get('transcriptStatus','pending')
        trans=f"[Texto](videos/{row['id']}/transcript.txt)" if status=='downloaded' else status
        lines.append(f"| {channel} | [{title}]({row['url']}) | {clock(row.get('duration') or 0)} | {trans} | {row.get('analysisStatus','pending')} |")
    (out/'INDEX.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['inventory','fetch','status','reconcile'])
    parser.add_argument('--output',default=str(DEFAULT_OUT));parser.add_argument('--config',default=str(ROOT/'tools/youtube-sources.json'))
    parser.add_argument('--playlist');parser.add_argument('--inventory-json');parser.add_argument('--limit',type=int,default=0)
    parser.add_argument('--ids');parser.add_argument('--force',action='store_true');parser.add_argument('--retry-failed',action='store_true');parser.add_argument('--delay',type=float,default=8.0)
    args=parser.parse_args()
    if args.command=='inventory':inventory(args)
    elif args.command=='fetch':return fetch(args)
    elif args.command=='reconcile':print(json.dumps({'recoveredTranscripts':reconcile(Path(args.output))}))
    else:
        out=Path(args.output);report(out,load(out/'catalog.json',[]));print(json.dumps(load(out/'status.json'),ensure_ascii=False,indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
