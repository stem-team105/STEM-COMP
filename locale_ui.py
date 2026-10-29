"""Arabic labels for the main family interface; evidence and detailed game rules stay English."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel,QAbstractButton
TEXT={
'Good days start with a game.':'أجمل الأيام تبدأ بلعبة.','A little movement. A little team spirit. Everyone together.':'حركة، وروح فريق، ولحظات تجمعنا جميعًا.',
'LAMATNA FAMILY SPORTS':'لمّتنا للرياضة العائلية','Big cheers.\nCloser families.':'هتافات تملأ المكان.\nوعائلة أقرب.',
'Your next family match starts here. Set up your teams, capture the action and review every round.':'مباراتكم العائلية القادمة تبدأ هنا. شكّلوا الفرق، وسجّلوا اللعب، وراجعوا كل جولة.',
'Start a football match  →':'ابدأوا مباراة كرة قدم  ←','Help us choose':'ساعدنا في الاختيار','Pick your next challenge':'اختاروا تحديكم القادم','Play  →':'لنلعب  ←',
'Choose your game':'اختاروا لعبتكم','5 games for your family':'خمس ألعاب لعائلتكم','Build your teams':'شكّلوا فرقكم','Names, rounds & quick tips':'أسماء وجولات ونصائح سريعة','Play & look back':'العبوا وراجعوا الجولة','Record, review & celebrate':'سجّلوا وراجعوا واحتفلوا',
'Meet your teams':'تعرّفوا على الفرق','The final whistle. The shared smiles.':'صافرة النهاية. وابتسامات تجمعنا.','Your scores, possession MVP and the moments worth playing back.':'نتائجكم وأفضل لاعب في الاستحواذ وأجمل اللحظات للمشاهدة مجددًا.',
'Team A points':'نقاط الفريق أ','Team B points':'نقاط الفريق ب','Players':'اللاعبون','Highest score':'أعلى نتيجة','Round':'الجولة',
'Teams':'الفرق','Results':'النتائج','Family sport, together.':'رياضة تجمع العائلة.',
'Five family games. Clear rules, timed rounds and results you can review.':'خمس ألعاب عائلية، وقواعد واضحة، وجولات محددة الوقت، ونتائج يمكنكم مراجعتها.',
'YOUR FAMILY GAME DAY':'يومكم الرياضي العائلي','A little team spirit.\nA lot of family time.':'روح الفريق.\nولحظات تجمع العائلة.',
'Start a football match, record the action and review goals, possession and your MVP.':'ابدأوا مباراة كرة قدم، وسجّلوا اللعب، وراجعوا الأهداف والاستحواذ وأفضل لاعب.',
'Play football  →':'لنلعب كرة القدم  ←','Your game. Your teams.':'لعبتكم. فرقكم.',
'Choose a game, add your family and check the equipment before playing.':'اختاروا لعبة، وأضيفوا أفراد العائلة، وتأكدوا من الأدوات قبل البدء.',
'Find your family’s next game':'اختاروا لعبة العائلة القادمة','Choose your energy, play space and available time.':'حددوا نشاطكم ومكان اللعب والوقت المتاح.',
'Every round counts.':'لكل جولة قيمتها.','Review your scoreboard, player MVP, replays and saved family matches.':'راجعوا النتائج وأفضل لاعب والتسجيلات والمباريات المحفوظة.',
'Plan another sports day':'خططوا ليوم رياضي آخر','Our next sports day':'يومنا الرياضي القادم','Plan your next match or family activity.':'خططوا للمباراة أو النشاط العائلي القادم.',
'Add a sports-day note':'أضيفوا ملاحظة عن يومكم الرياضي','Sports-day notes':'ملاحظات اليوم الرياضي','Keep a highlight or something to improve next match.':'احتفظوا بلقطة جميلة أو فكرة للتحسين في المباراة القادمة.',
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
