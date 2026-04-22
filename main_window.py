import sys
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QListWidget,
    QListWidgetItem, QTabWidget, QMessageBox, QFileDialog,
    QSplitter, QGroupBox, QFrame, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor

from models import Event, Question, Answer, QuestionCategory
from question_generator import QuestionGenerator
from answer_aggregator import AnswerAggregator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("傻狍子 - 刨根问底")
        self.setMinimumSize(1000, 700)
        
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
        header_font = QFont("Microsoft YaHei", 18, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        main_layout.addWidget(header_label)
        
        subtitle_label = QLabel("通过多层级提问，深入了解每一个事件")
        subtitle_font = QFont("Microsoft YaHei", 10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d;")
        main_layout.addWidget(subtitle_label)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #bdc3c7;
                width: 2px;
            }
        """)
        
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([350, 650])
        
        main_layout.addWidget(splitter)
        
        self.statusBar().showMessage("就绪 - 请输入事件开始刨根问底")
        
    def create_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        event_input_group = QGroupBox("输入事件")
        event_input_layout = QVBoxLayout(event_input_group)
        
        self.event_input = QTextEdit()
        self.event_input.setPlaceholderText("请输入一个事件，例如：\n- 今天上课了\n- 我和朋友去吃饭了\n- 昨天参加了一个会议\n\n系统将自动生成多层级问题，帮助您深入了解这个事件。")
        self.event_input.setMaximumHeight(120)
        self.event_input.setFont(QFont("Microsoft YaHei", 10))
        event_input_layout.addWidget(self.event_input)
        
        start_btn = QPushButton("开始刨根问底")
        start_btn.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        start_btn.clicked.connect(self.start_questioning)
        event_input_layout.addWidget(start_btn)
        
        layout.addWidget(event_input_group)
        
        questions_group = QGroupBox("问题列表")
        questions_layout = QVBoxLayout(questions_group)
        
        tabs = QTabWidget()
        tabs.setFont(QFont("Microsoft YaHei", 9))
        
        self.level1_list = QListWidget()
        self.level1_list.itemClicked.connect(self.on_question_selected)
        
        self.level2_list = QListWidget()
        self.level2_list.itemClicked.connect(self.on_question_selected)
        
        self.level3_list = QListWidget()
        self.level3_list.itemClicked.connect(self.on_question_selected)
        
        tabs.addTab(self.level1_list, "第一层问题")
        tabs.addTab(self.level2_list, "第二层问题")
        tabs.addTab(self.level3_list, "第三层问题")
        
        questions_layout.addWidget(tabs)
        
        progress_layout = QHBoxLayout()
        self.progress_label = QLabel("进度: 0/0 问题已回答")
        self.progress_label.setFont(QFont("Microsoft YaHei", 9))
        progress_layout.addWidget(self.progress_label)
        questions_layout.addLayout(progress_layout)
        
        layout.addWidget(questions_group)
        
        operations_group = QGroupBox("操作")
        operations_layout = QHBoxLayout(operations_group)
        
        save_btn = QPushButton("保存事件")
        save_btn.clicked.connect(self.save_event)
        save_btn.setEnabled(False)
        self.save_btn = save_btn
        
        load_btn = QPushButton("加载事件")
        load_btn.clicked.connect(self.load_event)
        
        generate_btn = QPushButton("生成报告")
        generate_btn.clicked.connect(self.generate_report)
        generate_btn.setEnabled(False)
        self.generate_btn = generate_btn
        
        operations_layout.addWidget(save_btn)
        operations_layout.addWidget(load_btn)
        operations_layout.addWidget(generate_btn)
        
        layout.addWidget(operations_group)
        
        return panel
        
    def create_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        current_question_group = QGroupBox("当前问题")
        current_question_layout = QVBoxLayout(current_question_group)
        
        question_info_layout = QHBoxLayout()
        
        self.question_category_label = QLabel("类别: -")
        self.question_category_label.setFont(QFont("Microsoft YaHei", 9))
        self.question_category_label.setStyleSheet("color: #7f8c8d;")
        question_info_layout.addWidget(self.question_category_label)
        
        self.question_level_label = QLabel("层级: -")
        self.question_level_label.setFont(QFont("Microsoft YaHei", 9))
        self.question_level_label.setStyleSheet("color: #7f8c8d;")
        question_info_layout.addWidget(self.question_level_label)
        
        question_info_layout.addStretch()
        
        current_question_layout.addLayout(question_info_layout)
        
        self.current_question_label = QLabel("请选择一个问题进行回答")
        self.current_question_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        self.current_question_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        self.current_question_label.setWordWrap(True)
        current_question_layout.addWidget(self.current_question_label)
        
        layout.addWidget(current_question_group)
        
        answer_group = QGroupBox("回答问题")
        answer_layout = QVBoxLayout(answer_group)
        
        self.answer_input = QTextEdit()
        self.answer_input.setPlaceholderText("请输入您的答案...\n（可以留空，表示该问题没有相关信息）")
        self.answer_input.setFont(QFont("Microsoft YaHei", 10))
        self.answer_input.setMaximumHeight(150)
        answer_layout.addWidget(self.answer_input)
        
        answer_btn_layout = QHBoxLayout()
        
        submit_answer_btn = QPushButton("提交答案")
        submit_answer_btn.setFont(QFont("Microsoft YaHei", 10))
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
        skip_btn.clicked.connect(self.skip_question)
        
        prev_question_btn = QPushButton("上一个问题")
        prev_question_btn.clicked.connect(self.prev_question)
        
        next_question_btn = QPushButton("下一个问题")
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
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_group)
        
        return panel
        
    def start_questioning(self):
        event_text = self.event_input.toPlainText().strip()
        if not event_text:
            QMessageBox.warning(self, "提示", "请输入一个事件！")
            return
        
        event_id = f"event_{uuid.uuid4().hex[:8]}"
        self.current_event = Event(
            id=event_id,
            initial_text=event_text
        )
        
        level1_questions = self.question_generator.generate_level1_questions(event_text)
        self.current_event.questions = level1_questions
        
        self.update_question_lists()
        self.update_progress()
        
        self.save_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        
        self.statusBar().showMessage(f"已创建事件，生成了 {len(level1_questions)} 个第一层问题")
        
        if level1_questions:
            self.select_question(level1_questions[0])
        
    def update_question_lists(self):
        if not self.current_event:
            self.level1_list.clear()
            self.level2_list.clear()
            self.level3_list.clear()
            return
        
        self.level1_list.clear()
        for question in self.current_event.questions:
            item = QListWidgetItem()
            item.setText(f"{question.text}")
            item.setData(Qt.UserRole, question.id)
            if question.is_answered:
                item.setForeground(QColor("#27ae60"))
                item.setText(f"✓ {question.text}")
            self.level1_list.addItem(item)
        
        self.level2_list.clear()
        self.level3_list.clear()
        
        for answer in self.current_event.answers.values():
            for question in answer.child_questions:
                item = QListWidgetItem()
                item.setText(f"{question.text}")
                item.setData(Qt.UserRole, question.id)
                if question.is_answered:
                    item.setForeground(QColor("#27ae60"))
                    item.setText(f"✓ {question.text}")
                
                if question.level == 2:
                    self.level2_list.addItem(item)
                elif question.level == 3:
                    self.level3_list.addItem(item)
                    
    def update_progress(self):
        if not self.current_event:
            self.progress_label.setText("进度: 0/0 问题已回答")
            return
        
        all_questions = self.current_event.get_all_questions()
        answered = len(self.current_event.get_answered_questions())
        total = len(all_questions)
        
        self.progress_label.setText(f"进度: {answered}/{total} 问题已回答")
        
    def on_question_selected(self, item: QListWidgetItem):
        question_id = item.data(Qt.UserRole)
        if not self.current_event:
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
        
        self.update_question_lists()
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
        
        self.update_question_lists()
        self.update_progress()
        
        self.next_question()
        
    def get_question_list(self, level: int) -> QListWidget:
        if level == 1:
            return self.level1_list
        elif level == 2:
            return self.level2_list
        elif level == 3:
            return self.level3_list
        return None
        
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
        
        question_list = self.get_question_list(next_question.level)
        if question_list:
            for i in range(question_list.count()):
                item = question_list.item(i)
                if item.data(Qt.UserRole) == next_question.id:
                    question_list.setCurrentItem(item)
                    break
        
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
        
        question_list = self.get_question_list(prev_question.level)
        if question_list:
            for i in range(question_list.count()):
                item = question_list.item(i)
                if item.data(Qt.UserRole) == prev_question.id:
                    question_list.setCurrentItem(item)
                    break
                    
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
                self.update_question_lists()
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
