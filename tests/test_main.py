import unittest
from subprocess import Popen
from collections import deque
from easy_net.models import Message
import socket
from sys import stdout, stderr
import random
from _thread import start_new_thread
import time


class RequestResponseTestCase(unittest.TestCase):
    addr = ('localhost', 8000)
    sock = None
    server = None
    buffer = deque()
    connections = []

    @classmethod
    def setUpClass(cls):
        socket.setdefaulttimeout(2)
        cls.server = Popen(['python', 'protocol_for_tests.py'], stdout=stdout, stderr=stderr)
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.server.kill()

    def tearDown(self):
        for sock in self.connections:
            sock.close()
        if self.sock:
            self.sock.close()
        self.sock = None
        self.buffer.clear()

    def setUp(self):
        self.sock = socket.create_connection(self.addr)

    def send(self, message):
        self.stat_send(self.sock, message)

    @staticmethod
    def stat_send(sock, message):
        sock.send(message.dump().encode() + b'\r\n')

    def recv(self):
        return self.stat_recv(self.sock)

    def stat_recv(self, sock):
        row = sock.recv(2048).strip()
        self.buffer.extend(map(Message.from_bytes, row.split(b'\r\n')))
        return self.buffer.popleft()

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

    def test_type(self):
        self.send(Message('test1'))
        answer = self.recv()
        self.assertEqual(answer.type, 'test1')
        self.send(Message('test2'))
        answer = self.recv()
        self.assertEqual(answer.type, 'test2')
        self.send(Message('test3'))
        answer = self.recv()
        self.assertEqual(answer.type, 'test3')

    def test_stress(self):
        self.connections = []
        messages = {}
        for i in range(1000):
            sock = socket.create_connection(self.addr)
            self.connections.append(sock)
            message = Message('echo', data={
                'msg': random.randint(0, 100000)
            })
            messages[message.callback] = message
            start_new_thread(self.stat_send, (sock, message))

        for sock in self.connections:
            mess = self.stat_recv(sock)
            send_message = messages.get(mess.callback)
            self.assertIsNotNone(send_message)
            self.assertEqual(mess.data, send_message.data)
            messages.pop(mess.callback)

        self.assertFalse(messages)


if __name__ == '__main__':
    unittest.main()
