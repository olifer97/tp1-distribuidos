import threading
import queue
import datetime
from miner import Miner
from block import Block
import json
import random

DIFFICULTY_MINED_BLOCKS = 256
SECONDS_WAITING_CHUNK = 5

class MinersHandler(threading.Thread):
    def __init__(self, n_miners, chunks_queue, stats_queue, writer_address):
        threading.Thread.__init__(self)
        self.chunks_queue = chunks_queue
        self.stats_queue = stats_queue
        self.blocks_queues = [queue.Queue() for i in range(n_miners)]
        self.stop_mining_queues = [queue.Queue() for i in range(n_miners)]
        self.outcome_queues = [queue.Queue() for i in range(n_miners)]
        self.n_miners = n_miners
        self.miners = [Miner(self.blocks_queues[i], self.stop_mining_queues[i],
                             self.outcome_queues[i], writer_address) for i in range(n_miners)]
        self.hearing_miners = [threading.Thread(
            target=self.hearOutcomeFromMiner, args=(i,)) for i in range(n_miners)]
        self.last_hash = None
        self.difficulty = 1
        self.proccesedBlocks = 0
        self.startTime = datetime.datetime.now()
        self.block = self.createBlock()
        self.startMiners()

    def checkProccesedBlock(self):
        self.proccesedBlocks += 1
        if self.proccesedBlocks >= DIFFICULTY_MINED_BLOCKS:
            elapsedTime = (datetime.datetime.now() -
                           self.startTime).total_seconds()
            self.difficulty *= (12/(elapsedTime/DIFFICULTY_MINED_BLOCKS))
            self.proccesedBlocks = 0
            self.startTime = datetime.datetime.now()

    def createBlock(self):
        self.checkProccesedBlock()
        newBlock = Block(self.last_hash, self.difficulty, [])
        newBlock.setTimestamp(datetime.datetime.now())
        return newBlock

    def sendBlock(self, block):
        random.shuffle(self.blocks_queues)
        for queue in self.blocks_queues:
            queue.put(block)
            queue.join()

    def waitQueues(self):
        for queue in self.blocks_queues:
            queue.join()

    def stopOtherMiners(self, succedeedMiner):
        for i in range(self.n_miners):
            if i != succedeedMiner:
                self.stop_mining_queues[i].put(True)
                print("mando q salio todo mal")
                self.stats_queue.put({"miner": i, "failed": True})
            else:
                print("mando que salio todo bien")
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
            outcome_data = self.outcome_queues[miner].get()
            outcome = json.loads(outcome_data)
            if bool(outcome['success']):
                print("lo logro! q capo sos {} {}".format(
                    miner, outcome["hash"]))
                self.last_hash = outcome["hash"]
                self.stopOtherMiners(miner)
            else:
                #save in stats
                print("fallo pobrecito")

    def send(self):
        self.sendBlock(self.block.serialize())
        self.block = self.createBlock()

    def run(self):
        while True:
            try:
                chunk = self.chunks_queue.get(timeout=SECONDS_WAITING_CHUNK)
                self.block.addChunk(chunk)
                if self.block.isFull():
                    print("BLOQUE LLENO")
                    self.send()
                self.chunks_queue.task_done()
            except queue.Empty:
                if not self.block.isEmpty():
                    print("SE CUMPLIO EL TIMEOUT")
                    self.send()

            