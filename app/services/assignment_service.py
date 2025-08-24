from datetime import datetime, timezone
import random
from typing import List, Sequence, Optional, Tuple
from app.schemas.assignment import AssignmentCreate, Assignment
from app.schemas.context import UserContext
from app.database.assignment_repo import AssignmentRepo

def create_assignment_id() -> str:
    # stesso formato che avevi nel repo
    return f"as-{random.randint(0, 99999):05d}"

def _is_teacher(role):
        return role == "teacher" or (isinstance(role, (list, tuple, set)) and "teacher" in role)

def _is_student(role):
        return role == "student" or (isinstance(role, (list, tuple, set)) and "student" in role)

class AssignmentService:

    @staticmethod
    async def create_assignment(
        data: AssignmentCreate,
        user: UserContext,
        repo: AssignmentRepo
    ) -> str:
        if not _is_teacher(user.role):
            raise PermissionError("Only teachers can create assignments")

        new_id = create_assignment_id()
        assignment = Assignment(
            assignmentId=new_id,
            teacherId=str(user.user_id),
            createdAt=datetime.now(timezone.utc),
            status="open",
            completedAt=None,
            **data.model_dump(),
        )

        inserted_id = await repo.create(assignment)
        if not inserted_id:
            raise RuntimeError("Creazione assignment fallita")

        # ritorna esattamente ciò che ti serve per RabbitMQ
        return inserted_id


    @staticmethod
    async def list_assignments(user: UserContext, repo: AssignmentRepo) -> Sequence[Assignment]:
        if _is_teacher(user.role):
            return await repo.find_for_teacher(user.user_id)
        if _is_student(user.role):
            return await repo.find_for_student(user.user_id)
        return []
    
    @staticmethod
    async def get_assignment(assignment_id: str, user: UserContext, repo: AssignmentRepo) -> Optional[Assignment]:
        doc = await repo.find_one(assignment_id)
        if not doc:
            return None
        if _is_teacher(user.role) and doc.teacherId != user.user_id:
            raise PermissionError("Accesso negato all'assignment")
        if _is_student(user.role) and user.user_id not in getattr(doc, "students", []):
            raise PermissionError("Non sei tra gli studenti assegnati")
        return doc

    @staticmethod
    async def delete_assignment(assignment_id: str, user: UserContext, repo: AssignmentRepo) -> bool:
        if not _is_teacher(user.role):
            raise PermissionError("Only teachers can delete assignments")
        return await repo.delete(assignment_id)
    
    @staticmethod
    async def sweep_deadlines(repo: AssignmentRepo) -> List[str]:
        """
        Esegue UNA passata: segna 'completed' gli assignment con deadline < now.
        Ritorna il numero di documenti aggiornati.
        """
        ts = datetime.now(timezone.utc)
        # normalizzazione: tronca ai millisecondi
        ts = ts.replace(microsecond=(ts.microsecond // 1000) * 1000)

        return await repo.update_assignment_state(ts)

        
