"""Family AI Game Day — Team 105. Run with py app.py (Python 3.11+)."""
import hashlib
import json
import os
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from core import GAMES, local_secret, sign, verify, validate, score
from judge import analyze, DEFAULT_MODEL

ROOT=Path(__file__).resolve().parent
BG='#0b1721'; CARD='#142634'; INK='#edf4f4'; MUTED='#9ab3bd'; ACCENT='#63e0bd'

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Family AI Game Day | Team 105')
        self.geometry('1180x800'); self.minsize(940,680); self.configure(bg=BG)
        self.key=local_secret(ROOT/'.local'); self.queue=queue.Queue(); self.busy=False
        self.players={}; self.points={}; self.possession={}; self.applied=set(); self.history=[]
        self.pending=None; self.video=None; self.turn=0; self.round=1; self.running=False; self.remaining=30; self.deadline=0
        self.game=tk.StringVar(value='Football'); self.api=tk.StringVar(value=os.getenv('GEMINI_API_KEY',''))
        self.model=tk.StringVar(value=os.getenv('GEMINI_MODEL',DEFAULT_MODEL)); self.round_limit=tk.StringVar(value='3')
        self.status=tk.StringVar(value='Ready to set up • No AI results yet')
        self.turn_text=tk.StringVar(value='Set up players to begin'); self.clock=tk.StringVar(value='00:30')
        style=ttk.Style(self); style.theme_use('clam')
        style.configure('TFrame',background=BG); style.configure('TLabel',background=BG,foreground=INK,font=('Segoe UI',11))
        style.configure('TButton',font=('Segoe UI',10,'bold'),padding=(12,9),background=CARD,foreground=INK,borderwidth=0)
        style.map('TButton',background=[('active','#285064')])
        style.configure('Accent.TButton',background=ACCENT,foreground=BG)
        style.configure('TNotebook',background=BG,borderwidth=0)
        style.configure('TNotebook.Tab',background=CARD,foreground=INK,padding=(20,12),font=('Segoe UI',10,'bold'))
        style.map('TNotebook.Tab',background=[('selected',ACCENT)],foreground=[('selected',BG)])
        style.configure('Treeview',background=CARD,fieldbackground=CARD,foreground=INK,rowheight=32,font=('Segoe UI',10))
        style.configure('Treeview.Heading',background='#244353',foreground=INK,font=('Segoe UI',10,'bold'))
        head=ttk.Frame(self,padding=(28,20)); head.pack(fill='x')
        ttk.Label(head,text='FAMILY / AI GAME DAY',font=('Segoe UI',24,'bold')).pack(side='left')
        ttk.Label(head,text='TEAM 105  •  CHAMPIONS',foreground=ACCENT).pack(side='right')
        self.tabs=ttk.Notebook(self); self.tabs.pack(fill='both',expand=True,padx=24,pady=(0,12))
        self.setup=ttk.Frame(self.tabs,padding=22); self.play=ttk.Frame(self.tabs,padding=22); self.results=ttk.Frame(self.tabs,padding=22)
        for page,label in [(self.setup,'01  Set up'),(self.play,'02  Play & judge'),(self.results,'03  Results')]: self.tabs.add(page,text=label)
        self.build_setup(); self.build_play(); self.build_results()
        ttk.Label(self,textvariable=self.status,foreground=ACCENT,padding=(26,8)).pack(fill='x')
        self.after(100,self.poll); self.after(100,self.tick)

    def label(self,parent,text,size=11,color=INK):
        w=ttk.Label(parent,text=text,font=('Segoe UI',size,'bold' if size>11 else 'normal'),foreground=color,wraplength=1000); w.pack(anchor='w',pady=(5,8)); return w

    def text(self,parent,height=5):
        w=tk.Text(parent,height=height,bg=CARD,fg=INK,insertbackground=ACCENT,relief='flat',font=('Segoe UI',11),padx=12,pady=10,wrap='word'); w.pack(fill='both',expand=False,pady=(0,10)); return w

    def build_setup(self):
        self.label(self.setup,'Choose the fun. Let the evidence decide.',20)
        line=ttk.Frame(self.setup); line.pack(fill='x',pady=6)
        ttk.Label(line,text='Game').pack(side='left',padx=(0,12))
        choice=ttk.Combobox(line,textvariable=self.game,values=list(GAMES),state='readonly',width=25); choice.pack(side='left'); choice.bind('<<ComboboxSelected>>',self.rules_changed)
        ttk.Label(line,text='Rounds').pack(side='left',padx=(25,10)); ttk.Spinbox(line,from_=1,to=10,textvariable=self.round_limit,width=5).pack(side='left')
        self.rules=ttk.Label(self.setup,text=GAMES['Football']['rules'],wraplength=1020,foreground=MUTED); self.rules.pack(fill='x',pady=12)
        cols=ttk.Frame(self.setup); cols.pack(fill='x'); left=ttk.Frame(cols); left.pack(side='left',fill='both',expand=True,padx=(0,15)); right=ttk.Frame(cols); right.pack(side='left',fill='both',expand=True)
        self.label(left,'Players — one per line: ID, team',12)
        self.roster=self.text(left,4); self.roster.insert('1.0','P1, A\nP2, A\nP3, B\nP4, B')
        self.label(right,'Camera / player identification',12)
        self.context=self.text(right,4); self.context.insert('1.0','Describe actual shirt colours and numbers here. For football: specify the goal each team attacks. For Dune Steps: describe marker positions.')
        self.label(self.setup,'AI connection — key stays in memory; never saved to the repository',12)
        row=ttk.Frame(self.setup); row.pack(fill='x',pady=5)
        ttk.Label(row,text='Gemini key').pack(side='left'); ttk.Entry(row,textvariable=self.api,show='•',width=38).pack(side='left',padx=10)
        ttk.Label(row,text='Model').pack(side='left',padx=(10,0)); ttk.Entry(row,textvariable=self.model,width=25).pack(side='left',padx=10)
        self.label(self.setup,'Use a short video with audio (MP4 / WebM / MOV, up to 14 MB). Clips are sent to Google for analysis only when you click Judge. Obtain participants’ permission before recording.',10,MUTED)
        ttk.Button(self.setup,text='Start new game →',style='Accent.TButton',command=self.start).pack(anchor='w',pady=12)

    def rules_changed(self,event=None): self.rules.config(text=GAMES[self.game.get()]['rules'])

    def build_play(self):
        top=ttk.Frame(self.play); top.pack(fill='x')
        ttk.Label(top,textvariable=self.turn_text,font=('Segoe UI',18,'bold')).pack(side='left')
        ttk.Label(top,textvariable=self.clock,font=('Consolas',30,'bold'),foreground=ACCENT).pack(side='right')
        self.play_rules=ttk.Label(self.play,text='',wraplength=1020,foreground=MUTED); self.play_rules.pack(fill='x',pady=12)
        row=ttk.Frame(self.play); row.pack(fill='x',pady=6)
        for text,fn in [('Start / pause timer',self.toggle_timer),('Reset timer',self.reset_timer),('Choose gameplay video',self.choose),('Open video',self.open_video)]: ttk.Button(row,text=text,command=fn).pack(side='left',padx=(0,8))
        self.file_label=ttk.Label(self.play,text='No video selected',foreground=MUTED); self.file_label.pack(anchor='w',pady=8)
        actions=ttk.Frame(self.play); actions.pack(fill='x',pady=8)
        self.judge_button=ttk.Button(actions,text='Judge video + audio',style='Accent.TButton',command=self.judge); self.judge_button.pack(side='left',padx=(0,8))
        ttk.Button(actions,text='Import signed report',command=self.import_report).pack(side='left',padx=(0,8))
        ttk.Button(actions,text='Export signed report',command=self.export_report).pack(side='left')
        self.progress=ttk.Progressbar(self.play,mode='indeterminate'); self.progress.pack(fill='x',pady=5)
        self.evidence=self.text(self.play,12); self.evidence.insert('1.0','The AI’s observations, timestamps and limitations will appear here.\nNo scores are generated until a real clip is analysed.'); self.evidence.config(state='disabled')
        bottom=ttk.Frame(self.play); bottom.pack(fill='x',pady=6)
        self.apply_button=ttk.Button(bottom,text='Apply verified evidence & next turn →',style='Accent.TButton',command=self.apply,state='disabled'); self.apply_button.pack(side='left')
        ttk.Button(bottom,text='Skip turn (no points)',command=self.skip).pack(side='left',padx=10)
        ttk.Button(bottom,text='View results',command=lambda:self.tabs.select(self.results)).pack(side='right')

    def build_results(self):
        self.label(self.results,'Every point has a reason.',20)
        self.result_title=ttk.Label(self.results,text='Start a game to see results.',font=('Segoe UI',14,'bold')); self.result_title.pack(anchor='w',pady=10)
        self.table=ttk.Treeview(self.results,columns=('player','team','points','possession'),show='headings',height=8)
        for col,title in [('player','Player'),('team','Team'),('points','Points'),('possession','Observed possession (s)')]: self.table.heading(col,text=title); self.table.column(col,width=180,anchor='center')
        self.table.pack(fill='x',pady=12)
        self.summary=ttk.Label(self.results,text='',wraplength=1000,foreground=MUTED); self.summary.pack(anchor='w',pady=10)
        row=ttk.Frame(self.results); row.pack(fill='x',pady=12)
        ttk.Button(row,text='Export results + evidence',command=self.export_results).pack(side='left',padx=(0,10))
        ttk.Button(row,text='Extra round / tie-break',command=self.extra_round).pack(side='left',padx=(0,10))
        ttk.Button(row,text='Choose another game',command=lambda:self.tabs.select(self.setup)).pack(side='left')
        self.label(self.results,'Possession is an AI estimate from visible play, not sensor measurement. Unknown or low-confidence periods are excluded. Tied possession produces joint MVPs. Review the evidence before presenting results.',10,MUTED)

    def start(self):
        if self.busy: return
        try:
            players={}
            for line in self.roster.get('1.0','end').strip().splitlines():
                parts=[x.strip() for x in line.split(',')]
                if len(parts)!=2 or not all(parts) or parts[0] in players: raise ValueError('Use unique player IDs and one team per line: P1, A')
                if len(parts[0])>24 or len(parts[1])>24: raise ValueError('Keep IDs and teams under 25 characters.')
                players[parts[0]]=parts[1]
            if not 2<=len(players)<=12: raise ValueError('Enter 2–12 players.')
            rounds=int(self.round_limit.get())
            if not 1<=rounds<=10: raise ValueError('Choose 1–10 rounds.')
            if GAMES[self.game.get()]['mode']=='Team' and len(set(players.values()))!=2: raise ValueError('Team games need exactly two teams.')
            if self.history and not messagebox.askyesno('New game','Export results first if needed. Start a new game and clear current scores?'): return
            self.players=players; self.active_game=self.game.get(); self.total_rounds=rounds; self.host_context=self.context.get('1.0','end').strip()
            self.points={p:0 for p in players}; self.possession={p:0.0 for p in players}; self.applied=set(); self.history=[]; self.turn=0; self.round=1; self.finished=False
            self.play_rules.config(text=GAMES[self.active_game]['rules']); self.clear_pending(); self.reset_timer(); self.refresh(); self.tabs.select(self.play)
        except ValueError as e: messagebox.showerror('Check setup',str(e))

    def current_player(self): return list(self.players)[self.turn%len(self.players)]
    def clear_pending(self):
        self.pending=None; self.video=None; self.file_label.config(text='No video selected'); self.apply_button.config(state='disabled')
    def refresh(self):
        if not self.players: return
        turn='All players' if self.active_game=='Football' else self.current_player()
        self.turn_text.set(f'{self.active_game}  /  Round {self.round}  /  {turn}' if not self.finished else self.active_game+'  /  Game complete')
        for item in self.table.get_children(): self.table.delete(item)
        for p in sorted(self.players,key=lambda p:self.points[p],reverse=True): self.table.insert('','end',values=(p,self.players[p],self.points[p],f'{self.possession[p]:.1f}' if self.active_game=='Football' else '—'))
        totals={}
        for p in self.players:
            entity=self.players[p] if GAMES[self.active_game]['mode']=='Team' else p
            totals[entity]=totals.get(entity,0)+self.points[p]
        highest=max(totals.values()); leaders=[k for k,v in totals.items() if v==highest]
        outcome=('Tie: ' if len(leaders)>1 else ('Winner: ' if self.finished else 'Leader: '))+', '.join(leaders)
        self.result_title.config(text=outcome+'  |  '+' · '.join(f'{k}: {v}' for k,v in totals.items()))
        detail=f'{len(self.history)} turns recorded. {len(self.applied)} verified clips applied.'
        if self.active_game=='Football':
            top=max(self.possession.values()); mvp=', '.join(p for p,v in self.possession.items() if abs(v-top)<0.001) if top else 'No possession evidence yet'
            team_pos={t:sum(self.possession[p] for p in self.players if self.players[p]==t) for t in set(self.players.values())}
            detail+='\nPossession MVP: '+mvp+'\nTeam possession: '+' · '.join(f'{t}: {v:.1f}s' for t,v in team_pos.items())
        self.summary.config(text=detail)

    def reset_timer(self): self.running=False; self.remaining=60 if getattr(self,'active_game','')=='Football' else 30; self.clock.set(f'{self.remaining//60:02d}:{self.remaining%60:02d}')
    def toggle_timer(self):
        if not self.players or self.finished: return
        if self.running: self.remaining=max(0,self.deadline-time.monotonic()); self.running=False
        else:
            if self.remaining<=0: self.reset_timer()
            self.deadline=time.monotonic()+self.remaining; self.running=True
    def tick(self):
        if self.running:
            self.remaining=max(0,self.deadline-time.monotonic()); seconds=int(self.remaining+0.999); self.clock.set(f'{seconds//60:02d}:{seconds%60:02d}')
            if not seconds: self.running=False; self.bell(); self.status.set('Time is up. Stop recording, then choose the gameplay clip.')
        self.after(100,self.tick)
    def choose(self):
        if self.busy: return
        path=filedialog.askopenfilename(filetypes=[('Gameplay video','*.mp4 *.webm *.mov')])
        if path: self.video=path; self.pending=None; self.apply_button.config(state='disabled'); self.file_label.config(text=Path(path).name)
    def open_video(self):
        if self.video:
            try:
                if os.name=='nt': os.startfile(self.video)
                else: import webbrowser; webbrowser.open(Path(self.video).as_uri())
            except OSError as e: messagebox.showerror('Video',str(e))
    def judge(self):
        if self.busy: return
        if not self.players or self.finished: messagebox.showinfo('Start game','Start a game with active turns first.'); return
        if not self.video: messagebox.showinfo('Video required','Choose a real gameplay clip with audio first.'); return
        args=(self.video,self.api.get(),self.model.get().strip(),self.active_game,dict(self.players),self.current_player(),self.host_context)
        if not args[1]: messagebox.showinfo('API key required','Enter your Gemini API key in Set up. It stays in memory.'); return
        self.busy=True; self.pending=None; self.apply_button.config(state='disabled'); self.judge_button.config(state='disabled'); self.progress.start(12); self.status.set('AI is watching and listening… This may take up to 150 seconds.')
        def worker():
            try: self.queue.put(('ok',sign(analyze(*args),self.key)))
            except Exception as e: self.queue.put(('error',str(e)))
        threading.Thread(target=worker,daemon=True).start()
    def poll(self):
        try:
            kind,value=self.queue.get_nowait(); self.busy=False; self.progress.stop(); self.judge_button.config(state='normal')
            if kind=='error': self.status.set('Judging failed. Scores unchanged.'); messagebox.showerror('AI judge',value)
            else:
                try: self.show_report(value)
                except (ValueError, KeyError, TypeError) as e:
                    self.status.set('Report rejected. Scores unchanged.'); messagebox.showerror('Invalid evidence', str(e))
        except queue.Empty: pass
        self.after(100,self.poll)
    def show_report(self,envelope):
        report=verify(envelope,self.key)
        validate(report,self.active_game,self.players,self.current_player())
        if report.get('roster')!=self.players or report.get('turn_player')!=self.current_player() or report.get('host_context')!=self.host_context: raise ValueError('Report setup differs from this match.')
        self.pending=envelope
        text=f"{report['status'].upper()} — {report['summary']}\n\n"
        for e in report['events']: text+=f"{e['time']:.1f}s | {e['player']} | {e['kind']} | confidence {e['confidence']:.0%}\n{e['evidence']}\n\n"
        text+='LIMITATIONS\n'+'\n'.join(str(x) for x in report['limitations'])
        if report.get('possession'): text+='\n\nPOSSESSION INTERVALS\n'+'\n'.join(f"{p['player']}: {p['start']}–{p['end']}s ({p['confidence']:.0%})" for p in report['possession'])
        text+='\n\nOnly events and intervals at confidence ≥75% are applied. Uncertain reports never change scores.'
        self.evidence.config(state='normal'); self.evidence.delete('1.0','end'); self.evidence.insert('1.0',text); self.evidence.config(state='disabled')
        self.apply_button.config(state='normal' if report['status']=='ok' else 'disabled'); self.status.set('Evidence ready for review.' if report['status']=='ok' else 'Uncertain evidence. Improve the recording and retry; no points applied.')
    def apply(self):
        if not self.pending or self.busy or self.finished: return
        try:
            report=verify(self.pending,self.key); validate(report,self.active_game,self.players,self.current_player())
            digest=report['video_sha256']
            if digest in self.applied: raise ValueError('This clip has already been scored in this game.')
            if report['status']!='ok': raise ValueError('Uncertain reports cannot be applied.')
            delta,pos=score(report,self.players)
            for p in self.players: self.points[p]+=delta[p]; self.possession[p]+=pos[p]
            self.applied.add(digest); self.history.append({'round':self.round,'turn':self.current_player(),'signed_evidence':self.pending}); self.advance()
        except (ValueError,KeyError) as e: messagebox.showerror('Cannot apply',str(e))
    def advance(self):
        if self.active_game=='Football': self.round+=1
        else:
            self.turn+=1
            if self.turn%len(self.players)==0: self.round+=1
        self.finished=self.round>self.total_rounds; self.clear_pending(); self.reset_timer(); self.refresh()
        self.status.set('Game complete. Export the results.' if self.finished else 'Next turn ready. Record a new clip.')
        if self.finished: self.tabs.select(self.results)
    def skip(self):
        if not self.players or self.busy or self.finished: return
        if messagebox.askyesno('Skip turn','Skip this turn with no points?'):
            self.history.append({'round':self.round,'turn':self.current_player(),'skipped':True}); self.advance()
    def extra_round(self):
        if not self.players or self.busy: return
        if not self.finished: messagebox.showinfo('Game in progress','Complete the current rounds first.'); return
        self.total_rounds=self.round; self.finished=False; self.refresh(); self.tabs.select(self.play)
    def export_report(self):
        if not self.pending: return
        self.save_json(self.pending,'judge-report.json')
    def import_report(self):
        if not self.players or self.busy or self.finished: return
        path=filedialog.askopenfilename(filetypes=[('Signed judge report','*.json')])
        if path:
            try: self.show_report(json.loads(Path(path).read_text(encoding='utf-8')))
            except (ValueError,KeyError,TypeError,OSError) as e: messagebox.showerror('Report rejected',str(e))
    def save_json(self,data,name):
        path=filedialog.asksaveasfilename(initialfile=name,defaultextension='.json',filetypes=[('JSON','*.json')])
        if path:
            try: Path(path).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8'); self.status.set('Saved '+Path(path).name)
            except OSError as e: messagebox.showerror('Save failed',str(e))
    def export_results(self):
        if self.players: self.save_json({'game':self.active_game,'players':self.players,'points':self.points,'possession_seconds':self.possession,'complete':self.finished,'history':self.history},'family-game-results.json')

if __name__=='__main__': App().mainloop()
