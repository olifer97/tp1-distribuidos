import datetime


class Miner:
    def __init__(self):
      # socket to blockchain manager
      # socket from miner manager
      print("Create miner")

    def meetsCondition(self, block):
        difficulty = block.difficulty() - 1
        return True if difficulty == 0 else block.hash() < (2**256) / difficulty

    def mine(self, block):
        timestamp = datetime.datetime.now()
        block.setTimestamp(timestamp)
        while not self.meetsCondition(block):
            block.addNonce()
            block.setTimestamp(datetime.datetime.now())

        # try to save block in blockchain manager
        # send hash to miner manager to notify succes or failure

        return block.hash()
