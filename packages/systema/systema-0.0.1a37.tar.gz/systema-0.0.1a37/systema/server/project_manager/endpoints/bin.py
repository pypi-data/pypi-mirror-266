from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status

from systema.models.bin import Bin, BinCreate, BinRead, BinUpdate
from systema.proxies.bin import BinProxy
from systema.server.auth.utils import get_current_active_user

router = APIRouter(
    prefix="/projects/{project_id}/bins",
    tags=["bins"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/", response_model=BinRead, status_code=status.HTTP_201_CREATED)
async def create_bin(bin: BinCreate, project_id: str):
    return BinProxy(project_id).create(bin)


@router.get("/", response_model=list[BinRead])
async def list_bins(project_id: str):
    return BinProxy(project_id).all()


@router.get("/{id}", response_model=BinRead)
async def get_bin(project_id: str, id: str):
    try:
        return BinProxy(project_id).get(id)
    except Bin.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bin not found")


@router.patch("/{id}", response_model=BinRead)
async def update_bin(project_id: str, id: str, data: BinUpdate):
    try:
        return BinProxy(project_id).update(id, data)
    except Bin.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bin not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bin(project_id: str, id: str):
    try:
        return BinProxy(project_id).delete(id)
    except Bin.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bin not found")


@router.post("/{id}/move/{direction}")
async def move_bin(project_id: str, id: str, direction: Literal["left", "right"]):
    try:
        return BinProxy(project_id).move(id, direction)
    except Bin.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bin not found")
