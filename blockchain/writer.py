import datetime
import threading
import time
import json
import socket

from utils_sock import *


class Writer(threading.Thread):
    def __init__(self, host, port):
      threading.Thread.__init__(self)
      # Create a TCP/IP socket
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

      # Bind the socket to the port
      self.sock.bind((host, port))

      # Listen for incoming connections
      self.sock.listen(1)

    def run(self):
      while True:
        # leer del socket y escribir en el archivo
        connection, client_address = self.sock.accept()

        size_block = bytes_8_to_number(recv(connection, NUMBER_SIZE))

        print("recibi el tamano del bloque {}".format(size_block))

        block = recv(connection, size_block).decode('utf-8')
        print("[WRITER] recibi {}".format(block))
        #intentar guardar en los archivos
        send(connection, ACK_SCHEME.pack(True)) #mando si fue bien o no
        close(connection)
        break
      close(self.sock)
