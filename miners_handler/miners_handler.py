import threading, queue
import datetime
from miner import Miner
from block import Block
import json
import asyncio

DIFFICULTY_MINED_BLOCKS = 256

class MinersHandler:
    def __init__(self, n_miners, writer_address):
      self.blocks_queues = [queue.Queue() for i in range(n_miners)]
      self.stop_mining_queues = [queue.Queue() for i in range(n_miners)]
      self.outcome_queues = [queue.Queue() for i in range(n_miners)]
      self.n_miners = n_miners
      self.miners = [Miner(self.blocks_queues[i], self.stop_mining_queues[i], self.outcome_queues[i], writer_address) for i in range(n_miners)]
      self.hearing_miners = [threading.Thread(target=self.hearOutcomeFromMiner, args=(i,)) for i in range(n_miners)]
      self.last_hash = None
      self.difficulty = 1
      self.proccesedBlocks = 0
      self.startTime = datetime.datetime.now()
      self.start()

    def checkProccesedBlock(self):
        self.proccesedBlocks +=1
        if self.proccesedBlocks >= DIFFICULTY_MINED_BLOCKS:
            elapsedTime = (datetime.datetime.now() - self.startTime).total_seconds()
            self.difficulty *= (12/(elapsedTime/DIFFICULTY_MINED_BLOCKS))
            self.proccesedBlocks = 0
            self.startTime = datetime.datetime.now()
            

    def send(self, chunks):
         
        self.checkProccesedBlock()
        print("voy a mandar {}".format(chunks))
        print("el lasthash es {}".format(self.last_hash))
        block = Block(self.last_hash, self.difficulty, chunks)
        block.setTimestamp(datetime.datetime.now())

        self.sendBlock(block.serialize())

    def sendBlock(self, block):
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

    def start(self):
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
                print("lo logro! q capo sos {}".format(outcome["hash"]))
                self.last_hash = outcome["hash"]
                self.stopOtherMiners(miner)
            else:
                #save in stats
                print("fallo pobrecito")
        
        

