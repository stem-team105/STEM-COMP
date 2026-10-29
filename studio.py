"""Modern desktop host application. Team 105 — Family AI Game Day."""
import hashlib,json,os,sys,time,uuid
from pathlib import Path
from PySide6.QtCore import Qt,QTimer,QThread,Signal,QUrl,QPropertyAnimation,QEasingCurve
from PySide6.QtGui import QPixmap,QImage,QFont,QColor,QShortcut,QKeySequence
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QPushButton,QFrame,QStackedWidget,QLineEdit,QTextEdit,QComboBox,QSpinBox,QProgressBar,QFileDialog,QMessageBox,QTableWidget,QTableWidgetItem,QHeaderView,QScrollArea,QGraphicsOpacityEffect,QDialog,QDialogButtonBox,QCheckBox)
from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput,QMediaDevices,QCamera,QAudioInput,QMediaCaptureSession,QMediaRecorder
from PySide6.QtMultimediaWidgets import QVideoWidget
from core import GAMES,local_secret,sign,verify,validate,score
from judge import analyze,DEFAULT_MODEL
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'.local'; DATA.mkdir(exist_ok=True)

DARK='''
QWidget {background:#0b1420;color:#eaf1f6;font-family:Segoe UI;font-size:14px;}
QFrame#sidebar {background:#101f2d;border-right:1px solid #223547;}
QFrame#card {background:#142434;border:1px solid #263d4f;border-radius:16px;}
QFrame#hero {background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #173b43,stop:1 #182b43);border:1px solid #326161;border-radius:20px;}
QLabel {background:transparent;} QLabel#muted {color:#9bb1c3;} QLabel#title {font-size:31px;font-weight:700;}
QLabel#eyebrow {color:#65dfbb;font-size:12px;font-weight:700;letter-spacing:2px;} QLabel#big {font-size:45px;font-weight:700;}
QPushButton {background:#20374a;border:1px solid #304c60;border-radius:10px;padding:12px 18px;font-weight:600;}
QPushButton:hover {background:#2b4e63;border-color:#64dfbc;} QPushButton:pressed {background:#355f70;}
QPushButton:disabled {color:#6d8392;background:#172632;} QPushButton#primary {background:#65dfbb;color:#082725;border:0;}
QPushButton#nav {text-align:left;background:transparent;border:0;padding:15px;} QPushButton#nav:checked {background:#234738;color:#8ff4ce;}
QLineEdit,QTextEdit,QComboBox,QSpinBox {background:#101f2e;border:1px solid #30495b;border-radius:9px;padding:10px;selection-background-color:#2f7467;}
QComboBox QAbstractItemView {background:#152b3b;color:#ffffff;selection-background-color:#285a50;}
QProgressBar {border:0;background:#1e3544;border-radius:5px;height:10px;text-align:center;} QProgressBar::chunk {background:#65dfbb;border-radius:5px;}
QTableWidget {background:#122434;gridline-color:#253c4c;border:1px solid #2a4253;border-radius:10px;alternate-background-color:#172d3d;}
QHeaderView::section {background:#203c4b;color:#a9c9d6;padding:12px;border:0;font-weight:600;}
QScrollArea {border:0;} QScrollBar:vertical {background:#102131;width:9px;} QScrollBar::handle:vertical {background:#355267;border-radius:4px;min-height:30px;}
QCheckBox {spacing:10px;} QToolTip {background:#254456;color:#fff;}
'''
LIGHT=DARK.replace('#0b1420','#edf3f6').replace('#eaf1f6','#152b3d').replace('#101f2d','#e1ebf1').replace('#142434','#ffffff').replace('#101f2e','#f6f9fc').replace('#9bb1c3','#536e82').replace('#122434','#ffffff').replace('#172d3d','#edf4f8').replace('#152b3b','#ffffff')

LIGHT+='QFrame#hero QLabel {color:#edf6fa;} QPushButton {background:#d8e6ed;color:#173449;} QPushButton:hover {background:#c5dce4;} QPushButton#nav:checked {background:#c4e9dc;color:#174337;} QPushButton#primary {background:#53cba9;color:#082725;} QLabel#eyebrow {color:#26755c;}'

def label(text,kind=None):
    w=QLabel(text); w.setWordWrap(True)
    if kind:w.setObjectName(kind)
    return w

def button(text,fn,primary=False):
    w=QPushButton(text);w.setCursor(Qt.PointingHandCursor);w.clicked.connect(fn)
    if primary:w.setObjectName('primary')
    return w

def card(title,subtitle='',hero=False):
    w=QFrame();w.setObjectName('hero' if hero else 'card');l=QVBoxLayout(w);l.setContentsMargins(22,20,22,20);l.setSpacing(12)
    if title:l.addWidget(label(title,'title' if hero else None))
    if subtitle:l.addWidget(label(subtitle,'muted'))
    return w,l

