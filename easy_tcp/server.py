from twisted.internet.protocol import Factory, error
from twisted.protocols.basic import LineReceiver
from twisted.internet.address import IPv4Address
from twisted.python import failure
from twisted.internet import reactor
from werkzeug.local import Local
from models import Message
from errors import BaseError, UnhandledRequest
import logging

connectionDone = failure.Failure(error.ConnectionDone())

local = Local()
protocol = local('protocol')

logging.basicConfig(level=logging.DEBUG,
                    format='%(name)-24s [LINE:%(lineno)-3s]# %(levelname)-8s [%(asctime)s]  %(message)s')
log = logging.getLogger('GLOBAL')


def error_cache(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except BaseError as ex:
            self.send_error_message(ex)

    return wrapper


class UserProtocol(LineReceiver):

    def __init__(self, address: IPv4Address, server):
        self.address = address
        self.log = logging.getLogger(repr((address.host, address.port)))
        self.server = server

        self.user = None

    def copy(self):
        return self

    @error_cache
    def lineReceived(self, line):
        self.log.debug('Message %s' % line)
        message = Message.from_json(line)

        func = self.server.handlers.get(message.type)
        if func:
            func(message.data, self)
        else:
            raise UnhandledRequest

    def rawDataReceived(self, data):
        pass

    def connectionMade(self):
        self.server.on_open_func(self) if self.server.on_open_func else None
        self.log.info('User connected')

    def connectionLost(self, reason=connectionDone):
        self.server.on_close_func(self, reason) if self.server.on_close_func else None
        self.log.info('Disconnected')

    def send_error_message(self, exception):
        self.send(Message('error', {
            'code': exception.code,
            'message': exception.message
        }))

    def send(self, message: Message):
        self.log.debug('Send %s  %s' % (message.type, message.data))
        self.sendLine(message.dump().encode('utf-8'))


class ServerFactory(Factory):
    handlers = {}
    on_close_func = None
    on_open_func = None

    port = None

    def handle(self, event):
        def decorator(func):
            def wrapper(data, proto):
                # noinspection PyUnresolvedReferences,PyDunderSlots
                local.protocol = proto
                return func(**data)

            self.handlers[event] = wrapper
            return wrapper

        return decorator

    def on_close(self):
        def decorator(func):
            def wrapper(proto, reason):
                # noinspection PyUnresolvedReferences,PyDunderSlots
                local.protocol = proto
                return func(reason)

            self.on_close_func = wrapper
            return wrapper

        return decorator

    def on_open(self):
        def decorator(func):
            def wrapper(proto):
                # noinspection PyUnresolvedReferences,PyDunderSlots
                local.protocol = proto
                return func()

            self.on_open_func = wrapper
            return wrapper

        return decorator

    def buildProtocol(self, addr: IPv4Address) -> UserProtocol:
        proto = self.protocol(addr, self)
        return proto

    def run(self, port=8956):
        port = port if not self.port else self.port
        self.protocol = UserProtocol
        reactor.listenTCP(port, self)
        log.info('Start server at %s' % port)
        reactor.run()
