from typing import Union


class ClassMapping:
    ___register: dict[str: type] = {}

    @staticmethod
    def register(value: str):
        def decorator(cls) -> None:
            ClassMapping.___register[value] = cls

        return decorator

    @staticmethod
    def getClass(value: str) -> Union[type, None]:
        return ClassMapping.___register.get(value, None)


register = ClassMapping.register
getClass = ClassMapping.getClass
