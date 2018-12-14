import unittest
from subprocess import Popen
from easy_net.models import Message
import socket
from sys import stdout, stderr
import random


class RequestResponseTestCase(unittest.TestCase):
    addr = ('localhost', 8000)
    sock = None
    server = None

    @classmethod
    def setUpClass(cls):
        socket.setdefaulttimeout(2)
        cls.server = Popen(['python', 'protocol_for_tests.py'], stdout=stdout, stderr=stderr)

    @classmethod
    def tearDownClass(cls):
        cls.server.kill()

    def tearDown(self):
        if self.sock:
            self.sock.close()
        self.sock = None

    def setUp(self):
        self.sock = socket.create_connection(self.addr)

    def send(self, message):
        self.sock.send(message.dump().encode() + b'\r\n')

    @staticmethod
    def stat_send(sock, message):
        sock.send(message.dump().encode() + b'\r\n')

    def recv(self):
        row = self.sock.recv(1024)
        return Message.from_bytes(row)

    def test_echo(self):
        self.send(Message('echo', {
            'msg': 'test'
        }))
        message = self.recv()
        self.assertEqual(message.type, 'echo_resp')
        self.assertEqual(message.data['msg'], 'test')

    def test_response(self):
        message = Message('get_users')
        self.send(message)
        resp = self.recv()
        self.assertEqual(message.callback, resp.callback)

    def test_await(self):
        self.send(Message('test_await'))
        message = self.recv()
        self.assertEqual(message.type, 'get_users')
        self.send(Message('users', {
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
        }, callback=message.callback))
        new_message = self.recv()
        self.assertEqual(new_message.type, 'received_users')
        self.assertEqual(new_message.callback, message.callback)

    def test_stress(self):
        connections = [self.sock]
        for i in range(1000):
            connections.append(socket.create_connection(self.addr))
            sock = random.choice(connections)
            self.stat_send(sock, Message('echo', data={
                'msg': random.randint(0, 100000)
            }))
        for sock in connections:
            sock.close()
        self.sock = None


if __name__ == '__main__':
    unittest.main()
