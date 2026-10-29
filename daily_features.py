"""Working daily family features for Lamatna; all records stay on this computer."""
from PySide6.QtCore import Qt,QDate
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QLineEdit,QComboBox,QDateEdit,QListWidget,QListWidgetItem,QTextEdit
from ui_kit import card,label,button
from family import FamilyStore
from recommendation import FamilyRecommender

class DailyFeatures:
    def init_family(self,directory):
        self.family_store=FamilyStore(directory/'family.sqlite3');self.match_context=['calm','indoors','5']
    def daily_card(self):
        w,c=card('Today, together','How much time and energy do you have? We will suggest a game.')
        row=QHBoxLayout();self.energy=QComboBox();self.space=QComboBox();self.minutes=QComboBox()
        for text,data in [('A quiet moment','calm'),('Feeling playful','playful'),('Ready to move','active')]:self.energy.addItem(text,data)
        for text,data in [('At home / indoors','indoors'),('Outside together','outdoors')]:self.space.addItem(text,data)
        for value in ['5','10','20']:self.minutes.addItem(value+' minutes',value)
        for control in [self.energy,self.space,self.minutes]:row.addWidget(control,1);control.currentIndexChanged.connect(self.update_suggestion)
        c.addLayout(row);self.suggestion=label('','heading');c.addWidget(self.suggestion);row=QHBoxLayout();row.addWidget(button('Try today’s suggestion',self.try_suggestion,True));row.addStretch();c.addLayout(row);self.update_suggestion();return w
    def checkin_context(self):return [self.energy.currentData(),self.space.currentData(),self.minutes.currentData()]
    def update_suggestion(self,*args):
        if not hasattr(self,'suggestion'):return
        self.suggested_game=FamilyRecommender(self.family_store.feedback()).suggest(self.checkin_context());self.suggestion.setText(self.suggested_game)
    def try_suggestion(self):self.select_game(self.suggested_game)
    def planner_card(self):
        w,c=card('Our next gathering','Add a small plan and tick it off when it is done.');row=QHBoxLayout();self.plan_title=QLineEdit();self.plan_title.setPlaceholderText('Dinner, a game night, or a call with grandparents…');row.addWidget(self.plan_title,1);self.plan_date=QDateEdit(QDate.currentDate());self.plan_date.setCalendarPopup(True);self.plan_date.setDisplayFormat('dd MMM yyyy');row.addWidget(self.plan_date);row.addWidget(button('Add plan',self.add_plan,True));c.addLayout(row);self.plans_list=QListWidget();self.plans_list.setMinimumHeight(100);self.plans_list.setMaximumHeight(155);self.plans_list.itemChanged.connect(self.plan_changed);c.addWidget(self.plans_list);self.refresh_plans();return w
    def add_plan(self):
        try:self.family_store.add_plan(self.plan_title.text(),self.plan_date.date().toString('yyyy-MM-dd'));self.plan_title.clear();self.refresh_plans();self.status.setText('Your family plan is saved.')
        except ValueError as e:self.error(str(e))
    def refresh_plans(self):
        self.plans_list.blockSignals(True);self.plans_list.clear()
        for ident,title,due,done in self.family_store.plans():
            item=QListWidgetItem(due+'  ·  '+title);item.setFlags(item.flags()|Qt.ItemIsUserCheckable);item.setData(Qt.UserRole,ident);item.setCheckState(Qt.Checked if done else Qt.Unchecked);self.plans_list.addItem(item)
        self.plans_list.blockSignals(False)
    def plan_changed(self,item):
        if item.data(Qt.UserRole) is not None:self.family_store.complete(item.data(Qt.UserRole),item.checkState()==Qt.Checked)
    def journal_card(self):
        w,c=card('Our memories','A sentence or two can keep a whole day alive.');self.memory_title=QLineEdit();self.memory_title.setPlaceholderText('Give this memory a name');c.addWidget(self.memory_title);self.memory_body=QTextEdit();self.memory_body.setPlaceholderText('What made today special? Arabic and English notes are welcome.');self.memory_body.setMaximumHeight(90);c.addWidget(self.memory_body);row=QHBoxLayout();row.addWidget(button('Save memory',self.save_memory,True));row.addStretch();c.addLayout(row);self.memories_list=QListWidget();self.memories_list.setMinimumHeight(85);self.memories_list.setMaximumHeight(130);self.memories_list.itemClicked.connect(self.show_memory);c.addWidget(self.memories_list);self.memory_preview=label('','muted');self.memory_preview.setMaximumHeight(180);self.memory_preview.setTextFormat(Qt.PlainText);c.addWidget(self.memory_preview);self.refresh_memories();return w
    def save_memory(self):
        try:self.family_store.add_memory(self.memory_title.text(),self.memory_body.toPlainText());self.memory_title.clear();self.memory_body.clear();self.refresh_memories();self.status.setText('A little memory, safely saved.')
        except ValueError as e:self.error(str(e))
    def refresh_memories(self):
        self.memories_list.clear()
        for ident,title,body,created in self.family_store.memories():
            item=QListWidgetItem(created[:10]+'  ·  '+title);item.setData(Qt.UserRole,body);self.memories_list.addItem(item)
    def show_memory(self,item):self.memory_preview.setText(item.data(Qt.UserRole) or '')
    def enjoy_game(self):
        if not self.players or not self.finished:self.error('Finish a game first, then tell us what you enjoyed.');return
        self.family_store.enjoy(self.session_id,self.match_context,self.active_game);self.update_suggestion();self.status.setText('Noted. Your family’s feedback will shape future suggestions.')
    def export_family(self):self.save_json(self.family_store.export(),'lamatna-family-notes.json')
