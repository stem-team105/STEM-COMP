"""RALLY: a calm family-first desktop experience over the tested match engine."""
import html,json,os,sys,time,uuid
from pathlib import Path
from PySide6.QtCore import Qt,QTimer,QUrl,QPropertyAnimation,QEasingCurve
from PySide6.QtGui import QPixmap,QIcon,QShortcut,QKeySequence,QDesktopServices
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QFrame,QStackedWidget,QLineEdit,QTextEdit,QComboBox,QSpinBox,QProgressBar,QFileDialog,QMessageBox,QTableWidget,QTableWidgetItem,QHeaderView,QScrollArea,QGraphicsOpacityEffect,QCheckBox,QSlider,QStackedLayout,QListWidget,QListWidgetItem,QAbstractItemView)
from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput,QMediaDevices,QCamera,QAudioInput,QMediaCaptureSession,QMediaRecorder
from PySide6.QtMultimediaWidgets import QVideoWidget
import session_ui
from session_ui import Studio as MatchEngine,Calibration
from core import GAMES,local_secret,sign,verify,validate
from judge import DEFAULT_MODEL
from ui_kit import theme,label,button,card,GameArt,GAME_INFO
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'.local';DATA.mkdir(exist_ok=True)
LIGHT=theme(False);DARK=theme(True)

