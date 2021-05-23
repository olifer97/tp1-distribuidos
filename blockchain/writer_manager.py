import datetime
import logging
import threading
import time
import json
import socket
import os
import queue
import signal

from block import Block
from constants import *
from writer import Writer
from custom_socket.server_socket import ServerSocket

class WriterManager(threading.Thread):
    def __init__(self, host, port, stop_event):
      threading.Thread.__init__(self)
      self.stop_event = stop_event
      self.socket = ServerSocket(host, port, 1)

      self.last_hash = None
      self.blocks_queue = queue.Queue()
      self.writer = Writer(self.blocks_queue, self.stop_event)
      self.writer.start()

    def run(self):
      while not self.stop_event.is_set():
        # leer del socket y escribir en el archivo
        client = self.socket.accept()

        if client == None:
          if self.stop_event.is_set():
            break
          continue

        block_data = self.socket.recv_from(client)
        if self.last_hash != block_data['info']['header']['prev_hash']:
          logging.info("Wrong prev hash: {}".format(block_data['info']['header']['prev_hash']))
          result = False
        else:
          self.last_hash = block_data['hash']
          logging.info("Block mined with hash: {}".format(block_data['hash']))
          result = True
          self.blocks_queue.put(block_data)

        self.socket.send_to(client, ACK_SCHEME.pack(result), encode=False)
        client.close()
      self.blocks_queue.join()
      self.stop_event.set()
      self.socket.close()
      logging.info("[WRITER MANAGER] Finished")
