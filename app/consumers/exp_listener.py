import json
import logging
import pika
import sys
import os
from dotenv import load_dotenv
from prometheus_client import Counter
from ..database import SessionLocal

load_dotenv(dotenv_path='../../.env')
logger = logging.getLogger(__name__)

EVENTS_PROCESSED = Counter("gamification_events_processed_total", "Total processed EXP events")
EVENTS_FAILED = Counter("gamification_events_failed_total", "Total failed EXP events")

EVENT_MAP = {
    "startup.profile.complete": "startup_profile_complete",
    "investor.profile.complete": "investor_profile_complete",
    "first.project.created": "first_project_created",
    "project.created": "project_created",
    "daily.login": "daily_login",
    "received.like": "received_like",
}

def start_event_consumer():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST"))
    )
    channel = connection.channel()

    dlx_exchange = "platform.events.dlx"
    dlq_queue = "gamification.exp.dlq"
    
    channel.exchange_declare(exchange=dlx_exchange, exchange_type="topic", durable=True)
    channel.queue_declare(queue=dlq_queue, durable=True)
    channel.queue_bind(exchange=dlx_exchange, queue=dlq_queue, routing_key="gamification.failed")
    channel.exchange_declare(exchange=os.getenv("RABBITMQ_EXCHANGE"), exchange_type="topic", durable=True)
    
    queue_args = {
        "x-dead-letter-exchange": dlx_exchange,
        "x-dead-letter-routing-key": "gamification.failed"
    }
    
    try:
        channel.queue_declare(
            queue=os.getenv("RABBITMQ_QUEUE_GAMIFICATION"), 
            durable=True,
            arguments=queue_args
        )
    except pika.exceptions.ChannelClosedByBroker as e:
        if e.reply_code == 406 and "inequivalent arg" in e.reply_text:
            logger.warning(f"Queue {os.getenv('RABBITMQ_QUEUE_GAMIFICATION')} exists with different args. Deleting and recreating...")
            
            channel = connection.channel()
            channel.queue_delete(queue=os.getenv("RABBITMQ_QUEUE_GAMIFICATION"))
            
            channel.queue_declare(
                queue=os.getenv("RABBITMQ_QUEUE_GAMIFICATION"), 
                durable=True,
                arguments=queue_args
            )
        else:
            raise e

    for key in EVENT_MAP.keys():
        channel.queue_bind(exchange=os.getenv("RABBITMQ_EXCHANGE"), queue=os.getenv("RABBITMQ_QUEUE_GAMIFICATION"), routing_key=key)

    def callback(ch, method, properties, body):
        db = SessionLocal()
        try:
            logger.info(f"Received message: {body}")
            event = json.loads(body)
            event_type = method.routing_key
            action_name = EVENT_MAP.get(event_type)
            
            if not action_name:
                logger.error(f"Unknown event type: {event_type}")
                EVENTS_FAILED.inc()
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return

            user_id = int(event["user_id"])
            reference_id = event.get("reference_id")
            user_role = event.get("role")
            
            logger.info(f"Processing action '{action_name}' for user {user_id} (role={user_role})")
        
            from ..services.exp_manager import award_experience_by_name
            
            result = award_experience_by_name(
                db=db,
                user_id=user_id,
                action_name=action_name,
                reference_id=reference_id,
                user_role=user_role
            )
            
            logger.info(f"Successfully processed event: {event_type} for user {user_id}. New Total EXP: {result.total_exp}")
            EVENTS_PROCESSED.inc()
            ch.basic_ack(delivery_tag=method.delivery_tag)
                
        except ValueError as e:
            logger.warning(f"Business logic error processing {method.routing_key}: {e}")
            EVENTS_FAILED.inc()
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Failed to process event {method.routing_key}: {e}", exc_info=True)
            EVENTS_FAILED.inc()
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        finally:
            db.close()

    channel.basic_consume(queue=os.getenv("RABBITMQ_QUEUE_GAMIFICATION"), on_message_callback=callback)
    logger.info("Gamification Consumer listening for EXP events...")
    channel.start_consuming()