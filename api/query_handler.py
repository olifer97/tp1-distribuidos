import threading
import queue
import datetime
from miner import Miner
from block import Block
from utils_sock import *
import json
import random
import logging
import os

STATS_FILE = "stats.json"

QUERY_RESPONSE_SIZE = 1024

class QueryHandler(threading.Thread):
    def __init__(self, n_miners, query_queue, stats_queue, response_queue, writer_address, reader_address):
        threading.Thread.__init__(self)
        self.query_queue = query_queue
        self.response_queue = response_queue
        self.reader_address = reader_address
        self.miner_stats = self.initializeStats(n_miners)
        self.stats_queue = stats_queue
        self.hearing_stats = threading.Thread(target=self.hearStats)
        self.hearing_stats.start()

    def initializeStats(self, n_miners):
        if not os.path.exists(STATS_FILE):
            stats = {}
            for i in range(n_miners):
                stats[i] = { "success": 0, "failed": 0 }
            return stats
        with open(STATS_FILE) as f:
            data = json.load(f)

    def writeStats(self):
        with open(STATS_FILE, 'w') as f:
          json.dump(self.miner_stats, f)
        

    def hearStats(self):
        logging.info("empiezo a escuchar las stats")
        while True:
            stats_data = self.stats_queue.get()
            logging.info("estaria recibiendo stats {}".format(stats_data))
            if 'success' in stats_data:
                self.miner_stats[stats_data["miner"]] = self.miner_stats.get(stats_data["miner"], { 'success': 0})
                self.miner_stats[stats_data["miner"]]['success'] += 1
            elif 'failed' in stats_data:
                self.miner_stats[stats_data["miner"]] = self.miner_stats.get(stats_data["miner"], { 'failed': 0})
                self.miner_stats[stats_data["miner"]]['failed'] += 1
            self.writeStats()

    def queryBlockchain(self, query_info): # TODO agregar mas threads
        
        self.sock = connect_send(json.dumps(query_info), self.reader_address)
        response = recv_and_cut(self.sock, QUERY_RESPONSE_SIZE)
        close(self.sock)

        return response

    def doRequest(self, request_info):
        # parse request and send to wrter o reader
        logging.info("la request fue {}".format(request_info))
        query = request_info['type']
        if query == 'st':
            return self.miner_stats
        else:
            return self.queryBlockchain(request_info)

    def run(self):
        logging.info("empiezo a escuchar las requests")
        while True:
            request = self.query_queue.get()
            self.query_queue.task_done()
            logging.info("la request es {}".format(request))
            response = self.doRequest(request["query"])
            logging.info("response es {}".format(response))
            self.response_queue.put({"socket": request["socket"], "info":response})
            self.response_queue.join()

            