class Worker(QThread):
    done=Signal(object); failed=Signal(str); progress=Signal(object)
    def __init__(self,fn):super().__init__();self.fn=fn
    def run(self):
        try:self.done.emit(self.fn(self.progress.emit))
        except Exception as e:self.failed.emit(str(e))

class PointImage(QLabel):
    clicked=Signal(float,float)
    def mousePressEvent(self,event):
        if self.pixmap() and not self.pixmap().isNull():
            p=event.position();pm=self.pixmap();left=(self.width()-pm.width())/2;top=(self.height()-pm.height())/2
            x=(p.x()-left)/pm.width();y=(p.y()-top)/pm.height()
            if 0<=x<=1 and 0<=y<=1:self.clicked.emit(x,y)

class Calibration(QDialog):
    def __init__(self,parent,path,players,existing):
        super().__init__(parent);self.setWindowTitle('Calibrate the camera view');self.resize(950,760);self.data=json.loads(json.dumps(existing));self.points={}
        import cv2
        cap=cv2.VideoCapture(str(path));ok,frame=cap.read();cap.release()
        if not ok:raise ValueError('Cannot read first video frame.')
        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB);h,w=rgb.shape[:2];self.base=QImage(rgb.data,w,h,rgb.strides[0],QImage.Format_RGB888).copy()
        box=QVBoxLayout(self);box.addWidget(label('Click actual positions in the first video frame. Everyone should stand apart at the start.','muted'))
        self.choice=QComboBox();self.roles=[f'Player {p}' for p in players]
        for t in sorted(set(players.values())):self.roles += [f'Goal {t} top-left',f'Goal {t} bottom-right']
        self.roles += ['Marker 1','Marker 2','Marker 3','Delivery top-left','Delivery bottom-right']
        self.choice.addItems(self.roles);box.addWidget(self.choice)
        self.image=PointImage();self.image.setAlignment(Qt.AlignCenter);self.image.setPixmap(QPixmap.fromImage(self.base).scaled(880,480,Qt.KeepAspectRatio,Qt.SmoothTransformation));self.image.clicked.connect(self.click);box.addWidget(self.image)
        self.info=label('Goal A means the goal where team A SCORES. Only calibrate items needed for your game.','muted');box.addWidget(self.info)
        self.log=QTextEdit();self.log.setReadOnly(True);self.log.setMaximumHeight(95);box.addWidget(self.log)
        controls=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);controls.accepted.connect(self.save);controls.rejected.connect(self.reject);box.addWidget(controls)
    def click(self,x,y):
        role=self.choice.currentText();self.points[role]=[round(x,4),round(y,4)];self.log.setPlainText('\n'.join(f'{k}: {v}' for k,v in self.points.items()));self.choice.setCurrentIndex(min(self.choice.currentIndex()+1,self.choice.count()-1))
    def save(self):
        for role,xy in self.points.items():
            if role.startswith('Player '):self.data.setdefault('players',{})[role[7:]]=xy
            elif role.startswith('Marker '):self.data.setdefault('markers',{})[role[7:]]=xy
        for prefix in [f'Goal {t}' for t in sorted(set(self.parent().players.values()))]+['Delivery']:
            a=self.points.get(prefix+' top-left');b=self.points.get(prefix+' bottom-right')
            if a and b:
                rect=[min(a[0],b[0]),min(a[1],b[1]),max(a[0],b[0]),max(a[1],b[1])]
                if prefix=='Delivery':self.data['delivery']=rect
                else:self.data.setdefault('goals',{})[prefix[5:]]=rect
        self.accept()

