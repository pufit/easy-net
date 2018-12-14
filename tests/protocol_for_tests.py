from easy_net.server import LineFactory, protocol
from easy_net.models import Message

server = LineFactory()


@server.handle('echo')
async def echo(message):
    protocol.send(Message('echo_resp', {
        'msg': message.data['msg']
    }))


@server.handle(['test1', 'test2', 'test3'])
async def event_type(message):
    protocol.send(Message(message.type, {
        'msg': 'it works'
    }))


@server.handle('get_users')
async def send_users(message):
    protocol.response(message, Message('users', {
        'users': [
            {
                'name': 'Dr. Clef',
                'age': 'CLASSIFIED'
            },
            {
                'name': 'Dr. Bright',
                'age': 'CLASSIFIED'
            }
        ]
    }))


@server.handle('test_await')
async def get_users(_):
    message = await protocol.send(Message('get_users'))
    print(message.data['users'])
    protocol.response(message, Message('received_users'))


if __name__ == '__main__':
    server.run(port=8000)
