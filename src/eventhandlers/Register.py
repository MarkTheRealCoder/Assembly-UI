import weakref
from typing import Type

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication

from src.events.Event import Event


class _Priority(int):

    ALL = -1
    URGENT = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3

    def __init__(self, value):
        super().__init__()


class _Register:
    def __init__(self):
        self.___reference: dict[type: dict[str: dict[_Priority: weakref.WeakKeyDictionary[object: dict]]]] = {}

    def get(self, event: type, identifier: str = None, priority: _Priority = None, **specifiers) \
            -> list[object]:
        return self.___get(event, identifier, priority, **specifiers)

    def add(self, event: type, identifier: str, priority: _Priority, value, **specifiers):
        self.___set(event, identifier, priority, value, **specifiers)

    def delete(self, obj):
        self.___remove(obj)

    def ___dive(self, event: type, identifier: str = None, priority: _Priority = None):
        """
        Dive into the register to get the specified event or list of events
        :param event:
        :param identifier:
        :param priority:
        :param specifiers:
        :return:
        """
        result = self.___reference.get(event, None)
        if result is None:
            self.___reference[event] = {}
            result = self.___reference[event]

        if identifier is not None:
            tmp = result.get(identifier, None)
            if tmp is None:
                result[identifier] = {}
                result = result[identifier]
            else:
                result = tmp

            if priority is not None:
                tmp = result.get(priority, None)
                if tmp is None:
                    result[priority] = weakref.WeakKeyDictionary()
                    result = result[priority]
                else:
                    result = tmp

        return result

    def ___deep_dive(self, depth, specifiers: dict) -> list[object]:
        """
        Dive into the register starting from the given depth to get the specified or not specified objects
        :param depth:
        :param specifiers:
        :return:
        """
        result = []
        if isinstance(depth, weakref.WeakKeyDictionary):
            specopy = specifiers.copy()
            delete = specopy.pop("___deleted", False)
            obj = specopy.pop("___obj", None)
            for key, value in depth.items():
                if not self.___is_specified(obj, key, specopy, value):
                    continue
                if delete:
                    self.___invalidate(value)
                elif self.___validity(value):
                    result.append(key)

        elif isinstance(depth, dict):
            for key, value in depth.items():
                    result += self.___deep_dive(value, specifiers)
        return result

    def ___validity(self, specifiers) -> bool:
        return not specifiers.get("___deleted", False)

    def ___invalidate(self, specifiers) -> None:
        specifiers["___deleted"] = True

    def ___is_specified(self, obj, key, specifiers, value) -> bool:
        vobj = obj is key                                                                   # valid object reference
        empty = specifiers == {}                                                            # empty specifiers
        specified = empty ^ all([value.get(k) == v for k, v in specifiers if k in value.keys()])
        return vobj or (specified and not vobj) or (empty and obj is None)

    def ___get(self, event: type, identifier: str, priority: _Priority, **specifiers) -> list[object]:
        depth = self.___dive(event, identifier, priority)
        return self.___deep_dive(depth, specifiers)

    def ___set(self, event: type, identifier: str, priority: _Priority, value: object, **specifiers) -> None:
        self.___dive(event, identifier, priority)[value] = specifiers

    def ___remove(self, obj) -> None:
        self.___deep_dive(self.___reference, {"___obj": obj, "___deleted": True})


class EventRegister:
    """
    Register class objects to events
    With this class you can create custom event handlers for your class without extending
    your base class event handlers like the event method or the eventFilter method.
    You can simply create an event that extends the Event class and create a method that follows this
    pattern: on{EventName}(self, event) and the EventRegister will call this method when the event is sent.
    """

    REFERENCE: _Register = _Register()

    ALL = _Priority(-1)
    URGENT = _Priority(0)
    HIGH = _Priority(1)
    NORMAL = _Priority(2)
    LOW = _Priority(3)

    @staticmethod
    def register(event, arg: str = "Main", priority: _Priority = NORMAL, **keys):
        """
        Register a class object to an event
        :param event: event
        :param arg: event\' subclass
        :param priority: event priority
        :return:
        """

        def wrapper(cls):

            init = cls.__init__

            def inner(self, *args, **kwargs):
                EventRegister.REFERENCE.add(event, arg, priority, self, **keys)

                return init(self, *args, **kwargs)

            cls.__init__ = inner

            if hasattr(cls, "event"):

                if hasattr(cls, "on"+event.__name__):
                    std = cls.event

                    def on(s, e):
                        if e == event:
                            try:
                                getattr(s, "on"+event.__name__)(e)
                            except TypeError:
                                raise TypeError(f"on{event.__name__} method must have the event parameter.")
                            return True
                        return std(s, e)

                    cls.event = on

            return cls

        return wrapper

    @staticmethod
    def mregister(obj: QObject, ev: type, arg: str = "Main", priority: _Priority = NORMAL, **keys):
        """
        Manually register an object to an event or an event specific subclass
        :param obj: object to register
        :param event: event
        :param arg: event\' subclass
        :return:
        """
        EventRegister.REFERENCE.add(ev, arg, priority, obj, **keys)
        if hasattr(obj, "event"):

            if hasattr(obj, "on"+ev.__name__):
                std = obj.event

                def on(e):
                    if e == ev:
                        try:
                            getattr(obj, "on"+ev.__name__)(e)
                        except TypeError:
                            raise TypeError(f"on{ev.__name__} method must have the event parameter.")
                        return True
                    return std(e)

                obj.event = on

    @staticmethod
    def get(event: type, arg: str = "Main", **specifiers):
        result = []
        result += EventRegister.REFERENCE.get(event, arg, EventRegister.URGENT, **specifiers)
        result += EventRegister.REFERENCE.get(event, arg, EventRegister.HIGH, **specifiers)
        result += EventRegister.REFERENCE.get(event, arg, EventRegister.NORMAL, **specifiers)
        result += EventRegister.REFERENCE.get(event, arg, EventRegister.LOW, **specifiers)
        if "id" in specifiers.keys():
            print(result)
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
        for ref in EventRegister.get(type(event), arg, **keys):
            app.sendEvent(ref, event)
            event.on(ref)

    @staticmethod
    def post(event: Type[Event], *args, arg: str = "*", **keys):
        """
        Post an event to all registered objects
        :param event: The event class to create the event to be posted
        :param args: arguments to be passed to the event class __init__
        :param arg: event\' subclass
        :return:
        """
        app = QApplication.instance()
        for ref in EventRegister.get(event, arg, **keys):
            e = event(*args)
            e.on(ref)
            app.postEvent(ref, e)


