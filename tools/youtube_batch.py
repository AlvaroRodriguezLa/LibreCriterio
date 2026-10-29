"""Cola local reanudable: subtítulos, pausa ante límites y ASR opcional de audio público."""
from __future__ import annotations
import argparse,json,os,subprocess,sys,time,traceback
from pathlib import Path
import youtube_collect as c


def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=c.DEFAULT_OUT)
 p.add_argument('--asr',action='store_true');p.add_argument('--model',choices=['base','small'],default='base')
 p.add_argument('--caption-cooldown',type=int,default=1800);p.add_argument('--max-videos',type=int,default=0)
 p.add_argument('--delay',type=float,default=8);args=p.parse_args(argv);out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
 from filelock import FileLock,Timeout
 lock=FileLock(str(out/'batch.lock'))
 try:lock.acquire(timeout=0)
 except Timeout:print('Ya hay un lote activo.',flush=True);return 1
 control=out/'batch-control.json';state=c.load(control,{})
 state.update({'pid':os.getpid(),'startedAt':c.now(),'status':'running','current':None})
 state.setdefault('captionBlockedUntil',0);state.setdefault('failures',[]);c.save(control,state)
 processed=0;attempted=set()
 def checkpoint(**values):state.update(values);state['updatedAt']=c.now();c.save(control,state)
 def run(tool,params):
  command=[sys.executable,'-u',str(c.ROOT/'tools'/tool),*params,'--output',str(out)]
  with (out/'worker.log').open('a',encoding='utf-8') as log:
   log.write('\n'+c.now()+' '+tool+' '+json.dumps(params)+'\n');log.flush()
   process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,cwd=c.ROOT)
   while process.poll() is None:
    if (out/'batch-stop.request').exists():
     process.terminate()
     try:process.wait(timeout=8)
     except subprocess.TimeoutExpired:process.kill();process.wait()
     raise KeyboardInterrupt
    time.sleep(1)
   return process.returncode
 try:
  c.reconcile(out)
  while True:
   if (out/'batch-stop.request').exists():raise KeyboardInterrupt
   rows=c.load(out/'catalog.json',[])
   rows=sorted((r for r in rows if r.get('transcriptStatus')!='downloaded' and r['id'] not in attempted),
     key=lambda r:(r.get('priority')!='high',not bool(r.get('topicsRequested')),r.get('duration') or 0,r.get('position',999)))
   if not rows or (args.max_videos and processed>=args.max_videos):break
   row=rows[0];vid=row['id'];checkpoint(current={'id':vid,'title':row.get('title'),'phase':'captions'},processedThisRun=processed)
   if time.time()>=state.get('captionBlockedUntil',0) and row.get('transcriptStatus')!='unavailable':
    run('youtube_collect.py',['fetch','--ids',vid,'--limit','1','--delay','0'])
    row=next(r for r in c.load(out/'catalog.json',[]) if r['id']==vid)
    if row.get('transcriptStatus')=='blocked':checkpoint(captionBlockedUntil=time.time()+args.caption_cooldown)
   if row.get('transcriptStatus')!='downloaded' and args.asr:
    checkpoint(current={'id':vid,'title':row.get('title'),'phase':'local_asr'})
    rc=run('youtube_asr.py',['--video-id',vid,'--download-audio','--model',args.model,'--device','cpu','--compute-type','int8'])
    if rc:state['failures'].append({'id':vid,'at':c.now(),'phase':'local_asr'})
    c.reconcile(out)
   elif row.get('transcriptStatus')!='downloaded' and state.get('captionBlockedUntil',0)>time.time():
    checkpoint(status='waiting_for_youtube',current=None)
    time.sleep(min(30,max(1,state['captionBlockedUntil']-time.time())));continue
   attempted.add(vid);processed+=1
   run('youtube_review.py',['build'])
   checkpoint(status='running',current=None,processedThisRun=processed)
   if args.delay:time.sleep(args.delay)
  final=c.load(out/'catalog.json',[]);pending=[r['id'] for r in final if r.get('transcriptStatus')!='downloaded']
  checkpoint(status='complete' if not pending else 'needs_attention',current=None,pending=pending,finishedAt=c.now(),processedThisRun=processed)
  print(json.dumps({'status':state['status'],'remaining':len(pending)},ensure_ascii=False),flush=True)
  return 0 if not pending else 2
 except KeyboardInterrupt:
  checkpoint(status='stopped',current=None);return 130
 except Exception as exc:
  checkpoint(status='error',error={'type':type(exc).__name__,'message':str(exc)[:800]});traceback.print_exc();return 2
 finally:lock.release()

if __name__=='__main__':raise SystemExit(main())
