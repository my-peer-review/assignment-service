from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence, Optional
from app.schemas.assignment import Assignment, AssignmentCreate

class AssignmentRepo(ABC):
    @abstractmethod
    async def create(self, data: AssignmentCreate, *, teacher_id: str) -> str:
        """Crea un assignment e ritorna l'ID generato."""
        raise NotImplementedError

    @abstractmethod
    async def find_for_teacher(self, teacher_id: str) -> Sequence[Assignment]:
        """Ritorna gli assignment per un dato teacher."""
        raise NotImplementedError

    @abstractmethod
    async def find_for_student(self, student_id: str) -> Sequence[Assignment]:
        """Ritorna gli assignment per un dato studente."""
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, assignment_id: str) -> Optional[Assignment]:
        """Ritorna un assignment per ID, oppure None se non esiste."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, assignment_id: str) -> bool:
        """Cancella un assignment. Ritorna True se qualcosa è stato cancellato."""
        raise NotImplementedError
