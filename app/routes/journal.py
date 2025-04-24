from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/journal",
    tags=["journal"],
    responses={404: {"description": "Not found"}},
)

# In-memory storage for journal entries until database implementation
journal_entries = {}  # character_id -> list of entries


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_journal_entry(character_id: str, text: str):
    """
    Create a new journal entry for a character
    """
    if character_id not in journal_entries:
        journal_entries[character_id] = []

    # Create a new entry
    entry = {
        "id": f"entry_{len(journal_entries[character_id])}",
        "character_id": character_id,
        "text": text,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    # Add to in-memory storage
    journal_entries[character_id].append(entry)

    return entry


@router.get("/character/{character_id}")
async def get_journal_entries(character_id: str) -> List[Dict[str, Any]]:
    """
    Get all journal entries for a character
    """
    if character_id not in journal_entries:
        return []

    return journal_entries[character_id]


@router.delete("/delete/{entry_id}")
async def delete_journal_entry(entry_id: str, character_id: str):
    """
    Delete a journal entry
    """
    if character_id not in journal_entries:
        raise HTTPException(status_code=404, detail="Character not found")

    for i, entry in enumerate(journal_entries[character_id]):
        if entry["id"] == entry_id:
            return journal_entries[character_id].pop(i)

    raise HTTPException(status_code=404, detail="Journal entry not found")
