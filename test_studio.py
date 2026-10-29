"""Offscreen GUI behaviour checks. Fixtures are synthetic, not gameplay evidence."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
try:
    from PySide6.QtWidgets import QApplication
    import studio
except ImportError:
    studio=None
from core import sign,verify

@unittest.skipIf(studio is None,'PySide6 not installed')
class StudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.patcher=patch.object(studio,'DATA',Path(self.tmp.name));self.patcher.start()
        self.w=studio.Studio();self.messages=[];self.w.error=self.messages.append;self.w.rounds.setValue(2);self.w.start_match()
    def tearDown(self):self.w.close();self.patcher.stop();self.tmp.cleanup()
    def report(self,local=False):
        return {'game':'Football','status':'uncertain' if local else 'ok','duration_seconds':20,'summary':'SYNTHETIC GUI TEST', 'limitations':['Not real gameplay.'],'events':[{'kind':'goal','player':'P1','time':5,'confidence':.9,'evidence':'Synthetic fixture only.'}], 'possession':[],'video_sha256':'testhash','roster':dict(self.w.players),'turn_player':'P1','host_context':self.w.host_context,'review_required':local}
    def test_five_pages_and_default_roster(self):self.assertEqual(self.w.stack.count(),5);self.assertEqual(len(self.w.players),4);self.assertEqual(self.messages,[])
    def test_apply_advances_and_autosaves(self):
        self.w.receive_report(sign(self.report(),self.w.secret));self.w.apply_report();self.assertEqual(self.w.points['P1'],1);self.assertEqual(self.w.round,2)
        files=list((Path(self.tmp.name)/'sessions').glob('*.json'));self.assertEqual(len(files),1)
        import json
        saved=verify(json.loads(files[0].read_text()),self.w.secret);self.assertEqual(saved['points']['P1'],1)
    def test_local_requires_review(self):
        self.w.receive_report(sign(self.report(True),self.w.secret));self.assertFalse(self.w.apply_button.isEnabled());self.w.apply_report();self.assertEqual(self.w.points['P1'],0)
        self.w.review.setChecked(True);self.assertTrue(self.w.apply_button.isEnabled());self.w.apply_report();self.assertEqual(self.w.points['P1'],1)
        self.assertTrue(self.w.history[0]['signed_evidence']['report']['human_reviewed'])
    def test_duplicate_clip_does_not_score(self):
        envelope=sign(self.report(),self.w.secret);self.w.receive_report(envelope);self.w.apply_report();self.w.receive_report(envelope);self.w.apply_report();self.assertEqual(self.w.points['P1'],1);self.assertIn('already',self.messages[-1])
    def test_individual_turn_advancement(self):
        self.w.game.setCurrentText('Dune Steps');self.w.start_match();self.w.advance();self.assertEqual(self.w.current_player(),'P2');self.assertEqual(self.w.round,1)
    def test_cloud_uncertain_blocked(self):
        r=self.report();r['status']='uncertain';self.w.receive_report(sign(r,self.w.secret));self.assertFalse(self.w.apply_button.isEnabled());self.w.apply_report();self.assertEqual(self.w.points['P1'],0)

    def test_preplay_tip_and_no_sidebar(self):
        self.w.select_game('Falcon Freeze');self.assertEqual(self.w.stack.currentIndex(),1);self.assertIn('no equipment',self.w.tip.text());self.assertEqual(len(self.w.nav),4)
    def test_favourites_persist(self):
        self.w.favourite('Dune Steps');self.w.filter_games('Favourites');self.assertIn('Dune Steps',self.w.favourites)
        import json
        saved=json.loads((Path(self.tmp.name)/'preferences.json').read_text());self.assertIn('Dune Steps',saved['favourites'])
    def test_timer_colours_change(self):
        self.w.remaining=30;self.w.show_clock();blue=self.w.clock.styleSheet();self.w.remaining=4;self.w.show_clock();self.assertNotEqual(blue,self.w.clock.styleSheet());self.assertEqual(self.w.clock.text(),'00:04')
    def test_offline_is_default(self):self.assertEqual(self.w.engine.currentIndex(),0);self.assertTrue(self.w.advanced_settings.isHidden())
    def test_saved_match_restores(self):
        self.w.receive_report(sign(self.report(),self.w.secret));self.w.apply_report();path=next((Path(self.tmp.name)/'sessions').glob('*.json'));self.w.points['P1']=8;self.w.players={};self.w.restore_session(str(path));self.assertEqual(self.w.points['P1'],1);self.assertEqual(self.w.round,2)

    def test_arabic_toggle_keeps_logo(self):
        self.w.toggle_language();self.assertEqual(self.w.nav[0].text(),'الرئيسية');self.assertFalse(self.w.brand.pixmap().isNull());self.w.toggle_language();self.assertEqual(self.w.nav[0].text(),'Home')
    def test_daily_memory_is_saved(self):
        self.w.memory_title.setText('First game');self.w.memory_body.setPlainText('A family moment.');self.w.save_memory();self.assertEqual(len(self.w.family_store.memories()),1)
    def test_family_plan_is_saved(self):
        self.w.plan_title.setText('Call grandparents');self.w.add_plan();self.assertEqual(len(self.w.family_store.plans()),1)

if __name__=='__main__':unittest.main()
