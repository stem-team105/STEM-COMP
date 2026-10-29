"""Lamatna's small, native Qt visual system — mobile-style spacing and desktop layouts."""
from pathlib import Path
from PySide6.QtCore import Qt,QRectF,QPointF
from PySide6.QtGui import QPainter,QPainterPath,QPen,QColor,QPolygonF,QIcon,QPixmap
from PySide6.QtWidgets import QLabel,QPushButton,QFrame,QVBoxLayout,QWidget

GAME_INFO={
'Football':('Team play','60 sec','#E0F1E8','#247A59','A ball, two goals and room to move.','Try a 2-on-2 mini match. Wear different colours and keep both goals in the camera view.','Keep the ball and every player visible.'),
'Majlis Delivery':('Team play','30 sec','#F9EADD','#B26E36','A tray and a soft ball.','Make a short delivery route. Take turns carrying the ball on a tray, then cheer your teammates on.','Walk slowly and clear the route first.'),
'Falcon Freeze':('Everyone plays','30 sec','#E4EDF9','#476FA7','Just yourselves and a little space.','Start here if you want a quick game with no equipment. Say MOVE, then FREEZE, and hold still for three seconds.','Use a steady camera and speak the cues clearly.'),
'Dune Steps':('Individual turns','30 sec','#EDE7FA','#8260AC','Three safe, numbered floor markers.','Lay out markers 1, 2 and 3. Follow 1–3–2–1–2–3 at a comfortable pace.','Use flat markers that will not slide.'),
'Family Story Relay':('Team play','30 sec','#F7EECF','#A88629','A microphone and your imagination.','Make up a family adventure. Include family, desert and kindness in three different sentences.','Take one turn at a time and speak clearly in English.')}

def theme(dark=False):
    bg,card,text,muted,border,field,soft=('#142720','#20382D','#F6F1E7','#B3C2B4','#3D5142','#192E24','#294837') if dark else ('#F6F5EF','#FFFFFF','#213F35','#697D73','#E4E8E0','#F6F8F3','#EAF1E7')
    accent='#C6AE85' if dark else '#92703E'
    arrow=(Path(__file__).resolve().parent/'assets'/('chevron-dark.svg' if dark else 'chevron.svg')).as_posix()
    return f'''
QWidget {{background:{bg};color:{text};font-family:Segoe UI;font-size:14px;}}
QLabel {{background:transparent;}} QFrame#card {{background:{card};border:1px solid {border};border-radius:24px;}}
QFrame#topbar,QFrame#dock {{background:{card};border:1px solid {border};border-radius:22px;}}
QLabel#title {{font-family:Georgia;font-size:32px;font-weight:600;letter-spacing:-0.6px;}} QLabel#heading {{font-size:19px;font-weight:700;}}
QFrame#hero {{background:#234D42;border:0;border-radius:28px;}}
QLabel#herotitle {{color:#FFFFFF;font-family:Georgia;font-size:36px;font-weight:600;}}
QLabel#herosub {{color:#D9E8DF;font-size:14px;}} QLabel#heroeyebrow {{color:#E7CE96;font-size:11px;font-weight:700;letter-spacing:2px;}}
QPushButton#heroaction {{background:#F1D69D;color:#234D42;border:0;font-weight:700;}}
QPushButton#heroaction:hover {{background:#FFE6B3;}}
QPushButton#herosecondary {{background:transparent;color:#F9FCF7;border:1px solid #7F9B8B;}}
QPushButton#herosecondary:hover {{background:#315F50;}}
QFrame#gamecard {{background:{card};border:1px solid {border};border-radius:22px;}}
QFrame#gamecard:hover {{border:1px solid #9EB89D;background:{field};}}
QLabel#metric {{font-size:29px;font-weight:700;letter-spacing:-1px;}}
QLabel#teamA {{background:#E6EFFA;color:#3B65A0;border-radius:12px;padding:8px 13px;font-weight:700;}}
QLabel#teamB {{background:#FBE8DC;color:#A35E3F;border-radius:12px;padding:8px 13px;font-weight:700;}}
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
QComboBox::drop-down {{border:0;width:28px;}} QComboBox {{padding-right:30px;}}
QComboBox::down-arrow {{image:url("{arrow}");width:12px;height:12px;}}
QTableWidget {{background:{card};gridline-color:{border};border:0;border-radius:16px;alternate-background-color:{field};}}
QHeaderView::section {{background:{field};color:{muted};padding:12px;border:0;font-weight:600;}}
QScrollArea {{border:0;background:transparent;}} QScrollBar:vertical {{background:transparent;width:7px;margin:0;}}
QScrollBar::handle:vertical {{background:#B7C9C2;border-radius:3px;min-height:30px;}} QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {{height:0;}}
QProgressBar {{background:{border};border:0;border-radius:4px;min-height:7px;max-height:7px;}} QProgressBar::chunk {{background:#92703E;border-radius:4px;}}
QSlider::groove:horizontal {{background:{border};height:4px;border-radius:2px;}} QSlider::handle:horizontal {{background:#234D42;width:13px;margin:-5px 0;border-radius:6px;}}
QCheckBox {{spacing:10px;}} QCheckBox::indicator {{width:20px;height:20px;}} QToolTip {{background:{card};color:{text};border:1px solid {border};padding:8px;}}
'''

