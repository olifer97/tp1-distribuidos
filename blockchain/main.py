
#import socket
import sys
import os
from writer_manager import WriterManager
from reader_manager import ReaderManager

# TODO: Check errors
HOST = os.environ["BLOCKCHAIN_IP"]
WRITER_PORT = int(os.environ["WRITER_PORT"])
READER_PORT = int(os.environ["READER_PORT"])
#LISTEN_CONNECTIONS = int(os.environ["SERVER_LISTEN_CONNECTIONS"])

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#rint('[SERVER] Socket created')


def main():
    writer = WriterManager(HOST, WRITER_PORT)
    writer.start()

    readers = ReaderManager(HOST, READER_PORT)
    readers.start()


if __name__ == "__main__":
    main()