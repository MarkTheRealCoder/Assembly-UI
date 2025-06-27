import logging
from pprint import pformat
from threading import Semaphore
from weakref import WeakKeyDictionary

from source.comms.handlers.Priority import Priority


class Register:

    class ___DictWrapper(WeakKeyDictionary):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __repr__(self):
            return "{\n\t" + "\n\t".join([f"{k}: {v}" for k, v in self.items()]) + "\n}"

        def __str__(self):
            return "{\n\t" + "\n\t".join([f"{k}: {v}" for k, v in self.items()]) + "\n}"

    def __init__(self):
        self.___reference: dict[type: dict[str: dict[Priority: Register.___DictWrapper[object: dict]]]] = {}
        self.___sem = Semaphore(1)
        logging.basicConfig(filename='register.log', level=logging.DEBUG,
                            format='%(asctime)s:%(levelname)s:%(message)s')

    def ___dive(self, event: type, identifier: str = None, priority: Priority = None):
        """
        Dive into the register to get the specified event or list of events
        :param event:
        :param identifier:
        :param priority:
        :param specifiers:
        :return:
        """

        result = self.___reference.get(event, None)

        # if the event is of type ClosingEvent, we need to log into a log file the whole register (reference) formatted with pformat
        if "ResizeEvent" in f"{event}":
            logging.debug(f"Register: {pformat(self.___reference)}")


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
                    result[priority] = Register.___DictWrapper()
                    result = result[priority]
                else:
                    result = tmp

        return result

    def ___deep_dive(self, depth: dict[object: dict], specifiers: dict) -> list[object]:
        """
        Dive into the register starting from the given depth to get the specified or not specified objects
        :param depth:
        :param specifiers:
        :return:
        """
        result = []
        if isinstance(depth, Register.___DictWrapper):
            toBeDeleted = []
            specopy = specifiers.copy()
            delete = specopy.pop("___deleted", False)
            obj = specopy.pop("___obj", None)
            for key, value in depth.items():
                if not self.___is_specified(obj, key, specopy, value):
                    continue
                if delete:
                    toBeDeleted.append(key)
                else:
                    result.append(key)
            for key in toBeDeleted:
                depth.pop(key)

        elif isinstance(depth, dict):
            for key, value in depth.items():
                result += self.___deep_dive(value, specifiers)
        return result


    def ___is_specified(self, obj, key, specifiers: dict, value) -> bool:
        vobj = obj is key                                                                   # valid object reference
        empty = specifiers == {}                                                            # empty specifiers
        values = [value.get(k, None) == v for k, v in specifiers.items() if k in value.keys()]      # values match
        specified = empty ^ (all(values) if values else False)                             # all values match
        return vobj or (not vobj and specified and obj is None)

    def get(self, event: type, identifier: str, priority: Priority, **specifiers) -> list[object]:
        self.___sem.acquire()
        depth: dict[object: dict] = self.___dive(event, identifier, priority)
        result = self.___deep_dive(depth, specifiers)
        self.___sem.release()
        return result

    def set(self, event: type, identifier: str, priority: Priority, value: object, **specifiers) -> None:
        self.___sem.acquire()
        try:
            d: Register.___DictWrapper = self.___dive(event, identifier, priority)
            if hasattr(value, '__weakref__'):  # Verifica se l'oggetto può essere referenziato debolmente
                d[value] = specifiers
            else:
                logging.warning(f"Impossibile creare riferimento debole per {value}")
        finally:
            self.___sem.release()


    def remove(self, obj) -> None:
        self.___sem.acquire()
        print(f"----------------------------------Removing: {obj}")
        self.___deep_dive(self.___reference, {"___obj": obj, "___deleted": True})
        self.___sem.release()



class IRegister:
    """
    Interface for the Register class
    """

    def __init__(self):
        self.___register: Register = Register()

    def get(self, event: type, identifier: str = None, priority: Priority = None, **specifiers) \
            -> list[object]:
        return self.___register.get(event, identifier, priority, **specifiers)

    def add(self, event: type, identifier: str, priority: Priority, value, **specifiers):
        self.___register.set(event, identifier, priority, value, **specifiers)

    def delete(self, obj):
        self.___register.remove(obj)