#!/usr/bin/env python3

import asyncio
import sys
import random

#
# PURPOSE:
# This function sends a message and receives a response from the server.
#
# PARAMETERS:
# 'ip_address' is the string that will be used as the connection to the server
# 'port' is the integer that will retain the port assigned to the server
# 'message' string that is going to be sent as a request to the server
#
# RETURN/SIDE EFFECTS:
# The function will send a command to the server, receive a response, decrypt the response
# and then return a string representation of the response from the server
#
# NOTES:
# The writer must be closed each time a request is made to the server
#
async def send_message(ip_address, port, message):
    reader, writer = await asyncio.open_connection(ip_address, port)
    writer.write(message.encode('utf-8') + b'\n')
    data = await reader.readline()
    received = data.decode("utf-8")
    writer.close()
    return received

#
# PURPOSE:
# Outputs the results made by a GET command in the server.
# Gets the new key that is going to be needed for output or saving messages
#
# PARAMETERS:
# 'received' a string that represents the response given by the server
# 'key' a string that represent where a message is saved.
#
# RETURN/SIDE EFFECTS:
# The function expects to return server message an prepare the key for getting or creating a messag
#
# NOTES:
# GET is added as part of the string to give the next command that needs to execute
#
def get_result(received, key):
    print(f'Received: {received}')
    key = received[0:8]
    message = 'GET' + str(key)
    return message, key

#
# PURPOSE:
# Generate an 8 digit random number
#
# RETURN/SIDE EFFECTS:
# This function will genearte a random numeric key that will be appended to a message
#
# NOTES:
# Keys starting with value 0 does not exist
#
def generate_random():
    randomKey = random.randint(10000000,99999999)
    return randomKey
#
# PURPOSE:
# Given an ip, port and key, the funciton expects to get an user input that will be appended
# to a 'PUT' string and the key parameter to make a PUT request to the server.
#
# PARAMETERS:
# 'ip_address' is the string that will be used as the connection to the server
# 'port' is the integer that will retain the port assigned to the server
# 'key' a string that represent where the new message is going to be saved.
#
# RETURN/SIDE EFFECTS:
# The function will call the send_message funciton, expecting to append a new message to the server
# with an appended numeric key in format '12345678MESSAGE'
#
# NOTES:
# A print statement is placed for debugging and result checking purpose
#
async def put_insert(ip_address, port, key):
    userMessage = input('Please insert a new message\n')
    generateKey = generate_random()
    message = 'PUT' + str(key) + str(generateKey) + str(userMessage)
    received = await send_message(ip_address, port, message)
    print(f'Received: {received}')

#
# PURPOSE:
# Given an ip, port and message. The client tries to read all the messages entered into the server
# starting with the given key in the command line and writes a new message.
#
# PARAMETERS:
# 'ip_address' is the string that will be used as the connection to the server
# 'port' is the integer that will retain the port assigned to the server
# 'message' a string that has a key and a message in it.
#
# RETURN/SIDE EFFECTS:
# The loop will run until the last message has been found, then the program will call the put_insert function
# and the loop will be finished
#
# NOTES:
# To succeed, it is expected that the user gives more than 8 key characters and at least 1 message character
# (a total of at least 9 characters)
#
async def client(ip_address, port, message):
    enteredMessage = False
    key = message[3:11]
    while not enteredMessage:
        received = await send_message(ip_address, port, message)
        if(received != '\n'):
            (message, key) = get_result(received, key)
        else:
            await put_insert(ip_address, port, key)
            enteredMessage = True


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
