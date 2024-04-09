from kolibri.callbacks.base import IEvent
from typing import Optional, Union, List
from kolibri.callbacks.base import BaseCallbackHandler
class CallbackManager:
    def __init__(self):
        self.callbacks = {}
        self.handlers = {}  # Event type to list of handlers mapping

    def register(self, event_instance):
        """
        Register a new event class instance.
        """
        if not isinstance(event_instance, IEvent):
            raise ValueError("Only instances of IEvent or its subclasses can be registered.")
        self.callbacks[event_instance.event_type] = event_instance


    def unregister(self, event_type):
        """
        Unregister an existing event class instance based on its event_type.
        """
        if event_type in self.callbacks:
            del self.callbacks[event_type]

    def register_handler(self, event_type, handler_func):
        """Register a handler for a specific event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        if handler_func not in self.handlers[event_type]:
            self.handlers[event_type].append(handler_func)

    def unregister_handler(self, event_type, handler_func):
        """Unregister a handler for a specific event type."""
        if event_type in self.handlers:
            self.handlers[event_type] = [f for f in self.handlers[event_type] if f != handler_func]

    def set_handlers(self, handlers):
        """Set handlers as the only handlers on the callback manager."""
        self.handlers = []
        self.inheritable_handlers = []
        for handler in handlers:
            self.register_handler(handler)

    def set_handler(self, handler) -> None:
        """Set handler as the only handler on the callback manager."""
        self.set_handlers([handler])
    def trigger(self, event_type, *args, **kwargs):
        """
        Trigger the registered event class methods and handlers for a specific event type.
        """
        event_instance = self.callbacks.get(event_type)
        dynamic_handler = None
        if event_instance:
            dynamic_handler = event_instance.on_start(*args, **kwargs)
            event_instance.on_execute(*args, **kwargs)
            event_instance.on_end(*args, **kwargs)

        # Call the dynamically determined handler
        if dynamic_handler:
            dynamic_handler.handle(*args, **kwargs)

        # Call the statically registered handlers
        for handler in self.handlers.get(event_type, []):
            handler.handle(*args, **kwargs)

    def handle_event(self, event_name, handlers, *args, **kwargs):
        """Handle the given event with a list of handlers."""
        if event_name not in self.callbacks:
            print(f"No event registered with the name: {event_name}")
            return

        event_instance = self.callbacks[event_name]
        event_instance.on_start(*args, **kwargs)

        for handler in handlers:
            if not isinstance(handler, BaseCallbackHandler):
                raise ValueError("Provided handler is not an instance of CallbackHandler or its subclass.")
            handler.handle(*args, **kwargs)

        event_instance.on_end(*args, **kwargs)


Callbacks = Optional[Union[List[BaseCallbackHandler], CallbackManager]]