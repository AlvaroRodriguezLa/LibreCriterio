import json,re,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import youtube_collect as c
import youtube_review as r

TEST_TMP=Path(__file__).resolve().parents[1]/'tmp'
TEST_TMP.mkdir(exist_ok=True)

class ReviewTests(unittest.TestCase):
 def test_html_data_cannot_end_the_script_element(self):
  with tempfile.TemporaryDirectory(dir=TEST_TMP) as folder:
   out=Path(folder)
   title='</script><script>alert(1)</script> cifra: 3.000€'
   c.save(out/'catalog.json',[{'id':'DkMdd420fzw','title':title,'url':'https://www.youtube.com/watch?v=DkMdd420fzw','channel':{'id':'x','name':'Canal'},'transcriptStatus':'pending'}])
   r.build(out)
   page=(out/'index.html').read_text(encoding='utf-8')
   payload=page.split('<script id="library-data" type="application/json">',1)[1].split('</script>',1)[0]
   self.assertNotIn('<script>',payload)
   self.assertEqual(json.loads(payload)['catalog'][0]['title'],title)

 def test_catalog_updates_preserve_other_processes_and_completed_review(self):
  with tempfile.TemporaryDirectory(dir=TEST_TMP) as folder:
   out=Path(folder)
   stale={'id':'DkMdd420fzw','analysisStatus':'pending','transcriptStatus':'pending'}
   c.update_row(out,stale)
   c.update_row(out,{'id':'DkMdd420fzw','analysisStatus':'reviewed_transcript','analysis':{'arguments':4}},['analysisStatus','analysis'])
   c.update_row(out,{'id':'7QCWJbj7TEQ','transcriptStatus':'downloaded'})
   c.update_row(out,{**stale,'transcriptStatus':'downloaded'})
   rows=c.load(out/'catalog.json')
   self.assertEqual(len(rows),2)
   self.assertEqual(rows[0]['analysisStatus'],'reviewed_transcript')
   self.assertEqual(rows[0]['analysis']['arguments'],4)
   self.assertEqual(rows[0]['transcriptStatus'],'downloaded')

 def test_pack_preserves_every_segment_once_in_order(self):
  with tempfile.TemporaryDirectory(dir=TEST_TMP) as folder:
   out=Path(folder)
   row={'id':'DkMdd420fzw','title':'Prueba','channel':{'name':'Canal'}}
   c.save(out/'catalog.json',[row])
   segments=[{'id':'s'+str(i).zfill(5),'start':i*2,'end':i*2+1,'text':'Cifra 15.000 y negación no'} for i in range(1,8)]
   c.save(out/'videos'/row['id']/'transcript.json',{'sha256Original':'hash','segments':segments})
   self.assertGreater(r.pack(out,max_words=8),1)
   pages=sorted((out/'review'/row['id']).glob('parte-*.md'))
   joined=''.join(p.read_text(encoding='utf-8') for p in pages)
   self.assertEqual(re.findall(r'\[(s[0-9]+) \|',joined),[s['id'] for s in segments])
   self.assertEqual(joined.count('Cifra 15.000 y negación no'),7)

 def test_unread_and_reversed_sequence_are_rejected(self):
  trans={'sha256Original':'hash','segments':[{'id':'s00001'}]}
  analysis={'videoId':'DkMdd420fzw','sourceTranscriptSha256':'hash','reviewMode':'transcript_only','readAllSegments':False,'arguments':[{'evidenceSegmentIds':['s00001'],'assessment':'keep'}]}
  with self.assertRaises(ValueError):r.validate_analysis(analysis,trans,'DkMdd420fzw')
  analysis['readAllSegments']=True
  analysis['narrativeSequence']=[{'start':5,'end':8},{'start':2,'end':4}]
  with self.assertRaises(ValueError):r.validate_analysis(analysis,trans,'DkMdd420fzw')

if __name__=='__main__':unittest.main()
