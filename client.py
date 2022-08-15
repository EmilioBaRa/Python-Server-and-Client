#!/usr/bin/env python3
import asyncio
import sys

async def client(ip_address, port, message):
    enteredMessage = False
    key = message[3:11]
    while not enteredMessage:
        reader, writer = await asyncio.open_connection(ip_address, port)
        writer.write(message.encode('utf-8') + b'\n')
        data = await reader.readline()
        received = data.decode("utf-8")
        writer.close()
        if(received != '\n'):
            print(f'Received: {received}')
            key = received[0:8]
            message = 'GET' + str(key)
        else:
            userMessage = input('Please insert a new message\n')
            message = 'PUT' + str(key) + str(userMessage)
            reader, writer = await asyncio.open_connection(ip_address, port)
            writer.write(message.encode('utf-8') + b'\n')
            data = await reader.readline()
            received = data.decode("utf-8")
            writer.close()
            print(f'Received: {received}')
            enteredMessage = True
        await writer.wait_closed()

if len(sys.argv) != 4:
    raise Exception('{sys.argv[0]} needs ip, port and key transmit')
    sys.exit(-1)

try:
    ip_address = str(sys.argv[1])
    port = int(sys.argv[2])
    key = str(sys.argv[3])
    if(len(key) != 8):
        raise Exception('Message must be a key of length 8')
        sys.exit(-1)
    message = 'GET' + key
    asyncio.run(client(ip_address, port, message))
except Exception as e:
    print(e)
