# coding=utf-8


from typing import Iterable


class AttrDict(dict):
    """属性字典，可以通过属性的方式访问字典"""

    def _get_key(self, item):  # noqa
        return item

    def __getattr__(self, item):
        return self.get(self._get_key(item))

    def __setattr__(self, item, value):
        self.__setitem__(self._get_key(item), value)

    def __delattr__(self, item):
        return self.__delitem__(self._get_key(item))


class IgnoreCaseAttrDict(AttrDict):

    def _get_key(self, item):
        for key in self.keys():
            if key.lower() == item.lower():
                return key
        return super()._get_key(item)


def to_attr_dict(data, cls=AttrDict):
    if not isinstance(data, Iterable) or isinstance(data, str):
        return data
    if isinstance(data, dict):
        return cls(((k, to_attr_dict(v)) for k, v in data.items()))
    return [to_attr_dict(item) for item in data]


if __name__ == '__main__':
    data = to_attr_dict([{'login': 1, 'b': 2}])
    print(data[0].login)
    pass