class Studio(MatchEngine):
    def __init__(self):
        # Only the presentation changes. The inherited engine still validates every score.
        QMainWindow.__init__(self);session_ui.DATA=DATA
        self.setWindowTitle('RALLY — Bring everyone into play');self.setWindowIcon(QIcon(str(ROOT/'assets/rally-mark.svg')));self.resize(1240,900);self.setMinimumSize(850,680)
        self.secret=local_secret(DATA);self.players={};self.points={};self.possession={};self.history=[];self.applied=set();self.round=1;self.turn=0;self.total_rounds=3;self.finished=False;self.pending=None;self.clip='';self.calibration={};self.worker=None;self.running=False;self.remaining=30;self.recording=False;self.session_id=str(uuid.uuid4());self.theme=False;self.favourites=set();self.motion=True;self.filter_name='All games';self.updating_roster=False
        self.stack=QStackedWidget();self.nav=[];self.pages=[];self.game_cards={};self.fav_buttons={}
        central=QWidget();self.setCentralWidget(central);outer=QVBoxLayout(central);outer.setContentsMargins(24,16,24,14);outer.setSpacing(12)
        top=QFrame();top.setObjectName('topbar');header=QHBoxLayout(top);header.setContentsMargins(22,5,16,5)
        self.brand=QLabel();self.brand.setFixedSize(110,48);self.brand.setPixmap(QPixmap(str(ROOT/'assets/rally-logo.svg')).scaled(110,48,Qt.KeepAspectRatio,Qt.SmoothTransformation));header.addWidget(self.brand);header.addStretch();tagline=label('A little play. A lot closer.','muted');tagline.setWordWrap(False);header.addWidget(tagline);header.addStretch();self.theme_button=button('Appearance',self.toggle_theme);self.theme_button.setObjectName('ghost');header.addWidget(self.theme_button);header.addWidget(button('Settings',lambda:self.navigate(4)));outer.addWidget(top)
        outer.addWidget(self.stack,1)
        dock_holder=QHBoxLayout();dock_holder.addStretch();dock=QFrame();dock.setObjectName('dock');dock_row=QHBoxLayout(dock);dock_row.setContentsMargins(7,6,7,6);dock_row.setSpacing(4)
        for i,title in enumerate(['Home','Family','Play','Moments']):
            b=button(title,lambda checked=False,i=i:self.navigate(i));b.setObjectName('tab');b.setCheckable(True);b.setMinimumWidth(100);dock_row.addWidget(b);self.nav.append(b)
        dock_holder.addWidget(dock);dock_holder.addStretch();outer.addLayout(dock_holder)
        self.status=label('Choose something fun for today.','muted');self.status.setAlignment(Qt.AlignCenter);self.status.setMinimumHeight(22);outer.addWidget(self.status)
        self.library_page();self.setup_page();self.arena_page();self.results_page();self.settings_page()
        self.timer=QTimer(self);self.timer.timeout.connect(self.tick);self.timer.start(100)
        self.load_preferences();self.update_models();self.refresh_saved();self.show_clock();self.navigate(0);QApplication.instance().setStyleSheet(theme(self.theme))
        for key,fn in [('F11',self.fullscreen),('Escape',self.showNormal),('Ctrl+O',self.choose_clip),('Ctrl+S',self.export_results)]:QShortcut(QKeySequence(key),self,activated=fn)
    def fullscreen(self):self.showNormal() if self.isFullScreen() else self.showFullScreen()
    def page(self,title,sub):
        content=QWidget();l=QVBoxLayout(content);l.setContentsMargins(12,10,12,14);l.setSpacing(20);l.addWidget(label(title,'title'));l.addWidget(label(sub,'muted'))
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setFrameShape(QFrame.NoFrame);scroll.setWidget(content);self.stack.addWidget(scroll);self.pages.append(scroll);return l
    def navigate(self,i):
        if i==2 and not self.players:i=1;self.status.setText('Pick a game and meet your players before you begin.')
        if i==3:self.refresh_saved()
        self.stack.setCurrentIndex(i)
        for k,b in enumerate(self.nav):b.setChecked(k==i)
        if hasattr(self,'animation'):
            self.animation.stop()
            if hasattr(self,'fade_target'):self.fade_target.setGraphicsEffect(None)
        if self.motion and i!=2:
            # Animate the scroll content, not the native video surface.
            target=self.pages[i].widget();self.fade_target=target;effect=QGraphicsOpacityEffect(target);target.setGraphicsEffect(effect);self.animation=QPropertyAnimation(effect,b'opacity',self);self.animation.setDuration(190);self.animation.setEasingCurve(QEasingCurve.OutCubic);self.animation.setStartValue(.65);self.animation.setEndValue(1);self.animation.finished.connect(lambda t=target:t.setGraphicsEffect(None));self.animation.start()
    def toggle_theme(self):
        self.theme=not self.theme;QApplication.instance().setStyleSheet(theme(self.theme));self.brand.setPixmap(QPixmap(str(ROOT/'assets'/('rally-logo-on-dark.svg' if self.theme else 'rally-logo.svg'))).scaled(110,48,Qt.KeepAspectRatio,Qt.SmoothTransformation));self.save_preferences(quiet=True)
    def library_page(self):
        l=self.page('Make room for a little fun.','Five ways to move, laugh and spend time together.')
        hero=QFrame();hero.setObjectName('card');h=QHBoxLayout(hero);h.setContentsMargins(28,26,28,26)
        text=QVBoxLayout();text.addWidget(label('A GOOD PLACE TO START','eyebrow'));text.addWidget(label('No equipment.\nJust your favourite people.','title'));text.addWidget(label('Try Falcon Freeze for a quick, playful break.\nMove, freeze, and see who can hold still.','muted'));row=QHBoxLayout();row.addWidget(button('Try Falcon Freeze  →',lambda:self.select_game('Falcon Freeze'),True));duration=label('30 sec','duration');duration.setMaximumWidth(95);row.addWidget(duration);row.addStretch();text.addLayout(row);h.addLayout(text,1);h.addWidget(GameArt('Falcon Freeze',150));l.addWidget(hero)
        row=QHBoxLayout();browse_title=label('Find your next game','heading');browse_title.setWordWrap(False);row.addWidget(browse_title);row.addStretch();self.filter=QComboBox();self.filter.addItems(['All games','Team games','Individual games','Favourites']);self.filter.currentTextChanged.connect(self.filter_games);row.addWidget(self.filter);l.addLayout(row)
        grid=QGridLayout();grid.setSpacing(16)
        descriptions={'Football':'A friendly match with goals, shared moments and a player MVP.','Majlis Delivery':'Steady hands, a soft ball, and a delivery worth cheering for.','Falcon Freeze':'A quick game of moving, freezing and trying not to laugh.','Dune Steps':'Follow a little trail. Take each step at your own pace.','Family Story Relay':'Three words. One shared adventure. Let your imagination lead.'}
        for i,name in enumerate(GAMES):
            info=GAME_INFO[name];w,c=card();top=QHBoxLayout();top.addWidget(GameArt(name,62));top.addStretch();fav=button('☆',lambda checked=False,n=name:self.favourite(n));fav.setObjectName('ghost');fav.setCheckable(True);fav.setToolTip('Save to favourites');top.addWidget(fav);self.fav_buttons[name]=fav;c.addLayout(top);c.addWidget(label(name,'heading'));c.addWidget(label(descriptions[name],'muted'));row=QHBoxLayout();row.addWidget(label(info[0],'pill'));row.addStretch();row.addWidget(label(info[1],'duration'));c.addLayout(row);c.addWidget(button('Let’s play  →',lambda checked=False,n=name:self.select_game(n),True));grid.addWidget(w,i//2,i%2);self.game_cards[name]=w
        l.addLayout(grid);self.favourite_empty=label('Save a game with the star to find it here.','muted');self.favourite_empty.hide();l.addWidget(self.favourite_empty);l.addStretch()
    def filter_games(self,value):
        self.filter_name=value;shown=0
        for name,w in self.game_cards.items():
            visible=value=='All games' or (value=='Team games' and GAMES[name]['mode']=='Team') or (value=='Individual games' and GAMES[name]['mode']=='Individual') or (value=='Favourites' and name in self.favourites);w.setVisible(visible);shown+=visible
        self.favourite_empty.setVisible(not shown)
    def favourite(self,name):
        self.favourites.symmetric_difference_update({name});self.fav_buttons[name].setText('★' if name in self.favourites else '☆');self.fav_buttons[name].setChecked(name in self.favourites);self.filter_games(self.filter.currentText());self.save_preferences(quiet=True)
    def select_game(self,name):self.game.setCurrentText(name);self.change_rules(name);self.navigate(1)
    def setup_page(self):
        l=self.page('A small plan. Then, play.','Choose a game, gather your people, and check the quick suggestion below.')
        row=QHBoxLayout();self.game=QComboBox();self.game.addItems(GAMES);self.game.currentTextChanged.connect(self.change_rules);row.addWidget(self.game,1);row.addWidget(label('Rounds','muted'));self.rounds=QSpinBox();self.rounds.setRange(1,10);self.rounds.setValue(1);row.addWidget(self.rounds);l.addLayout(row)
        w,c=card();self.tip_heading=label('Before you play','heading');c.addWidget(self.tip_heading);self.tip=label('','muted');c.addWidget(self.tip);row=QHBoxLayout();self.equipment=label('','pill');row.addWidget(self.equipment,1);self.setup_duration=label('60 sec','duration');row.addWidget(self.setup_duration);c.addLayout(row);self.safe_tip=label('','muted');c.addWidget(self.safe_tip);l.addWidget(w)
        w,c=card('Who’s joining?','Use names or short nicknames. For team games, choose A or B.');self.people=QTableWidget(4,2);self.people.setHorizontalHeaderLabels(['Person','Team']);self.people.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);self.people.verticalHeader().hide();self.people.setSelectionBehavior(QAbstractItemView.SelectRows);self.people.setMinimumHeight(190);self.people.setMaximumHeight(230)
        for i in range(4):self.people.setItem(i,0,QTableWidgetItem('P'+str(i+1)));self.people.setItem(i,1,QTableWidgetItem('A' if i<2 else 'B'))
        self.people.cellChanged.connect(self.sync_roster);c.addWidget(self.people);row=QHBoxLayout();row.addWidget(button('+ Add person',self.add_person));row.addWidget(button('Remove selected',self.remove_person));row.addStretch();c.addLayout(row);l.addWidget(w)
        self.roster=QTextEdit();self.roster.hide();self.sync_roster()
        w,c=card('A few helpful details','Who is wearing which colour? For football, which way is each team playing?');self.context=QTextEdit();self.context.setMaximumHeight(90);self.context.setPlaceholderText('P1 wears red. P2 wears blue. Team A scores in the right-hand goal…');c.addWidget(self.context);rules_toggle=button('Read the full rules',lambda:self.rules.setVisible(not self.rules.isVisible()));rules_toggle.setObjectName('ghost');c.addWidget(rules_toggle);self.rules=label(GAMES['Football']['rules'],'muted');self.rules.hide();c.addWidget(self.rules);l.addWidget(w)
        l.addWidget(button('Everyone ready? Start playing  →',self.start_match,True));l.addStretch();self.change_rules('Football')
    def change_rules(self,name):
        if not hasattr(self,'rules'):return
        info=GAME_INFO[name];self.rules.setText(GAMES[name]['rules']);self.tip_heading.setText('Before you play '+name);self.tip.setText('Our suggestion: '+info[5]);self.equipment.setText(info[4]);self.setup_duration.setText(info[1]+' per round' if name=='Football' else info[1]+' per turn');self.safe_tip.setText(info[6])
    def sync_roster(self,*args):
        if self.updating_roster:return
        lines=[]
        for i in range(self.people.rowCount()):lines.append(', '.join(self.people.item(i,j).text().strip() if self.people.item(i,j) else '' for j in range(2)))
        if hasattr(self,'roster'):self.roster.setPlainText('\n'.join(lines))
    def add_person(self):
        if self.people.rowCount()>=12:return
        i=self.people.rowCount();self.people.insertRow(i);self.people.setItem(i,0,QTableWidgetItem('P'+str(i+1)));self.people.setItem(i,1,QTableWidgetItem('A' if i%2==0 else 'B'));self.sync_roster()
    def remove_person(self):
        i=self.people.currentRow()
        if i>=0 and self.people.rowCount()>2:self.people.removeRow(i);self.sync_roster()
    def start_match(self):
        self.sync_roster();super().start_match()
        if self.players:self.save_preferences(quiet=True);self.status.setText('Your round is ready. Record the action or add a video.')
    def arena_page(self):
        l=self.page('Let the good times roll.','Record a turn, look back at the highlights, then save the points.')
        w,c=card();row=QHBoxLayout();col=QVBoxLayout();self.turn_label=label('Set up a game first.','heading');col.addWidget(self.turn_label);self.clock_hint=label('Ready when you are.','muted');col.addWidget(self.clock_hint);row.addLayout(col,1);self.clock=label('00:30');self.clock.setMinimumWidth(170);self.clock.setAlignment(Qt.AlignCenter);row.addWidget(self.clock);c.addLayout(row);self.round_progress=QProgressBar();self.round_progress.setRange(0,1000);self.round_progress.setTextVisible(False);c.addWidget(self.round_progress);row=QHBoxLayout();self.timer_button=button('Start timer',self.toggle_timer,True);row.addWidget(self.timer_button);row.addWidget(button('Reset',self.reset_clock));row.addStretch();row.addWidget(button('Skip this turn',self.skip));c.addLayout(row);l.addWidget(w)
        w,c=card();self.video=QVideoWidget();self.video.setMinimumHeight(250);self.video.setMaximumHeight(350);self.video.setStyleSheet('background:#132F37;border-radius:18px;');video_container=QWidget();video_stack=QStackedLayout(video_container);video_stack.setStackingMode(QStackedLayout.StackAll);video_stack.setContentsMargins(0,0,0,0);video_stack.addWidget(self.video);self.video_empty=QLabel('Your next great moment starts here.\n\nRecord a turn or add a family video.');self.video_empty.setAlignment(Qt.AlignCenter);self.video_empty.setStyleSheet('background:#14343D;color:#D0E7E2;font-size:19px;border-radius:20px;');video_stack.addWidget(self.video_empty);c.addWidget(video_container);self.seek=QSlider(Qt.Horizontal);self.seek.setRange(0,0);c.addWidget(self.seek)
        self.player=QMediaPlayer(self);self.audio=QAudioOutput(self);self.player.setAudioOutput(self.audio);self.player.setVideoOutput(self.video);self.player.errorOccurred.connect(lambda *args:self.status.setText('Could not play the video: '+self.player.errorString()));self.player.sourceChanged.connect(lambda url:self.video_empty.setVisible(url.isEmpty() and not self.camera));self.player.durationChanged.connect(lambda d:self.seek.setRange(0,int(d)));self.player.positionChanged.connect(self.seek.setValue);self.seek.sliderMoved.connect(self.player.setPosition)
        self.capture=QMediaCaptureSession(self);self.recorder=QMediaRecorder(self);self.capture.setRecorder(self.recorder);self.recorder.errorOccurred.connect(lambda *args:self.error('Recording: '+self.recorder.errorString()));self.recorder.recorderStateChanged.connect(self.recorder_state);self.camera=None
        row=QHBoxLayout();self.record_button=button('Record a turn',self.record,True);row.addWidget(self.record_button);row.addWidget(button('Add a video',self.choose_clip));row.addWidget(button('Play / pause',self.play_pause));row.addWidget(button('Close camera',self.stop_camera));c.addLayout(row);self.clip_label=label('Your camera preview or selected recording appears here.','muted');c.addWidget(self.clip_label);l.addWidget(w)
        row=QHBoxLayout();self.judge_button=button('Find this round’s results  →',self.judge,True);row.addWidget(self.judge_button,1);row.addWidget(button('Set up camera view',self.calibrate));l.addLayout(row);self.progress=QProgressBar();self.progress.setRange(0,100);self.progress.setValue(0);self.progress.setTextVisible(False);l.addWidget(self.progress)
        self.result_card,self.result_layout=card('A quick look back','Review the suggested points against your recording. Unclear moments need a closer look.');self.evidence=QTextEdit();self.evidence.setReadOnly(True);self.evidence.setMinimumHeight(150);self.evidence.setMaximumHeight(260);self.evidence.setPlaceholderText('What happened this round will appear here.');self.result_layout.addWidget(self.evidence);self.review=QCheckBox('I checked the suggested points against the recording.');self.review.hide();self.review.toggled.connect(self.update_apply);self.result_layout.addWidget(self.review);self.apply_button=button('Save points & next turn  →',self.apply_report,True);self.apply_button.setEnabled(False);self.result_layout.addWidget(self.apply_button);l.addWidget(self.result_card)
        row=QHBoxLayout();row.addWidget(button('View scoreboard',lambda:self.navigate(3)));detail=button('More recording options',lambda:self.advanced_round.setVisible(not self.advanced_round.isVisible()));detail.setObjectName('ghost');row.addWidget(detail);l.addLayout(row)
        self.advanced_round=QWidget();a=QHBoxLayout(self.advanced_round)
        for text,fn in [('Open video externally',self.open_external),('Import results',self.import_report),('Export results report',self.export_report)]:a.addWidget(button(text,fn))
        self.advanced_round.hide();l.addWidget(self.advanced_round);l.addStretch()
    def show_clock(self):
        seconds=int(self.remaining+.99);self.clock.setText(f'{seconds//60:02d}:{seconds%60:02d}')
        colour,bg=('#B64A4A','#FDE7E2') if seconds<=5 else (('#A47A22','#FBF0D0') if seconds<=15 else ('#3D70AD','#E7EFFC'))
        self.clock.setStyleSheet(f'font-size:40px;font-weight:700;color:{colour};background:{bg};border-radius:18px;padding:8px 18px;')
        if hasattr(self,'round_progress'):self.round_progress.setValue(int(1000*max(0,self.remaining)/(60 if getattr(self,'active_game','')=='Football' else 30)))
    def toggle_timer(self):
        super().toggle_timer();self.timer_button.setText('Pause timer' if self.running else 'Resume timer');self.clock_hint.setText('Enjoy the round.' if self.running else 'Take a breath. Continue when you’re ready.')
    def reset_clock(self):
        super().reset_clock()
        if hasattr(self,'timer_button'):self.timer_button.setText('Start timer');self.clock_hint.setText('Ready when you are.')
    def tick(self):
        was_running=self.running;super().tick()
        if was_running and not self.running:self.timer_button.setText('Round finished');self.clock_hint.setText('Time’s up. Save your recording and find the results.');self.status.setText('That’s time! Stop your recording and look back at the round.')
    def start_camera(self):
        if self.is_busy() or self.camera:return
        devices=QMediaDevices.videoInputs()
        if not devices:self.error('No camera was found. You can add a phone recording instead.');return
        index=min(self.camera_choice.currentIndex(),len(devices)-1);device=devices[max(0,index)];self.player.stop();self.camera=QCamera(device,self);self.camera.errorOccurred.connect(lambda *args:self.status.setText('Camera: '+self.camera.errorString() if self.camera else 'Camera closed'));self.capture.setCamera(self.camera);self.capture.setVideoOutput(self.video)
        formats=[f for f in device.videoFormats() if f.resolution().width()<=1280 and f.resolution().height()<=720]
        if formats:self.camera.setCameraFormat(min(formats,key=lambda f:abs(f.resolution().width()-640)+abs(f.resolution().height()-480)))
        self.mic=QAudioInput(self);self.capture.setAudioInput(self.mic);self.camera.start();self.video_empty.hide();self.status.setText('Camera ready. The microphone is included when you record.')
    def recorder_state(self,state):
        self.recording=state==QMediaRecorder.RecordingState;self.record_button.setText('Stop recording' if self.recording else 'Record a turn');self.judge_button.setEnabled(not self.recording and not self.is_busy())
    def record(self):
        if self.is_busy():return
        self.pending=None;self.apply_button.setEnabled(False);self.review.setChecked(False);super().record();self.record_button.setText('Stop recording' if self.recording else 'Record a turn')
    def stop_camera(self):
        super().stop_camera()
        if hasattr(self,'record_button'):self.record_button.setText('Record a turn')
        if hasattr(self,'video_empty'):self.video_empty.setVisible(not self.clip)
    def calibration_needed(self):
        if self.active_game=='Football':return set(self.calibration.get('players',{}))!=set(self.players) or not all(t in self.calibration.get('goals',{}) for t in set(self.players.values()))
        if self.active_game=='Dune Steps':return len(self.calibration.get('markers',{}))!=3
        if self.active_game=='Majlis Delivery':return 'delivery' not in self.calibration
        return False
    def judge(self):
        if not self.players or self.finished:self.error('Start a game with your family first.');return
        if not self.clip or self.recording or self.recorder.recorderState()!=QMediaRecorder.StoppedState:self.error('Add a video or finish recording your turn first.');return
        if self.active_engine==0 and self.calibration_needed():
            self.status.setText('One small setup: show us where the people and play areas are.');self.calibrate()
            if self.calibration_needed():return
        if self.active_engine!=0:super().judge();return
        from local_ai import analyze_local
        args=(self.clip,self.active_game,dict(self.players),self.current_player(),self.host_context,json.loads(json.dumps(self.calibration)))
        self.player.pause();self.pending=None;self.apply_button.setEnabled(False);self.status.setText('Looking through your round. You can keep using the app.');profile=self.performance.currentData() or 'balanced';self.task(lambda progress:sign(analyze_local(*args,progress,profile=profile),self.secret),self.receive_report)
    def receive_report(self,envelope):
        super().receive_report(envelope)
        if self.pending:self.status.setText('Your suggested results are ready. Check the recording before saving points.')
    def render_report(self,envelope):
        r=envelope['report'];self.pending=envelope;self.review.setChecked(False);self.review.setVisible(bool(r.get('review_required')));lines=[]
        names={'goal':'Goal','delivery':'Delivery','drop':'Dropped object','freeze_success':'Held the freeze','freeze_movement':'Moved during the freeze','correct_step':'Correct step','wrong_step':'Wrong marker','valid_sentence':'Story word used'}
        for e in r['events']:
            lines.append('<b>'+html.escape(names.get(e['kind'],e['kind']))+' · '+html.escape(e['player'])+'</b> <span style="color:#4A77AF">'+f"{e['time']:.1f}s"+'</span><br>'+html.escape(e['evidence']))
        if not lines:lines=['No clear scoring moments were found. Check the camera view and try a shorter, clearer recording.']
        if r.get('transcript'):lines.append('<b>What we heard</b><br>'+html.escape(r['transcript']))
        if r.get('possession'):
            totals={p:sum(x['end']-x['start'] for x in r['possession'] if x['player']==p) for p in self.players};lines.append('<b>Time with the ball (estimated)</b><br>'+' · '.join(html.escape(p)+f' {v:.1f}s' for p,v in totals.items()))
        lines.append('<b>Please check</b><br>'+html.escape(' '.join(r['limitations'])));self.evidence.setHtml('<br><br>'.join(lines));self.update_apply()
    def task_error(self,message):
        if 'No module named' in message:message='The game support package isn’t installed yet. Close the app, run Install-Local-AI.bat, then reopen RALLY.'
        self.error(message);self.status.setText('We couldn’t finish this round. Your points have not changed.')
    def task_progress(self,value):
        if isinstance(value,int):self.progress.setRange(0,100);self.progress.setValue(value)
        else:self.status.setText(str(value).replace('Local AI','Game support').replace('models','game files'))
    def results_page(self):
        l=self.page('Good games. Better memories.','Your current scoreboard, favourite moments and saved family games.')
        w,c=card('This game');self.outcome=label('Your next game is waiting.','title');c.addWidget(self.outcome);self.mvp=label('Play a round to start your scoreboard.','muted');c.addWidget(self.mvp);l.addWidget(w)
        self.table=QTableWidget(0,4);self.table.setHorizontalHeaderLabels(['Person','Team','Points','Time with the ball']);self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);self.table.verticalHeader().hide();self.table.setEditTriggers(QAbstractItemView.NoEditTriggers);self.table.setMinimumHeight(180);self.table.setMaximumHeight(260);l.addWidget(self.table)
        w,c=card('Look back at a turn');self.history_box=QComboBox();c.addWidget(self.history_box);row=QHBoxLayout();row.addWidget(button('Replay turn',self.replay));row.addWidget(button('Save a copy',self.export_results));row.addWidget(button('One more round',self.extra_round));c.addLayout(row);self.audit=QTextEdit();self.audit.setReadOnly(True);self.audit.setMaximumHeight(100);self.audit.hide();l.addWidget(w)
        w,c=card('Your saved games','Continue where you left off. Your games are saved on this computer.');self.saved_list=QListWidget();self.saved_list.setMinimumHeight(125);self.saved_list.setMaximumHeight(220);self.saved_list.itemDoubleClicked.connect(lambda item:self.load_selected());c.addWidget(self.saved_list);row=QHBoxLayout();row.addWidget(button('Continue selected game',self.load_selected,True));row.addWidget(button('Open another saved file',self.resume));c.addLayout(row);l.addWidget(w);l.addStretch()
    def refresh(self):
        super().refresh()
        if self.players:
            for i in range(self.history_box.count()):self.history_box.setItemText(i,self.history_box.itemText(i).replace('AI evidence','results'))
    def refresh_saved(self):
        if not hasattr(self,'saved_list'):return
        self.saved_list.clear();folder=DATA/'sessions';paths=sorted(folder.glob('*.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:30]
        for path in paths:
            try:
                data=verify(json.loads(path.read_text(encoding='utf-8')),self.secret);n=len(data.get('players',{}));text=data['active_game']+'  ·  '+str(n)+' people  ·  '+('Finished' if data.get('finished') else 'Round '+str(data.get('round',1)));item=QListWidgetItem(text);item.setData(Qt.UserRole,str(path));self.saved_list.addItem(item)
            except (OSError,ValueError,KeyError):continue
        if self.saved_list.count():self.saved_list.setCurrentRow(0)
        else:self.saved_list.addItem('Your first saved game will appear here.');self.saved_list.item(0).setFlags(Qt.NoItemFlags)
    def load_selected(self):
        item=self.saved_list.currentItem()
        if item and item.data(Qt.UserRole):self.restore_session(item.data(Qt.UserRole))
    def restore_session(self,path):
        if self.is_busy():return
        if self.players:self.autosave()
        try:
            data=verify(json.loads(Path(path).read_text(encoding='utf-8')),self.secret)
            for k,v in data.items():setattr(self,k,set(v) if k=='applied' else v)
            self.pending=None;self.clip='';self.reset_clock();self.refresh();self.navigate(3 if self.finished else 2);self.status.setText('Welcome back. Your saved game is ready.')
        except (OSError,ValueError,KeyError) as e:self.error(str(e))
    def resume(self):
        if self.is_busy():return
        path,_=QFileDialog.getOpenFileName(self,'Continue a saved game',str(DATA/'sessions'),'Saved game (*.json)')
        if path:self.restore_session(path)
    def settings_page(self):
        l=self.page('Make yourself at home.','A few preferences, then back to the fun.')
        w,c=card('Your experience');row=QHBoxLayout();row.addWidget(label('Camera','muted'));self.camera_choice=QComboBox();self.camera_choice.addItems([d.description() for d in QMediaDevices.videoInputs()] or ['No camera found']);row.addWidget(self.camera_choice,1);c.addLayout(row);row=QHBoxLayout();row.addWidget(label('Processing preference','muted'));self.performance=QComboBox();self.performance.addItem('Balanced — everyday play','balanced');self.performance.addItem('Eco — less processing','eco');self.performance.addItem('Detail — more processing','detail');row.addWidget(self.performance,1);c.addLayout(row);c.addWidget(label('Eco checks fewer, smaller frames. Detail takes longer and may help with small or fast objects. Every result still needs review.','muted'));self.reduced_motion=QCheckBox('Reduce animation');self.reduced_motion.toggled.connect(lambda checked:setattr(self,'motion',not checked));c.addWidget(self.reduced_motion);c.addWidget(button('Switch light / dark',self.toggle_theme));l.addWidget(w)
        w,c=card('Game support','Once the game files are installed, video and speech can be processed on this computer without an account or API key.');self.models_status=label('Checking game files…','pill');c.addWidget(self.models_status);c.addWidget(button('Set up offline game support',self.prepare_models));c.addWidget(label('First setup needs internet. If packages are missing, run Install-Local-AI.bat once.','muted'));l.addWidget(w)
        w,c=card('Saved games');c.addWidget(button('Open recordings & saved games',self.open_data));c.addWidget(button('Save preferences',lambda:self.save_preferences()));l.addWidget(w)
        toggle=button('Advanced connection options',lambda:self.advanced_settings.setVisible(not self.advanced_settings.isVisible()));toggle.setObjectName('ghost');l.addWidget(toggle)
        self.advanced_settings=QWidget();c=QVBoxLayout(self.advanced_settings);self.engine=QComboBox();self.engine.addItems(['On this computer — no key needed','Optional cloud connection']);c.addWidget(self.engine);self.api=QLineEdit(os.getenv('GEMINI_API_KEY',''));self.api.setEchoMode(QLineEdit.Password);self.api.setPlaceholderText('Optional Gemini API key — stays in memory');c.addWidget(self.api);self.model=QLineEdit(os.getenv('GEMINI_MODEL',DEFAULT_MODEL));c.addWidget(self.model);c.addWidget(label('Cloud mode sends the selected recording to Google only when you request results. Local mode uses YOLO11n, YOLO11n Pose and Vosk. Pretrained models and experimental rules can miss or misidentify events. Review goal crossing, tray support, player identities and sentence coherence.','muted'));self.advanced_settings.hide();l.addWidget(self.advanced_settings);l.addStretch()
    def update_models(self):
        names=['yolo11n.pt','yolo11n-pose.pt','vosk-model-small-en-us-0.15'];count=sum((ROOT/'models'/n).exists() for n in names);self.models_status.setText('Offline game files ready' if count==3 else 'First-time setup needed  ·  '+str(count)+'/3 files ready')
    def prepare_models(self):
        from local_ai import download_models
        self.status.setText('Preparing your game files. Keep this window open.');self.task(lambda progress:download_models(progress),lambda result:self.status.setText('Your offline game files are ready.'))
    def save_preferences(self,quiet=False):
        try:
            p={'roster':self.roster.toPlainText(),'context':self.context.toPlainText(),'model':self.model.text(),'theme':self.theme,'favourites':sorted(self.favourites),'performance':self.performance.currentData(),'motion':self.motion};(DATA/'preferences.json').write_text(json.dumps(p),encoding='utf-8')
            if not quiet:self.status.setText('Your preferences are saved.')
        except OSError as e:self.error(str(e))
    def load_preferences(self):
        try:p=json.loads((DATA/'preferences.json').read_text(encoding='utf-8'))
        except (OSError,ValueError):return
        if p.get('roster'):
            self.updating_roster=True;rows=[s.split(',',1) for s in p['roster'].splitlines() if ',' in s];self.people.setRowCount(len(rows))
            for i,row in enumerate(rows):
                for j,v in enumerate(row):self.people.setItem(i,j,QTableWidgetItem(v.strip()))
            self.updating_roster=False;self.sync_roster()
        self.context.setPlainText(p.get('context',''));self.model.setText(p.get('model',DEFAULT_MODEL));self.theme=bool(p.get('theme',False));self.favourites=set(p.get('favourites',[]));self.motion=bool(p.get('motion',True));self.reduced_motion.setChecked(not self.motion);idx=self.performance.findData(p.get('performance','balanced'));self.performance.setCurrentIndex(max(0,idx))
        for name,b in self.fav_buttons.items():b.setText('★' if name in self.favourites else '☆');b.setChecked(name in self.favourites)
        if self.theme:self.brand.setPixmap(QPixmap(str(ROOT/'assets/rally-logo-on-dark.svg')).scaled(110,48,Qt.KeepAspectRatio,Qt.SmoothTransformation))
    def error(self,text):QMessageBox.warning(self,'RALLY',text)
    def closeEvent(self,event):
        if self.is_busy():self.error('Please let this round finish processing before you close RALLY.');event.ignore();return
        self.save_preferences(quiet=True);super().closeEvent(event)

if __name__=='__main__':
    app=QApplication(sys.argv);app.setStyle('Fusion');app.setStyleSheet(LIGHT);w=Studio();w.show();sys.exit(app.exec())
