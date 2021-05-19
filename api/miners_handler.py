from threading import Thread, BoundedSemaphore, Barrier
import multiprocessing as mp
import queue
import datetime
from miner import Miner
from block import Block
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
            target=self.hearOutcomeFromMiner, args=(i,)) for i in range(n_miners)]
        self.last_hash = None
        self.difficulty = 1
        self.proccesedBlocks = 0
        self.startTime = datetime.datetime.now()
        self.block = self.createEmptyBlock()
        self.barrier = Barrier(n_miners + 1)
        self.startMiners()
        

    def checkProccesedBlock(self):
        self.proccesedBlocks += 1
        if self.proccesedBlocks >= DIFFICULTY_MINED_BLOCKS:
            elapsedTime = (datetime.datetime.now() -
                           self.startTime).total_seconds()
            self.difficulty *= (12/(elapsedTime/DIFFICULTY_MINED_BLOCKS))
            self.proccesedBlocks = 0
            self.startTime = datetime.datetime.now()

    def createEmptyBlock(self):
        self.checkProccesedBlock()
        newBlock = Block(self.last_hash, self.difficulty, [])
        newBlock.setTimestamp(datetime.datetime.now())
        return newBlock

    def sendBlock(self, block): # TODO: Agregar fairnes
        #random.shuffle(self.blocks_queues)
        for queue in self.blocks_queues:
            queue.put(block)

    def waitQueues(self):
        for queue in self.blocks_queues:
            queue.join()

    def stopOtherMiners(self, succedeedMiner):
        for i in range(self.n_miners):
            if i != succedeedMiner:
                self.stop_mining_queues[i].put(True)
                self.stats_queue.put({"miner": i, "failed": True})
            else:
                self.stats_queue.put({"miner": i, "success": True})

    def startMiners(self):
        for i in range(self.n_miners):
            self.miners[i].start()
            self.hearing_miners[i].start()

    def join(self):
        for i in range(self.n_miners):
            self.miners[i].join()
            self.hearing_miners[i].join()

    def hearOutcomeFromMiner(self, miner):
        while True:
            logging.info("SOY EL HEARING MINER {} POR GETEAT Y VOY A ESPERAR".format(miner))
            self.barrier.wait()
            outcome_data = self.outcome_queues[miner].get()
            outcome = json.loads(outcome_data)
            if bool(outcome['success']):
                logging.info("I succeded in mining {} with hash: {}".format(
                    miner, outcome["hash"]))
                self.last_hash = outcome["hash"]
                self.stopOtherMiners(miner)
            else:
                logging.info("Failed in mining")

    def send(self):
        logging.info("SOY EL MINERS HANDLER POR MANDAR Y VOY A ESPERAR")
        self.barrier.wait()
        self.sendBlock(self.block.serialize())
        self.block = self.createEmptyBlock()

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

            