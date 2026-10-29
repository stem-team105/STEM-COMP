"""Synthetic unit fixtures validate code, NOT real AI accuracy."""
import copy
import unittest
from unittest.mock import patch
import tempfile
from pathlib import Path
from core import sign,verify,validate,score,GAMES
from judge import analyze

PLAYERS={'P1':'A','P2':'B'}
def sample():
    return {'game':'Football','status':'ok','duration_seconds':20,'summary':'Test fixture','limitations':[],
      'events':[{'kind':'goal','player':'P1','time':8,'confidence':0.9,'evidence':'Test fixture: ball crosses goal line.'}],
      'possession':[{'player':'P1','start':0,'end':6,'confidence':0.9},{'player':'P2','start':7,'end':10,'confidence':0.8}]}

class Tests(unittest.TestCase):
    def test_signed_roundtrip(self): self.assertEqual(verify(sign(sample(),b'secret'),b'secret'),sample())
    def test_tamper_rejected(self):
        envelope=sign(sample(),b'secret'); envelope['report']['events'][0]['player']='P2'
        with self.assertRaises(ValueError): verify(envelope,b'secret')
    def test_wrong_key_rejected(self):
        with self.assertRaises(ValueError): verify(sign(sample(),b'a'),b'b')
    def test_football(self):
        r=validate(sample(),'Football',PLAYERS,'P1'); points,pos=score(r,PLAYERS)
        self.assertEqual(points,{'P1':1,'P2':0}); self.assertEqual(pos,{'P1':6,'P2':3})
    def test_low_confidence_excluded(self):
        r=sample(); r['events'][0]['confidence']=0.6; self.assertEqual(score(r,PLAYERS)[0]['P1'],0)
    def test_uncertain_not_scored(self):
        r=sample(); r['status']='uncertain'; self.assertEqual(score(r,PLAYERS),({'P1':0,'P2':0},{'P1':0.0,'P2':0.0}))
    def test_overlap_rejected(self):
        r=sample(); r['possession'][1]['start']=5
        with self.assertRaises(ValueError): validate(r,'Football',PLAYERS,'P1')
    def test_unknown_player_rejected(self):
        r=sample(); r['events'][0]['player']='P9'
        with self.assertRaises(ValueError): validate(r,'Football',PLAYERS,'P1')
    def test_duplicate_event_rejected(self):
        r=sample(); r['events'].append(copy.deepcopy(r['events'][0]))
        with self.assertRaises(ValueError): validate(r,'Football',PLAYERS,'P1')
    def test_nan_rejected(self):
        r=sample(); r['events'][0]['time']=float('nan')
        with self.assertRaises(ValueError): validate(r,'Football',PLAYERS,'P1')
    def test_original_games_scoring(self):
        for game in list(GAMES)[1:]:
            kind=next(iter(GAMES[game]['events'])); r=sample(); r.update(game=game,possession=[])
            r['events'][0]['kind']=kind
            validate(r,game,PLAYERS,'P1'); self.assertEqual(score(r,PLAYERS)[0]['P1'],GAMES[game]['events'][kind])
    def test_other_turn_rejected(self):
        r=sample(); r.update(game='Majlis Delivery',possession=[]); r['events'][0]['kind']='delivery'
        with self.assertRaises(ValueError): validate(r,'Majlis Delivery',PLAYERS,'P2')
    def test_no_key(self):
        with self.assertRaises(ValueError): analyze('missing.mp4','','model','Football',PLAYERS,'P1','')
    def test_real_request_parsing_with_mock_transport(self):
        import json
        response={'candidates':[{'content':{'parts':[{'text':json.dumps(sample())}]}}]}
        class Reply:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self): return json.dumps(response).encode()
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'test.mp4'; p.write_bytes(b'SYNTHETIC TEST ONLY')
            with patch('urllib.request.urlopen',return_value=Reply()):
                r=analyze(p,'test-key','test-model','Football',PLAYERS,'P1','red / blue')
                self.assertEqual(r['model'],'test-model'); self.assertEqual(len(r['video_sha256']),64)

if __name__=='__main__': unittest.main()
