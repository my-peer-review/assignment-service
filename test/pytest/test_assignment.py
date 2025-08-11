# tests/unit/test_assignment_service.py
import pytest
from datetime import datetime, timedelta, timezone

from app.services.assignment import (
    create_assignment, list_assignments, get_assignment, delete_assignment
)
from app.schemas.assignment import AssignmentCreate, Assignment
from app.schemas.context import UserContext


# ------------------------- Fake repository (minimale) -------------------------
class FakeAssignmentRepo:
    def __init__(self):
        self.items: dict[str, Assignment] = {}

    async def create(self, data: AssignmentCreate, *, teacher_id: str) -> str:
        from uuid import uuid4
        new_id = str(uuid4())
        a = Assignment(
            id=new_id,
            createdAt=datetime.now(timezone.utc),
            teacherId=teacher_id,
            **data.model_dump(),
        )
        self.items[new_id] = a
        return new_id

    async def find_for_teacher(self, teacher_id: str):
        return [a for a in self.items.values() if a.teacherId == teacher_id]

    async def find_for_student(self, student_id: str):
        return [a for a in self.items.values() if student_id in getattr(a, "students", [])]

    async def find_one(self, assignment_id: str):
        return self.items.get(assignment_id)

    async def delete(self, assignment_id: str):
        return self.items.pop(assignment_id, None) is not None


# ------------------------------- Fixtures -------------------------------------
@pytest.fixture
def repo():
    return FakeAssignmentRepo()

@pytest.fixture
def teacher():
    return UserContext(user_id="t1", role="teacher")

@pytest.fixture
def other_teacher():
    return UserContext(user_id="t2", role="teacher")

@pytest.fixture
def student():
    return UserContext(user_id="s1", role="student")

@pytest.fixture
def student2():
    return UserContext(user_id="s2", role="student")


def _make_create(**overrides):
    future = datetime.now(timezone.utc) + timedelta(days=7)
    base = dict(
        title="Compito",
        description="Desc",
        deadline=future,
        students=[],
        content="Testo",
    )
    base.update(overrides)
    return AssignmentCreate(**base)


# --------------------------------- Tests --------------------------------------
@pytest.mark.asyncio
async def test_create_requires_teacher(repo, student):
    with pytest.raises(PermissionError):
        await create_assignment(_make_create(), student, repo)

@pytest.mark.asyncio
async def test_create_ok(repo, teacher):
    new_id = await create_assignment(_make_create(students=["s1", "s2"]), teacher, repo)
    assert new_id
    saved = await repo.find_one(new_id)
    assert saved is not None
    assert saved.teacherId == "t1"
    assert saved.students == ["s1", "s2"]

@pytest.mark.asyncio
async def test_list_for_teacher(repo, teacher, other_teacher):
    # seed
    a1 = await repo.create(_make_create(title="A"), teacher_id=teacher.user_id)
    a2 = await repo.create(_make_create(title="B"), teacher_id=teacher.user_id)
    _  = await repo.create(_make_create(title="C"), teacher_id=other_teacher.user_id)

    items = await list_assignments(teacher, repo)
    ids = {a.id for a in items}
    titles = {a.title for a in items}
    assert {a1, a2}.issubset(ids)
    assert titles == {"A", "B"}

@pytest.mark.asyncio
async def test_list_for_student(repo, teacher, student):
    _ = await repo.create(_make_create(title="SoloS1", students=["s1"]), teacher_id=teacher.user_id)
    _ = await repo.create(_make_create(title="SoloS2", students=["s2"]), teacher_id=teacher.user_id)

    items = await list_assignments(student, repo)
    assert len(items) == 1
    assert items[0].title == "SoloS1"

@pytest.mark.asyncio
async def test_list_other_role_returns_empty(repo, teacher):
    other = UserContext(user_id="x1", role="admin")
    _ = await repo.create(_make_create(title="A"), teacher_id=teacher.user_id)
    items = await list_assignments(other, repo)
    assert items == []

@pytest.mark.asyncio
async def test_get_teacher_access_ok(repo, teacher, other_teacher):
    aid = await repo.create(_make_create(title="X"), teacher_id=teacher.user_id)
    item = await get_assignment(aid, teacher, repo)
    assert item is not None
    with pytest.raises(PermissionError):
        await get_assignment(aid, other_teacher, repo)

@pytest.mark.asyncio
async def test_get_student_access_ok_and_denied(repo, teacher, student, student2):
    aid = await repo.create(_make_create(title="X", students=["s1"]), teacher_id=teacher.user_id)
    ok = await get_assignment(aid, student, repo)
    assert ok is not None
    with pytest.raises(PermissionError):
        await get_assignment(aid, student2, repo)

@pytest.mark.asyncio
async def test_delete_requires_teacher(repo, student):
    with pytest.raises(PermissionError):
        await delete_assignment("non-existent", student, repo)

@pytest.mark.asyncio
async def test_delete_ok_and_not_found(repo, teacher):
    aid = await repo.create(_make_create(), teacher_id=teacher.user_id)
    assert await delete_assignment(aid, teacher, repo) is True
    assert await delete_assignment(aid, teacher, repo) is False
