def singleton(cls: type):
    def __new__singleton(cls: type, *args, **kwargs):
        if not hasattr(cls, "__singleton"):
            cls.__singleton = object.__new__(cls)  # type: ignore[attr-defined]
        return cls.__singleton  # type: ignore[attr-defined]
    cls.__new__ = __new__singleton  # type: ignore[method-assign]
    return cls