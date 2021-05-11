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

class WriterManager(threading.Thread):
    def __init__(self, host, port):
      threading.Thread.__init__(self)
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

        block_data = json.loads(recv_and_cut(connection, MAX_BLOCK_SIZE))

        if self.last_hash != block_data['info']['header']['prev_hash']:
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
