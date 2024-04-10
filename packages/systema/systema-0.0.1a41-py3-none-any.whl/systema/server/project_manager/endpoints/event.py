from fastapi import APIRouter, Depends, HTTPException, status

from systema.models.event import Event, EventCreate, EventRead, EventUpdate
from systema.proxies.event import EventProxy
from systema.server.auth.utils import get_current_active_user

router = APIRouter(
    prefix="/projects/{project_id}/events",
    tags=["events"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, project_id: str):
    return EventProxy(project_id).create(event)


@router.get("/", response_model=list[EventRead])
async def list_events(project_id: str):
    return EventProxy(project_id).all()


@router.get("/{id}", response_model=EventRead)
async def get_event(project_id: str, id: str):
    try:
        return EventProxy(project_id).get(id)
    except Event.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")


@router.patch("/{id}", response_model=EventRead)
async def update_event(project_id: str, id: str, data: EventUpdate):
    try:
        return EventProxy(project_id).update(id, data)
    except Event.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(project_id: str, id: str):
    try:
        return EventProxy(project_id).delete(id)
    except Event.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
