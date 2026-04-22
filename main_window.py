import sys
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QFileDialog, QSplitter, QGroupBox, QComboBox,
    QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from models import Event, Question, Answer, QuestionCategory
from question_generator import QuestionGenerator
from answer_aggregator import AnswerAggregator


EVENT_EXAMPLES = [
    "今天上午去公司开会了",
    "和朋友一起去餐厅吃饭",
    "昨天下午参加了课程培训",
    "周末和家人去公园游玩",
    "晚上在家学习编程",
    "上周和同事出差去了北京",
    "今天收到了快递包裹",
    "昨天参加了朋友的婚礼",
    "晚上去健身房锻炼",
    "今天下午面试了新工作"
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("傻狍子 - 刨根问底")
        self.setMinimumSize(1200, 800)
        
        self.current_event: Optional[Event] = None
        self.question_generator = QuestionGenerator()
        self.answer_aggregator = AnswerAggregator()
        
        self.events_history: List[Event] = []
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        header_label = QLabel("傻狍子 - 刨根问底")
        header_font = QFont("Microsoft YaHei", 20, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #2c3e50; padding: 15px;")
        main_layout.addWidget(header_label)
        
        subtitle_label = QLabel("通过多层级提问，深入了解每一个事件")
        subtitle_font = QFont("Microsoft YaHei", 11)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; padding-bottom: 10px;")
        main_layout.addWidget(subtitle_label)
        
        event_input_panel = self.create_event_input_panel()
        main_layout.addWidget(event_input_panel)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #bdc3c7;
                width: 2px;
            }
        """)
        
        left_panel = self.create_questions_tree_panel()
        splitter.addWidget(left_panel)
        
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 700])
        
        main_layout.addWidget(splitter, 1)
        
        self.statusBar().showMessage("就绪 - 请选择或输入一个事件开始刨根问底")
        
    def create_event_input_panel(self) -> QGroupBox:
        group_box = QGroupBox("输入事件")
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #3498db;
            }
        """)
        
        layout = QVBoxLayout(group_box)
        layout.setSpacing(10)
        
        example_layout = QHBoxLayout()
        
        example_label = QLabel("选择示例事件：")
        example_label.setFont(QFont("Microsoft YaHei", 10))
        example_layout.addWidget(example_label)
        
        self.example_combo = QComboBox()
        self.example_combo.setFont(QFont("Microsoft YaHei", 10))
        self.example_combo.addItem("-- 选择示例事件 --")
        self.example_combo.addItems(EVENT_EXAMPLES)
        self.example_combo.currentIndexChanged.connect(self.on_example_selected)
        self.example_combo.setMinimumWidth(300)
        example_layout.addWidget(self.example_combo)
        
        example_layout.addStretch()
        layout.addLayout(example_layout)
        
        input_layout = QHBoxLayout()
        
        input_label = QLabel("或输入事件：")
        input_label.setFont(QFont("Microsoft YaHei", 10))
        input_layout.addWidget(input_label)
        
        self.event_input = QTextEdit()
        self.event_input.setPlaceholderText("请输入一个事件，例如：\n- 今天上课了\n- 我和朋友去吃饭了\n- 昨天参加了一个会议\n\n系统将自动生成多层级问题，帮助您深入了解这个事件。")
        self.event_input.setMaximumHeight(80)
        self.event_input.setFont(QFont("Microsoft YaHei", 10))
        self.event_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        input_layout.addWidget(self.event_input, 1)
        
        start_btn = QPushButton("开始刨根问底")
        start_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        start_btn.setMinimumWidth(150)
        start_btn.setMinimumHeight(50)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        start_btn.clicked.connect(self.start_questioning)
        input_layout.addWidget(start_btn)
        
        layout.addLayout(input_layout)
        
        operations_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存事件")
        save_btn.clicked.connect(self.save_event)
        save_btn.setEnabled(False)
        save_btn.setMinimumWidth(100)
        self.save_btn = save_btn
        
        load_btn = QPushButton("加载事件")
        load_btn.clicked.connect(self.load_event)
        load_btn.setMinimumWidth(100)
        
        generate_btn = QPushButton("生成报告")
        generate_btn.clicked.connect(self.generate_report)
        generate_btn.setEnabled(False)
        generate_btn.setMinimumWidth(100)
        self.generate_btn = generate_btn
        
        operations_layout.addStretch()
        operations_layout.addWidget(save_btn)
        operations_layout.addWidget(load_btn)
        operations_layout.addWidget(generate_btn)
        operations_layout.addStretch()
        
        layout.addLayout(operations_layout)
        
        return group_box
        
    def create_questions_tree_panel(self) -> QGroupBox:
        group_box = QGroupBox("问题列表（树形结构）")
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #27ae60;
            }
        """)
        
        layout = QVBoxLayout(group_box)
        layout.setSpacing(5)
        
        self.questions_tree = QTreeWidget()
        self.questions_tree.setHeaderLabel("问题层级结构")
        self.questions_tree.setFont(QFont("Microsoft YaHei", 10))
        self.questions_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #fafafa;
            }
            QTreeWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #e8f4fc;
            }
        """)
        self.questions_tree.itemClicked.connect(self.on_tree_item_clicked)
        
        self.questions_tree.setHeaderLabels(["问题", "状态", "层级"])
        self.questions_tree.setColumnWidth(0, 380)
        self.questions_tree.setColumnWidth(1, 60)
        self.questions_tree.setColumnWidth(2, 45)
        
        layout.addWidget(self.questions_tree)
        
        progress_layout = QHBoxLayout()
        self.progress_label = QLabel("进度: 0/0 问题已回答")
        self.progress_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.progress_label.setStyleSheet("color: #2c3e50;")
        progress_layout.addWidget(self.progress_label)
        progress_layout.addStretch()
        
        layout.addLayout(progress_layout)
        
        return group_box
        
    def create_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        current_question_group = QGroupBox("当前问题")
        current_question_layout = QVBoxLayout(current_question_group)
        
        question_info_layout = QHBoxLayout()
        
        self.question_category_label = QLabel("类别: -")
        self.question_category_label.setFont(QFont("Microsoft YaHei", 10))
        self.question_category_label.setStyleSheet("color: #7f8c8d; padding: 5px; background-color: #ecf0f1; border-radius: 3px;")
        question_info_layout.addWidget(self.question_category_label)
        
        self.question_level_label = QLabel("层级: -")
        self.question_level_label.setFont(QFont("Microsoft YaHei", 10))
        self.question_level_label.setStyleSheet("color: #7f8c8d; padding: 5px; background-color: #ecf0f1; border-radius: 3px;")
        question_info_layout.addWidget(self.question_level_label)
        
        question_info_layout.addStretch()
        
        current_question_layout.addLayout(question_info_layout)
        
        self.current_question_label = QLabel("请从左侧树形结构选择一个问题进行回答")
        self.current_question_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        self.current_question_label.setStyleSheet("""
            color: #2c3e50; 
            padding: 15px; 
            background-color: #e8f4fc; 
            border-radius: 8px;
            border-left: 4px solid #3498db;
        """)
        self.current_question_label.setWordWrap(True)
        self.current_question_label.setMinimumHeight(80)
        current_question_layout.addWidget(self.current_question_label)
        
        layout.addWidget(current_question_group)
        
        answer_group = QGroupBox("回答问题")
        answer_layout = QVBoxLayout(answer_group)
        
        self.answer_input = QTextEdit()
        self.answer_input.setPlaceholderText("请输入您的答案...\n（可以留空，表示该问题没有相关信息）")
        self.answer_input.setFont(QFont("Microsoft YaHei", 10))
        self.answer_input.setMinimumHeight(120)
        answer_layout.addWidget(self.answer_input)
        
        answer_btn_layout = QHBoxLayout()
        
        submit_answer_btn = QPushButton("提交答案")
        submit_answer_btn.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        submit_answer_btn.setMinimumWidth(120)
        submit_answer_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        submit_answer_btn.clicked.connect(self.submit_answer)
        
        skip_btn = QPushButton("跳过（留空）")
        skip_btn.setFont(QFont("Microsoft YaHei", 10))
        skip_btn.setMinimumWidth(100)
        skip_btn.clicked.connect(self.skip_question)
        
        prev_question_btn = QPushButton("上一个问题")
        prev_question_btn.setFont(QFont("Microsoft YaHei", 10))
        prev_question_btn.clicked.connect(self.prev_question)
        
        next_question_btn = QPushButton("下一个问题")
        next_question_btn.setFont(QFont("Microsoft YaHei", 10))
        next_question_btn.clicked.connect(self.next_question)
        
        answer_btn_layout.addWidget(submit_answer_btn)
        answer_btn_layout.addWidget(skip_btn)
        answer_btn_layout.addStretch()
        answer_btn_layout.addWidget(prev_question_btn)
        answer_btn_layout.addWidget(next_question_btn)
        
        answer_layout.addLayout(answer_btn_layout)
        
        layout.addWidget(answer_group)
        
        summary_group = QGroupBox("事件汇总")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFont(QFont("Microsoft YaHei", 10))
        self.summary_text.setPlaceholderText("当您回答完所有问题后，点击\"生成报告\"按钮查看汇总结果...")
        self.summary_text.setMinimumHeight(150)
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_group)
        
        return panel
        
    def on_example_selected(self, index):
        if index > 0:
            selected_text = self.example_combo.currentText()
            self.event_input.setPlainText(selected_text)
            
    def start_questioning(self):
        event_text = self.event_input.toPlainText().strip()
        if not event_text:
            QMessageBox.warning(self, "提示", "请选择或输入一个事件！")
            return
        
        event_id = f"event_{uuid.uuid4().hex[:8]}"
        self.current_event = Event(
            id=event_id,
            initial_text=event_text
        )
        
        level1_questions = self.question_generator.generate_level1_questions(event_text)
        self.current_event.questions = level1_questions
        
        self.update_question_tree()
        self.update_progress()
        
        self.save_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        
        self.statusBar().showMessage(f"已创建事件，生成了 {len(level1_questions)} 个第一层问题")
        
        if level1_questions:
            self.select_question(level1_questions[0])
            
    def update_question_tree(self):
        self.questions_tree.clear()
        
        if not self.current_event:
            return
        
        root_item = QTreeWidgetItem(self.questions_tree)
        root_item.setText(0, f"事件：{self.current_event.initial_text}")
        root_item.setText(1, "")
        root_item.setText(2, "根")
        root_item.setForeground(0, QColor("#2980b9"))
        root_item.setFont(0, QFont("Microsoft YaHei", 10, QFont.Bold))
        root_item.setExpanded(True)
        
        level1_item = QTreeWidgetItem(root_item)
        level1_item.setText(0, "第一层问题")
        level1_item.setText(1, "")
        level1_item.setText(2, "L1")
        level1_item.setForeground(0, QColor("#8e44ad"))
        level1_item.setFont(0, QFont("Microsoft YaHei", 9, QFont.Bold))
        level1_item.setExpanded(True)
        
        for question in self.current_event.questions:
            self._add_question_to_tree(level1_item, question, 1)
        
        level2_item = QTreeWidgetItem(root_item)
        level2_item.setText(0, "第二层问题")
        level2_item.setText(1, "")
        level2_item.setText(2, "L2")
        level2_item.setForeground(0, QColor("#d35400"))
        level2_item.setFont(0, QFont("Microsoft YaHei", 9, QFont.Bold))
        
        level3_item = QTreeWidgetItem(root_item)
        level3_item.setText(0, "第三层问题")
        level3_item.setText(1, "")
        level3_item.setText(2, "L3")
        level3_item.setForeground(0, QColor("#c0392b"))
        level3_item.setFont(0, QFont("Microsoft YaHei", 9, QFont.Bold))
        
        for answer in self.current_event.answers.values():
            for question in answer.child_questions:
                if question.level == 2:
                    self._add_question_to_tree(level2_item, question, 2)
                elif question.level == 3:
                    self._add_question_to_tree(level3_item, question, 3)
        
        if level2_item.childCount() > 0:
            level2_item.setExpanded(True)
        if level3_item.childCount() > 0:
            level3_item.setExpanded(True)
            
    def _add_question_to_tree(self, parent: QTreeWidgetItem, question: Question, level: int):
        item = QTreeWidgetItem(parent)
        
        display_text = question.text
        if question.is_answered:
            display_text = f"✓ {question.text}"
            item.setForeground(0, QColor("#27ae60"))
        else:
            item.setForeground(0, QColor("#2c3e50"))
        
        item.setText(0, display_text)
        item.setText(1, "已答" if question.is_answered else "待答")
        item.setText(2, f"L{level}")
        
        if question.is_answered:
            item.setForeground(1, QColor("#27ae60"))
        else:
            item.setForeground(1, QColor("#e74c3c"))
        
        item.setData(0, Qt.UserRole, question.id)
        
        return item
        
    def update_progress(self):
        if not self.current_event:
            self.progress_label.setText("进度: 0/0 问题已回答")
            return
        
        all_questions = self.current_event.get_all_questions()
        answered = len(self.current_event.get_answered_questions())
        total = len(all_questions)
        
        self.progress_label.setText(f"进度: {answered}/{total} 问题已回答")
        
    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        question_id = item.data(0, Qt.UserRole)
        if not question_id or not self.current_event:
            return
        
        question = self.current_event.get_question_by_id(question_id)
        if question:
            self.select_question(question)
            
    def select_question(self, question: Question):
        self.current_question_label.setText(question.text)
        self.question_category_label.setText(f"类别: {question.category.value}")
        self.question_level_label.setText(f"层级: 第{question.level}层")
        
        existing_answer = self.current_event.get_answer_by_question_id(question.id)
        if existing_answer:
            self.answer_input.setPlainText(existing_answer.text)
        else:
            self.answer_input.clear()
            
        self.current_question_id = question.id
        
        self._highlight_question_in_tree(question.id)
        
    def _highlight_question_in_tree(self, question_id: str):
        def find_item(parent_item):
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                item_data = child.data(0, Qt.UserRole)
                if item_data == question_id:
                    return child
                found = find_item(child)
                if found:
                    return found
            return None
        
        for i in range(self.questions_tree.topLevelItemCount()):
            root = self.questions_tree.topLevelItem(i)
            item = find_item(root)
            if item:
                self.questions_tree.setCurrentItem(item)
                self.questions_tree.scrollToItem(item)
                break
        
    def submit_answer(self):
        if not self.current_event or not hasattr(self, 'current_question_id'):
            QMessageBox.warning(self, "提示", "请先选择一个问题！")
            return
        
        answer_text = self.answer_input.toPlainText().strip()
        
        question = self.current_event.get_question_by_id(self.current_question_id)
        if not question:
            return
        
        if self.current_event.get_answer_by_question_id(question.id):
            existing_answer = self.current_event.get_answer_by_question_id(question.id)
            existing_answer.text = answer_text
        else:
            answer = self.current_event.add_answer(
                question_id=question.id,
                answer_text=answer_text,
                level=question.level
            )
            
            if question.level < 3 and answer_text:
                child_questions = self.question_generator.generate_questions_for_answer(
                    answer_id=answer.id,
                    answer_text=answer_text,
                    parent_category=question.category,
                    current_level=question.level,
                    parent_question_text=question.text
                )
                
                if child_questions:
                    self.current_event.add_child_questions(answer.id, child_questions)
                    self.statusBar().showMessage(f"已生成 {len(child_questions)} 个第{question.level + 1}层问题")
        
        self.update_question_tree()
        self.update_progress()
        
        self.next_question()
        
    def skip_question(self):
        if not self.current_event or not hasattr(self, 'current_question_id'):
            return
        
        question = self.current_event.get_question_by_id(self.current_question_id)
        if not question:
            return
        
        answer = self.current_event.add_answer(
            question_id=question.id,
            answer_text="",
            level=question.level
        )
        
        self.update_question_tree()
        self.update_progress()
        
        self.next_question()
        
    def next_question(self):
        if not self.current_event:
            return
        
        all_questions = self.current_event.get_all_questions()
        if not all_questions:
            return
        
        current_index = -1
        for i, q in enumerate(all_questions):
            if hasattr(self, 'current_question_id') and q.id == self.current_question_id:
                current_index = i
                break
        
        next_index = current_index + 1
        if next_index >= len(all_questions):
            QMessageBox.information(self, "提示", "这是最后一个问题了！")
            return
        
        next_question = all_questions[next_index]
        self.select_question(next_question)
        
    def prev_question(self):
        if not self.current_event:
            return
        
        all_questions = self.current_event.get_all_questions()
        if not all_questions:
            return
        
        current_index = len(all_questions)
        for i, q in enumerate(all_questions):
            if hasattr(self, 'current_question_id') and q.id == self.current_question_id:
                current_index = i
                break
        
        prev_index = current_index - 1
        if prev_index < 0:
            QMessageBox.information(self, "提示", "这是第一个问题了！")
            return
        
        prev_question = all_questions[prev_index]
        self.select_question(prev_question)
                    
    def save_event(self):
        if not self.current_event:
            QMessageBox.warning(self, "提示", "没有可保存的事件！")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存事件",
            f"事件_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON文件 (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_event.to_dict(), f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "成功", f"事件已保存到：\n{file_path}")
                self.statusBar().showMessage(f"事件已保存: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败：{str(e)}")
                
    def load_event(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "加载事件",
            "",
            "JSON文件 (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.current_event = Event.from_dict(data)
                
                self.event_input.setPlainText(self.current_event.initial_text)
                self.example_combo.setCurrentIndex(0)
                self.update_question_tree()
                self.update_progress()
                
                self.save_btn.setEnabled(True)
                self.generate_btn.setEnabled(True)
                
                QMessageBox.information(self, "成功", f"事件已加载：\n{self.current_event.initial_text}")
                self.statusBar().showMessage(f"事件已加载: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载失败：{str(e)}")
                
    def generate_report(self):
        if not self.current_event:
            QMessageBox.warning(self, "提示", "没有可生成报告的事件！")
            return
        
        summary = self.answer_aggregator.aggregate(self.current_event)
        self.summary_text.setPlainText(summary)
        
        self.statusBar().showMessage("报告已生成")
