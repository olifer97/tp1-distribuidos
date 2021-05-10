import threading
import queue
import datetime
from miner import Miner
from block import Block
import json
import random
import logging

DIFFICULTY_MINED_BLOCKS = 256
SECONDS_WAITING_CHUNK = 30

class QueryHandler(threading.Thread):
    def __init__(self, query_queue, stats_queue, response_queue, writer_address, reader_address):
        threading.Thread.__init__(self)
        self.query_queue = query_queue
        self.response_queue = response_queue
        self.writer_address = writer_address
        self.reader_address = reader_address
        self.miner_stats = {}
        self.stats_queue = stats_queue
        self.hearing_stats = threading.Thread(target=self.hearStats)
        logging.info("ME ESTOY CREANDO SOY EL QUERY HANDLERRRR")

        self.hearing_stats.start()

    def hearStats(self):
        logging.info("empiezo a escuchar las stats")
        while True:
            stats_data = self.stats_queue.get()
            logging.info("estaria recibiendo stats {}".format(stats_data))
            if 'success' in stats_data:
                self.miner_stats[stats_data["miner"]] = self.miner_stats.get(stats_data["miner"], { 'success': 0})
                self.miner_stats[stats_data["miner"]]['success'] += 1
            elif stats_data["failed"]:
                self.miner_stats[stats_data["miner"]] = self.miner_stats.get(stats_data["miner"], { 'failed': 0})
                self.miner_stats[stats_data["miner"]]['failed'] += 1

    def doRequest(self, request):
        # parse request and send to wrter o reader
        logging.info("la request fue {}".format(request))
        return self.miner_stats

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

            