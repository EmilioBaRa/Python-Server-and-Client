import pytest
import subprocess
import time
import random
import socket
import sys

def stop_container():
    print('\n\n')
    cmd = subprocess.run(['sudo', 'docker', 'stop', '226-message-server'], capture_output=True)
    print(cmd)
    cmd = subprocess.run(['sudo', 'docker', 'rm', '226-message-server'], capture_output=True)
    print(cmd)

def setup_module(module):
    stop_container()
    cmd = subprocess.run(['sudo', 'docker', 'build', '-t', '226-message-server', '.'], capture_output=True)
    print(cmd)
    cmd = subprocess.run(['sudo', 'docker', 'run', '-d', '--name', '226-message-server', '-p', '12345:12345', '226-message-server'], capture_output=True)
    print(cmd)
    time.sleep(5) # Ugly; should properly detect when the container is up and running
    print('\n\n')

def teardown_module(module):
    stop_container()
    print('\n\n')

def transmit(message):
    print('----\n')
    input = subprocess.Popen(['echo', message], stdout=subprocess.PIPE)
    print('>', input.args)
    output= subprocess.check_output(['nc', '127.0.0.1', '12345'], stdin=input.stdout)
    print('<', output)
    return output

def test_invalid_command():
    output = transmit('Test')
    assert output == b'NO\n'

def test_missing_key_for_put():
    output = transmit('PUT')
    assert output == b'NO\n'

def test_invalid_key_for_put():
    key = 'PUT'
    for i in range(7):
        key = key + str(i)
        output = transmit(key)
        assert output == b'NO\n'

def test_valid_key():
    output = transmit('PUTabcdefghThis is a test')
    assert output == b'OK\n'

    output = transmit('GETabcdefgh')
    assert output == b'This is a test\n'

def test_missing_key_for_get():
    print()
    output = transmit('GET')
    assert output == b'\n'

def test_invalid_key_for_get():
    print()
    key = 'GET'
    for i in range(10):
        key = key + str(i)
        output = transmit(key)
        assert output == b'\n'

def test_message_size():
    print()
    putKey = 'PUTijklmnop'
    getKey = 'GETijklmnop'
    putMsg = ''
    for i in range(160):
        putMsg = putMsg + str(i % 10)
        output = transmit(putKey + putMsg)
        assert output == b'OK\n'

        output = transmit(getKey)
        assert output == (putMsg + '\n').encode('utf-8')

    output = transmit(putKey + putMsg + 'X')
    assert output == b'NO\n'

    output = transmit(getKey)
    assert output == (putMsg + '\n').encode('utf-8')

def get_line(current_socket):
    KEY_SIZE = 8
    MSG_SIZE = 160
    BUF_SIZE = 3 + KEY_SIZE + MSG_SIZE
    buffer = b''
    size = 0
    while True:
        data = current_socket.recv(1)
        size += 1
        if data == b'\n' or size >= BUF_SIZE:
            return buffer
        buffer = buffer + data

def setup_cnx(num):
    HOST = '127.0.0.1'
    PORT = 12345

    print('Client', num, 'starting')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    return sock

def send_put_msg(sock, num):
    KEY_SIZE = 8
    MSG_SIZE = 160
    BUF_SIZE = 3 + KEY_SIZE + MSG_SIZE
    PUT_CMD = 'PUT'

    key = str(num) + ''
    while len(key) < KEY_SIZE:
        key = key + str(random.randint(0, 9))

    msg = ''
    while len(msg) < MSG_SIZE:
        msg = msg + str(random.randint(0, 9))

    print('Client', num, 'sending', PUT_CMD, key)
    sock.sendall((PUT_CMD + key + msg + '\n').encode('utf-8'))
    print('Client', num, 'received', get_line(sock))

    return (key, msg)

def send_get_msg(sock, num, key, msg):
    sock.close()

    HOST = '127.0.0.1'
    GET_CMD = 'GET'
    PORT = 12345

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print('Client', num, 'sending', GET_CMD, key)
    sock.sendall((GET_CMD + key + '\n').encode('utf-8'))
    data = get_line(sock)
    assert msg.encode('utf-8') == data
    print('Client', num, 'received', ('' if msg.encode('utf-8') == data else 'in') + 'correct message')


def test_multiple_sessions():
    NUM_SESSIONS = 5

    if len(sys.argv) == 2:
        newVal = int(sys.argv[1])
        if NUM_SESSIONS < newVal:
            NUM_SESSIONS = newVal

    socks = []
    msgs = []
    for i in range(NUM_SESSIONS):
        socks.append((i, setup_cnx(i)))

    for (i, sock) in reversed(socks):
        msgs.append((i, sock, send_put_msg(sock, i)))

    for (i, sock, (key, msg)) in msgs:
        send_get_msg(sock, i, key, msg)

def send_individually(s, sock):
    for c in s:
        sock.sendall(str(c).encode('utf-8'))
    return get_line(sock)

def test_fragmentation():
    sock = setup_cnx(-1)
    fragmented_put_cmd = 'PUTabcdefghThis is a test\nX'
    if send_individually(fragmented_put_cmd, sock) != b'OK':
        print(b'Last get failed')
        assert False
    else:
        print(b'Last get ok')
        assert True
    sock.close()

    sock = setup_cnx(-2)
    fragmented_get_cmd = 'GETabcdefgh\n'
    if send_individually(fragmented_get_cmd, sock) != b'This is a test':
        print(b'Last get failed')
        assert False
    else:
        print(b'Last get ok')
        assert True
    sock.close()

