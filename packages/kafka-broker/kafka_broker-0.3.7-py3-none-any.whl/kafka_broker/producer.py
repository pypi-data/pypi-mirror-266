import logging
from typing import Callable
from confluent_kafka import Producer
from .exceptions.cache import KeyNotFoundException

from .classes.cache import Cache
from .classes.event_object import EventObject


def default_callback(err, msg):
    if err:
        logging.error("Message failed delivery: {}".format(err))


def produce(
    config: dict,
    cache: Cache,
    logger: logging.Logger,
    topic: str,
    event_object: EventObject,
    callback: Callable = default_callback,
):
    """Produce an event to the kafka message queue."""
    logging.debug("just_some_spacing :D")
    logging.debug("just_some_spacing :D")
    logging.critical(f"start_instruction: {event_object.data.get('start_instruction')}")

    kafka_config = config["kafka.default"]
    kafka_config.update(config["kafka.producer"])

    producer = Producer(kafka_config)
    event_object.add_audit_log(config["general"]["current_location"])
    event_json = event_object.encode()
    
    logging.debug("just_some_spacing :D")
    logging.debug("just_some_spacing :D")
    logging.critical(f"event_json: {event_json}")

    producer.produce(
        topic,
        key=str(event_object.correlation_id),
        value=event_json,
        callback=callback,
    )

    producer.poll(100)
    producer.flush()
    
    try:
        cache.update(event_object)
    except KeyNotFoundException:
        cache.add(event_object)

    logger.info(
        "Produced - topic {topic}: key = {key} \n\tvalue = {value}".format(
            topic=topic,
            key=f"{str(event_object.correlation_id)}",
            value=f"{event_json}...",
        )
    )
