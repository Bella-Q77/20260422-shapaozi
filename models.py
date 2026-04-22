from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class QuestionCategory(Enum):
    PERSON = "人物"
    OBJECT = "对象"
    EVENT = "事件"


@dataclass
class Question:
    id: str
    text: str
    category: QuestionCategory
    level: int
    parent_answer_id: Optional[str] = None
    is_answered: bool = False


@dataclass
class Answer:
    id: str
    question_id: str
    text: str
    level: int
    child_questions: List[Question] = field(default_factory=list)


@dataclass
class Event:
    id: str
    initial_text: str
    level: int = 0
    questions: List[Question] = field(default_factory=list)
    answers: Dict[str, Answer] = field(default_factory=dict)
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        for q in self.questions:
            if q.id == question_id:
                return q
        for answer in self.answers.values():
            for q in answer.child_questions:
                if q.id == question_id:
                    return q
        return None
    
    def get_answer_by_question_id(self, question_id: str) -> Optional[Answer]:
        return self.answers.get(question_id)
    
    def add_answer(self, question_id: str, answer_text: str, level: int) -> Answer:
        answer_id = f"answer_{question_id}"
        answer = Answer(
            id=answer_id,
            question_id=question_id,
            text=answer_text,
            level=level
        )
        self.answers[question_id] = answer
        
        question = self.get_question_by_id(question_id)
        if question:
            question.is_answered = True
        
        return answer
    
    def add_child_questions(self, parent_answer_id: str, questions: List[Question]) -> None:
        for answer in self.answers.values():
            if answer.id == parent_answer_id:
                answer.child_questions.extend(questions)
                break
    
    def get_all_questions(self) -> List[Question]:
        all_questions = list(self.questions)
        for answer in self.answers.values():
            all_questions.extend(answer.child_questions)
        return all_questions
    
    def get_questions_by_level(self, level: int) -> List[Question]:
        return [q for q in self.get_all_questions() if q.level == level]
    
    def get_unanswered_questions(self) -> List[Question]:
        return [q for q in self.get_all_questions() if not q.is_answered]
    
    def get_answered_questions(self) -> List[Question]:
        return [q for q in self.get_all_questions() if q.is_answered]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "initial_text": self.initial_text,
            "level": self.level,
            "questions": [
                {
                    "id": q.id,
                    "text": q.text,
                    "category": q.category.value,
                    "level": q.level,
                    "parent_answer_id": q.parent_answer_id,
                    "is_answered": q.is_answered
                }
                for q in self.questions
            ],
            "answers": {
                qid: {
                    "id": a.id,
                    "question_id": a.question_id,
                    "text": a.text,
                    "level": a.level,
                    "child_questions": [
                        {
                            "id": cq.id,
                            "text": cq.text,
                            "category": cq.category.value,
                            "level": cq.level,
                            "parent_answer_id": cq.parent_answer_id,
                            "is_answered": cq.is_answered
                        }
                        for cq in a.child_questions
                    ]
                }
                for qid, a in self.answers.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        event = cls(
            id=data["id"],
            initial_text=data["initial_text"],
            level=data["level"]
        )
        
        for q_data in data["questions"]:
            question = Question(
                id=q_data["id"],
                text=q_data["text"],
                category=QuestionCategory(q_data["category"]),
                level=q_data["level"],
                parent_answer_id=q_data.get("parent_answer_id"),
                is_answered=q_data["is_answered"]
            )
            event.questions.append(question)
        
        for qid, a_data in data["answers"].items():
            answer = Answer(
                id=a_data["id"],
                question_id=a_data["question_id"],
                text=a_data["text"],
                level=a_data["level"]
            )
            
            for cq_data in a_data["child_questions"]:
                child_question = Question(
                    id=cq_data["id"],
                    text=cq_data["text"],
                    category=QuestionCategory(cq_data["category"]),
                    level=cq_data["level"],
                    parent_answer_id=cq_data.get("parent_answer_id"),
                    is_answered=cq_data["is_answered"]
                )
                answer.child_questions.append(child_question)
            
            event.answers[qid] = answer
        
        return event
