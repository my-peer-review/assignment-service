from typing import Sequence, Optional
from app.schemas.assignment import AssignmentCreate, Assignment
from app.schemas.context import UserContext
from app.database.assignment import AssignmentRepo

def _is_teacher(role):
    return role == "teacher" or (isinstance(role, (list, tuple, set)) and "teacher" in role)

def _is_student(role):
    return role == "student" or (isinstance(role, (list, tuple, set)) and "student" in role)

async def create_assignment(data: AssignmentCreate, user: UserContext, repo: AssignmentRepo) -> str:
    if not _is_teacher(user.role):
        raise PermissionError("Only teachers can create assignments")
    return await repo.create(data, teacher_id=user.user_id)

async def list_assignments(user: UserContext, repo: AssignmentRepo) -> Sequence[Assignment]:
    if _is_teacher(user.role):
        return await repo.find_for_teacher(user.user_id)
    if _is_student(user.role):
        return await repo.find_for_student(user.user_id)
    return []

async def get_assignment(assignment_id: str, user: UserContext, repo: AssignmentRepo) -> Optional[Assignment]:
    doc = await repo.find_one(assignment_id)
    if not doc:
        return None
    if _is_teacher(user.role) and doc.teacherId != user.user_id:
        raise PermissionError("Accesso negato all'assignment")
    if _is_student(user.role) and user.user_id not in getattr(doc, "students", []):
        raise PermissionError("Non sei tra gli studenti assegnati")
    return doc

async def delete_assignment(assignment_id: str, user: UserContext, repo: AssignmentRepo) -> bool:
    if not _is_teacher(user.role):
        raise PermissionError("Only teachers can delete assignments")
    return await repo.delete(assignment_id)