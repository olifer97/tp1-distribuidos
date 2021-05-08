
#import socket
import sys
import os
from writer import Writer

# TODO: Check errors
HOST = os.environ["WRITER_IP"]
PORT = int(os.environ["WRITER_PORT"])
#LISTEN_CONNECTIONS = int(os.environ["SERVER_LISTEN_CONNECTIONS"])

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#rint('[SERVER] Socket created')


def main():
    writer = Writer(HOST, PORT)

    writer.start()
    writer.join()


if __name__ == "__main__":
    main()