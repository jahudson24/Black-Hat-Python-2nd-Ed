# Simple Netcat replacement program

import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()


class NetCat:
    def __init__(self, args, buffer=None):
        # initialize the NetCat object
        self.args = args
        self.buffer = buffer
        # Create the socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)

    # Set up simple entry point
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send

    def send(self):
        # Connect to the target and port
        self.socket.connect((self.args.target, self.args.port))
        # If we have a buffer we send that to the target first
        if self.buffer:
            self.socket.send(self.buffer)
        try:
            # Loop to receive the data from the target
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    # Once data is over, break out of the loop
                    if recv_len < 4096:
                        break
                # If response requires input, pause loop to allow response
                if response:
                    print(response)
                    buffer = input('>')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        # Allows CTRL-C to close the connection
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

    def listen(self):
        # Binds to target and port
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        # Sets up listening loop, passing the connected socket to the handle method
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket))
            client_thread.start()

    # Implement ability to perform file uploads, execute commands, and create interactive shell
    def handle(self, client_socket):
        # Execute function gets passed a command and sends the output back to the socket
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        # Sets up a loop to listen and then write response to a file
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
        # For setting up a shell
        # Send a prompt to the sender and then execute the returned command string using the execute function
        # Return output to the sender
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BHP Net Tool',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent('''Example: netcat.py -t 192.168.1.108 -p 5555 -l -c 
                                     # command shell
                                     | netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file 
                                     | netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat/etc/passwd\" # execute command
                                     | echo 'ABC' | ./netcat.py -t 192.168.1.108 - p 135 # echo text to server port 135
                                     | netcat.py -t 192.168.1.108 -p 5555 # connect to server
                                     '''))
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
    nc = NetCat(args, buffer.encode())
    nc.run()
