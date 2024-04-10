from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status

from systema.models.item import (
    Item,
    ItemCreate,
    ItemRead,
    ItemUpdate,
)
from systema.proxies.item import ItemProxy
from systema.server.auth.utils import get_current_active_user

router = APIRouter(
    prefix="/projects/{project_id}/items",
    tags=["items"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate, project_id: str):
    return ItemProxy(project_id).create(item)


@router.get("/", response_model=list[ItemRead])
async def list_items(project_id: str):
    return ItemProxy(project_id).all()


@router.get("/{id}", response_model=ItemRead)
async def get_item(project_id: str, id: str):
    try:
        return ItemProxy(project_id).get(id)
    except Item.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")


@router.patch("/{id}", response_model=ItemRead)
async def update_item(project_id: str, id: str, data: ItemUpdate):
    try:
        return ItemProxy(project_id).update(id, data)
    except Item.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(project_id: str, id: str):
    try:
        return ItemProxy(project_id).delete(id)
    except Item.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")


@router.post("/{id}/move/{direction}")
async def move_item(project_id: str, id: str, direction: Literal["up", "down"]):
    try:
        return ItemProxy(project_id).move(id, direction)
    except Item.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")


@router.post("/{id}/toggle")
async def toggle_item(project_id: str, id: str):
    try:
        return ItemProxy(project_id).toggle(id)
    except Item.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
