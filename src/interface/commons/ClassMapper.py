class ClassMapper:
    ___CLSS: dict[str: type] = {}

    @staticmethod
    def register(k: str):

        def wrapper(cls):
            ClassMapper.___CLSS[k] = cls
            return cls

        return wrapper

    @staticmethod
    def getClass(k: str):
        return ClassMapper.___CLSS.get(k, None)


register = ClassMapper.register
getClass = ClassMapper.getClass
