#!/usr/bin/env python3
import datetime
from miners_handler import MinersHandler
from request_handler import RequestHandler
from query_handler import QueryHandler
import queue

import logging

import sys
import os
import signal
import threading

def handle_exit(sig, frame):
    raise(SystemExit)

signal.signal(signal.SIGTERM, handle_exit)


def parse_config_params():
    """ Parse env variables to find program config params

    Function that search and parse program configuration parameters in the
    program environment variables. If at least one of the config parameters
    is not found a KeyError exception is thrown. If a parameter could not
    be parsed, a ValueError is thrown. If parsing succeeded, the function
    returns a map with the env variables
    """
    config_params = {}
    try:
        config_params["api_port"] = int(os.environ["API_PORT"])
        config_params["reader_port"] = int(os.environ["READER_PORT"])
        config_params["writer_port"] = int(os.environ["WRITER_PORT"])
        config_params["listen_backlog"] = int(os.environ["API_LISTENERS"])
        config_params["n_workers"] = int(os.environ["N_WORKERS"])
        config_params["n_miners"] = int(os.environ["N_MINERS"])
        config_params["threshold"] = int(os.environ["CHUNKS_THRESHHOLD"])
        config_params['blockchain_host'] = os.environ["BLOCKCHAIN_IP"]
    except KeyError as e:
        raise KeyError(
            "Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError(
            "Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params


def main():
    config = parse_config_params()

    chunks_queue = queue.Queue(maxsize=config['threshold'])
    query_queue = queue.Queue()
    stats_queue = queue.Queue()
    response_queue = queue.Queue()
    stop_event = threading.Event()

    miners_handler = MinersHandler(config['n_miners'], chunks_queue, stats_queue, (
        config['blockchain_host'], config['writer_port']), stop_event)
    miners_handler.start()

    query_handler = QueryHandler(config['n_miners'], query_queue, stats_queue, response_queue, (
        config['blockchain_host'], config['writer_port']), (config['blockchain_host'], config['reader_port']), stop_event)
    query_handler.start()

    request_handler = RequestHandler(
        config['api_port'], config['listen_backlog'], chunks_queue, query_queue, response_queue, config['n_workers'], stop_event)
    request_handler.run()
    miners_handler.join()
    query_handler.join()



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()
