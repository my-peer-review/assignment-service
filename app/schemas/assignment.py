from pydantic import BaseModel
from typing import List
from datetime import datetime

class AssignmentCreate(BaseModel):
    title: str
    description: str
    deadline: datetime
    students: List[str]
    content: str

class Assignment(AssignmentCreate):
    assignmentId: str
    teacherId: str
    createdAt: datetime
