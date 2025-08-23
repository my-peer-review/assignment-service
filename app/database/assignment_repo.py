from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence, Optional
from app.schemas.assignment import Assignment, AssignmentCreate

class AssignmentRepo(ABC):
    @abstractmethod
    async def create(self, data: AssignmentCreate) -> str:
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
    
    @abstractmethod
    async def update_assignment_state(self, now: Optional[datetime] = None) -> int:
        """Aggiorna lo stato degli assignment presenti nel database se la sua deadline è minore a now, 
        ritorna il numero di aggiornamente effettuati"""
        raise NotImplementedError
