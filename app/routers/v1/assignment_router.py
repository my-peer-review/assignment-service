from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.assignment import AssignmentCreate, Assignment
from app.schemas.context import UserContext
from app.database.assignment import AssignmentRepo 
from app.services import assignment as assignment_service

router = APIRouter()

# Dependency: prende il repo messo in app.state dal lifespan
def get_assignment_repo(request: Request) -> AssignmentRepo:
    repo = getattr(request.app.state, "assignment_repo", None)
    if repo is None:
        raise RuntimeError("Repository non inizializzato")
    return repo

# Sostituisci con la tua auth reale
async def get_current_user() -> UserContext:
    return UserContext(user_id="u1", role="teacher")

@router.post("/assignments", status_code=status.HTTP_201_CREATED)
async def create_assignment_endpoint(
    assignment: AssignmentCreate,
    user: UserContext = Depends(get_current_user),
    repo: AssignmentRepo = Depends(get_assignment_repo),
):
    try:
        new_id = await assignment_service.create_assignment(assignment, user, repo)
        location = f"/api/v1/assignments/{new_id}"
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Assignment created successfully.", "id": new_id},
            headers={"Location": location},
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/assignments", response_model=list[Assignment])
async def list_assignments_endpoint(
    user: UserContext = Depends(get_current_user),
    repo: AssignmentRepo = Depends(get_assignment_repo),
):
    return await assignment_service.list_assignments(user, repo)

@router.get("/assignments/{assignment_id}", response_model=Assignment | None)
async def get_assignment_endpoint(
    assignment_id: str,
    user: UserContext = Depends(get_current_user),
    repo: AssignmentRepo = Depends(get_assignment_repo),
):
    try:
        result = await assignment_service.get_assignment(assignment_id, user, repo)
        if result is None:
            raise HTTPException(status_code=404, detail="Assignment not found")
        return result
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment_endpoint(
    assignment_id: str,
    user: UserContext = Depends(get_current_user),
    repo: AssignmentRepo = Depends(get_assignment_repo),
):
    try:
        deleted = await assignment_service.delete_assignment(assignment_id, user, repo)
        if not deleted:
            raise HTTPException(status_code=404, detail="Assignment not found")
        # 204: nessun body
        return
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
