"""Lamatna's small, native Qt visual system — mobile-style spacing and desktop layouts."""
from PySide6.QtCore import Qt,QRectF,QPointF
from PySide6.QtGui import QPainter,QPainterPath,QPen,QColor,QPolygonF
from PySide6.QtWidgets import QLabel,QPushButton,QFrame,QVBoxLayout,QWidget

GAME_INFO={
'Football':('Team play','60 sec','#E0F1E8','#247A59','A ball, two goals and room to move.','Try a 2-on-2 mini match. Wear different colours and keep both goals in the camera view.','Keep the ball and every player visible.'),
'Majlis Delivery':('Team play','30 sec','#F9EADD','#B26E36','A tray and a soft ball.','Make a short delivery route. Take turns carrying the ball on a tray, then cheer your teammates on.','Walk slowly and clear the route first.'),
'Falcon Freeze':('Everyone plays','30 sec','#E4EDF9','#476FA7','Just yourselves and a little space.','Start here if you want a quick game with no equipment. Say MOVE, then FREEZE, and hold still for three seconds.','Use a steady camera and speak the cues clearly.'),
'Dune Steps':('Individual turns','30 sec','#EDE7FA','#8260AC','Three safe, numbered floor markers.','Lay out markers 1, 2 and 3. Follow 1–3–2–1–2–3 at a comfortable pace.','Use flat markers that will not slide.'),
'Family Story Relay':('Team play','30 sec','#F7EECF','#A88629','A microphone and your imagination.','Make up a family adventure. Include family, desert and kindness in three different sentences.','Take one turn at a time and speak clearly in English.')}

def theme(dark=False):
    bg,card,text,muted,border,field,soft=('#162720','#20382D','#F6F1E7','#B3C2B4','#3D5142','#192E24','#294837') if dark else ('#F7F3EB','#FFFDFA','#243F36','#68786D','#E6DED0','#F6F1E7','#E9EFE5')
    accent='#C6AE85' if dark else '#92703E'
    return f'''
QWidget {{background:{bg};color:{text};font-family:Segoe UI;font-size:14px;}}
QLabel {{background:transparent;}} QFrame#card {{background:{card};border:1px solid {border};border-radius:24px;}}
QFrame#topbar,QFrame#dock {{background:{card};border:1px solid {border};border-radius:22px;}}
QLabel#title {{font-family:Georgia;font-size:34px;font-weight:600;letter-spacing:-0.6px;}} QLabel#heading {{font-size:20px;font-weight:700;}}
QLabel#muted {{color:{muted};}} QLabel#eyebrow {{color:{accent};font-size:11px;font-weight:700;letter-spacing:2px;}}
QLabel#duration {{background:#E7EFFC;color:#3867AC;border-radius:12px;padding:8px 13px;font-weight:700;}}
QLabel#pill {{background:{soft};color:{accent};border-radius:12px;padding:8px 12px;font-weight:600;}}
QPushButton {{background:{field};color:{text};border:1px solid {border};border-radius:14px;padding:11px 18px;font-weight:600;min-height:22px;}}
QPushButton:hover {{background:{soft};border-color:#B7A27E;}} QPushButton:pressed {{background:#C8E9DE;color:#164A3B;}}
QPushButton#primary {{background:#234D42;color:#FFFFFF;border:0;}} QPushButton#primary:hover {{background:#193D33;}}
QPushButton#ghost {{background:transparent;border:0;color:{muted};padding:8px 12px;}} QPushButton#ghost:checked {{color:#168363;}}
QPushButton#tab {{background:transparent;border:0;color:{muted};border-radius:15px;padding:10px 18px;}}
QPushButton#tab:checked {{background:{soft};color:{accent};}} QPushButton:disabled {{background:{field};color:#A1ADAB;border-color:{border};}}
QLineEdit,QTextEdit,QComboBox,QSpinBox {{background:{field};border:1px solid {border};border-radius:12px;padding:10px;selection-background-color:#CBEADE;}}
QComboBox QAbstractItemView {{background:{card};color:{text};selection-background-color:{soft};}}
QTableWidget {{background:{card};gridline-color:{border};border:0;border-radius:16px;alternate-background-color:{field};}}
QHeaderView::section {{background:{field};color:{muted};padding:12px;border:0;font-weight:600;}}
QScrollArea {{border:0;background:transparent;}} QScrollBar:vertical {{background:transparent;width:7px;margin:0;}}
QScrollBar::handle:vertical {{background:#B7C9C2;border-radius:3px;min-height:30px;}} QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {{height:0;}}
QProgressBar {{background:{border};border:0;border-radius:4px;min-height:7px;max-height:7px;}} QProgressBar::chunk {{background:#92703E;border-radius:4px;}}
QSlider::groove:horizontal {{background:{border};height:4px;border-radius:2px;}} QSlider::handle:horizontal {{background:#234D42;width:13px;margin:-5px 0;border-radius:6px;}}
QCheckBox {{spacing:10px;}} QCheckBox::indicator {{width:20px;height:20px;}} QToolTip {{background:{card};color:{text};border:1px solid {border};padding:8px;}}
'''

