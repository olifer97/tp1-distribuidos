import datetime
import threading
import time
import json
import socket
import os
import queue

from utils_sock import *
from block import Block
from constants import *
from writer import Writer


class Blockchain():
    def __init__(self, host, port):
      # Create a TCP/IP socket
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

      # Bind the socket to the port
      self.sock.bind((host, port))

      # Listen for incoming connections
      self.sock.listen(1)
      self.last_hash = None
      self.blocks_queue = queue.Queue()
      self.writer = Writer(self.blocks_queue)
      self.writer.start()

    def run(self):
      while True:
        # leer del socket y escribir en el archivo
        connection, client_address = self.sock.accept()

        size_block = bytes_8_to_number(recv(connection, NUMBER_SIZE))

        print("recibi el tamano del bloque {}".format(size_block))

        block_data = json.loads(recv(connection, size_block).decode('utf-8'))
        print("[WRITER] recibi {}".format(block_data))

        print("lasthash {} block prev hash {}".format(self.last_hash, block_data['info']['header']['prev_hash']))

        if self.last_hash != block_data['info']['header']['prev_hash']:
          print("FALLO {}".format(block_data['hash']))
          result = False
        else:
          self.last_hash = block_data['hash']
          print("EXITO! {}".format(block_data['hash']))
          result = True
          self.blocks_queue.put(block_data)
        #intentar guardar en los archivos
        send(connection, ACK_SCHEME.pack(result)) #mando si fue bien o no
        close(connection)
      close(self.sock)
