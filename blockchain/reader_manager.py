import datetime
import threading
import time
import json
import socket
import os
import queue

from block import Block
from constants import *
from reader import Reader
from custom_socket.server_socket import ServerSocket

class ReaderManager(threading.Thread):
    def __init__(self, host, port, n_readers):
      threading.Thread.__init__(self)
      self.socket = ServerSocket(host, port, 1)

      self.n_readers = n_readers
      self.request_queue = queue.Queue()
      self.response_queue = queue.Queue() 
      self.readers = [Reader(self.request_queue, self.response_queue) for i in range(n_readers)]
      self.hearing_readers = threading.Thread(target=self.hearResponses)
      self.startReaders()
      self.hearing_readers.start()

    def startReaders(self):
        for i in range(self.n_readers):
            self.readers[i].start()

    def hearResponses(self):
        while True:
            response = self.response_queue.get()
            response["socket"].send_with_size(json.dumps(response["response"]))

    def run(self):
      while True:
        # leer del socket y escribir en el archivo
        client = self.socket.accept()

        request_data = self.socket.recv_from(client)
        self.request_queue.put({"socket": client, "request": request_data})
        
      self.socket.close()
