
import logging
from typing import Callable

from .cache import Cache, cache_item, innitialize_connection
from .classes.event_object import EventObject

def  produce_cache(
    config: dict,
    event_object: EventObject,
):
    cache_config = config["kafka.default"]
    cache_config.update(config["kafka.cache"])

    client = Cache(cache_config)

    cached_item = client.add(event_object)
    if cached_item is None:
        raise Exception("lmao: you thought it worked, SIIIIIIIKE")