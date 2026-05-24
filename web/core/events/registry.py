from collections import defaultdict

class EventRegistry:
    _handlers = defaultdict(list)

    @classmethod
    def register(cls, event_name:str):
        def decorator(handler):
            cls._handlers[event_name].append(handler)

            return handler
        return decorator
    
    @classmethod
    def get_handlers(cls, event_name: str):
        return cls._handlers.get(event_name, [])