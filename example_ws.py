from easy_net.server import WebSocketFactory, protocol
from easy_net.models import Message

server = WebSocketFactory('ws://0.0.0.0:8000')


@server.handle('echo')
async def echo(msg: str):
    protocol.send(Message('echo_resp', msg))


if __name__ == '__main__':
    server.run(port=8000)
