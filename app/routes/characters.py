from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/characters", tags=["characters"])


@router.post("/", response_model=schemas.Character)
def create_character(character: schemas.CharacterCreate, db: Session = Depends(get_db)):
    db_character = models.Character(**character.dict())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character


@router.get("/", response_model=List[schemas.Character])
def read_characters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    characters = db.query(models.Character).offset(skip).limit(limit).all()
    return characters


@router.get("/{character_id}", response_model=schemas.Character)
def read_character(character_id: int, db: Session = Depends(get_db)):
    db_character = (
        db.query(models.Character).filter(models.Character.id == character_id).first()
    )
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return db_character
