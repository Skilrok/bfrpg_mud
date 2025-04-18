from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/")
def get_room(room_id: int, db: Session = Depends(get_db)):
    # TODO: Implement room retrieval logic
    return {"message": f"Room {room_id} details"}


@router.get("/{room_id}/exits")
def get_room_exits(room_id: int, db: Session = Depends(get_db)):
    # TODO: Implement room exits logic
    return {"message": f"Exits for room {room_id}"}


@router.get("/{room_id}/characters")
def get_room_characters(room_id: int, db: Session = Depends(get_db)):
    # TODO: Implement room characters logic
    return {"message": f"Characters in room {room_id}"}
