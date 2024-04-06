import logging
from typing import Self

from ..enums import EventStatus
from ..broker_manager import broker_manager
from .event_object import EventObject


class EventRouter:
    """A simple router.
    Bind events to expose them to the router.
    Bind routers to expand the router.
    """
    def __init__(self, name: str) -> None:
        self.name = name
        self.binds = {}

    def check_bind(self, name):
        if self.binds.get(name) is not None:            
            raise KeyError(f"Bind name '{name}' is already in use.")

    def bind_event(self, name):
        self.check_bind(name)
        def inner(func):
            self.binds[name] = func
            return func
        return inner
    
    def include_binder(self, binder: Self):
        self.check_bind(binder.name)
        self.binds[binder.name] = binder

    def execute_event(self, event_object: EventObject, events: list[str] = None):
        try:
            if not events:
                events = event_object.event.split(".")

            for key, func in self.binds.items():
                if key == events[0]:
                    if isinstance(func, EventRouter):
                        return func.execute_event(event_object, events[1:])
                    
                    return func(event_object=event_object)
            else:
                logging.warning(f"Event '{event_object.event}' not found in '{self.name}'")

        except Exception as exc:
            self.exception_handler(exc, event_object)

    def exception_handler(self, exc: Exception, event_object: EventObject):
        logging.exception(exc)
        event_object.as_reply()
        event_object.status = EventStatus.ERROR
        broker_manager.cache.update(event_object)
