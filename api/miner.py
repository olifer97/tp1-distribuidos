import datetime
import threading
import multiprocessing as mp
import queue
import time
import json
import logging
from block import Block
from constants import *
from custom_socket.client_socket import ClientSocket

class Miner(mp.Process):
    def __init__(self, queue_blocks, stop_mining_queue, outcome_queue, writer_address, stop):
      mp.Process.__init__(self)
      self.stop = stop
      self.queue_blocks = queue_blocks
      self.stop_mining_queue = stop_mining_queue
      self.outcome_queue = outcome_queue
      self.writer_address = writer_address

    def _meets_condition(self, block):
      return block.hash() < (2**256) / block.difficulty()

    def _send_to_blockchain(self, block, block_hash):
      try:
        self.sock = ClientSocket(address = self.writer_address)
        self.sock.send_with_size(block)

        blockchain_response = ACK_SCHEME.unpack(self.sock.recv_with_size(decode=False))[0]

        return {"success": blockchain_response, "hash": block_hash}
      except:
        logging.info("[MINER] Failed by socket connection")
        return {"success": False}

    def mine(self, block):
      timestamp = datetime.datetime.now()
      block.setTimestamp(timestamp)
      while self.stop_mining_queue.empty() and not self._meets_condition(block):
          block.addNonce()
          block.setTimestamp(datetime.datetime.now())

      if self.stop_mining_queue.empty():
        block_hash = block.hash()

        data = json.dumps({"hash": block_hash, "info": block.asDict()})

        outcome = self._send_to_blockchain(data, block_hash)
      else:
        logging.info("I should stop mining")
        
        outcome = {"success": False}

      if not self.stop_mining_queue.empty():
        self.stop_mining_queue.get_nowait()

      logging.info("Outcome is: {}".format(outcome))

      return self.outcome_queue.put(json.dumps(outcome))
        

    def run(self):
      while not self.stop.is_set():
        try:
          block_data = self.queue_blocks.get(timeout=TIMEOUT_WAITING_MESSAGE)
          logging.info("Got block data: {}".format(block_data))
          self.mine(Block.deserialize(block_data))
        except queue.Empty:
          continue
      self.outcome_queue.close()
      logging.info("[MINER] Finished")