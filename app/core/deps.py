from fastapi import Request
from app.database.assignment_repo import AssignmentRepo
from app.services.publisher_service import AssignmentPublisher

def get_repository(request: Request) -> AssignmentRepo:
    repo = getattr(request.app.state, "assignment_repo", None)
    if repo is None:
        raise RuntimeError("Repository non inizializzato")
    return repo

def get_publisher(request: Request) -> AssignmentPublisher:
    publisher = getattr(request.app.state, "assignment_publisher", None)
    if publisher is None:
        raise RuntimeError("Publiscer non inizializzato")
    return publisher