from easy_net.server import LineFactory, protocol
from easy_net.models import Message

server = LineFactory()


@server.handle('echo')
async def echo(message):
    protocol.send(Message('echo_resp', {
        'msg': message.data['msg']
    }))


@server.handle(['test1', 'test2', 'test3'])
async def test(message):
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


@server.on_open()
async def get_users():
    data = await protocol.send(Message('get_users'))
    print(data['users'])


if __name__ == '__main__':
    server.run(port=8000)
