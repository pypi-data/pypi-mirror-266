from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status

from systema.models.card import Card, CardCreate, CardRead, CardUpdate
from systema.proxies.card import CardProxy
from systema.server.auth.utils import get_current_active_user

router = APIRouter(
    prefix="/projects/{project_id}/cards",
    tags=["cards"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/", response_model=CardRead, status_code=status.HTTP_201_CREATED)
async def create_card(card: CardCreate, project_id: str):
    return CardProxy(project_id).create(card)


@router.get("/", response_model=list[CardRead])
async def list_cards(project_id: str):
    return CardProxy(project_id).all()


@router.get("/{id}", response_model=CardRead)
async def get_card(project_id: str, id: str):
    try:
        return CardProxy(project_id).get(id)
    except Card.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Card not found")


@router.patch("/{id}", response_model=CardRead)
async def update_card(project_id: str, id: str, data: CardUpdate):
    try:
        return CardProxy(project_id).update(id, data)
    except Card.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Card not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(project_id: str, id: str):
    try:
        return CardProxy(project_id).delete(id)
    except Card.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Card not found")


@router.post("/{id}/move/{direction}")
async def move_card(
    project_id: str, id: str, direction: Literal["up", "down", "left", "right"]
):
    try:
        return CardProxy(project_id).move(id, direction)
    except Card.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Card not found")
