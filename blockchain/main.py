
#import socket
import sys
import os
from writer_manager import WriterManager
from reader_manager import ReaderManager

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
    except KeyError as e:
        raise KeyError(
            "Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError(
            "Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params

def main():
    config = parse_config_params()
    writer = WriterManager(config['blockchain_host'], config['writer_port'])
    writer.start()

    readers = ReaderManager(config['blockchain_host'], config['reader_port'])
    readers.start()


if __name__ == "__main__":
    main()