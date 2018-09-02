from easy_tcp.server import LineFactory, protocol
from easy_tcp.models import Message

server = LineFactory()


@server.handle('echo')
def echo(msg: str):
    protocol.send(Message('echo_resp', msg))


if __name__ == '__main__':
    server.run(port=8000)
