from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse

from app.schemas.assignment import AssignmentCreate, Assignment
from app.schemas.context import UserContext
from app.database.assignment import AssignmentRepo
from app.core.deps import get_repository          # <- spostato in core
from app.core.auth import get_current_user        # <- la tua auth in core
from app.services.assignment import AssignmentService

router = APIRouter()

RepoDep = Annotated[AssignmentRepo, Depends(get_repository)]
UserDep = Annotated[UserContext, Depends(get_current_user)]

@router.post("/assignments", status_code=status.HTTP_201_CREATED)
async def create_assignment_endpoint(
    assignment: AssignmentCreate,
    user: UserDep,
    repo: RepoDep,
):
    try:
        new_id = await AssignmentService.create_assignment(assignment, user, repo)
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
    user: UserDep,
    repo: RepoDep,
):
    return await AssignmentService.list_assignments(user, repo)

@router.get("/assignments/{assignment_id}", response_model=Assignment | None)
async def get_assignment_endpoint(
    assignment_id: str,
    user: UserDep,
    repo: RepoDep,
):
    try:
        result = await AssignmentService.get_assignment(assignment_id, user, repo)
        if result is None:
            raise HTTPException(status_code=404, detail="Assignment not found")
        return result
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment_endpoint(
    assignment_id: str,
    user: UserDep,
    repo: RepoDep,
):
    try:
        deleted = await AssignmentService.delete_assignment(assignment_id, user, repo)
        if not deleted:
            raise HTTPException(status_code=404, detail="Assignment not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
