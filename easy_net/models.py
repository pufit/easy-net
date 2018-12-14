from .errors import BadRequest
from typing import Any, TypeVar
import json
import attr
import time
import uuid

T = TypeVar('T', int, str)


@attr.s
class Message:
    type = attr.ib(type=str)
    data = attr.ib(factory=dict)
    callback = attr.ib(factory=lambda: str(uuid.uuid4()))

    @data.validator
    @type.validator
    def check_type(self, attribute, value):
        if attribute.name == 'type' and (not value or not isinstance(value, str)) or \
                attribute.name == 'data' and not isinstance(value, dict):
            raise BadRequest

    @classmethod
    def from_bytes(cls, message: bytes):
        return cls.from_json(message.decode('utf-8'))

    @classmethod
    def from_json(cls, message: str):
        try:
            message_dict = json.loads(message)
        except (ValueError, UnicodeDecodeError):
            raise BadRequest
        message_type = message_dict.get('type')
        return cls(message_type, message_dict.get('data'), message_dict.get('callback'))

    def dump(self):
        return json.dumps(attr.asdict(self))


class TempStructure:
    update_time = 5
    expire = 60

    def __init__(self):
        self.last_check = time.time()


class TempDict(dict, TempStructure):
    def __init__(self, *args, factory=list):
        dict.__init__(self, *args)
        TempStructure.__init__(self)
        self.factory = factory

    def __setitem__(self, key: T, value: Any):
        self.check()
        super().__setitem__(key, {
            'time': time.time(),
            'value': value
        })

    def __getitem__(self, key: T):
        self.check()
        if key not in self and self.factory:
            value = self.factory()
            self[key] = value
            return value
        return super().__getitem__(key)['value']

    def check(self):
        if time.time() - self.last_check < self.update_time:
            return
        for key, value in self.copy().items():
            if time.time() - value['time'] >= self.expire:
                del self[key]
