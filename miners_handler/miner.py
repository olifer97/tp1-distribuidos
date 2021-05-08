import datetime
import threading
import time
import random
import json
from utils_sock import *

WRITER_REPONSE_SIZE = 1


class Miner(threading.Thread):
    def __init__(self, queue_blocks, stop_mining_queue, outcome_queue, writer_address):
      threading.Thread.__init__(self)
      self.queue_blocks = queue_blocks
      self.stop_mining_queue = stop_mining_queue
      self.outcome_queue = outcome_queue
      self.writer_address = writer_address
      #print("el socket con el writer {}".format(self.sock))

    def meetsCondition(self, block):
      return block.hash() < (2**256) / block.difficulty()

    def mine(self, block):
      timestamp = datetime.datetime.now()
      block.setTimestamp(timestamp)
      while self.stop_mining_queue.empty() and not self.meetsCondition(block):
          print("nolologreee")
          block.addNonce()
          block.setTimestamp(datetime.datetime.now())

      if self.stop_mining_queue.empty():
        print("paro de minar")

        data = json.dumps({"hash": block.hash(), "block": block.serialize()})

        self.sock = create_and_connect_client_socket(self.writer_address)

        send(self.sock, number_to_8_bytes(len(data)))

        send(self.sock, str.encode(data, 'utf-8'))

        blockchain_response = ACK_SCHEME.unpack(recv(self.sock, WRITER_REPONSE_SIZE))

        outcome = {"success": blockchain_response, "hash": block.hash()}
      else:
        print("me mandaron a parar")
        outcome = {"success": False}

      return self.outcome_queue.put(json.dumps(outcome))
        

    def run(self):
      while True:
        print("HOLAAAA")
        block = self.queue_blocks.get()
        print("recibi un bloque: {}".format(block.serialize()))
        self.mine(block)
        self.queue_blocks.task_done()
        break
