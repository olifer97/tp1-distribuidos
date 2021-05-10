#!/usr/bin/env python3
import datetime
from miners_handler import MinersHandler
from request_handler import RequestHandler
from query_handler import QueryHandler
import queue

import logging

import sys
import os

N_MINERS = int(os.environ["N_MINERS"])
BLOCKCHAIN_HOST = os.environ["BLOCKCHAIN_IP"]
WRITER_PORT = int(os.environ["WRITER_PORT"])

READER_PORT = int(os.environ["READER_PORT"])

API_PORT = int(os.environ["API_PORT"])

def main():

    chunks_queue = queue.Queue()
    query_queue = queue.Queue()
    stats_queue = queue.Queue()
    response_queue = queue.Queue()

    miners_handler = MinersHandler(N_MINERS, chunks_queue, stats_queue, (BLOCKCHAIN_HOST, WRITER_PORT))
    miners_handler.start()

    query_handler = QueryHandler(N_MINERS, query_queue, stats_queue, response_queue, (BLOCKCHAIN_HOST, WRITER_PORT), (BLOCKCHAIN_HOST, READER_PORT))
    query_handler.start()

    request_handler = RequestHandler(API_PORT, 1, chunks_queue, query_queue, response_queue)
    request_handler.run()

    

if __name__ == "__main__":
    logging.basicConfig(
		format='%(asctime)s %(levelname)-8s %(message)s',
		level=logging.INFO,
		datefmt='%Y-%m-%d %H:%M:%S',
	)
    main()