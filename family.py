"""Small local family planner, memory journal and explicit recommendation feedback."""
import json,sqlite3
from datetime import datetime
from pathlib import Path

class FamilyStore:
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS plans(id INTEGER PRIMARY KEY,title TEXT NOT NULL,due TEXT NOT NULL,done INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY,title TEXT NOT NULL,body TEXT NOT NULL,created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS feedback(session TEXT PRIMARY KEY,context TEXT NOT NULL,game TEXT NOT NULL);''')
    def connect(self):return sqlite3.connect(self.path)
    def plans(self):
        with self.connect() as db:return db.execute('SELECT id,title,due,done FROM plans ORDER BY done,due,id DESC').fetchall()
    def add_plan(self,title,due):
        title=title.strip()
        if not title or len(title)>160:raise ValueError('Give your plan a short title (up to 160 characters).')
        datetime.strptime(due,'%Y-%m-%d')
        with self.connect() as db:db.execute('INSERT INTO plans(title,due) VALUES(?,?)',(title,due))
    def complete(self,plan_id,done):
        with self.connect() as db:db.execute('UPDATE plans SET done=? WHERE id=?',(int(bool(done)),int(plan_id)))
    def add_memory(self,title,body):
        title=title.strip();body=body.strip()
        if not title or not body or len(title)>160 or len(body)>6000:raise ValueError('Add a title and a memory (up to 6,000 characters).')
        with self.connect() as db:db.execute('INSERT INTO memories(title,body,created) VALUES(?,?,?)',(title,body,datetime.now().isoformat(timespec='seconds')))
    def memories(self):
        with self.connect() as db:return db.execute('SELECT id,title,body,created FROM memories ORDER BY id DESC').fetchall()
    def enjoy(self,session,context,game):
        with self.connect() as db:db.execute('INSERT OR IGNORE INTO feedback(session,context,game) VALUES(?,?,?)',(session,json.dumps(context),game))
    def feedback(self):
        with self.connect() as db:return [(json.loads(c),g) for c,g in db.execute('SELECT context,game FROM feedback').fetchall()]
    def export(self):return {'plans':self.plans(),'memories':self.memories(),'enjoyed_games':self.feedback()}
