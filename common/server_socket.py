import socket
import logging
import json
from utils import *
from constants import *
from client_socket import ClientSocket
from base_socket import Socket

class ServerSocket(Socket):
    def __init__(self, host, port, listen_backlog):
        Socket.__init__(self)
        self.bind_listen(host, port, listen_backlog)     
        
    def bind_listen(self, host, port, listen_backlog):
        self.socket.bind((host, port))
        self.socket.listen(listen_backlog)


    def accept(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info("Proceed to accept new connections")
        c, addr = self.socket.accept()
        logging.info('Got connection from {}'.format(addr))
        return ClientSocket(connection = c)

    def send_to(self, client_sock, data, encode=True):
        client_sock.send_with_size(data, encode)

    def recv_from(self, client_sock, decode = True):
        return client_sock.recv_with_size(decode)