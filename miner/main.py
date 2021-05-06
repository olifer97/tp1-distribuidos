#!/usr/bin/env python3

import datetime

from miner import Miner
from block import Block


def main():
    miner = Miner()
    # add direction to other entities
    chunks = ["hola", "como", "estas"]
    block = Block(123, 1, chunks)
    block.setTimestamp(datetime.datetime.now())
    print("Block serialized: {}".format(block.serialize()))

    print("Hash: {}".format(miner.mine(block)))


if __name__ == "__main__":
    main()