def navigation_icon(index,active=False,dark=False):
    """Small native line icons, with clear active contrast in either appearance."""
    colour=QColor('#E5C993' if dark and active else '#C4D3C9' if dark else '#234D42' if active else '#718477')
    pixmap=QPixmap(48,48);pixmap.fill(Qt.transparent);p=QPainter(pixmap);p.setRenderHint(QPainter.Antialiasing);p.scale(2,2);p.setPen(QPen(colour,1.7,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin));p.setBrush(Qt.NoBrush)
    if index==0:
        p.drawPolyline(QPolygonF([QPointF(3,10),QPointF(12,3),QPointF(21,10)]));p.drawRoundedRect(QRectF(5,10,14,11),2,2);p.drawRect(QRectF(10,14,4,7))
    elif index==1:
        p.drawEllipse(QRectF(8,3,7,7));p.drawArc(QRectF(4,12,15,14),0,180*16);p.drawEllipse(QRectF(18,6,4,4));p.drawArc(QRectF(17,13,8,9),0,140*16)
    elif index==2:
        p.drawEllipse(QRectF(3,3,18,18));p.drawPolygon(QPolygonF([QPointF(12,8),QPointF(16,11),QPointF(14,16),QPointF(9,16),QPointF(8,11)]))
    else:
        p.drawPolyline(QPolygonF([QPointF(7,4),QPointF(17,4),QPointF(17,10),QPointF(14,14),QPointF(10,14),QPointF(7,10),QPointF(7,4)]));p.drawArc(QRectF(2,5,8,8),90*16,180*16);p.drawArc(QRectF(14,5,8,8),-90*16,180*16);p.drawLine(12,14,12,20);p.drawLine(8,21,16,21)
    p.end();return QIcon(pixmap)

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


class FamilySportScene(QWidget):
    """Original vector artwork: family football with a palm and courtyard skyline."""
    def __init__(self,parent=None):
        super().__init__(parent);self.setFixedSize(340,218);self.setAttribute(Qt.WA_TranslucentBackground);self.setStyleSheet('background:transparent;')
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.scale(self.width()/340,self.height()/218);p.setPen(Qt.NoPen)
        p.setBrush(QColor('#315F50'));p.drawEllipse(QRectF(28,0,295,218));p.setBrush(QColor('#EACD8F'));p.drawEllipse(QRectF(279,12,17,17))
        p.setBrush(QColor('#829B7C'));p.drawRoundedRect(QRectF(190,28,84,62),6,6)
        for x in [190,207,224,241,258]:p.drawRect(QRectF(x,22,11,14))
        p.setBrush(QColor('#234D42'));arch=QPainterPath(QPointF(221,90));arch.lineTo(221,62);arch.quadTo(231,43,241,62);arch.lineTo(241,90);arch.closeSubpath();p.drawPath(arch)
        p.setPen(QPen(QColor('#DCC496'),4,Qt.SolidLine,Qt.RoundCap));p.drawLine(53,85,58,30)
        p.setPen(QPen(QColor('#8EAC87'),7,Qt.SolidLine,Qt.RoundCap))
        for end in [(32,28),(42,15),(60,12),(77,20),(82,34)]:
            leaf=QPainterPath(QPointF(58,35));leaf.quadTo(QPointF(57,16),QPointF(*end));p.drawPath(leaf)
        p.setPen(Qt.NoPen);p.setBrush(QColor('#56856C'));p.drawRoundedRect(QRectF(8,86,324,124),25,25)
        p.setPen(QPen(QColor('#AAC0A2'),1.5));p.setBrush(Qt.NoBrush);p.drawRoundedRect(QRectF(24,99,291,94),12,12);p.drawLine(168,99,168,193);p.drawEllipse(QRectF(143,122,50,49));p.drawRect(QRectF(24,122,35,47));p.drawRect(QRectF(281,122,34,47))
        p.setPen(QPen(QColor('#F4E5C8'),3,Qt.SolidLine,Qt.RoundCap));p.drawPolyline(QPolygonF([QPointF(286,124),QPointF(286,100),QPointF(321,100),QPointF(321,130)]))
        p.setPen(QPen(QColor('#C1D5BE'),1));
        for x in [295,304,313]:p.drawLine(x,102,x,128)
        for y in [110,119,128]:p.drawLine(287,y,320,y)
        # Stylized family players; the illustration is decorative, never test footage.
        for x,y,size,shirt in [(95,112,1.0,'#EED294'),(211,139,.78,'#ECA88C'),(257,100,.88,'#BDD6DD')]:
            p.save();p.translate(x,y);p.scale(size,size);p.setPen(Qt.NoPen);p.setBrush(QColor('#345E4C'));p.drawEllipse(QRectF(-16,42,39,9));p.setPen(QPen(QColor('#E5C3A4'),5,Qt.SolidLine,Qt.RoundCap));p.drawLine(-5,5,-18,20);p.drawLine(9,5,22,-4);p.setPen(QPen(QColor('#E7ECE0'),6,Qt.SolidLine,Qt.RoundCap));p.drawLine(-1,24,-8,43);p.drawLine(7,24,22,38);p.setPen(Qt.NoPen);p.setBrush(QColor(shirt));p.drawRoundedRect(QRectF(-9,-1,23,29),7,7);p.setBrush(QColor('#E5C3A4'));p.drawEllipse(QRectF(-5,-20,15,17));p.restore()
        p.setPen(QPen(QColor('#F9F6EA'),2));p.setBrush(QColor('#F9F6EA'));p.drawEllipse(QRectF(170,167,20,20));p.setPen(Qt.NoPen);p.setBrush(QColor('#234D42'));p.drawPolygon(QPolygonF([QPointF(180,172),QPointF(185,176),QPointF(183,182),QPointF(177,182),QPointF(175,176)]))
