from easy_tcp.server import WebSocketFactory, protocol
from easy_tcp.models import Message

server = WebSocketFactory('ws://0.0.0.0:8000')


@server.handle('echo')
def echo(msg: str):
    protocol.send(Message('echo_resp', msg))


if __name__ == '__main__':
    server.run(port=8000)
