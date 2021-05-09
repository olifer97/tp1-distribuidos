import datetime
import threading
import time
import json
import socket

from utils_sock import *
from block import Block


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
      self.last_hash = None

    def run(self):
      while True:
        # leer del socket y escribir en el archivo
        connection, client_address = self.sock.accept()

        size_block = bytes_8_to_number(recv(connection, NUMBER_SIZE))

        print("recibi el tamano del bloque {}".format(size_block))

        block_data = json.loads(recv(connection, size_block).decode('utf-8'))
        print("[WRITER] recibi {}".format(block_data))

        #block = Block.deserialize(block_data['info'])

        print("lasthash {} block prev hash {}".format(self.last_hash, block_data['info']['header']['prev_hash']))

        if self.last_hash != block_data['info']['header']['prev_hash']:
          print("FALLO {}".format(block_data['hash']))
          result = False
        else:
          self.last_hash = block_data['hash']
          print("EXITO! {}".format(block_data['hash']))
          result = True
          with open('{}.json'.format(block_data['hash']), 'w') as f:
            json.dump(block_data['info'], f)
        #intentar guardar en los archivos
        send(connection, ACK_SCHEME.pack(result)) #mando si fue bien o no
        close(connection)
      close(self.sock)
