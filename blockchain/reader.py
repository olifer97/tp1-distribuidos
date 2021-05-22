import datetime
import threading
import time
import json
import os

from block import Block
from constants import *
from filelock import FileLock

class Reader(threading.Thread):
    def __init__(self, request_queue, response_queue):
      threading.Thread.__init__(self)
      self.request_queue = request_queue
      self.response_queue = response_queue

    
    def getBlock(self, hash):
        filename = "{}.json".format(hash)
        if not os.path.exists(filename): 
            return {"response": "Block not found"}
        filelock = FileLock()
        f = filelock.acquire_readonly(filename)
        block = json.load(f)
        filelock.release(f)
        return block

    def getBlocksInMinute(self, min_timestamp):
        response = []
        timestamp_only_hour = min_timestamp.replace(minute= 0, second=0, microsecond=0).strftime(TIMESTAMP_FORMAT)
        filename = "{}.json".format(timestamp_only_hour)

        if not os.path.exists(filename): 
            return response

        max_timetamp = min_timestamp + datetime.timedelta(minutes=1)

        filelock = FileLock()
        f = filelock.acquire_readonly(filename)
        data = json.load(f)
        filelock.release(f)
        for entry in data["entries"]:
                timestamp = datetime.datetime.strptime(entry['timestamp'], TIMESTAMP_FORMAT)
                if timestamp >= min_timestamp and timestamp <= max_timetamp:
                    block_hash = entry['hash']
                    response.append(self.getBlock(block_hash))
        return response

    def run(self):
      while True:
        request = self.request_queue.get()

        if request['request']['type'] == 'gh':
            block = self.getBlock(request['request']['hash'])
            self.response_queue.put({'socket': request['socket'] , 'response': block})

        if request['request']['type'] == 'gm':
            timestamp = datetime.datetime.strptime(request['request']['timestamp'], TIMESTAMP_FORMAT)
            blocks = self.getBlocksInMinute(timestamp)
            self.response_queue.put({'socket': request['socket'], 'response': blocks})
        
        
