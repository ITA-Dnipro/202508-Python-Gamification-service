from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Text, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base


class ExpAction(Base):
    __tablename__ = "exp_action"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=True)
    repeatable = Column(Boolean, nullable=False, default=True)
    exp_value = Column(Integer, nullable=False, default=10)
    description = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint("name", "role", name="uq_expaction_name_role"),
    )


class UserExperience(Base):
    __tablename__ = "user_experience"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    role = Column(String(50), nullable=True)
    total_exp = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint("user_id", "role", name="uq_user_role"),
    )


class ExpTransaction(Base):
    __tablename__ = "exp_transaction"
    id = Column(Integer, primary_key=True, index=True)
    user_experience_id = Column(Integer, ForeignKey("user_experience.id", ondelete="CASCADE"))
    user_id = Column(Integer, nullable=False)
    action_id = Column(Integer, ForeignKey("exp_action.id", ondelete="RESTRICT"))
    exp_awarded = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reference_id = Column(String(100), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_experience_id", "action_id", "reference_id", name="uq_userexp_action_ref"),
    )

    action = relationship("ExpAction")
    user_experience = relationship("UserExperience")
