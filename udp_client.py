"""udp_client.py

    Run python autograder.py

Champlain College CSI-235, Spring 2018
The following code was written by Joshua Auerbach (jauerbach@champlain.edu)
"""

import socket
import constants
import uuid
import random


# adapted from https://stackoverflow.com/questions/14749328/python-how-to-check-whether-optional-function-parameter-is-set
# and https://github.com/brandon-rhodes/fopnp
DEFAULT = uuid.uuid4()


# Time out exception

class TimeOutError(Exception):
    pass


# one line summary

class UDPClient:

    # class initializer

    def __init__(self, host, port, temp_bool=DEFAULT):
        if temp_bool is DEFAULT:
            self.request_id = -1
        elif temp_bool:
            print("AAAAAAA true")
            self.request_id = random.randint(0, constants.MAX_ID)
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.connect((host, port))
            print('Client socket name is {}'.format(self.sock.getsockname()))
        except:
            raise TimeOutError('Failed to set a socket')

    # one line summary

    def send_message_by_character(self, message):
        if self.request_id >= 0:
            print("AAAAA ID")
            # message = self.request_id + "|" + message
            # print('Server says {!r}'.format(data.decode('ascii')))
            message_list_send = list(message)
            message_len = len(message_list_send)
            message_list_receive = []
            for i in range(0, message_len):
                temp_delay = constants.INITIAL_TIMEOUT
                while True:
                    data = message_list_send[i].encode('ascii')
                    self.sock.send(data)
                    print('Waiting up to {} seconds for a reply'.format(temp_delay))
                    self.sock.settimeout(temp_delay)
                    try:
                        data = self.sock.recv(constants.MAX_BYTES)
                    except socket.timeout as exc:
                        temp_delay *= 2  # wait even longer for the next request
                        if temp_delay > 2.0:
                            raise TimeOutError('I think the server is down') from exc
                    else:
                        break  # we are done, and can stop looping
                message_list_receive.append(data.decode('ascii'))
            message_str_receive = "".join(message_list_receive)
            print('Server says {!r}'.format(message_str_receive))
            return message_str_receive
        else:
            message_list_send = list(message)
            message_len = len(message_list_send)
            message_list_receive = []
            for i in range(0, message_len):
                temp_delay = constants.INITIAL_TIMEOUT
                while True:
                    data = message_list_send[i].encode('ascii')
                    self.sock.send(data)
                    print('Waiting up to {} seconds for a reply'.format(temp_delay))
                    self.sock.settimeout(temp_delay)
                    try:
                        data = self.sock.recv(constants.MAX_BYTES)
                    except socket.timeout as exc:
                        temp_delay *= 2  # wait even longer for the next request
                        if temp_delay > 2.0:
                            raise TimeOutError('I think the server is down') from exc
                    else:
                        break  # we are done, and can stop looping
                message_list_receive.append(data.decode('ascii'))
            message_str_receive = "".join(message_list_receive)
            print('Server says {!r}'.format(message_str_receive))
            return message_str_receive


if __name__ == "__main__":
    # some basic tests, for more extensive tests run the autograder!
    client = UDPClient("hawk.champlain.edu", 9998)
    print(client.send_message_by_character("hello world"))

    client = UDPClient("hawk.champlain.edu", 9999, True)
    print(client.send_message_by_character("hello world"))
