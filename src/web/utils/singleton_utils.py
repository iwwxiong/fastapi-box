
def supertuple(*args):
    return tuple([tuple(arg) for arg in args if isinstance(arg, list)])


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        key = (cls, supertuple(*args), supertuple(*kwargs.values()))
        if key not in cls._instances:
            cls._instances[key] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[key]
