import datetime
import threading
import multiprocessing as mp
import time
import json
import logging
from utils_sock import *
from block import Block

WRITER_REPONSE_SIZE = 1

class Miner(mp.Process):
    def __init__(self, queue_blocks, stop_mining_queue, outcome_queue, writer_address):
      mp.Process.__init__(self)
      self.queue_blocks = queue_blocks
      self.stop_mining_queue = stop_mining_queue
      self.outcome_queue = outcome_queue
      self.writer_address = writer_address

    def meetsCondition(self, block):
      return block.hash() < (2**256) / block.difficulty()

    def mine(self, block):
      timestamp = datetime.datetime.now()
      block.setTimestamp(timestamp)
      while self.stop_mining_queue.empty() and not self.meetsCondition(block):
          info.logging("tratando de encontrar el hash")
          block.addNonce()
          block.setTimestamp(datetime.datetime.now())

      if self.stop_mining_queue.empty():
        block_hash = block.hash()

        data = json.dumps({"hash": block_hash, "info": block.asDict()})

        self.sock = connect_send(data, self.writer_address)

        blockchain_response = ACK_SCHEME.unpack(recv_and_cut(self.sock, WRITER_REPONSE_SIZE, decode=False))[0]

        outcome = {"success": blockchain_response, "hash": block_hash}
      else:
        logging.info("I should stop mining")
        self.stop_mining_queue.get_nowait()
        outcome = {"success": False}

      return self.outcome_queue.put(json.dumps(outcome))
        

    def run(self):
      while True:
        block_data = self.queue_blocks.get()
        logging.info("Got block data: {}".format(block_data))
        self.mine(Block.deserialize(block_data))