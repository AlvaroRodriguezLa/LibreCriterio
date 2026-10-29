import importlib.util,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import youtube_collect as c
import youtube_review as r
class CollectionTests(unittest.TestCase):
 def test_rolling_captions_keep_original_words_and_numbers(self):
  result=c.normalize_segments([{'start':0,'duration':4,'text':'Una cifra de 15.000 euros'},{'start':2,'duration':4,'text':'15.000 euros no crea riqueza'}])
  self.assertEqual([s['text'] for s in result],['Una cifra de 15.000 euros','no crea riqueza'])
 def test_rhetorical_repetition_without_overlap_is_retained(self):
  result=c.normalize_segments([{'start':0,'duration':2,'text':'No es tuyo'},{'start':3,'duration':2,'text':'No es tuyo'}]);self.assertEqual(len(result),2)
 def test_same_video_preserves_both_requested_contexts(self):
  rows=c.merge_catalog([{'id':'DkMdd420fzw','title':'Expresión','channel':'Un canal'}],[{'id':'DkMdd420fzw','topics':['bandidos','expresion'],'contexts':['A','B']}])
  self.assertEqual(len(rows),1);self.assertEqual(rows[0]['topicsRequested'],['bandidos','expresion']);self.assertEqual(rows[0]['speakers'],[])
 def test_resume_preserves_downloaded_state(self):
  old=[{'id':'DkMdd420fzw','transcriptStatus':'downloaded'}];rows=c.merge_catalog([{'id':'DkMdd420fzw'}],[],old);self.assertEqual(rows[0]['transcriptStatus'],'downloaded')
 def test_analysis_rejects_invented_evidence_and_stale_transcript(self):
  trans={'sha256Original':'hash','segments':[{'id':'s00001'}]};a={'videoId':'DkMdd420fzw','sourceTranscriptSha256':'hash','reviewMode':'transcript_only','readAllSegments':True,'arguments':[{'evidenceSegmentIds':['invented'],'assessment':'keep'}]}
  with self.assertRaises(ValueError):r.validate_analysis(a,trans,'DkMdd420fzw')
  a['arguments'][0]['evidenceSegmentIds']=['s00001'];self.assertEqual(r.validate_analysis(a,trans,'DkMdd420fzw')['arguments'],1)
  a['sourceTranscriptSha256']='old'
  with self.assertRaises(ValueError):r.validate_analysis(a,trans,'DkMdd420fzw')
if __name__=='__main__':unittest.main()