class Studio(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle('Family AI Game Day • Team 105');self.resize(1380,900);self.setMinimumSize(1050,720)
        self.secret=local_secret(DATA);self.players={};self.points={};self.possession={};self.history=[];self.applied=set();self.round=1;self.turn=0;self.total_rounds=3;self.finished=False;self.pending=None;self.clip='';self.calibration={};self.worker=None;self.running=False;self.remaining=30;self.recording=False;self.session_id=str(uuid.uuid4());self.theme=False
        central=QWidget();self.setCentralWidget(central);root=QHBoxLayout(central);root.setContentsMargins(0,0,0,0);root.setSpacing(0)
        side=QFrame();side.setObjectName('sidebar');side.setFixedWidth(225);s=QVBoxLayout(side);s.setContentsMargins(18,30,18,20)
        s.addWidget(label('FAMILY\nGAME DAY','title'));s.addWidget(label('AI HOST • TEAM 105','eyebrow'));s.addSpacing(35)
        self.stack=QStackedWidget();self.nav=[]
        for i,name in enumerate(['◈  Game library','◎  Match setup','▶  Game arena','▤  Results & replay','⚙  AI & settings']):
            b=button(name,lambda checked=False,i=i:self.navigate(i));b.setObjectName('nav');b.setCheckable(True);s.addWidget(b);self.nav.append(b)
        s.addStretch();s.addWidget(label('CHAMPIONS / 2026','eyebrow'));s.addWidget(label('Real play. Clear evidence.\nOne family, five challenges.','muted'));s.addWidget(button('Switch theme',self.toggle_theme))
        root.addWidget(side);area=QWidget();a=QVBoxLayout(area);a.setContentsMargins(24,16,24,12);a.addWidget(self.stack,1)
        self.status=label('Ready • Choose a game to begin.','muted');a.addWidget(self.status);root.addWidget(area,1)
        self.library_page();self.setup_page();self.arena_page();self.results_page();self.settings_page()
        self.timer=QTimer(self);self.timer.timeout.connect(self.tick);self.timer.start(100)
        self.navigate(0);self.update_models();self.load_preferences()
        QShortcut(QKeySequence('F11'),self,activated=lambda:self.showNormal() if self.isFullScreen() else self.showFullScreen())
        QShortcut(QKeySequence('Escape'),self,activated=self.showNormal)
        QShortcut(QKeySequence('Ctrl+O'),self,activated=self.choose_clip)
        QShortcut(QKeySequence('Ctrl+S'),self,activated=self.export_results)
    def page(self,title,sub):
        content=QWidget();l=QVBoxLayout(content);l.setContentsMargins(4,5,12,10);l.setSpacing(18);l.addWidget(label(title,'title'));l.addWidget(label(sub,'muted'))
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(content);self.stack.addWidget(scroll);return l
    def navigate(self,i):
        self.stack.setCurrentIndex(i)
        for k,b in enumerate(self.nav):b.setChecked(k==i)
        effect=QGraphicsOpacityEffect(self.stack);self.stack.setGraphicsEffect(effect);self.animation=QPropertyAnimation(effect,b'opacity',self);self.animation.setDuration(180);self.animation.setStartValue(.35);self.animation.setEndValue(1.0);self.animation.start()
    def toggle_theme(self):self.theme=not self.theme;QApplication.instance().setStyleSheet(LIGHT if self.theme else DARK)
    def library_page(self):
        l=self.page('Your next family game starts here.','A shared game collection, a host in control, and AI observations you can inspect.')
        w,c=card('Make time for real play.','Football, movement, teamwork and storytelling — hosted in one desktop workspace.',True);c.addWidget(label('05 GAMES     •     TEAM + SOLO     •     LOCAL AI OPTION','eyebrow'));l.addWidget(w)
        grid=QGridLayout();icons=['01','02','03','04','05'];descs=['Track goals and observed possession. Celebrate a player MVP.','Carry a soft object on a tray. Deliver, return and work together.','Move with the family. Hold still when the host says freeze.','Follow a six-step route across numbered floor markers.','Build a shared story using family, desert and kindness.']
        for i,(name,spec) in enumerate(GAMES.items()):
            w,c=card(icons[i]+'  '+name,descs[i]);c.addWidget(label(spec['mode'].upper()+'  /  '+('60 SEC' if i==0 else '30 SEC'),'eyebrow'));c.addWidget(button('Set up this game →',lambda checked=False,n=name:self.select_game(n),True));grid.addWidget(w,i//2,i%2)
        l.addLayout(grid);l.addStretch()
    def select_game(self,name):self.game.setCurrentText(name);self.navigate(1)
    def setup_page(self):
        l=self.page('Build your match.','Set the people, rules and identification details before the first turn.')
        w,c=card('Match details');row=QHBoxLayout();self.game=QComboBox();self.game.addItems(GAMES);self.game.currentTextChanged.connect(self.change_rules);self.rounds=QSpinBox();self.rounds.setRange(1,10);self.rounds.setValue(3);row.addWidget(label('Game'));row.addWidget(self.game,1);row.addWidget(label('Rounds'));row.addWidget(self.rounds);c.addLayout(row);self.rules=label(GAMES['Football']['rules'],'muted');c.addWidget(self.rules);l.addWidget(w)
        row=QHBoxLayout();w,c=card('Players & teams','One per line: player ID, team. Use clearly distinguishable shirts.');self.roster=QTextEdit();self.roster.setPlainText('P1, A\nP2, A\nP3, B\nP4, B');self.roster.setMaximumHeight(150);c.addWidget(self.roster);row.addWidget(w)
        w,c=card('What should the judge know?','Describe visible shirt numbers, colours and goal direction.');self.context=QTextEdit();self.context.setPlaceholderText('P1: red shirt #1; P2: red #2; P3: blue #3; P4: blue #4. Team A attacks the right goal…');self.context.setMaximumHeight(150);c.addWidget(self.context);row.addWidget(w);l.addLayout(row)
        w,c=card('Choose an AI engine');self.engine=QComboBox();self.engine.addItems(['Local AI • offline after model download','Cloud AI • Gemini video + audio']);c.addWidget(self.engine);c.addWidget(label('Local mode proposes observations for host review. Cloud mode reasons over video and audio. All scores use the displayed game rules.','muted'));l.addWidget(w)
        l.addWidget(button('Everyone ready — start match →',self.start_match,True));l.addStretch()
    def change_rules(self,name):self.rules.setText(GAMES[name]['rules'])
    def start_match(self):
        if self.is_busy():return
        try:
            roster={}
            for line in self.roster.toPlainText().strip().splitlines():
                p=[x.strip() for x in line.split(',')]
                if len(p)!=2 or not all(p) or p[0] in roster or max(map(len,p))>24:raise ValueError('Use unique IDs, one player per line: P1, A')
                roster[p[0]]=p[1]
            if not 2<=len(roster)<=12:raise ValueError('Enter between 2 and 12 players.')
            if GAMES[self.game.currentText()]['mode']=='Team' and len(set(roster.values()))!=2:raise ValueError('Team games require exactly two teams.')
            if self.history and QMessageBox.question(self,'Start new match','Current match is saved locally. Start a new match?')!=QMessageBox.Yes:return
            self.players=roster;self.active_game=self.game.currentText();self.host_context=self.context.toPlainText();self.active_engine=self.engine.currentIndex();self.total_rounds=self.rounds.value();self.round=1;self.turn=0;self.finished=False;self.points=dict.fromkeys(roster,0);self.possession=dict.fromkeys(roster,0.0);self.history=[];self.applied=set();self.calibration={};self.session_id=str(uuid.uuid4());self.pending=None;self.clip='';self.player.stop();self.clip_label.setText('No clip selected. Record or upload fresh gameplay.');self.evidence.clear();self.review.setChecked(False);self.apply_button.setEnabled(False);self.reset_clock();self.refresh();self.autosave();self.navigate(2)
        except ValueError as e:self.error(str(e))
    def arena_page(self):
        l=self.page('The game arena.','Record real play, inspect what the AI sees, and apply explained decisions.')
        row=QHBoxLayout();self.turn_label=label('Set up a match first.','title');row.addWidget(self.turn_label,1);self.clock=label('00:30','big');row.addWidget(self.clock);l.addLayout(row)
        row=QHBoxLayout();self.video=QVideoWidget();self.video.setMinimumHeight(260);self.video.setMaximumHeight(340);row.addWidget(self.video,3)
        w,c=card('Host controls');self.timer_button=button('Start / pause timer',self.toggle_timer);c.addWidget(self.timer_button);c.addWidget(button('Reset timer',self.reset_clock));self.camera_button=button('Start camera',self.start_camera);c.addWidget(self.camera_button);self.record_button=button('● Record with audio',self.record);c.addWidget(self.record_button);c.addWidget(button('Stop camera / recording',self.stop_camera));row.addWidget(w,1);l.addLayout(row)
        self.player=QMediaPlayer(self);self.audio=QAudioOutput(self);self.player.setAudioOutput(self.audio);self.player.setVideoOutput(self.video);self.player.errorOccurred.connect(lambda *args:self.status.setText('Playback: '+self.player.errorString()))
        self.capture=QMediaCaptureSession(self);self.recorder=QMediaRecorder(self);self.capture.setRecorder(self.recorder);self.recorder.errorOccurred.connect(lambda *args:self.error('Recording: '+self.recorder.errorString()));self.camera=None
        row=QHBoxLayout()
        for text,fn in [('Upload clip',self.choose_clip),('Play / pause',self.play_pause),('Calibrate local AI',self.calibrate),('Open video externally',self.open_external)]:row.addWidget(button(text,fn))
        l.addLayout(row);self.clip_label=label('No clip selected. Use the built-in camera or upload a gameplay recording.','muted');l.addWidget(self.clip_label)
        row=QHBoxLayout();self.judge_button=button('Analyse gameplay →',self.judge,True);row.addWidget(self.judge_button);row.addWidget(button('Import signed report',self.import_report));row.addWidget(button('Export signed report',self.export_report));l.addLayout(row)
        self.progress=QProgressBar();self.progress.setValue(0);l.addWidget(self.progress)
        self.evidence=QTextEdit();self.evidence.setReadOnly(True);self.evidence.setMinimumHeight(170);self.evidence.setPlaceholderText('Timestamped observations, transcript, possession and limitations appear here.');l.addWidget(self.evidence)
        self.review=QCheckBox('I reviewed the local AI candidates against the footage and confirm every listed event.');self.review.setVisible(False);self.review.toggled.connect(self.update_apply);l.addWidget(self.review)
        row=QHBoxLayout();self.apply_button=button('Apply results & next turn →',self.apply_report,True);self.apply_button.setEnabled(False);row.addWidget(self.apply_button);row.addWidget(button('Skip turn',self.skip));row.addWidget(button('View scoreboard',lambda:self.navigate(3)));l.addLayout(row)
    def reset_clock(self):self.running=False;self.remaining=60 if getattr(self,'active_game','')=='Football' else 30;self.show_clock()
    def show_clock(self):s=int(self.remaining+.99);self.clock.setText(f'{s//60:02d}:{s%60:02d}')
    def toggle_timer(self):
        if not self.players or self.finished:return
        if self.running:self.remaining=max(0,self.deadline-time.monotonic());self.running=False
        else:
            if self.remaining<=0:self.reset_clock()
            self.deadline=time.monotonic()+self.remaining;self.running=True
    def tick(self):
        if self.running:
            self.remaining=max(0,self.deadline-time.monotonic());self.show_clock()
            if self.remaining<=0:self.running=False;QApplication.beep();self.status.setText('Time is up. Stop the recording and analyse the clip.')
    def start_camera(self):
        if self.is_busy():return
        if self.camera:return
        devices=QMediaDevices.videoInputs()
        if not devices:self.error('No camera available. Upload a phone recording instead.');return
        self.player.stop();self.camera=QCamera(devices[0],self);self.camera.errorOccurred.connect(lambda *args:self.status.setText('Camera: '+self.camera.errorString() if self.camera else 'Camera stopped'));self.capture.setCamera(self.camera);self.capture.setVideoOutput(self.video)
        self.mic=QAudioInput(self);self.capture.setAudioInput(self.mic);self.camera.start();self.status.setText('Camera active • microphone enabled for recording.')
    def record(self):
        if self.is_busy():return
        if self.recording:self.recorder.stop();self.recording=False;self.record_button.setText('● Record with audio');self.status.setText('Recording saved. Stop camera to replay.');return
        self.start_camera()
        if not self.camera:return
        folder=DATA/'recordings';folder.mkdir(exist_ok=True);self.clip=str(folder/(time.strftime('%Y%m%d-%H%M%S')+'.mp4'));self.recorder.setOutputLocation(QUrl.fromLocalFile(self.clip));self.recorder.setQuality(QMediaRecorder.NormalQuality);self.recorder.record();self.recording=True;self.record_button.setText('■ Stop recording');self.clip_label.setText(Path(self.clip).name)
    def stop_camera(self):
        if self.recording:self.recorder.stop();self.recording=False;self.record_button.setText('● Record with audio')
        if self.camera:self.camera.stop();self.capture.setCamera(None);self.camera.deleteLater();self.camera=None
        self.capture.setVideoOutput(None);self.player.setVideoOutput(self.video)
        if self.clip:self.player.setSource(QUrl.fromLocalFile(self.clip))
    def choose_clip(self):
        if self.is_busy():return
        path,_=QFileDialog.getOpenFileName(self,'Gameplay video','','Video (*.mp4 *.mov *.webm *.avi)')
        if path:self.stop_camera();self.clip=path;self.pending=None;self.review.setChecked(False);self.apply_button.setEnabled(False);self.clip_label.setText(Path(path).name);self.player.setSource(QUrl.fromLocalFile(path));self.player.play()
    def play_pause(self):
        if self.camera:self.stop_camera()
        if self.player.playbackState()==QMediaPlayer.PlayingState:self.player.pause()
        elif self.clip:self.player.play()
    def open_external(self):
        if self.clip:
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.clip))
    def calibrate(self):
        if not self.clip or not self.players:self.error('Start a match and choose its video first.');return
        try:
            dialog=Calibration(self,self.clip,self.players,self.calibration)
            if dialog.exec():self.calibration=dialog.data;self.autosave();self.status.setText('Camera calibration saved for this match.')
        except Exception as e:self.error(str(e))
    def current_player(self):return list(self.players)[self.turn%len(self.players)]
    def is_busy(self):return self.worker is not None and self.worker.isRunning()
    def task(self,fn,done):
        if self.is_busy():self.error('An AI task is still running.');return
        self.worker=Worker(fn);self.worker.progress.connect(self.task_progress);self.worker.done.connect(done);self.worker.failed.connect(self.task_error);self.worker.finished.connect(self.task_finished);self.progress.setRange(0,0);self.judge_button.setEnabled(False);self.worker.start()
    def task_progress(self,value):
        if isinstance(value,int):self.progress.setRange(0,100);self.progress.setValue(value)
        else:self.status.setText(str(value))
    def task_error(self,message):
        if 'No module named' in message:message+='\nRun Install-Local-AI.bat from the extracted project folder, then reopen the app.'
        self.error(message);self.status.setText('Task failed • scores unchanged.')
    def task_finished(self):self.progress.setRange(0,100);self.progress.setValue(100);self.judge_button.setEnabled(True);self.update_models()
    def judge(self):
        if not self.players or self.finished:self.error('Start an active match first.');return
        if not self.clip or self.recording:self.error('Choose a video or stop recording first.');return
        self.player.pause();self.pending=None;self.apply_button.setEnabled(False)
        if self.active_engine==0:
            from local_ai import analyze_local
            args=(self.clip,self.active_game,dict(self.players),self.current_player(),self.host_context,json.loads(json.dumps(self.calibration)))
            self.status.setText('Local AI analysing on this PC…')
            self.task(lambda progress:sign(analyze_local(*args,progress),self.secret),self.receive_report)
        else:
            args=(self.clip,self.api.text(),self.model.text(),self.active_game,dict(self.players),self.current_player(),self.host_context)
            self.status.setText('Cloud AI analysing video and audio…')
            self.task(lambda progress:sign(analyze(*args),self.secret),self.receive_report)
    def receive_report(self,envelope):
        try:
            r=verify(envelope,self.secret);validate(r,self.active_game,self.players,self.current_player())
            if r.get('roster')!=self.players or r.get('turn_player')!=self.current_player() or r.get('host_context')!=self.host_context:raise ValueError('Report belongs to a different setup or turn.')
            self.render_report(envelope)
        except Exception as e:self.error(str(e))
    def render_report(self,envelope):
            r=envelope['report']
            self.pending=envelope;self.review.setChecked(False);self.review.setVisible(bool(r.get('review_required')))
            text=r['summary']+'\n\n'
            for e in r['events']:text+=f"{e['time']:.1f}s  /  {e['player']}  /  {e['kind']}  /  {e['confidence']:.0%}\n{e['evidence']}\n\n"
            if r.get('transcript'):text+='TRANSCRIPT\n'+r['transcript']+'\n\n'
            if r['possession']:text+='POSSESSION ESTIMATES\n'+'\n'.join(f"{p['player']}: {p['start']}–{p['end']} seconds" for p in r['possession'])+'\n\n'
            text+='LIMITATIONS\n'+'\n'.join(r['limitations']);self.evidence.setPlainText(text);self.update_apply();self.status.setText('Evidence ready. Inspect the clip before applying results.')
    def update_apply(self):
        r=self.pending['report'] if self.pending else {};self.apply_button.setEnabled(bool(r) and (r.get('status')=='ok' or (r.get('review_required') and self.review.isChecked())))
    def apply_report(self):
        if self.is_busy() or not self.pending or self.finished:return
        try:
            r=verify(self.pending,self.secret);validate(r,self.active_game,self.players,self.current_player())
            if r['video_sha256'] in self.applied:raise ValueError('This clip has already been applied in this match.')
            envelope=self.pending
            if r.get('review_required'):
                if not self.review.isChecked():raise ValueError('Local candidates require footage review first.')
                r=json.loads(json.dumps(r));r['status']='ok';r['human_reviewed']=True;r['reviewed_at']=time.strftime('%Y-%m-%dT%H:%M:%S');envelope=sign(r,self.secret)
            if r['status']!='ok':raise ValueError('Uncertain evidence cannot be scored.')
            delta,pos=score(r,self.players)
            for p in self.players:self.points[p]+=delta[p];self.possession[p]+=pos[p]
            self.applied.add(r['video_sha256']);self.history.append({'round':self.round,'turn':self.current_player(),'clip':self.clip,'signed_evidence':envelope});self.advance()
        except Exception as e:self.error(str(e))
    def advance(self):
        if self.active_game=='Football':self.round+=1
        else:
            self.turn+=1
            if self.turn%len(self.players)==0:self.round+=1
        self.finished=self.round>self.total_rounds;self.pending=None;self.review.setChecked(False);self.apply_button.setEnabled(False);self.reset_clock();self.refresh();self.autosave()
        self.status.setText('Match complete. Review results and export evidence.' if self.finished else 'Next turn ready. Choose a fresh clip before judging.')
        if self.finished:self.navigate(3)
    def skip(self):
        if not self.players or self.finished or self.is_busy():return
        if QMessageBox.question(self,'Skip turn','Record a skipped turn with zero points?')==QMessageBox.Yes:self.history.append({'round':self.round,'turn':self.current_player(),'skipped':True});self.advance()
    def results_page(self):
        l=self.page('The family scoreboard.','Saved scores, explained decisions and replayable moments.')
        w,c=card('Match overview',hero=True);self.outcome=label('Start a game to see results.','title');c.addWidget(self.outcome);self.mvp=label('Possession MVP appears for football.','muted');c.addWidget(self.mvp);l.addWidget(w)
        self.table=QTableWidget(0,4);self.table.setHorizontalHeaderLabels(['Player','Team','Points','Possession (seconds)']);self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);self.table.setAlternatingRowColors(True);self.table.setEditTriggers(QTableWidget.NoEditTriggers);self.table.setMinimumHeight(240);l.addWidget(self.table)
        self.history_box=QComboBox();self.history_box.setMinimumWidth(200);l.addWidget(self.history_box)
        row=QHBoxLayout()
        for text,fn in [('Replay selected turn',self.replay),('Export full results',self.export_results),('Extra round',self.extra_round),('Resume saved match',self.resume)]:row.addWidget(button(text,fn))
        l.addLayout(row);self.audit=QTextEdit();self.audit.setReadOnly(True);self.audit.setMaximumHeight(150);l.addWidget(self.audit);l.addStretch()
    def refresh(self):
        if not self.players:return
        self.turn_label.setText(self.active_game+'\n'+('Match complete' if self.finished else f'Round {self.round}/{self.total_rounds} • '+('All players' if self.active_game=='Football' else self.current_player())))
        ranked=sorted(self.players,key=lambda p:self.points[p],reverse=True);self.table.setRowCount(len(ranked))
        for i,p in enumerate(ranked):
            for j,v in enumerate([p,self.players[p],self.points[p],f'{self.possession[p]:.1f}' if self.active_game=='Football' else '—']):self.table.setItem(i,j,QTableWidgetItem(str(v)))
        totals={}
        for p in self.players:
            entity=self.players[p] if GAMES[self.active_game]['mode']=='Team' else p;totals[entity]=totals.get(entity,0)+self.points[p]
        best=max(totals.values());leaders=[k for k,v in totals.items() if v==best];self.outcome.setText(('Tie: ' if len(leaders)>1 else ('Winner: ' if self.finished else 'Leader: '))+', '.join(leaders)+'\n'+'   ·   '.join(f'{k}  {v}' for k,v in totals.items()))
        top=max(self.possession.values());mvp=', '.join(p for p in self.players if abs(self.possession[p]-top)<.001) if top else 'Awaiting evidence'
        teampos={t:sum(self.possession[p] for p in self.players if self.players[p]==t) for t in set(self.players.values())}
        self.mvp.setText(('Possession MVP: '+mvp+'\n'+'  ·  '.join(f'Team {t}: {v:.1f}s' for t,v in teampos.items())) if self.active_game=='Football' else 'Individual turns contribute to the displayed game standings.')
        self.history_box.clear();self.audit.clear()
        for h in self.history:
            self.history_box.addItem(f"Round {h['round']} / {h['turn']}"+(' / skipped' if h.get('skipped') else ' / AI evidence'))
            if not h.get('skipped'):self.audit.append(h['signed_evidence']['report']['summary'])
    def replay(self):
        i=self.history_box.currentIndex()
        if i>=0 and self.history[i].get('clip'):
            path=self.history[i]['clip']
            if not Path(path).exists():self.error('Original clip is no longer available at its saved path.');return
            self.clip=path;self.stop_camera();self.player.setSource(QUrl.fromLocalFile(path));self.player.play();self.navigate(2);self.render_report(self.history[i]['signed_evidence']);self.pending=None;self.review.setVisible(False);self.apply_button.setEnabled(False)
    def extra_round(self):
        if not self.players or self.is_busy():return
        if not self.finished:self.error('Complete the current rounds first.');return
        self.total_rounds=self.round;self.finished=False;self.refresh();self.autosave();self.navigate(2)
    def payload(self):return {k:getattr(self,k) for k in ['session_id','players','points','possession','history','round','turn','total_rounds','finished','active_game','active_engine','host_context','calibration']}|{'applied':list(self.applied)}
    def autosave(self):
        if not self.players:return
        try:
            folder=DATA/'sessions';folder.mkdir(exist_ok=True);path=folder/(self.session_id+'.json');temp=path.with_suffix('.tmp');temp.write_text(json.dumps(sign(self.payload(),self.secret),indent=2),encoding='utf-8');temp.replace(path)
        except OSError as e:self.status.setText('Autosave failed: '+str(e))
    def resume(self):
        if self.is_busy():return
        path,_=QFileDialog.getOpenFileName(self,'Resume a signed session',str(DATA/'sessions'),'JSON (*.json)')
        if path:
            try:
                data=verify(json.loads(Path(path).read_text(encoding='utf-8')),self.secret)
                for k,v in data.items():setattr(self,k,set(v) if k=='applied' else v)
                self.pending=None;self.reset_clock();self.refresh();self.navigate(2);self.status.setText('Saved match restored.')
            except Exception as e:self.error(str(e))
    def save_json(self,data,name):
        path,_=QFileDialog.getSaveFileName(self,'Save file',name,'JSON (*.json)')
        if path:
            try:Path(path).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8');self.status.setText('Saved '+Path(path).name)
            except OSError as e:self.error(str(e))
    def export_results(self):
        if self.players:self.save_json(sign(self.payload(),self.secret),'family-game-results.json')
    def import_report(self):
        if not self.players or self.is_busy() or self.finished:return
        path,_=QFileDialog.getOpenFileName(self,'Import signed evidence','','JSON (*.json)')
        if path:
            try:self.receive_report(json.loads(Path(path).read_text(encoding='utf-8')))
            except Exception as e:self.error(str(e))
    def export_report(self):
        if self.pending:self.save_json(self.pending,'judge-report.json')
    def settings_page(self):
        l=self.page('AI that fits your setup.','Local models for offline observations, optional cloud reasoning, and clear control over your data.')
        w,c=card('Built-in local AI','YOLO11n detects people and sports balls. YOLO11n Pose estimates body landmarks. Vosk transcribes English speech. Models download once; footage is processed on your PC in local mode.');self.models_status=label('Checking model files…','eyebrow');c.addWidget(self.models_status);c.addWidget(button('Download / prepare local models',self.prepare_models,True));c.addWidget(label('Install local dependencies first using Install-Local-AI.bat. Downloads include pretrained weights and a roughly 40 MB speech model. First setup requires internet. Local candidate decisions require host review.','muted'));l.addWidget(w)
        w,c=card('Optional cloud judge','Only the Cloud engine sends selected footage to Google when Analyse is clicked.');self.api=QLineEdit(os.getenv('GEMINI_API_KEY',''));self.api.setEchoMode(QLineEdit.Password);self.api.setPlaceholderText('Gemini API key — memory only');self.model=QLineEdit(os.getenv('GEMINI_MODEL',DEFAULT_MODEL));c.addWidget(self.api);c.addWidget(self.model);l.addWidget(w)
        w,c=card('Your workspace','Matches autosave after each turn. Keys and recordings remain outside source control.');c.addWidget(button('Open saved sessions folder',self.open_data));c.addWidget(button('Save setup preferences',self.save_preferences));c.addWidget(label('Local AI is an experimental assistant. Whole-ball goal crossing, identities during player crossings, tray support and sentence coherence require review. Use a fixed camera and retain original recordings.','muted'));l.addWidget(w);l.addStretch()
    def prepare_models(self):
        from local_ai import download_models
        self.task(lambda progress:download_models(progress),lambda result:self.status.setText('Local models ready. Choose Local AI in Match setup.'))
    def update_models(self):
        names=['yolo11n.pt','yolo11n-pose.pt','vosk-model-small-en-us-0.15'];count=sum((ROOT/'models'/n).exists() for n in names);self.models_status.setText(f'{count}/3 local model files ready')
    def open_data(self):
        from PySide6.QtGui import QDesktopServices
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(DATA)))
    def save_preferences(self):
        try:(DATA/'preferences.json').write_text(json.dumps({'roster':self.roster.toPlainText(),'context':self.context.toPlainText(),'model':self.model.text(),'theme':self.theme}),encoding='utf-8');self.status.setText('Preferences saved. API key was not saved.')
        except OSError as e:self.error(str(e))
    def load_preferences(self):
        try:
            p=json.loads((DATA/'preferences.json').read_text(encoding='utf-8'));self.roster.setPlainText(p.get('roster',''));self.context.setPlainText(p.get('context',''));self.model.setText(p.get('model',DEFAULT_MODEL))
            if p.get('theme'):self.toggle_theme()
        except (OSError,ValueError):pass
    def error(self,text):QMessageBox.warning(self,'Family AI Game Day',text)
    def closeEvent(self,event):
        if self.is_busy():self.error('Wait for the current AI task to finish before closing.');event.ignore();return
        self.autosave();self.stop_camera();self.player.stop();event.accept()

if __name__=='__main__':
    app=QApplication(sys.argv);app.setStyle('Fusion');app.setStyleSheet(DARK);window=Studio();window.show();sys.exit(app.exec())
