"""Prepara revisión, valida evidencia y genera el índice de conocimiento local."""
from __future__ import annotations
import argparse,json,re,html,sys
from pathlib import Path
import youtube_collect as collect

def evidence_ids(value):
    found=[]
    if isinstance(value,dict):
        for key,item in value.items():
            if key=='evidenceSegmentIds':
                if not isinstance(item,list):raise ValueError('evidenceSegmentIds debe ser lista')
                found.extend(item)
            else:found.extend(evidence_ids(item))
    elif isinstance(value,list):
        for item in value:found.extend(evidence_ids(item))
    return found

def validate_analysis(analysis,transcript,video_id):
    if analysis.get('videoId')!=video_id:raise ValueError('Vídeo incorrecto')
    if analysis.get('sourceTranscriptSha256')!=transcript.get('sha256Original'):raise ValueError('La transcripción cambió: revisar de nuevo')
    if analysis.get('reviewMode') not in {'transcript_only','audiovisual_review'}:raise ValueError('Modo de revisión desconocido')
    if analysis.get('readAllSegments') is not True:raise ValueError('Lectura incompleta')
    segments={s['id']:s for s in transcript.get('segments',[])}
    all_ids=evidence_ids(analysis)
    if not all_ids:raise ValueError('Ficha sin evidencia')
    invalid=set(all_ids)-set(segments)
    if invalid:raise ValueError('Segmentos inexistentes: '+','.join(sorted(invalid)))
    for argument in analysis.get('arguments',[]):
        if not argument.get('evidenceSegmentIds'):raise ValueError('Argumento sin evidencia')
        if argument.get('assessment') not in {'keep','qualify','reject','needs_verification'}:raise ValueError('Juicio de argumento inválido')
    sequence=analysis.get('narrativeSequence',[])
    last=-1
    for step in sequence:
        start=step.get('start');end=step.get('end')
        if not isinstance(start,(int,float)) or not isinstance(end,(int,float)) or start<last or end<start:raise ValueError('Secuencia temporal inválida')
        last=start
    return {'arguments':len(analysis.get('arguments',[])),'sequenceSteps':len(sequence),'evidenceReferences':len(all_ids)}

def validate(out):
    catalog=collect.load(out/'catalog.json',[]);results=[];failures=[]
    for row in catalog:
        path=out/'analysis'/(row['id']+'.json')
        if not path.exists():continue
        try:
            analysis=collect.load(path);trans=collect.load(out/'videos'/row['id']/'transcript.json')
            if not trans:raise ValueError('No existe la transcripción original')
            result=validate_analysis(analysis,trans,row['id']);row['analysisStatus']=analysis.get('status','reviewed_transcript')
            row['analysis']={'path':f"analysis/{row['id']}.json",'mode':analysis['reviewMode'],**result};results.append({'id':row['id'],**result})
        except (ValueError,TypeError,KeyError) as exc:
            row['analysisStatus']='invalid';failures.append({'id':row['id'],'error':str(exc)})
    for row in catalog: collect.update_row(out,row,['analysisStatus','analysis'])
    catalog=collect.load(out/'catalog.json',[]);collect.report(out,catalog)
    collect.save(out/'validation.json',{'at':collect.now(),'valid':len(results),'failures':failures,'results':results})
    return results,failures

def pack(out,max_words=1800):
    protocol=(collect.ROOT/'tools/YOUTUBE_REVIEW_PROTOCOL.md').read_text(encoding='utf-8')
    count=0
    for row in collect.load(out/'catalog.json',[]):
        trans=collect.load(out/'videos'/row['id']/'transcript.json')
        if not trans:continue
        chunks=[];current=[];words=0
        for seg in trans['segments']:
            n=len(seg['text'].split())
            if current and words+n>max_words:chunks.append(current);current=[];words=0
            current.append(seg);words+=n
        if current:chunks.append(current)
        for index,chunk in enumerate(chunks,1):
            path=out/'review'/row['id']/f'parte-{index:03}.md';path.parent.mkdir(parents=True,exist_ok=True)
            text=protocol+'\n\n# Fuente\n\n'+json.dumps({'videoId':row['id'],'title':row['title'],'channel':row['channel'],
                'sourceTranscriptSha256':trans['sha256Original'],'part':index,'parts':len(chunks)},ensure_ascii=False,indent=2)+'\n\n'
            text+='\n'.join(f"[{s['id']} | {collect.clock(s['start'])}–{collect.clock(s['end'])}] {s['text']}" for s in chunk)
            path.write_text(text+'\n',encoding='utf-8');count+=1
    return count

def build(out):
    validate(out)
    catalog=collect.load(out/'catalog.json',[]);analyses={}
    for row in catalog:
        if row.get('analysisStatus')=='reviewed_transcript':analyses[row['id']]=collect.load(out/'analysis'/(row['id']+'.json'))
    template=(collect.ROOT/'tools/templates/youtube-library.html').read_text(encoding='utf-8')
    payload=json.dumps({'catalog':catalog,'analyses':analyses,'status':collect.load(out/'status.json')},ensure_ascii=False).replace('<','\\u003c')
    (out/'index.html').write_text(template.replace('__LIBRARY_DATA__',payload),encoding='utf-8')
    return len(analyses)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['pack','validate','build','serve']);p.add_argument('--output',type=Path,default=collect.DEFAULT_OUT);p.add_argument('--port',type=int,default=4333)
    a=p.parse_args();out=a.output.resolve()
    if a.command=='pack':print(json.dumps({'reviewParts':pack(out)}))
    elif a.command=='validate':
        results,failures=validate(out);print(json.dumps({'valid':len(results),'failures':failures},ensure_ascii=False));return bool(failures)
    elif a.command=='build':print(json.dumps({'reviewedVideos':build(out),'index':str(out/'index.html')}))
    else:
        build(out)
        from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
        from functools import partial
        handler=partial(SimpleHTTPRequestHandler,directory=str(out));server=ThreadingHTTPServer(('127.0.0.1',a.port),handler)
        print(f'Biblioteca privada local: http://127.0.0.1:{a.port}/',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
        finally:server.server_close()
    return 0
if __name__=='__main__':raise SystemExit(main())
