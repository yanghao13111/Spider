from collections import defaultdict


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class KeyWordSingleton(type):

    _instances = defaultdict(dict)

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, 'singleton_signature') or not callable(cls.singleton_signature):
            raise TypeError(
                f"{cls.__name__} must implement a 'singleton_signature' method for KeyWordSingleton to work.")
        key_word = cls.singleton_signature(*args, **kwargs)
        if cls not in cls._instances or key_word not in cls._instances[cls]:
            cls._instances[cls][key_word] = super(
                KeyWordSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls][key_word]