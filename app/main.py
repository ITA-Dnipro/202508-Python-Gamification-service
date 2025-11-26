from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from .database import engine, Base, SessionLocal
from .config.default_actions import DEFAULT_EXP_ACTIONS
from . import models
from .routers import gamification
import logging

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Gamification Service",
    description="Microservice for managing user experience and gamification",
    version="1.0.0"
)


app.include_router(gamification.router)

@app.on_event("startup")
def create_default_exp_actions():
    """
    Create default ExpAction records on application startup.
    """
    db = SessionLocal()
    try:
        created_count = 0
        for action_data in DEFAULT_EXP_ACTIONS:
            existing_action = db.query(models.ExpAction).filter(
                models.ExpAction.name == action_data["name"],
                models.ExpAction.role == action_data.get("role")
            ).first()

            if not existing_action:
                new_action = models.ExpAction(**action_data)
                db.add(new_action)
                created_count += 1
                logger.info(f"Created default action: {action_data['name']} (role={action_data.get('role')})")

        db.commit()
        logger.info(f"Default ExpActions initialized. Created {created_count} new actions.")
    except IntegrityError as e:
        db.rollback()
        raise e
    except Exception as e:
        logger.error(f"Error creating default ExpActions: {e}")
        db.rollback()
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "service": "Gamification",
        "status": "running"
    }
