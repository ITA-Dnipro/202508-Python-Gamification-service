from fastapi import APIRouter, Depends, Request, Body, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas, crud
from ..services import exp_manager
from typing import Optional
from ..auth import get_current_user_role, get_current_user_id

router = APIRouter(prefix="/api/gamification", tags=["gamification"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/startup/{startup_id}/award-exp", response_model=schemas.UserExperience)
def award_experience_startup(
        startup_id: int,
        request: Request,
        action_name: str = Body(..., embed=True),
        reference_id: Optional[int] = Body(None, embed=True),
        db: Session = Depends(get_db),
):  
    user_id = get_current_user_id(token=request.headers.get("Authorization").split(" ")[1])
    if user_id != startup_id:
        raise HTTPException(status_code=403, detail="Operation not permitted for this user")
    role = get_current_user_role(token=request.headers.get("Authorization").split(" ")[1])
    if role != "startup":
        raise HTTPException(status_code=403, detail="Operation not permitted for this user role")
    
    award = exp_manager.award_experience_by_name(
        db=db,
        user_id=startup_id,
        action_name=action_name,
        reference_id=reference_id,
        user_role="startup",
        request=request,
    )
    db.commit()
    return award


@router.post("/investor/{investor_id}/award-exp", response_model=schemas.UserExperience)
def award_experience_investor(
        investor_id: int,
        request: Request,
        action_name: str = Body(..., embed=True),
        reference_id: Optional[int] = Body(None, embed=True),
        db: Session = Depends(get_db),
):
    user_id = get_current_user_id(token=request.headers.get("Authorization").split(" ")[1])
    if user_id != investor_id:
        raise HTTPException(status_code=403, detail="Operation not permitted for this user")
    role = get_current_user_role(token=request.headers.get("Authorization").split(" ")[1])
    if role != "investor":
        raise HTTPException(status_code=403, detail="Operation not permitted for this user role")
    
    award = exp_manager.award_experience_by_name(
        db=db,
        user_id=investor_id,
        action_name=action_name,
        reference_id=reference_id,
        user_role="investor",
        request=request,
    )
    db.commit()
    return award


@router.get("/startup/{startup_id}/experience", response_model=schemas.UserExperience)
def get_startup_experience(startup_id: int, db: Session = Depends(get_db)):
    user_exp = crud.get_user_experience(db=db, user_id=startup_id, role="startup")
    if not user_exp:
        user_exp = crud.create_user_experience(db=db, user_id=startup_id, role="startup")
    db.commit()
    return user_exp


@router.get("/investor/{investor_id}/experience", response_model=schemas.UserExperience)
def get_investor_experience(investor_id: int, db: Session = Depends(get_db)):
    user_exp = crud.get_user_experience(db=db, user_id=investor_id, role="investor")
    if not user_exp:
        user_exp = crud.create_user_experience(db=db, user_id=investor_id, role="investor")
    db.commit()
    return user_exp

