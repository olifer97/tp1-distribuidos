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
from reader import Reader

N_READERS = 5

REQUEST_SIZE = 1024

class ReaderManager(threading.Thread):
    def __init__(self, host, port):
      threading.Thread.__init__(self)
      # Create a TCP/IP socket
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


      # Bind the socket to the port
      self.sock.bind((host, port))

      # Listen for incoming connections
      self.sock.listen(1)

      self.request_queue = queue.Queue()
      self.response_queue = queue.Queue() 
      self.readers = [Reader(self.request_queue, self.response_queue) for i in range(N_READERS)]
      self.hearing_readers = threading.Thread(target=self.hearResponses)
      self.startReaders()
      self.hearing_readers.start()

    def startReaders(self):
        for i in range(N_READERS):
            self.readers[i].start()

    def hearResponses(self):
        #logging.info("empiezo a escuchar las stats")
        while True:
            response = self.response_queue.get()
            send(response["socket"], str(response["response"]).encode('utf-8'))
            #close(response["socket"])
            

    def run(self):
      while True:
        # leer del socket y escribir en el archivo
        connection, client_address = self.sock.accept()

        request_data = json.loads(connection.recv(REQUEST_SIZE).rstrip().decode())

        self.request_queue.put({"socket": connection, "request": request_data})
        
      close(self.sock)
