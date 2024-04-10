from fastapi import APIRouter, Depends, HTTPException, status

from systema.models.task import (
    Task,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from systema.proxies.task import TaskProxy
from systema.server.auth.utils import get_current_active_user

router = APIRouter(
    prefix="/projects/{project_id}/tasks",
    tags=["tasks"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(project_id: str, task: TaskCreate):
    return TaskProxy(project_id).create(task)


@router.get("/", response_model=list[TaskRead])
async def list_tasks(project_id: str):
    return TaskProxy(project_id).all()


@router.get("/{id}", response_model=TaskRead)
async def get_task(project_id: str, id: str):
    try:
        return TaskProxy(project_id).get(id)
    except Task.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")


@router.patch("/{id}", response_model=TaskRead)
async def edit_task(project_id: str, id: str, task: TaskUpdate):
    try:
        return TaskProxy(project_id).update(id, task)
    except Task.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, id: str):
    try:
        return TaskProxy(project_id).delete(id)
    except Task.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
