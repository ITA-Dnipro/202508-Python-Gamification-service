import sys
import os
import pytest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app import crud, models, schemas


def setup_in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    models.Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


@pytest.mark.parametrize("role", [None, "startup", "investor"])
def test_award_exp_correctly(role):
    engine, SessionLocal = setup_in_memory_db()
    db = SessionLocal()

    action = models.ExpAction(name=f"test_award_{role}", role=role, exp_value=25, repeatable=True)
    db.add(action)
    db.commit()
    db.refresh(action)
    user_exp = crud.create_user_experience(db, user_id=1, role=role)

    tx = schemas.ExpTransaction(
        user_experience_id=user_exp.id,
        user_id=1,
        action_id=action.id,
        exp_awarded=action.exp_value,
        reference=1001,
    )

    crud.create_exp_transaction(db, tx)
    updated = crud.update_total_exp(db, user_id=1, exp_value=action.exp_value, role=role)

    assert updated is not None
    assert updated.total_exp == 25

    db.close()


@pytest.mark.parametrize("role", [None, "startup", "investor"])
def test_prevent_duplicate_transaction_for_same_reference(role):
    engine, SessionLocal = setup_in_memory_db()
    db = SessionLocal()

    action = models.ExpAction(name=f"test_dup_{role}", role=role, exp_value=10, repeatable=False)
    db.add(action)
    db.commit()
    db.refresh(action)

    awarded = action.exp_value

    user_exp = crud.create_user_experience(db, user_id=2, role=role)

    tx = schemas.ExpTransaction(
        user_experience_id=user_exp.id,
        user_id=2,
        action_id=action.id,
        exp_awarded=action.exp_value,
        reference=2002,
    )

    crud.create_exp_transaction(db, tx)
    crud.update_total_exp(db, user_id=2, exp_value=action.exp_value, role=role)
    db.commit()
    
    dup = schemas.ExpTransaction(
        user_experience_id=user_exp.id,
        user_id=2,
        action_id=action.id,
        exp_awarded=action.exp_value,
        reference=2002,
    )

    db_dup = SessionLocal()
    try:
        with pytest.raises(IntegrityError):
            crud.create_exp_transaction(db_dup, dup)
    finally:
        try:
            db_dup.rollback()
        except Exception:
            pass
        db_dup.close()

    db.close()

    db2 = SessionLocal()
    ue = crud.get_user_experience(db2, user_id=2, role=role)
    assert ue is not None
    assert ue.total_exp == awarded
    db2.close()
