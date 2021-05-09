#!/usr/bin/env python3
import datetime
from miners_handler import MinersHandler
from request_handler import RequestHandler
import queue

import logging

import sys
import os

N_MINERS = int(os.environ["N_MINERS"])
WRITER_HOST = os.environ["WRITER_IP"]
WRITER_PORT = int(os.environ["WRITER_PORT"])

API_PORT = int(os.environ["API_PORT"])

def main():

    chunks_queue = queue.Queue()

    miners_handler = MinersHandler(N_MINERS, chunks_queue, (WRITER_HOST, WRITER_PORT))
    miners_handler.start()

    request_handler = RequestHandler(API_PORT, 1, chunks_queue)
    request_handler.run()

if __name__ == "__main__":
    logging.basicConfig(
		format='%(asctime)s %(levelname)-8s %(message)s',
		level=logging.INFO,
		datefmt='%Y-%m-%d %H:%M:%S',
	)
    main()