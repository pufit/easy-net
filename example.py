from easy_tcp.server import LineFactory, protocol
from easy_tcp.models import Message

server = LineFactory()


@server.handle('echo')
def echo(msg: str):
    protocol.send(Message('echo_resp', {
        'msg': msg
    }))


@server.handle(['test1', 'test2', 'test3'])
def test():
    protocol.send(Message(protocol.event_type, {
        'msg': 'it works'
    }))


if __name__ == '__main__':
    server.run(port=8000)
