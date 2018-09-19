from errors import BadRequest
import json
import attr


@attr.s
class Message:

    type = attr.ib(type=str)
    data = attr.ib(factory=dict)

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
        return cls(message_type, message_dict.get('data'))

    def dump(self):
        return attr.asdict(self)
