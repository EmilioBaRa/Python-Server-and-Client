#!/usr/bin/python3

import asyncio
import sys

KEY_SIZE = 8
MAX_MSG_SIZE = 160
ERROR_RESPONSE = b"NO\n"
GET_CMD = "GET".encode('utf-8')
HOST = ''
NUM_CONNECTIONS = 1
OK_RESPONSE = b'OK\n'
PORT = 12345
PUT_CMD = "PUT".encode('utf-8')

messages = {}

#
# PURPOSE:
# Given a string, extracts the key and message from it
#
# PARAMETERS:
# 's' is the string that will be used for the key and message extraction
#
# RETURN/SIDE EFFECTS:
# Returns (key, message, flag), where flag is True if the extraction
# succeeded, False otherwise
#
# NOTES:
# To succeed, the string must be of format "KEYMSG" where KEY is of length KEY_SIZE
#
def get_key(s):
    print(s[:KEY_SIZE])
    if len(s) < KEY_SIZE:
        return ("", "", False)
    else:
        return (s[:KEY_SIZE], s[KEY_SIZE:], True)

#
# PURPOSE:
# Given a string, extracts the key and message, and stores the message in messages[key]
#
# PARAMETERS:
# 's' is the string that will be used for the key and message extraction
#
# RETURN/SIDE EFFECTS:
# Returns OK_RESPONSE on success, ERROR_RESPONSE otherwise
#
# NOTES:
# To succeed, the string must be of format "KEYMSG" where KEY is of length KEY_SIZE
# and MSG does not exceed MAX_MSG_SIZE
#
def process_put(s):
    (key, msg, ok) = get_key(s)
    if (not ok) or (len(msg) > MAX_MSG_SIZE):
        return ERROR_RESPONSE

    messages[key] = msg

    return OK_RESPONSE

#
# PURPOSE:
# Given a string, extracts the key and message from it, and returns message[key]
#
# PARAMETERS:
# 's' is the string that will be used for the key and message extraction
#
# RETURN/SIDE EFFECTS:
# Returns the message if the extraction succeeded, and b'' otherwise
#
# NOTES:
# To succeed, the string must be of format "KEY" where KEY is of length KEY_SIZE
#
def process_get(s):
    (key, msg, ok) = get_key(s)
    if not ok or len(msg) != 0 or not key in messages:
        return b'\n'
    return messages[key] + b'\n'

#
# PURPOSE:
# Given a string, parses the string and implements the contained PUT or GET command
# only if the length is more or equal to eleven
#
# PARAMETERS:
# 's' is the string that will be used for parsing
#
# RETURN/SIDE EFFECTS:
# Returns the result of the command if the extraction succeeded, ERROR_RESPONSE  or blank line 
# otherwise
#
# NOTES:
# The string is assumed to be of format "CMDKEYMSG" where CMD is either PUT_CMD or GET_CMD,
# KEY is of length KEY_SIZE, and MSG varies depending on the command. See process_put(s)
# and process_get(s) for details regarding what the commands do and their return values
#
def process_line(s):
    if s.startswith(PUT_CMD):
        if len(s) >= 11:
            return process_put(s[(len(PUT_CMD)):])
        else:
            return ERROR_RESPONSE
    elif s.startswith(GET_CMD):
        if len(s) == 11:
            return process_get(s[(len(GET_CMD)):])
        else:
            return b'\n'
    else:
        return ERROR_RESPONSE

#
# PURPOSE:
# Given an encrypted message removes any special characters
#
# PARAMETERS:
# 'bytesMessage' is the bytes variable that will be transformed to string
#  to remove any special characters
#
# RETURN/SIDE EFFECTS:
# Returns a bytes variable based on the process_line function operations
#
# NOTES:
# It is assumed that a client will sent an alphanumeric message encrypted in bytes,
# the client is using a command line and the termination character of the message is
# a \n (enter tab)
#
def format_line(bytesMessage):
    sMessage = bytesMessage.decode('utf-8')
    sMessage = sMessage.strip()
    print(sMessage)
    message = sMessage.encode('utf-8')
    return process_line(message)

#
# PURPOSE:
# Responding to the client terminal based on a message sent by the client
#
# PARAMETERS:
# 'reader' is an async library parameter that will read the client message
# 'writer' is an async library parameter that will output in the client terminal
#
# RETURN/SIDE EFFECTS:
# Will send a message to the client based on the message received from the client
# and the message analysis by the format_line function
#
# NOTES:
# The client needs to send an encrypted in bytes message, 'data' variable
#
async def echo(reader, writer):
    data = await reader.readline()
    message = format_line(data)
    writer.write(message)
    await writer.drain()
    writer.close()
    await writer.wait_closed()

#
# PURPOSE:
# Starts a server in 'HOST' and 'PORT'
#
# RETURN/SIDE EFFECTS:
# It will start the server waiting for an echo command from the client,
# when the client starts an echo command, the echo function will be called
#
# NOTES:
# The client must use the same host 'HOST' and port 'PORT', to connect establish
# connection with the server
#
async def main():
    server = await asyncio.start_server(echo, HOST, PORT)
    await server.serve_forever()

asyncio.run(main())
