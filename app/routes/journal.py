from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/journal", tags=["journal"])


@router.post("/")
def create_journal_entry(entry: dict, db: Session = Depends(get_db)):
    # TODO: Implement journal entry creation
    return {"message": "Journal entry created"}


@router.get("/{character_id}")
def get_journal_entries(character_id: int, db: Session = Depends(get_db)):
    # TODO: Implement journal entry retrieval
    return {"message": f"Journal entries for character {character_id}"}


@router.delete("/{entry_id}")
def delete_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    # TODO: Implement journal entry deletion
    return {"message": f"Deleted journal entry {entry_id}"}
