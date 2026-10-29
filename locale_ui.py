"""Arabic labels for the main family interface; evidence and detailed game rules stay English."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel,QAbstractButton
TEXT={
'Home':'الرئيسية','Family':'العائلة','Play':'نلعب','Moments':'ذكرياتنا','Settings':'الإعدادات','Appearance':'المظهر',
'Closer, in the little moments.':'لحظات صغيرة، تجمعنا أكثر.','Family time, shared stories and a little friendly competition.':'وقت للعائلة، وحكايات مشتركة، ومنافسة ودّية.',
'OUR TIME, TOGETHER':'لمّتنا، كل يوم','Rooted in family.\nMade for your everyday.':'من عائلتنا.\nولأجمل أوقاتنا.',
'A quick game, a shared plan, or a memory worth keeping.':'لعبة سريعة، خطة تجمعنا، أو ذكرى نحتفظ بها.',
'Try Falcon Freeze  →':'جرّب لعبة الصقر  ←','Find your next game':'اختر لعبتكم القادمة','Let’s play  →':'لنلعب  ←',
'Today, together':'اليوم، معًا','How much time and energy do you have? We will suggest a game.':'كم لديكم من الوقت والطاقة؟ سنقترح لعبة مناسبة.',
'Try today’s suggestion':'جرّب اقتراح اليوم','A small plan. Then, play.':'نخطط قليلًا، ثم نلعب.','Rounds':'الجولات',
'Who’s joining?':'من سيشارك؟','+ Add person':'+ إضافة شخص','Remove selected':'حذف المحدد','A few helpful details':'تفاصيل تساعدنا',
'Read the full rules':'اقرأ القواعد كاملة','Everyone ready? Start playing  →':'هل الجميع مستعد؟ لنبدأ  ←',
'Our next gathering':'لمّتنا القادمة','Add a small plan and tick it off when it is done.':'أضف خطة صغيرة، وحدّدها عند إتمامها.',
'Add plan':'أضف خطة','Let the good times roll.':'لنصنع وقتًا جميلًا.','Start timer':'ابدأ المؤقت','Pause timer':'أوقف المؤقت مؤقتًا','Resume timer':'تابع المؤقت','Reset':'إعادة ضبط','Skip this turn':'تجاوز هذا الدور',
'Record a turn':'سجّل دورًا','Stop recording':'أوقف التسجيل','Add a video':'أضف فيديو','Play / pause':'تشغيل / إيقاف','Close camera':'إغلاق الكاميرا',
'Find this round’s results  →':'نتائج هذه الجولة  ←','Set up camera view':'تحديد الأشخاص والملعب','A quick look back':'نظرة على الجولة',
'I checked the suggested points against the recording.':'راجعت النقاط المقترحة مع التسجيل.','Save points & next turn  →':'احفظ النقاط والدور التالي  ←',
'View scoreboard':'عرض النتائج','More recording options':'خيارات تسجيل إضافية','Good games. Better memories.':'ألعاب جميلة، وذكريات أجمل.',
'Our memories':'ذكرياتنا','A sentence or two can keep a whole day alive.':'جملة أو اثنتان تحفظان يومًا كاملًا.','Save memory':'احفظ الذكرى','This game':'هذه اللعبة','Look back at a turn':'استعد أحد الأدوار','Replay turn':'شاهد الدور','Save a copy':'احفظ نسخة','One more round':'جولة إضافية','We enjoyed this':'استمتعنا بهذه اللعبة',
'Your saved games':'ألعابكم المحفوظة','Continue selected game':'تابع اللعبة المحددة','Open another saved file':'افتح ملفًا محفوظًا',
'Make yourself at home.':'أهلًا بكم في لمّتنا.','Your experience':'تجربتكم','Camera':'الكاميرا','Processing preference':'طريقة المعالجة','Reduce animation':'تقليل الحركة','Switch light / dark':'المظهر الفاتح / الداكن','Game support':'دعم الألعاب','Set up offline game support':'إعداد دعم الألعاب دون اتصال','Saved games':'الألعاب المحفوظة','Open recordings & saved games':'افتح التسجيلات والألعاب المحفوظة','Save preferences':'احفظ التفضيلات','Advanced connection options':'خيارات اتصال متقدمة','Export family notes':'تصدير ملاحظات العائلة',
'Football':'كرة القدم','Majlis Delivery':'توصيل المجلس','Falcon Freeze':'ثبات الصقر','Dune Steps':'خطوات الكثبان','Family Story Relay':'حكاية العائلة','Team play':'لعب جماعي','Everyone plays':'لعبة للجميع','Individual turns':'أدوار فردية'}

def apply_language(window,language):
    arabic=language=='ar';window.setLayoutDirection(Qt.RightToLeft if arabic else Qt.LeftToRight)
    for node in window.findChildren(QLabel)+window.findChildren(QAbstractButton):
        if node is window.language_button:continue
        if isinstance(node,QLabel) and node.pixmap() and not node.pixmap().isNull():continue
        current=node.text();last=node.property('lamatna_ar_text');english=node.property('lamatna_en_text') if current==last else current
        if english is None:english=current
        node.setProperty('lamatna_en_text',english)
        translated=TEXT.get(english,english)
        if english.startswith('Before you play '):translated='قبل أن نلعب '+TEXT.get(english[16:],english[16:])
        node.setProperty('lamatna_ar_text',translated);node.setText(translated if arabic else english)
    window.language_button.setText('English' if arabic else 'العربية')
