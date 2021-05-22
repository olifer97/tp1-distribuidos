import logging
import sys
import os
import signal
import threading

from writer_manager import WriterManager
from reader_manager import ReaderManager

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
        config_params["reader_port"] = int(os.environ["READER_PORT"])
        config_params["writer_port"] = int(os.environ["WRITER_PORT"])
        config_params['blockchain_host'] = os.environ["BLOCKCHAIN_IP"]
        config_params["n_readers"] = int(os.environ["N_READERS"])
    except KeyError as e:
        raise KeyError(
            "Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError(
            "Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params

def main():
    try:
        stop_event = threading.Event() # used to signal termination to the threads
        config = parse_config_params()
        writer = WriterManager(config['blockchain_host'], config['writer_port'], stop_event)
        writer.start()

        readers = ReaderManager(config['blockchain_host'], config['reader_port'], config['n_readers'], stop_event)
        readers.start() 
        writer.join()
        readers.join()
    except SystemExit:
        stop_event.set()



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()