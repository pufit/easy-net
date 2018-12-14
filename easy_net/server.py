from autobahn.twisted.websocket import WebSocketServerFactory as _WebSocketServerFactory, \
    WebSocketServerProtocol
from twisted.internet.protocol import Factory as _Factory, error
from twisted.protocols.basic import LineReceiver
from twisted.internet.address import IPv4Address
from twisted.python import failure
from twisted.internet import reactor, defer
from werkzeug.local import Local
from .models import Message, TempDict
from .errors import BaseError, UnhandledRequest
from collections import defaultdict
import logging

connectionDone = failure.Failure(error.ConnectionDone())

local = Local()
protocol: 'AbstractProtocol' = local('protocol')
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


class AbstractProtocol:

    def __init__(self, address: IPv4Address, server: 'AbstractFactory'):
        self.address = address
        self.console = logging.getLogger(repr((address.host, address.port)))
        self.server = server

        self.user = None

    @error_cache
    def handle_message(self, message: Message):
        self.console.debug('Message %s' % message)

        callbacks = self.server.callbacks[message.callback]
        if callbacks:
            for i in range(len(callbacks)):
                callbacks.pop(i).callback(message)
            return

        funcs = self.server.handlers[message.type]
        for func in funcs:
            func(message, self)
        if not funcs:
            raise UnhandledRequest

    def on_message(self, data, is_binary=True):
        if is_binary:
            return self.handle_message(Message.from_bytes(data))
        return self.handle_message(Message.from_json(data))

    def copy(self):
        return self

    def connection_made(self):
        self.server.on_open_func(self) if self.server.on_open_func else None
        self.console.info('User connected')

    def connection_lost(self, reason=connectionDone):
        self.server.on_close_func(self, reason) if self.server.on_close_func else None
        self.console.info('Disconnected')

    def send_error_message(self, exception):
        self.send(Message('error', {
            'code': exception.code,
            'message': exception.message
        }))

    def response(self, to: Message, message: Message):
        message.callback = to.callback
        return self.send(message)

    def send(self, message: Message):
        self.console.debug('Send %s' % message)
        d = defer.Deferred()
        self.server.callbacks[message.callback].append(d)
        return d


class LineProtocol(AbstractProtocol, LineReceiver):

    def lineReceived(self, line):
        self.on_message(line)

    def rawDataReceived(self, data):
        pass

    def connectionMade(self):
        self.connection_made()

    def connectionLost(self, reason=connectionDone):
        self.connection_lost()

    def send(self, message: Message):
        self.sendLine(message.dump().encode('utf-8'))
        return super().send(message)


class WebSocketProtocol(WebSocketServerProtocol, AbstractProtocol):

    def __init__(self, addr, server):
        WebSocketServerProtocol.__init__(self)
        AbstractProtocol.__init__(self, addr, server)
        self.factory = server

    def onConnect(self, request):
        self.connection_made()

    def onClose(self, was_clean, code, reason):
        self.connection_lost(reason)

    def onMessage(self, payload, is_binary):
        self.on_message(payload, is_binary)

    def send(self, message: Message):
        self.sendMessage(message.dump().encode('utf-8'))
        return super().send(message)


class AbstractFactory:
    handlers = defaultdict(lambda: [])
    callbacks = TempDict()
    on_close_func = None
    on_open_func = None

    def __init__(self, proto=LineProtocol):
        self.protocol = proto
        self.port = None

    def handle(self, event):
        if isinstance(event, str):
            event = [event]

        def decorator(func: callable):
            def wrapper(message: 'Message', proto: 'AbstractProtocol'):
                # noinspection PyUnresolvedReferences,PyDunderSlots
                local.protocol = proto
                d = func(message)
                return defer.ensureDeferred(d)

            for e in event:
                self.handlers[e].append(wrapper)
            return wrapper

        return decorator

    def on_close(self):
        def decorator(func):
            def wrapper(proto, reason):
                # noinspection PyUnresolvedReferences,PyDunderSlots
                local.protocol = proto
                d = func(reason) if func.__code__.co_varnames else func()
                return defer.ensureDeferred(d)

            self.on_close_func = wrapper
            return wrapper

        return decorator

    def on_open(self):
        def decorator(func):
            def wrapper(proto):
                # noinspection PyUnresolvedReferences,PyDunderSlots
                local.protocol = proto
                return defer.ensureDeferred(func())

            self.on_open_func = wrapper
            return wrapper

        return decorator

    def build_protocol(self, addr: IPv4Address) -> AbstractProtocol:
        proto = self.protocol(addr, self)
        return proto

    def prepare(self, port):
        self.port = reactor.listenTCP(port, self)
        log.info('Listen %s server at %s' % (self.protocol, port))

    def run(self, port=8956):
        self.prepare(port)
        reactor.run()


class LineFactory(_Factory, AbstractFactory):
    def buildProtocol(self, addr: IPv4Address) -> AbstractProtocol:
        return self.build_protocol(addr)


class WebSocketFactory(_WebSocketServerFactory, AbstractFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = WebSocketProtocol

    def buildProtocol(self, addr: IPv4Address) -> AbstractProtocol:
        return self.build_protocol(addr)
