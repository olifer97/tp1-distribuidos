from threading import Thread, BoundedSemaphore, Barrier
import multiprocessing as mp
import queue
import datetime
from miner import Miner
from block import Block
from shared_value import SharedValue
import json
import logging
import time
import random

DIFFICULTY_MINED_BLOCKS = 256
SECONDS_WAITING_CHUNK = 10

class MinersHandler(Thread):
    def __init__(self, n_miners, chunks_queue, stats_queue, writer_address):
        Thread.__init__(self)
        self.chunks_queue = chunks_queue
        self.stats_queue = stats_queue
        self.blocks_queues = [mp.Queue() for i in range(n_miners)]
        self.stop_mining_queues = [mp.Queue() for i in range(n_miners)]
        self.outcome_queues = [mp.Queue() for i in range(n_miners)]
        self.n_miners = n_miners
        self.miners = [Miner(self.blocks_queues[i], self.stop_mining_queues[i],
                             self.outcome_queues[i], writer_address) for i in range(n_miners)]
        self.hearing_miners = [Thread(
            target=self._hear_outcome_from_miner, args=(i,)) for i in range(n_miners)]
        self.last_hash = SharedValue()
        self.difficulty = 1
        self.proccesedBlocks = 0
        self.startTime = datetime.datetime.now()
        self.block = self._create_empty_block()
        self.barrier = Barrier(n_miners + 1)
        self._start_miners()
        

    def _check_proccesed_block(self):
        self.proccesedBlocks += 1
        if self.proccesedBlocks >= DIFFICULTY_MINED_BLOCKS:
            elapsedTime = (datetime.datetime.now() -
                           self.startTime).total_seconds()
            self.difficulty *= (12/(elapsedTime/DIFFICULTY_MINED_BLOCKS))
            self.proccesedBlocks = 0
            self.startTime = datetime.datetime.now()

    def _create_empty_block(self):
        self._check_proccesed_block()
        newBlock = Block(self.difficulty, [])
        newBlock.setTimestamp(datetime.datetime.now())
        return newBlock

    def _send_block(self, block):
        for queue in self.blocks_queues:
            queue.put(block)

    def _stop_other_miners(self, succedeedMiner):
        for i in range(self.n_miners):
            if i != succedeedMiner:
                self.stop_mining_queues[i].put(True)
                self.stats_queue.put({"miner": i, "status": 'failed'})
            else:
                self.stats_queue.put({"miner": i, "status": 'success'})

    def _start_miners(self):
        for i in range(self.n_miners):
            self.miners[i].start()
            self.hearing_miners[i].start()

    def _hear_outcome_from_miner(self, miner):
        while True:
            logging.info("[HEARING MINER {}] Waiting to get outcome".format(miner))
            self.barrier.wait()
            outcome_data = self.outcome_queues[miner].get()
            outcome = json.loads(outcome_data)
            if bool(outcome['success']):
                logging.info("[HEARING MINER {}] Succeded mining with hash: {}".format(
                    miner, outcome["hash"]))
                logging.info("[HEARING MINER {}] Update last hash".format(miner))
                self.last_hash.update(outcome["hash"])
                self._stop_other_miners(miner)
            else:
                logging.info("[HEARING MINER {}] Failed mining".format(miner))

    def send(self):
        logging.info("[MINERS HANDLER] Waiting to send")
        self.barrier.wait()
        self.block.setPrevHash(self.last_hash.read())
        self._send_block(self.block.serialize())
        self.block = self._create_empty_block()

    def run(self):
        while True:
            try:
                chunk = self.chunks_queue.get(timeout=SECONDS_WAITING_CHUNK)
                self.block.addChunk(chunk)
                if self.block.isFull():
                    self.send()
            except queue.Empty:
                if not self.block.isEmpty():
                    self.send()

            