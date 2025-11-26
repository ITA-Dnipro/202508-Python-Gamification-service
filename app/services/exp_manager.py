from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Request
from typing import Optional
from .. import crud, schemas


def award_experience_by_name(
        db: Session,
        user_id: int,
        action_name: str,
        reference_id: Optional[int] = None,
        user_role: Optional[str] = None,
        request: Optional[Request] = None,
):
    """
    Awards experience to a user for a specific action.
    """

    db_action = crud.get_exp_action_by_name(db, action_name, role=user_role)
    
    if not db_action:
        raise HTTPException(
            status_code=400,
            detail=f"Action '{action_name}' is not available for role '{user_role}'"
        )
    
    user_exp = crud.get_user_experience(db, user_id, user_role)
    if not user_exp:
        user_exp = crud.create_user_experience(db, user_id, user_role)

    if hasattr(db_action, "repeatable") and not db_action.repeatable:
        existing = crud.get_existing_transaction(db, user_exp.id, db_action.id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Experience for action '{action_name}' can be awarded only once"
            )

    try:
        transaction = schemas.ExpTransaction(
            user_experience_id=user_exp.id,
            user_id=user_id,
            action_id=db_action.id,
            exp_awarded=db_action.exp_value,
            reference_id=reference_id,
        )
        crud.create_exp_transaction(db, transaction)
        db_user_exp = crud.update_total_exp(db, user_id, db_action.exp_value, user_role)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Experience already awarded for this action and reference")

    if not db_user_exp:
        raise ValueError("Failed to update user experience")

    return db_user_exp
