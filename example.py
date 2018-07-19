from easy_tcp.server import ServerFactory, protocol
from easy_tcp.models import Message

server = ServerFactory()


@server.handle('hello')
def hello_world(message: str):
    print(message)
    protocol.send(Message('hello_response', 'Hello world!'))


if __name__ == '__main__':
    server.run(port=8000)
