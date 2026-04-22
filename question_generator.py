from typing import List, Dict, Optional
from models import Question, QuestionCategory
import uuid
import re


class QuestionGenerator:
    def __init__(self):
        self.question_counter = 0
        self._init_question_templates()
        self._init_entity_patterns()
    
    def _init_entity_patterns(self):
        self.person_titles = [
            "总", "经理", "总监", "老板", "老师", "教授", "医生", "护士",
            "工程师", "设计师", "会计", "律师", "警察", "消防员", "司机",
            "同学", "同事", "朋友", "家人", "亲戚", "领导", "下属", "员工",
            "主管", "主任", "部长", "处长", "局长", "厅长", "部长", "主席",
            "书记", "委员", "代表", "董事", "监事", "总裁", "CEO", "COO",
            "CTO", "CFO", "CIO", "创始人", "合伙人", "投资者", "股东"
        ]
        
        self.person_prefixes = ["老", "小", "大"]
        self.conjunctions = ["和", "与", "及", "跟", "、", "，", ",", "；", ";", "还有"]
        
        self.chinese_provinces = [
            "北京", "上海", "天津", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
            "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
            "广东", "广西", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海",
            "台湾", "内蒙古", "新疆", "西藏", "宁夏", "广西", "香港", "澳门"
        ]
        
        self.chinese_cities = [
            "北京", "上海", "广州", "深圳", "杭州", "南京", "苏州", "成都", "武汉",
            "西安", "重庆", "天津", "郑州", "长沙", "东莞", "宁波", "佛山", "合肥",
            "青岛", "大连", "厦门", "福州", "济南", "昆明", "哈尔滨", "沈阳", "长春",
            "石家庄", "太原", "兰州", "贵阳", "南宁", "海口", "乌鲁木齐", "呼和浩特",
            "拉萨", "银川", "西宁"
        ]
        
        self.object_types = {
            "课程": ["课程", "课", "学科", "科目"],
            "书籍": ["书", "课本", "教材", "讲义", "教程"],
            "会议": ["会议", "会", "研讨会", "座谈会", "培训会"],
            "地点": ["教室", "办公室", "会议室", "餐厅", "酒店", "商场", "学校", "公司"],
            "时间": ["早上", "上午", "下午", "晚上", "今天", "明天", "昨天", "上周", "下周"]
        }
        
        self.question_type_patterns = {
            "地点": ["来自哪里", "在哪里", "哪个地方", "地点", "哪里人", "家乡", "籍贯"],
            "时间": ["什么时候", "时间", "几点", "日期", "星期"],
            "年龄": ["多大年纪", "年龄", "几岁", "多大"],
            "身份": ["身份", "是谁", "什么职位", "职位"],
            "工作": ["负责什么", "工作", "做什么"],
            "数量": ["多少", "几个", "人数"]
        }
    
    def _init_question_templates(self):
        self.level1_templates = {
            QuestionCategory.PERSON: [
                "谁参与了这个事件？",
                "这个事件的主体是谁？",
                "涉及哪些人物？"
            ],
            QuestionCategory.OBJECT: [
                "这个事件涉及什么事物？",
                "使用了什么物品或工具？",
                "有哪些相关的对象？"
            ],
            QuestionCategory.EVENT: [
                "这个事件发生在什么时候？",
                "这个事件发生在哪里？",
                "这个事件的具体内容是什么？"
            ]
        }
        
        self.person_detail_questions = [
            "{entity}的身份是什么？",
            "{entity}负责什么工作？",
            "{entity}来自哪里？",
            "{entity}多大年纪？",
            "{entity}有什么特点？",
            "{entity}的上级是谁？",
            "{entity}管理多少人？"
        ]
        
        self.object_detail_questions = [
            "{entity}的用途是什么？",
            "{entity}来自哪里？",
            "{entity}的数量有多少？",
            "{entity}的价格是多少？",
            "{entity}是谁提供的？",
            "{entity}有什么特点？",
            "{entity}的质量如何？"
        ]
        
        self.event_detail_questions = [
            "{entity}的具体时间是？",
            "{entity}的具体地点是？",
            "{entity}持续了多久？",
            "{entity}是如何发生的？",
            "{entity}的结果是什么？",
            "{entity}有什么影响？"
        ]
        
        self.smart_keywords = {
            "上课": {
                QuestionCategory.PERSON: ["谁上课了？", "和谁一起上课？", "老师是谁？"],
                QuestionCategory.OBJECT: ["上的什么课程？", "使用什么教材？", "在哪个教室上课？"],
                QuestionCategory.EVENT: ["什么时候上课？", "上课持续了多久？", "今天学习的内容是什么？"]
            },
            "吃饭": {
                QuestionCategory.PERSON: ["谁吃饭了？", "和谁一起吃的？", "谁做的饭？"],
                QuestionCategory.OBJECT: ["吃的什么？", "在哪里吃的？", "花费了多少钱？"],
                QuestionCategory.EVENT: ["什么时候吃的？", "吃了多久？", "饭菜味道如何？"]
            },
            "工作": {
                QuestionCategory.PERSON: ["谁在工作？", "和谁一起工作？", "领导是谁？"],
                QuestionCategory.OBJECT: ["做的什么工作？", "使用什么工具？", "工作地点在哪里？"],
                QuestionCategory.EVENT: ["什么时候工作？", "工作了多久？", "工作完成情况如何？"]
            },
            "学习": {
                QuestionCategory.PERSON: ["谁在学习？", "和谁一起学习？", "老师是谁？"],
                QuestionCategory.OBJECT: ["学习什么内容？", "使用什么教材？", "在哪里学习？"],
                QuestionCategory.EVENT: ["什么时候学习？", "学习了多久？", "学习效果如何？"]
            },
            "旅游": {
                QuestionCategory.PERSON: ["谁去旅游了？", "和谁一起去的？", "导游是谁？"],
                QuestionCategory.OBJECT: ["去了哪里旅游？", "乘坐什么交通工具？", "花费了多少钱？"],
                QuestionCategory.EVENT: ["什么时候去的？", "旅游了几天？", "旅游感受如何？"]
            },
            "购物": {
                QuestionCategory.PERSON: ["谁在购物？", "和谁一起购物？", "售货员是谁？"],
                QuestionCategory.OBJECT: ["买了什么东西？", "在哪里买的？", "花费了多少钱？"],
                QuestionCategory.EVENT: ["什么时候买的？", "购物花了多久？", "对购买的商品满意吗？"]
            },
            "开会": {
                QuestionCategory.PERSON: ["谁参加了会议？", "会议主持人是谁？", "有多少人参加？"],
                QuestionCategory.OBJECT: ["会议主题是什么？", "在哪里开会？", "使用什么设备？"],
                QuestionCategory.EVENT: ["什么时候开会？", "会议持续了多久？", "会议结果是什么？"]
            },
            "运动": {
                QuestionCategory.PERSON: ["谁在运动？", "和谁一起运动？", "教练是谁？"],
                QuestionCategory.OBJECT: ["做的什么运动？", "在哪里运动？", "使用什么器材？"],
                QuestionCategory.EVENT: ["什么时候运动？", "运动了多久？", "运动感受如何？"]
            }
        }
    
    def _extract_person_entities(self, text: str) -> List[str]:
        entities = []
        
        for conj in self.conjunctions:
            text = text.replace(conj, "|")
        
        parts = re.split(r'[|、，,；;\s]+', text)
        parts = [p.strip() for p in parts if p.strip()]
        
        for part in parts:
            if len(part) >= 1:
                for title in self.person_titles:
                    if title in part and len(part) > len(title):
                        entities.append(part)
                        break
                else:
                    if len(part) >= 2 or (len(part) == 1 and part[0] in self.person_prefixes):
                        entities.append(part)
        
        entities = [e for e in entities if len(e) >= 1]
        
        return entities if entities else [text.strip()]
    
    def _extract_object_entities(self, text: str) -> List[str]:
        entities = []
        
        for conj in self.conjunctions:
            text = text.replace(conj, "|")
        
        parts = re.split(r'[|、，,；;\s]+', text)
        parts = [p.strip() for p in parts if p.strip()]
        
        for part in parts:
            if len(part) >= 1:
                entities.append(part)
        
        return entities if entities else [text.strip()]
    
    def _generate_question_id(self) -> str:
        self.question_counter += 1
        return f"q_{self.question_counter}_{uuid.uuid4().hex[:8]}"
    
    def generate_level1_questions(self, event_text: str) -> List[Question]:
        questions = []
        
        matched_keyword = None
        for keyword, templates in self.smart_keywords.items():
            if keyword in event_text:
                matched_keyword = keyword
                break
        
        if matched_keyword:
            templates = self.smart_keywords[matched_keyword]
            for category in [QuestionCategory.PERSON, QuestionCategory.OBJECT, QuestionCategory.EVENT]:
                if category in templates:
                    for q_text in templates[category][:3]:
                        question = Question(
                            id=self._generate_question_id(),
                            text=q_text,
                            category=category,
                            level=1
                        )
                        questions.append(question)
        else:
            for category in [QuestionCategory.PERSON, QuestionCategory.OBJECT, QuestionCategory.EVENT]:
                templates = self.level1_templates[category]
                for q_text in templates[:3]:
                    question = Question(
                        id=self._generate_question_id(),
                        text=q_text,
                        category=category,
                        level=1
                    )
                    questions.append(question)
        
        return questions
    
    def generate_level2_questions(self, parent_answer_id: str, answer_text: str, parent_category: QuestionCategory) -> List[Question]:
        questions = []
        
        if not answer_text or not answer_text.strip():
            return questions
        
        if parent_category == QuestionCategory.PERSON:
            entities = self._extract_person_entities(answer_text)
            templates = self.person_detail_questions
        elif parent_category == QuestionCategory.OBJECT:
            entities = self._extract_object_entities(answer_text)
            templates = self.object_detail_questions
        else:
            entities = [answer_text.strip()]
            templates = self.event_detail_questions
        
        for entity in entities:
            if not entity or not entity.strip():
                continue
            
            entity = entity.strip()
            
            questions_for_entity = []
            for template in templates:
                q_text = template.replace("{entity}", entity)
                questions_for_entity.append(q_text)
            
            selected_questions = questions_for_entity[:3]
            
            for i, q_text in enumerate(selected_questions):
                if i == 0:
                    category = QuestionCategory.PERSON
                elif i == 1:
                    category = QuestionCategory.OBJECT
                else:
                    category = QuestionCategory.EVENT
                
                question = Question(
                    id=self._generate_question_id(),
                    text=q_text,
                    category=category,
                    level=2,
                    parent_answer_id=parent_answer_id
                )
                questions.append(question)
        
        return questions
    
    def generate_level3_questions(self, parent_answer_id: str, answer_text: str, parent_category: QuestionCategory, parent_question_text: str = "") -> List[Question]:
        questions = []
        
        if not answer_text or not answer_text.strip():
            return questions
        
        answer_text = answer_text.strip()
        
        is_place = False
        is_time = False
        is_position = False
        is_course = False
        is_book = False
        is_age = False
        
        if any(province in answer_text for province in self.chinese_provinces):
            is_place = True
        elif any(city in answer_text for city in self.chinese_cities):
            is_place = True
        
        position_keywords = [
            "主管", "经理", "总监", "主任", "部长", "处长", "局长", "厅长",
            "总裁", "CEO", "COO", "CTO", "CFO", "领导", "老板", "创始人",
            "合伙人", "投资者", "股东", "董事", "监事", "书记", "主席"
        ]
        is_position = any(keyword in answer_text for keyword in position_keywords)
        
        course_keywords = ["课程", "课", "学科", "科目", "教程"]
        is_course = any(keyword in answer_text for keyword in course_keywords)
        
        book_keywords = ["书", "课本", "教材", "讲义", "教程", "著作"]
        is_book = any(keyword in answer_text for keyword in book_keywords)
        
        place_keywords = ["教室", "办公室", "会议室", "餐厅", "酒店", "商场", "学校", "公司", "地点"]
        if any(keyword in answer_text for keyword in place_keywords):
            is_place = True
        
        time_keywords = ["早上", "上午", "下午", "晚上", "今天", "明天", "昨天", "上周", "下周", "时间"]
        is_time = any(keyword in answer_text for keyword in time_keywords)
        
        age_patterns = ["岁", "年龄", "多大"]
        is_age = any(pattern in answer_text for pattern in age_patterns) or answer_text.isdigit()
        
        if parent_question_text:
            for q_type, patterns in self.question_type_patterns.items():
                for pattern in patterns:
                    if pattern in parent_question_text:
                        if q_type == "地点":
                            is_place = True
                        elif q_type == "时间":
                            is_time = True
                        elif q_type == "年龄":
                            is_age = True
                        break
        
        templates = []
        
        if is_place:
            templates = [
                f"'{answer_text}'的具体位置是哪里？",
                f"'{answer_text}'有什么特点？",
                f"'{answer_text}'属于哪个省份或城市？",
                f"'{answer_text}'的气候如何？",
                f"'{answer_text}'有什么著名景点？"
            ]
        elif is_time:
            templates = [
                f"'{answer_text}'具体是几点？",
                f"'{answer_text}'是哪个日期？",
                f"'{answer_text}'是星期几？",
                f"'{answer_text}'持续了多久？",
                f"'{answer_text}'之后还有什么安排？"
            ]
        elif is_age:
            templates = [
                f"'{answer_text}'是实岁还是虚岁？",
                f"'{answer_text}'的属相是什么？",
                f"'{answer_text}'的星座是什么？",
                f"'{answer_text}'的出生年份是？",
                f"'{answer_text}'的生日是哪天？"
            ]
        elif parent_category == QuestionCategory.PERSON:
            if is_position:
                templates = [
                    f"'{answer_text}'具体负责什么业务？",
                    f"'{answer_text}'的上级是谁？",
                    f"'{answer_text}'管理多少人？",
                    f"'{answer_text}'的日常工作是什么？",
                    f"'{answer_text}'在哪个部门工作？"
                ]
            else:
                templates = [
                    f"'{answer_text}'的具体职责是什么？",
                    f"'{answer_text}'与这个事件有什么关系？",
                    f"'{answer_text}'的背景是什么？",
                    f"'{answer_text}'有什么特点？",
                    f"'{answer_text}'的联系方式是什么？"
                ]
        
        elif parent_category == QuestionCategory.OBJECT:
            if is_course:
                templates = [
                    f"'{answer_text}'的主要内容是什么？",
                    f"'{answer_text}'是谁教授的？",
                    f"'{answer_text}'在哪个教室上课？",
                    f"'{answer_text}'每周上几次？",
                    f"'{answer_text}'使用什么教材？"
                ]
            elif is_book:
                templates = [
                    f"'{answer_text}'的主要内容是什么？",
                    f"'{answer_text}'是谁编写的？",
                    f"'{answer_text}'是哪个出版社出版的？",
                    f"'{answer_text}'出版于哪一年？",
                    f"'{answer_text}'有多少页？"
                ]
            else:
                templates = [
                    f"'{answer_text}'的具体用途是什么？",
                    f"'{answer_text}'的数量有多少？",
                    f"'{answer_text}'的价值是多少？",
                    f"'{answer_text}'来自哪里？",
                    f"'{answer_text}'是谁提供的？"
                ]
        
        else:
            templates = [
                f"'{answer_text}'的具体情况是什么？",
                f"'{answer_text}'有什么特别之处？",
                f"'{answer_text}'与其他相关事物有什么关系？",
                f"'{answer_text}'的背景是什么？",
                f"'{answer_text}'有什么影响？"
            ]
        
        for i, q_text in enumerate(templates[:3]):
            if i == 0:
                category = QuestionCategory.PERSON
            elif i == 1:
                category = QuestionCategory.OBJECT
            else:
                category = QuestionCategory.EVENT
            
            question = Question(
                id=self._generate_question_id(),
                text=q_text,
                category=category,
                level=3,
                parent_answer_id=parent_answer_id
            )
            questions.append(question)
        
        return questions
    
    def generate_questions_for_answer(self, answer_id: str, answer_text: str, parent_category: QuestionCategory, current_level: int, parent_question_text: str = "") -> List[Question]:
        if current_level == 1:
            return self.generate_level2_questions(answer_id, answer_text, parent_category)
        elif current_level == 2:
            return self.generate_level3_questions(answer_id, answer_text, parent_category, parent_question_text)
        else:
            return []
