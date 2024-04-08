from forbiddenfruit import curse


class Object:
    def __init__(self, dictionary: dict):
        for key, value in dictionary.items():
            if type(value) is dict:
                setattr(self, key, Object(value))
            else:
                setattr(self, key, value)


def to_object(self: dict):
    return Object(self)


curse(dict, "to_object", to_object)
