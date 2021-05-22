import datetime
import threading
import time
import json
import socket
import os
import logging
import queue

from block import Block
from constants import *
from filelock import FileLock


class Writer(threading.Thread):
    def __init__(self, queue_blocks, stop_event):
      threading.Thread.__init__(self)
      self.queue_blocks = queue_blocks
      self.stop_event = stop_event

    def _save_block(self, block_data):
      timestamp = datetime.datetime.strptime(block_data['info']['header']['timestamp'], TIMESTAMP_FORMAT).replace(minute= 0, second=0, microsecond=0)
      timestamp_without_seconds = timestamp.strftime(TIMESTAMP_FORMAT)

      filename = "{}.json".format(timestamp.strftime(TIMESTAMP_FORMAT))
      entry = { "timestamp": block_data['info']['header']['timestamp'], "hash": block_data['hash']}
      if not os.path.exists(filename):
        filelock = FileLock()
        f = filelock.acquire_writeonly(filename)
        json.dump({"entries": [entry]}, f)
        filelock.release(f)
      else:
        filelock = FileLock()
        f = filelock.acquire_writeonly(filename, type='r+')
        data = json.load(f)
        data["entries"].append(entry)
        f.seek(0)
        json.dump(data, f)
        filelock.release(f) 
        

      with open('{}.json'.format(block_data['hash']), 'w') as f:
          json.dump(block_data['info'], f)

    def run(self):
      logging.info("[WRITER] Starts")
      while not self.stop_event.is_set():
        try:
            block_data = self.queue_blocks.get(timeout=TIMEOUT_WAITING_MESSAGE)
            self.queue_blocks.task_done()
            self._save_block(block_data)
        except queue.Empty:
            if self.stop_event.is_set():
                logging.info("[WRITER] Finished")
                break
