from easy_tcp.server import ServerFactory, protocol
from easy_tcp.models import Message
from twisted.internet import reactor

server = ServerFactory()


@server.handle('echo')
def echo(msg: str):
    proto = protocol.copy()
    reactor.callLater(10, lambda x: proto.send(Message('echo', x)), msg)


if __name__ == '__main__':
    server.run(port=8000)
