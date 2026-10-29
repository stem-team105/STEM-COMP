"""No real accuracy claims: unit tests use synthetic speech and a fake decoder."""
import hashlib,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
from local_ai import video_digest,analyze_local,PROFILES

class LocalTests(unittest.TestCase):
    def test_streaming_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'clip.mp4';p.write_bytes(b'fixture'*100000);self.assertEqual(video_digest(p),hashlib.sha256(p.read_bytes()).hexdigest())
    def test_eco_uses_less_work(self):
        self.assertLess(PROFILES['eco'][0],PROFILES['detail'][0]);self.assertLess(PROFILES['eco'][1],PROFILES['detail'][1]);self.assertLessEqual(PROFILES['eco'][2],2)
    def test_speech_turn_needs_no_vision_model(self):
        class Capture:
            def get(self,key):return 30 if key==1 else 300
            def isOpened(self):return True
            def release(self):pass
        fake=types.SimpleNamespace(VideoCapture=lambda path:Capture(),CAP_PROP_FPS=1,CAP_PROP_FRAME_COUNT=2)
        words=[{'word':word,'start':i*3+1,'end':i*3+2,'conf':.9} for i,word in enumerate(['family','desert','kindness'])]
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'clip.mp4';p.write_bytes(b'test')
            with patch.dict('sys.modules',{'cv2':fake,'ultralytics':None}),patch('local_ai.transcribe',return_value=words):
                r=analyze_local(p,'Family Story Relay',{'P1':'A','P2':'B'},'P1','',{})
            self.assertEqual(len(r['events']),3);self.assertTrue(r['review_required']);self.assertEqual(r['status'],'uncertain')

if __name__=='__main__':unittest.main()
