from fastapi import Request
from app.database.assignment_repo import AssignmentRepo

def get_repository(request: Request) -> AssignmentRepo:
    repo = getattr(request.app.state, "assignment_repo", None)
    if repo is None:
        raise RuntimeError("Repository non inizializzato")
    return repo