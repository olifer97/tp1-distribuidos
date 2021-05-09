import datetime
import threading
import time
import json
import socket
import os

from utils_sock import *
from block import Block
from constants import *


class Writer(threading.Thread):
    def __init__(self, queue_blocks):
      threading.Thread.__init__(self)
      self.queue_blocks = queue_blocks

    def saveBlock(self, block_data):
      timestamp = datetime.datetime.strptime(block_data['info']['header']['timestamp'], TIMESTAMP_FORMAT).replace(minute= 0, second=0, microsecond=0)
      timestamp_without_seconds = timestamp.strftime(TIMESTAMP_FORMAT)

      filename = "{}.json".format(timestamp.strftime(TIMESTAMP_FORMAT))
      entry = { "timestamp": block_data['info']['header']['timestamp'], "hash": block_data['hash']}
      if not os.path.exists(filename):
        with open(filename, 'w') as f:
          json.dump({"entries": [entry]}, f)
      else:
        with open(filename, "r+") as index:
          data = json.load(index)
          data["entries"].append(entry)
          index.seek(0)
          json.dump(data, index)
          
        

      with open('{}.json'.format(block_data['hash']), 'w') as f:
          json.dump(block_data['info'], f)

    def run(self):
      while True:
        block_data = self.queue_blocks.get()
        self.saveBlock(block_data)
