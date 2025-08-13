# app/repositories/mongo_assignment.py
from datetime import datetime, timezone
from typing import Sequence, Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from uuid import uuid4

from app.database.assignment import AssignmentRepo
from app.schemas.assignment import Assignment, AssignmentCreate


class MongoAssignmentRepository(AssignmentRepo):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.col = db["assignments"]

    def _from_doc(self, d: dict) -> Assignment:
        return Assignment(
            id=str(d["assignmentId"]),
            createdAt=d["createdAt"],
            teacherId=d["teacherId"],
            **{k: v for k, v in d.items() if k not in {"_id", "createdAt", "teacherId"}}
        )

    def _to_doc(self, a_id: str, data: AssignmentCreate, teacher_id: str) -> dict:
        return {
            "assignmentId": a_id,
            "createdAt": datetime.now(timezone.utc),
            "teacherId": teacher_id,
            **data.model_dump(),
        }

    async def create(self, data: AssignmentCreate, *, teacher_id: str) -> str:
        new_id = str(uuid4())
        doc = self._to_doc(new_id, data, teacher_id)
        await self.col.insert_one(doc)
        return new_id

    async def find_for_teacher(self, teacher_id: str) -> Sequence[Assignment]:
        cursor = self.col.find({"teacherId": str(teacher_id)})
        docs: List[dict] = [d async for d in cursor]
        return [self._from_doc(d) for d in docs]

    async def find_for_student(self, student_id: str) -> Sequence[Assignment]:
        cursor = self.col.find({"students": {"$in": [str(student_id)]}})
        docs: List[dict] = [d async for d in cursor]
        return [self._from_doc(d) for d in docs]

    async def find_one(self, assignment_id: str) -> Optional[Assignment]:
        d = await self.col.find_one({"assignmentId": str(assignment_id)})
        return self._from_doc(d) if d else None

    async def delete(self, assignment_id: str) -> bool:
        res = await self.col.delete_one({"assignmentId": str(assignment_id)})
        return res.deleted_count > 0

    async def ensure_indexes(self):
        await self.col.create_index("teacherId")
        await self.col.create_index("students")
