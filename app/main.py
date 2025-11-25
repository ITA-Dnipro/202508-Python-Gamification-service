from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from prometheus_client import make_asgi_app
from .database import engine, Base, SessionLocal
from .config.default_actions import DEFAULT_EXP_ACTIONS
from . import models
import logging
import threading
import pika
import os

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Gamification Service",
    description="Microservice for managing user experience and gamification",
    version="1.0.0"
)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

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
    
    def start_event_consumer_thread():
        import time
        max_retries = 7
        retry_delay = 10
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Starting RabbitMQ consumer (attempt {attempt}/{max_retries})...")
                from .consumers.exp_listener import start_event_consumer
                start_event_consumer()
                break
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Failed to start consumer (attempt {attempt}/{max_retries}): {e}")
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed to start event consumer after {max_retries} attempts: {e}", exc_info=True)
    
    consumer_thread = threading.Thread(target=start_event_consumer_thread, daemon=True)
    consumer_thread.start()
    logger.info("RabbitMQ consumer thread started")


@app.get("/")
def root():
    return {
        "service": "Gamification",
        "status": "running"
    }

@app.get("/health/rabbitmq")
def rabbitmq_health():
    """
    Check RabbitMQ connection status.
    """
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST"), connection_attempts=1, socket_timeout=2)
        )
        if connection.is_open:
            connection.close()
            return {"status": "connected", "host": os.getenv("RABBITMQ_HOST")}
        else:
            raise HTTPException(status_code=503, detail="RabbitMQ connection closed")
    except Exception as e:
        logger.error(f"RabbitMQ health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"RabbitMQ unavailable: {str(e)}")
