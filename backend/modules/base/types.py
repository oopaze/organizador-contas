from abc import ABCMeta


class OptionType:
    def __init__(self, label: str, value: str):
        self.label = label
        self.value = value


class TypeItem(metaclass=ABCMeta):
    def __init__(self, name: str, default: dict = {}, **kwargs):
        self.name = name

        for key, value in kwargs.items():
            setattr(self, key, value)

        if default:
            for key, value in default.items():
                if not hasattr(self, key):
                    setattr(self, key, value)

    def get_as_django_choice(self):
        return (self.name, getattr(self, "value", self.name))

    def get_as_option(self):
        return OptionType(self.name, getattr(self, "value", self.name))


class BaseType(metaclass=ABCMeta):
    @classmethod
    def get_all(cls) -> list[TypeItem]:
        return [item for item in cls.__dict__.values() if isinstance(item, TypeItem)]

    @classmethod
    def get_by_name(cls, name: str):
        for item in cls.get_all():
            if item.name == name:
                return item
        raise ValueError(f"{name} not found in {cls.__name__}")

    @classmethod
    def get_by_attribute_value(cls, value: str, attribute: str):
        for item in cls.get_all():
            if getattr(item, attribute) == value:
                return item
        raise ValueError(f"{value} not found in {cls.__name__}")

    @classmethod
    def get_all_as_options(cls):
        return [item.get_as_django_choice() for item in cls.get_all()]
