from typing import Type

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication

from source.comms.handlers.Priority import Priority
from source.comms.handlers.Register import IRegister


def lazy_load():
    from source.comms.events import Event
    return Event

class EventRegister:
    """
    Register class objects to events
    With this class you can create custom event handlers for your class without extending
    your base class event handlers like the event method or the eventFilter method.
    You can simply create an event that extends the Event class and create a method that follows this
    pattern: on{EventName}(self, event) and the EventRegister will call this method when the event is sent.
    """
    Event = lazy_load()
    REFERENCE: IRegister = IRegister()

    ALL = Priority(-1)
    URGENT = Priority(0)
    HIGH = Priority(1)
    NORMAL = Priority(2)
    LOW = Priority(3)

    @staticmethod
    def register(evenT, arg: str = "Main", priority: Priority = NORMAL, **keys):
        """
        Register a class object to an event
        :param event: event
        :param arg: event\' subclass
        :param priority: event priority
        :return:
        """

        def wrapper(cls):

            class Wrapper(cls):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    EventRegister.REFERENCE.add(evenT, arg, priority, self, **keys)

                def event(self, e):
                    if hasattr(cls, "on"+evenT.__name__):
                        if e == evenT:
                            try:
                                getattr(self, "on"+evenT.__name__)(e)
                            except TypeError:
                                raise TypeError(f"on{evenT.__name__} method must have the event parameter.")
                            return True

                    return super().event(e)

            custom_name = f"{cls.__name__}"
            module_name = cls.__module__
            Wrapper.__module__ = module_name
            Wrapper.__name__ = custom_name
            Wrapper.__str__ = lambda self: f"<{module_name}.{custom_name} (EXT) at {hex(id(self))}>"
            Wrapper.__repr__ = lambda self: f"<{module_name}.{custom_name} (EXT) at {hex(id(self))}>"
            return Wrapper

        return wrapper

    @staticmethod
    def mregister(obj: QObject, ev: type, arg: str = "Main", priority: Priority = NORMAL, **keys):
        """
        Manually register an object to an event or an event specific subclass
        :param obj: object to register
        :param event: event
        :param arg: event\' subclass
        :return:
        """
        # if "ClosingEvent" in f"{ev}":
        #     print(f"CLOSINGEVENT REGISTERED FOR : {obj} - {keys}")
        if "ResizeEvent" in str(ev):
            print(f"Registering {obj} to {ev} with args {arg} and keys {keys}")
        EventRegister.REFERENCE.add(ev, arg, priority, obj, **keys)
        if hasattr(obj, "event"):

            if hasattr(obj, "on"+ev.__name__):
                std = obj.event

                def on(self, e):
                    if e == ev:
                        try:
                            getattr(obj, "on"+ev.__name__)(e)
                        except TypeError:
                            raise TypeError(f"on{ev.__name__} method must have the event parameter.")
                        return True
                    return super(obj.__class__, self).event(e)

                obj.event = on.__get__(obj, obj.__class__)

    @staticmethod
    def get(event: type, arg: str = "Main", **specifiers):
        result = []
        result += EventRegister.REFERENCE.get(event, arg, EventRegister.URGENT, **specifiers)
        result += EventRegister.REFERENCE.get(event, arg, EventRegister.HIGH, **specifiers)
        result += EventRegister.REFERENCE.get(event, arg, EventRegister.NORMAL, **specifiers)
        result += EventRegister.REFERENCE.get(event, arg, EventRegister.LOW, **specifiers)
        return result

    @staticmethod
    def remove(obj):
        EventRegister.REFERENCE.delete(obj)

    @staticmethod
    def send(event: Event, arg: str, **keys):
        """
        Send an event to all registered objects
        :param event: event
        :param arg: event\' subclass
        :return:
        """
        app = QApplication.instance()
        # print(f"Keys {keys}")
        refs = EventRegister.get(type(event), arg, **keys)
        for ref in refs:
            event.on(ref)
            app.sendEvent(ref, event)

    @staticmethod
    def post(event: Type[Event], *args, arg: str = "*", **keys):
        """
        Post an event to all registered objects
        :param event: The event class to create the event to be posted
        :param args: arguments to be passed to the event class __init__
        :param arg: event\' subclass
        :return:
        """
        if not isinstance(event, type):
            raise TypeError("Event must be a class")
        app = QApplication.instance()
        refs = EventRegister.get(event, arg, **keys)
        if "ResiteEvent" in str(event):
            print(f"Posting {event} to {refs}")
        for ref in refs:
            e = event(*args)
            e.on(ref)
            app.postEvent(ref, e)