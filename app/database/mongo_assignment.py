# app/repositories/mongo_assignment.py
from datetime import datetime, timezone
from typing import Sequence, Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.assignment_repo import AssignmentRepo
from app.schemas.assignment import Assignment


class MongoAssignmentRepository(AssignmentRepo):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.col = db["assignments"]

    def _from_doc(self, d: dict) -> Assignment:
        base = {k: v for k, v in d.items() if k not in {"_id"}}
        return Assignment(**base)

    def _to_doc_from_model(self, a: Assignment) -> dict:
        doc = a.model_dump()
        # fallback di sicurezza
        doc.setdefault("createdAt", datetime.now(timezone.utc))
        doc.setdefault("status", "open")
        doc.setdefault("completedAt", None)
        return doc

    async def create(self, assignment: Assignment) -> str:
        """
        Inserisce un Assignment completo (con id già generato nel service).
        """
        doc = self._to_doc_from_model(assignment)
        await self.col.insert_one(doc)
        return assignment.assignmentId

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
    
    async def update_assignment_state(self, now: Optional[datetime] = None) -> int:
        ts = now or datetime.now(timezone.utc)
        res = await self.col.update_many(
            {"deadline": {"$lt": ts}, "status": {"$ne": "completed"}},
            {"$set": {"status": "completed", "completedAt": ts}},
        )
        return res.modified_count or 0

    async def ensure_indexes(self):
        await self.col.create_index("teacherId")
        await self.col.create_index("students")
        await self.col.create_index([("deadline", 1), ("status", 1)])
