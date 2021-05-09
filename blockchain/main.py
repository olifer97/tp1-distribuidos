
#import socket
import sys
import os
from blockchain import Blockchain

# TODO: Check errors
HOST = os.environ["WRITER_IP"]
PORT = int(os.environ["WRITER_PORT"])
#LISTEN_CONNECTIONS = int(os.environ["SERVER_LISTEN_CONNECTIONS"])

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#rint('[SERVER] Socket created')


def main():
    blockchain = Blockchain(HOST, PORT)

    blockchain.run()


if __name__ == "__main__":
    main()