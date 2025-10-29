from fastapi import FastAPI
from .database import engine, Base, SessionLocal
from .routers import gamification
from .config.default_actions import DEFAULT_EXP_ACTIONS
from . import models
import logging

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Gamification Service",
    description="Microservice for managing user experience and gamification",
    version="1.0.0"
)


@app.on_event("startup")
async def create_default_exp_actions():
    """
    Create default ExpAction records on application startup.
    """
    db = SessionLocal()
    try:
        for action_data in DEFAULT_EXP_ACTIONS:
            existing_action = db.query(models.ExpAction).filter(
                models.ExpAction.name == action_data["name"],
                models.ExpAction.role == action_data.get("role")
            ).first()

            if not existing_action:
                new_action = models.ExpAction(**action_data)
                db.add(new_action)
                logger.info(f"Created default action: {action_data['name']} (role={action_data.get('role')})")

        db.commit()
        logger.info("Default ExpActions initialized successfully")
    except Exception as e:
        logger.error(f"Error creating default ExpActions: {e}")
        db.rollback()
    finally:
        db.close()


app.include_router(gamification.router)


@app.get("/")
def root():
    return {
        "service": "Gamification",
        "status": "running"
    }
