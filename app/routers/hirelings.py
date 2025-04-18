from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import models, schemas
from ..database import get_db
from . import auth

router = APIRouter()


@router.post("/", response_model=schemas.Hireling)
async def create_hireling(
    hireling: schemas.HirelingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    try:
        # Create the hireling with user data
        db_hireling = models.Hireling(
            name=hireling.name,
            character_class=hireling.character_class,
            level=hireling.level,
            experience=hireling.experience,
            loyalty=hireling.loyalty,
            wage=hireling.wage,
            user_id=current_user.id,
            is_available=True,
            hireling_type=hireling.hireling_type,
        )
        db.add(db_hireling)
        db.commit()
        db.refresh(db_hireling)
        
        # Convert to Pydantic model
        return schemas.Hireling.from_orm(db_hireling)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create hireling: {str(e)}"
        )


@router.get("/", response_model=List[schemas.Hireling])
async def get_hirelings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    try:
        hirelings = (
            db.query(models.Hireling)
            .filter(models.Hireling.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        # Update payment status for all hirelings
        for hireling in hirelings:
            if hireling.last_payment_date:
                days_since_payment = (datetime.utcnow() - hireling.last_payment_date).days
                if days_since_payment > 0:
                    hireling.days_unpaid = days_since_payment
                    # Loyalty decreases by 5 points per unpaid day
                    hireling.update_loyalty(-5.0 * days_since_payment)
        
        db.commit()
        
        # Convert to Pydantic models
        return [schemas.Hireling.from_orm(h) for h in hirelings]
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error retrieving hirelings: {str(e)}")


@router.get("/{hireling_id}", response_model=schemas.Hireling)
async def get_hireling(
    hireling_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    try:
        hireling = (
            db.query(models.Hireling)
            .filter(
                models.Hireling.id == hireling_id,
                models.Hireling.user_id == current_user.id,
            )
            .first()
        )
        if hireling is None:
            raise HTTPException(status_code=404, detail="Hireling not found")

        # Update payment status and loyalty
        if hireling.last_payment_date:
            days_since_payment = (datetime.utcnow() - hireling.last_payment_date).days
            if days_since_payment > 0:
                hireling.days_unpaid = days_since_payment
                # Loyalty decreases by 5 points per unpaid day
                hireling.update_loyalty(-5.0 * days_since_payment)
                db.commit()
                db.refresh(hireling)

        # Return Pydantic model
        return schemas.Hireling.from_orm(hireling)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error retrieving hireling: {str(e)}")


@router.put("/{hireling_id}/hire/{character_id}", response_model=schemas.Hireling)
async def hire_hireling(
    hireling_id: int,
    character_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    try:
        # Debug log the input values to help diagnose issues
        print(f"Hiring hireling: hireling_id={hireling_id}, character_id={character_id}, user_id={current_user.id}")
        
        # Verify the character belongs to the user
        character = (
            db.query(models.Character)
            .filter(
                models.Character.id == character_id,
                models.Character.user_id == current_user.id,
            )
            .first()
        )
        if character is None:
            raise HTTPException(status_code=404, detail="Character not found")

        # Get and update the hireling
        hireling = (
            db.query(models.Hireling)
            .filter(
                models.Hireling.id == hireling_id,
                models.Hireling.user_id == current_user.id,
            )
            .first()
        )
        if hireling is None:
            raise HTTPException(status_code=404, detail="Hireling not found")

        hireling.master_id = character_id
        hireling.is_available = False
        db.commit()
        db.refresh(hireling)
        
        # Return a Pydantic model
        result = schemas.Hireling.from_orm(hireling)
        return result
    except Exception as e:
        db.rollback()
        print(f"Error in hire_hireling: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error hiring hireling: {str(e)}")


@router.put("/{hireling_id}/dismiss", response_model=schemas.Hireling)
async def dismiss_hireling(
    hireling_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    try:
        hireling = (
            db.query(models.Hireling)
            .filter(
                models.Hireling.id == hireling_id,
                models.Hireling.user_id == current_user.id,
            )
            .first()
        )
        if hireling is None:
            raise HTTPException(status_code=404, detail="Hireling not found")

        hireling.master_id = None
        hireling.is_available = True
        db.commit()
        db.refresh(hireling)
        
        # Return a Pydantic model
        return schemas.Hireling.from_orm(hireling)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error dismissing hireling: {str(e)}")


@router.put("/{hireling_id}/pay", response_model=schemas.Hireling)
async def pay_hireling(
    hireling_id: int,
    days: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    try:
        hireling = (
            db.query(models.Hireling)
            .filter(
                models.Hireling.id == hireling_id,
                models.Hireling.user_id == current_user.id,
            )
            .first()
        )
        if hireling is None:
            raise HTTPException(status_code=404, detail="Hireling not found")

        # Calculate total payment
        total_payment = hireling.wage * days

        # Update hireling's payment status
        hireling.last_payment_date = datetime.utcnow()
        hireling.days_unpaid = 0
        hireling.update_loyalty(2.0 * days)  # Increase loyalty by 2 points per day paid

        db.commit()
        db.refresh(hireling)
        
        # Return a Pydantic model
        return schemas.Hireling.from_orm(hireling)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error paying hireling: {str(e)}")


@router.put("/{hireling_id}/reward", response_model=schemas.Hireling)
async def reward_hireling(
    hireling_id: int,
    amount: float,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    try:
        hireling = (
            db.query(models.Hireling)
            .filter(
                models.Hireling.id == hireling_id,
                models.Hireling.user_id == current_user.id,
            )
            .first()
        )
        if hireling is None:
            raise HTTPException(status_code=404, detail="Hireling not found")

        # Increase loyalty based on reward amount
        loyalty_increase = min(amount / 10, 10.0)  # Max 10 points per reward
        hireling.update_loyalty(loyalty_increase)

        db.commit()
        db.refresh(hireling)
        
        # Return a Pydantic model
        return schemas.Hireling.from_orm(hireling)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error rewarding hireling: {str(e)}")