def label(text,kind=None):
    w=QLabel(text);w.setWordWrap(kind not in ('duration','pill'))
    if kind:w.setObjectName(kind)
    return w

def button(text,fn,primary=False):
    w=QPushButton(text);w.setCursor(Qt.PointingHandCursor);w.clicked.connect(fn)
    if primary:w.setObjectName('primary')
    return w

def card(title='',subtitle=''):
    w=QFrame();w.setObjectName('card');layout=QVBoxLayout(w);layout.setContentsMargins(24,22,24,22);layout.setSpacing(12)
    if title:layout.addWidget(label(title,'heading'))
    if subtitle:layout.addWidget(label(subtitle,'muted'))
    return w,layout

class GameArt(QWidget):
    """Resolution-independent illustrations; no font-dependent emoji."""
    def __init__(self,game,size=70,parent=None):
        super().__init__(parent);self.game=game;self.setFixedSize(size,size)
    def paintEvent(self,event):
        info=GAME_INFO[self.game];p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.scale(self.width()/100,self.height()/100);p.setPen(Qt.NoPen);p.setBrush(QColor(info[2]));p.drawRoundedRect(QRectF(0,0,100,100),28,28)
        color=QColor(info[3]);pen=QPen(color,3.5,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin);p.setPen(pen);p.setBrush(Qt.NoBrush)
        if self.game=='Football':
            p.drawEllipse(QRectF(23,23,54,54));poly=QPolygonF([QPointF(50,36),QPointF(63,45),QPointF(58,60),QPointF(42,60),QPointF(37,45)]);p.setBrush(color);p.drawPolygon(poly)
            for a,b in [((50,36),(50,24)),((63,45),(75,41)),((58,60),(66,71)),((42,60),(34,71)),((37,45),(25,41))]:p.drawLine(QPointF(*a),QPointF(*b))
        elif self.game=='Majlis Delivery':
            p.drawLine(24,66,76,66);p.drawLine(30,73,70,73);p.drawArc(QRectF(30,36,40,48),0,180*16);p.drawEllipse(QRectF(46,28,8,8))
        elif self.game=='Falcon Freeze':
            path=QPainterPath(QPointF(22,57));path.cubicTo(36,32,45,39,50,50);path.cubicTo(57,31,68,33,80,42);path.cubicTo(68,42,62,52,57,66);path.lineTo(47,72);path.cubicTo(48,59,38,48,22,57);p.drawPath(path)
        elif self.game=='Dune Steps':
            for x,y in [(32,29),(57,52)]:p.drawRoundedRect(QRectF(x,y,14,25),7,7);p.drawEllipse(QRectF(x,y-8,14,6))
        else:
            p.drawRoundedRect(QRectF(23,27,55,40),13,13);p.drawLine(35,67,31,76);p.drawLine(31,76,47,67)
            for x in [37,51,65]:p.setBrush(color);p.drawEllipse(QRectF(x-2,45,4,4))


class HeritageScene(QWidget):
    """A small courtyard-and-palm illustration inspired by Emirati home architecture."""
    def __init__(self,parent=None):super().__init__(parent);self.setFixedSize(260,170)
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.setPen(Qt.NoPen);p.setBrush(QColor('#EFE5D3'));p.drawRoundedRect(QRectF(0,0,260,170),70,70)
        p.setBrush(QColor('#E0D2B8'));p.drawEllipse(QRectF(-30,130,320,80));p.setBrush(QColor('#D3BE99'));p.drawRoundedRect(QRectF(64,54,136,106),8,8)
        p.setBrush(QColor('#EBDFC6'));p.drawRect(QRectF(54,45,156,18))
        for x in [61,87,113,139,165,191]:p.drawRect(QRectF(x,34,13,17))
        p.setBrush(QColor('#365A47'));arch=QPainterPath(QPointF(109,159));arch.lineTo(109,109);arch.cubicTo(109,94,121,84,132,77);arch.cubicTo(143,84,155,94,155,109);arch.lineTo(155,159);arch.closeSubpath();p.drawPath(arch)
        p.setPen(QPen(QColor('#92703E'),5,Qt.SolidLine,Qt.RoundCap));p.drawLine(34,146,40,67)
        p.setPen(QPen(QColor('#466851'),9,Qt.SolidLine,Qt.RoundCap))
        for end in [(12,62),(18,42),(39,35),(58,43),(67,61)]:
            leaf=QPainterPath(QPointF(40,66));leaf.quadTo(QPointF(38,39),QPointF(*end));p.drawPath(leaf)
        p.setPen(Qt.NoPen);p.setBrush(QColor('#92703E'));p.drawEllipse(QRectF(218,22,12,12))
