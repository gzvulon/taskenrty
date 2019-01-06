import json

try:
    from pathlib2 import Path
except:
    from pathlib import Path

from ruamel.yaml import YAML
yaml = YAML(typ='safe')
# yaml.default_flow_style = None


class SmartField(object):
    """Field Descriptor used for name intellisense"""

    def __init__(self, value=None):
        self.value = value

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        return instance[self._name]

    def __set__(self, instance, value):
        self.value = instance[self._name] = value


class BaseModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        cls = super(BaseModelMeta, mcs).__new__(mcs, name, bases, attrs)
        for attr, obj in attrs.items():
            if isinstance(obj, SmartField):
                obj.__set_name__(cls, attr)
        return cls


# --- trick to stop intelligence ---
def _get_base():
    return dict


_ModelBase = _get_base()


# --- trick to stop intelligence ---

class ModelBase(_ModelBase):

    def to_yaml(self, filepath):
        with Path(filepath).open('w') as fp:
            yaml.dump(dict(self), fp)

    @classmethod
    def from_yaml(cls, filepath):
        with Path(filepath).open('r') as fp:
            return cls(yaml.load(fp))

    def to_json(self, filepath):
        with Path(filepath).open('w') as fp:
            json.dump(self, fp, indent=2, sort_keys=True)

    @classmethod
    def from_json(cls, filepath):
        with Path(filepath).open('r') as fp:
            return cls(json.load(fp))

    def to_struct(self):
        return self

    @classmethod
    def from_struct(cls, struct):
        return cls(struct)

    @classmethod
    def from_path(cls, path):
        if path.endswith('yml') or path.endswith('yaml'):
            return cls.from_yaml(path)
        elif path.endswith('json'):
            return cls.from_json(path)
        else:
            raise Exception('path is not supported: {}'
                            '(only json and yaml)'.format(path))

    def to_path(self, path):
        if path.endswith('yml') or path.endswith('yaml'):
            return self.to_yaml(path)
        elif path.endswith('json'):
            return self.to_json(path)
        else:
            raise Exception('path is not supported: {}'
                            '(only json and yaml)'.format(path))

    @classmethod
    def from_iter(cls, iterable):
        for it in iterable:
            yield cls(it)

