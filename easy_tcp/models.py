from errors import BadRequest
import json


class Message:

    def __init__(self, message_type: str, data=None):
        self.type = message_type
        self.data = data if data else {}

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
        if not message_type:
            raise BadRequest
        return cls(message_type, message_dict.get('data'))

    def dump(self):
        return json.dumps({
            'type': self.type,
            'data': self.data
        })

    def __repr__(self):
        return '<Message %s,  %s>' % (self.type, self.data)
