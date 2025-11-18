from sqlalchemy.orm import Session
from typing import Optional
from . import models, schemas
from sqlalchemy import update
import logging

logger = logging.getLogger(__name__)


def get_exp_action_by_name(db: Session, action_name: str, role: str) -> Optional[models.ExpAction]:
    action = db.query(models.ExpAction).filter(
        models.ExpAction.name == action_name, 
        models.ExpAction.role == role
    ).first()
    
    if not action:
        action = db.query(models.ExpAction).filter(
            models.ExpAction.name == action_name,
            models.ExpAction.role == None
        ).first()
    
    return action


def create_exp_transaction(db: Session, transaction: schemas.ExpTransaction) -> models.ExpTransaction:
    tx_data = transaction.dict()
    db_transaction = models.ExpTransaction(**tx_data)
    db.add(db_transaction)
    db.flush()
    db.refresh(db_transaction)
    return db_transaction


def get_existing_transaction(db: Session, user_experience_id: int, action_id: int):
    return db.query(models.ExpTransaction).filter(
        models.ExpTransaction.user_experience_id == user_experience_id,
        models.ExpTransaction.action_id == action_id
    ).first()


def create_user_experience(db: Session, user_id: int, role: Optional[str]):
    user_exp = models.UserExperience(user_id=user_id, role=role, total_exp=0)
    db.add(user_exp)
    db.flush()
    db.refresh(user_exp)
    return user_exp


def get_user_experience(db: Session, user_id: int, role: Optional[str]):
    return db.query(models.UserExperience).filter(
        models.UserExperience.user_id == user_id,
        models.UserExperience.role == role
    ).first()


def update_total_exp(db: Session, user_id: int, exp_value: int, role: Optional[str]):
    stmt = (
        update(models.UserExperience)
        .where(models.UserExperience.user_id == user_id)
        .where(models.UserExperience.role == role)
        .values(total_exp=models.UserExperience.total_exp + exp_value)
    )
    result = db.execute(stmt)
    db.flush()

    if result.rowcount == 0:
        return None
    else:
        logger.info(f"User {user_id} gained {exp_value} exp (role={role})")

    return get_user_experience(db, user_id, role)
