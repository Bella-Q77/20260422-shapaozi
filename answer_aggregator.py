from typing import Dict, List, Optional
from models import Event, Question, Answer, QuestionCategory


class AnswerAggregator:
    def __init__(self):
        self.question_mappings = {
            "谁参与了这个事件？": "人物",
            "这个事件的主体是谁？": "人物",
            "涉及哪些人物？": "人物",
            "谁上课了？": "上课的人",
            "和谁一起上课？": "一起上课的人",
            "老师是谁？": "老师",
            "谁吃饭了？": "吃饭的人",
            "和谁一起吃的？": "一起吃饭的人",
            "谁做的饭？": "做饭的人",
            "谁在工作？": "工作的人",
            "和谁一起工作？": "一起工作的人",
            "领导是谁？": "领导",
            "谁在学习？": "学习的人",
            "和谁一起学习？": "一起学习的人",
            "谁去旅游了？": "旅游的人",
            "和谁一起去的？": "一起旅游的人",
            "导游是谁？": "导游",
            "谁在购物？": "购物的人",
            "和谁一起购物？": "一起购物的人",
            "售货员是谁？": "售货员",
            "谁参加了会议？": "参会人员",
            "会议主持人是谁？": "主持人",
            "有多少人参加？": "参会人数",
            "谁在运动？": "运动的人",
            "和谁一起运动？": "一起运动的人",
            "教练是谁？": "教练",
            
            "这个事件涉及什么事物？": "涉及的事物",
            "使用了什么物品或工具？": "使用的物品",
            "有哪些相关的对象？": "相关对象",
            "上的什么课程？": "课程",
            "使用什么教材？": "教材",
            "在哪个教室上课？": "教室",
            "吃的什么？": "食物",
            "在哪里吃的？": "吃饭地点",
            "花费了多少钱？": "花费",
            "做的什么工作？": "工作内容",
            "使用什么工具？": "工作工具",
            "工作地点在哪里？": "工作地点",
            "学习什么内容？": "学习内容",
            "在哪里学习？": "学习地点",
            "去了哪里旅游？": "旅游地点",
            "乘坐什么交通工具？": "交通工具",
            "买了什么东西？": "购买的商品",
            "在哪里买的？": "购物地点",
            "会议主题是什么？": "会议主题",
            "在哪里开会？": "会议地点",
            "使用什么设备？": "会议设备",
            "做的什么运动？": "运动项目",
            "在哪里运动？": "运动地点",
            "使用什么器材？": "运动器材",
            
            "这个事件发生在什么时候？": "时间",
            "这个事件发生在哪里？": "地点",
            "这个事件的具体内容是什么？": "具体内容",
            "什么时候上课？": "上课时间",
            "上课持续了多久？": "上课时长",
            "今天学习的内容是什么？": "学习内容",
            "什么时候吃的？": "吃饭时间",
            "吃了多久？": "吃饭时长",
            "饭菜味道如何？": "饭菜评价",
            "什么时候工作？": "工作时间",
            "工作了多久？": "工作时长",
            "工作完成情况如何？": "工作完成情况",
            "什么时候学习？": "学习时间",
            "学习了多久？": "学习时长",
            "学习效果如何？": "学习效果",
            "什么时候去的？": "旅游时间",
            "旅游了几天？": "旅游天数",
            "旅游感受如何？": "旅游感受",
            "什么时候买的？": "购物时间",
            "购物花了多久？": "购物时长",
            "对购买的商品满意吗？": "商品满意度",
            "什么时候开会？": "会议时间",
            "会议持续了多久？": "会议时长",
            "会议结果是什么？": "会议结果",
            "什么时候运动？": "运动时间",
            "运动了多久？": "运动时长",
            "运动感受如何？": "运动感受",
            
            "这个人是谁？": "人物详情",
            "这个人的身份是什么？": "人物身份",
            "这个人有什么特点？": "人物特点",
            "这个人来自哪里？": "人物来源",
            "这个人多大年纪？": "人物年龄",
            
            "这个事物具体是什么？": "事物详情",
            "这个事物有什么特点？": "事物特点",
            "这个事物的用途是什么？": "事物用途",
            "这个事物的数量有多少？": "事物数量",
            
            "这个时间具体是几点？": "具体时间",
            "这个地点具体在哪里？": "具体地点",
            "这个事件持续了多久？": "持续时间",
            "这个事件是如何发生的？": "发生方式",
            "这个事件的结果是什么？": "事件结果"
        }
    
    def _get_question_label(self, question_text: str) -> str:
        return self.question_mappings.get(question_text, question_text)
    
    def _collect_all_answers(self, event: Event) -> Dict[str, Dict]:
        all_answers = {}
        
        for question in event.questions:
            if question.is_answered:
                answer = event.get_answer_by_question_id(question.id)
                if answer and answer.text.strip():
                    label = self._get_question_label(question.text)
                    all_answers[question.id] = {
                        "label": label,
                        "question": question.text,
                        "answer": answer.text,
                        "category": question.category,
                        "level": question.level,
                        "child_answers": {}
                    }
                    
                    for child_question in answer.child_questions:
                        if child_question.is_answered:
                            child_answer = event.get_answer_by_question_id(child_question.id)
                            if child_answer and child_answer.text.strip():
                                child_label = self._get_question_label(child_question.text)
                                all_answers[question.id]["child_answers"][child_question.id] = {
                                    "label": child_label,
                                    "question": child_question.text,
                                    "answer": child_answer.text,
                                    "category": child_question.category,
                                    "level": child_question.level,
                                    "sub_child_answers": {}
                                }
                                
                                for sub_child_question in child_answer.child_questions:
                                    if sub_child_question.is_answered:
                                        sub_child_answer = event.get_answer_by_question_id(sub_child_question.id)
                                        if sub_child_answer and sub_child_answer.text.strip():
                                            sub_child_label = self._get_question_label(sub_child_question.text)
                                            all_answers[question.id]["child_answers"][child_question.id]["sub_child_answers"][sub_child_question.id] = {
                                                "label": sub_child_label,
                                                "question": sub_child_question.text,
                                                "answer": sub_child_answer.text,
                                                "category": sub_child_question.category,
                                                "level": sub_child_question.level
                                            }
        
        return all_answers
    
    def aggregate(self, event: Event) -> str:
        all_answers = self._collect_all_answers(event)
        
        if not all_answers:
            return f"事件：{event.initial_text}\n\n（暂无详细回答）"
        
        person_answers = []
        object_answers = []
        event_answers = []
        
        for qid, ans_data in all_answers.items():
            if ans_data["category"] == QuestionCategory.PERSON:
                person_answers.append(ans_data)
            elif ans_data["category"] == QuestionCategory.OBJECT:
                object_answers.append(ans_data)
            else:
                event_answers.append(ans_data)
        
        result_parts = []
        result_parts.append(f"事件：{event.initial_text}")
        result_parts.append("")
        
        if person_answers:
            result_parts.append("【人物信息】")
            for ans in person_answers:
                line = f"• {ans['label']}：{ans['answer']}"
                result_parts.append(line)
                
                for child_ans in ans["child_answers"].values():
                    child_line = f"  └─ {child_ans['label']}：{child_ans['answer']}"
                    result_parts.append(child_line)
                    
                    for sub_child_ans in child_ans["sub_child_answers"].values():
                        sub_child_line = f"    └─ {sub_child_ans['label']}：{sub_child_ans['answer']}"
                        result_parts.append(sub_child_line)
            result_parts.append("")
        
        if object_answers:
            result_parts.append("【对象信息】")
            for ans in object_answers:
                line = f"• {ans['label']}：{ans['answer']}"
                result_parts.append(line)
                
                for child_ans in ans["child_answers"].values():
                    child_line = f"  └─ {child_ans['label']}：{child_ans['answer']}"
                    result_parts.append(child_line)
                    
                    for sub_child_ans in child_ans["sub_child_answers"].values():
                        sub_child_line = f"    └─ {sub_child_ans['label']}：{sub_child_ans['answer']}"
                        result_parts.append(sub_child_line)
            result_parts.append("")
        
        if event_answers:
            result_parts.append("【事件详情】")
            for ans in event_answers:
                line = f"• {ans['label']}：{ans['answer']}"
                result_parts.append(line)
                
                for child_ans in ans["child_answers"].values():
                    child_line = f"  └─ {child_ans['label']}：{child_ans['answer']}"
                    result_parts.append(child_line)
                    
                    for sub_child_ans in child_ans["sub_child_answers"].values():
                        sub_child_line = f"    └─ {sub_child_ans['label']}：{sub_child_ans['answer']}"
                        result_parts.append(sub_child_line)
            result_parts.append("")
        
        result_parts.append("")
        result_parts.append("=" * 50)
        result_parts.append("完整事件描述：")
        
        narrative = self._generate_narrative(event, all_answers)
        result_parts.append(narrative)
        
        return "\n".join(result_parts)
    
    def _generate_narrative(self, event: Event, all_answers: Dict) -> str:
        narrative_parts = []
        
        base_text = event.initial_text
        
        time_info = ""
        place_info = ""
        person_info = ""
        object_info = ""
        detail_info = ""
        
        for qid, ans_data in all_answers.items():
            answer = ans_data["answer"]
            
            if ans_data["category"] == QuestionCategory.EVENT:
                if "时间" in ans_data["label"] or "时候" in ans_data["label"]:
                    time_info = answer
                elif "地点" in ans_data["label"] or "哪里" in ans_data["label"]:
                    place_info = answer
                else:
                    detail_info = answer
            
            elif ans_data["category"] == QuestionCategory.PERSON:
                if person_info:
                    person_info += f"，{ans_data['label']}是{answer}"
                else:
                    person_info = f"{ans_data['label']}是{answer}"
                
                for child_ans in ans_data["child_answers"].values():
                    person_info += f"，{child_ans['label']}：{child_ans['answer']}"
            
            elif ans_data["category"] == QuestionCategory.OBJECT:
                if object_info:
                    object_info += f"，{ans_data['label']}是{answer}"
                else:
                    object_info = f"{ans_data['label']}是{answer}"
                
                for child_ans in ans_data["child_answers"].values():
                    object_info += f"，{child_ans['label']}：{child_ans['answer']}"
        
        if time_info:
            narrative_parts.append(f"{time_info}，")
        
        if person_info:
            narrative_parts.append(f"{person_info}，")
        
        narrative_parts.append(base_text)
        
        if place_info:
            narrative_parts.append(f"，地点在{place_info}")
        
        if object_info:
            narrative_parts.append(f"，{object_info}")
        
        if detail_info:
            narrative_parts.append(f"。{detail_info}")
        
        narrative = "".join(narrative_parts)
        if not narrative.endswith("。"):
            narrative += "。"
        
        return narrative
