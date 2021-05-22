import datetime
import threading
import time
import json
import socket
import os
import queue
import signal
import logging

from block import Block
from constants import *
from reader import Reader
from custom_socket.server_socket import ServerSocket

class ReaderManager(threading.Thread):
    def __init__(self, host, port, n_readers, stop_event):
      threading.Thread.__init__(self)
      self.socket = ServerSocket(host, port, 1)

      self.stop_event = stop_event
      self.n_readers = n_readers
      self.request_queue = queue.Queue()
      self.response_queue = queue.Queue() 
      self.readers = [Reader(self.request_queue, self.response_queue, self.stop_event) for i in range(n_readers)]
      self.hearing_readers = threading.Thread(target=self._hear_responses)
      self._start_readers()
      self.hearing_readers.start()

    def _start_readers(self):
        for i in range(self.n_readers):
            self.readers[i].start()

    def _join_readers(self):
        for i in range(self.n_readers):
            self.readers[i].join()

    def _hear_responses(self):
        while not self.stop_event.is_set():
          try:
            response = self.response_queue.get(timeout=TIMEOUT_WAITING_MESSAGE)
            self.response_queue.task_done()
            response["socket"].send_with_size(json.dumps(response["response"]))
          except queue.Empty:
            if self.stop_event.is_set():
              if not self.request_queue.empty(): self.request_queue.join()
              break

    def run(self):
      while not self.stop_event.is_set():
          # leer del socket y escribir en el archivo
          client = self.socket.accept()
          if client == None:
            if self.stop_event.is_set():
              break
            continue
          request_data = self.socket.recv_from(client)
          self.request_queue.put({"socket": client, "request": request_data})
      logging.info("[READER MANAGER] Starts to finish")
      # stop data collection. Let the logging thread finish logging everything in the queue
      if not self.request_queue.empty(): self.request_queue.join()
      #if not self.response_queue.empty(): self.response_queue.join()
      self._join_readers()
      self.socket.close()
      logging.info("[READER MANAGER] Finished")
