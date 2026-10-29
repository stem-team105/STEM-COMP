import tempfile,unittest
from pathlib import Path
from family import FamilyStore
from recommendation import FamilyRecommender,SEEDS

class FamilyTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'family.db';self.store=FamilyStore(self.path)
    def tearDown(self):self.tmp.cleanup()
    def test_plan_survives_reopening(self):
        self.store.add_plan('Family game night','2026-10-29');ident=self.store.plans()[0][0];self.store.complete(ident,True);self.assertEqual(FamilyStore(self.path).plans()[0][3],1)
    def test_bilingual_memory(self):
        self.store.add_memory('يوم جميل','We played together. لعبنا معًا.');self.assertIn('لعبنا',FamilyStore(self.path).memories()[0][2])
    def test_blank_memory_rejected(self):
        with self.assertRaises(ValueError):self.store.add_memory('','')
    def test_invalid_plan_date_rejected(self):
        with self.assertRaises(ValueError):self.store.add_plan('Dinner','tomorrow')
    def test_feedback_recorded_once_per_session(self):
        for _ in range(3):self.store.enjoy('same-session',['calm','indoors','5'],'Family Story Relay')
        self.assertEqual(len(self.store.feedback()),1)
    def test_parameterized_text(self):
        title="Grandma's night; DROP TABLE plans;";self.store.add_plan(title,'2026-10-29');self.assertEqual(self.store.plans()[0][1],title)

class RecommendationTests(unittest.TestCase):
    def test_indoor_suggestions_exclude_football(self):self.assertNotEqual(FamilyRecommender().suggest(['active','indoors','10']),'Football')
    def test_explicit_feedback_changes_preference(self):
        context=['calm','indoors','5'];self.assertEqual(FamilyRecommender().suggest(context),'Family Story Relay');self.assertEqual(FamilyRecommender([(context,'Falcon Freeze')]*30).suggest(context),'Falcon Freeze')
    def test_seed_inventory_is_explicit(self):self.assertEqual(len(SEEDS),20);self.assertEqual(len({g for _,g in SEEDS}),5)

if __name__=='__main__':unittest.main()
