#!/usr/bin/env python3
import datetime
from miners_handler import MinersHandler

#import socket
import sys
import os

# TODO: Check errors
#HOST = os.environ["SERVER_IP"]
#PORT = int(os.environ["SERVER_PORT"])
#LISTEN_CONNECTIONS = int(os.environ["SERVER_LISTEN_CONNECTIONS"])

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#rint('[SERVER] Socket created')

HOST = os.environ["WRITER_IP"]
PORT = int(os.environ["WRITER_PORT"])


def main():
    handler = MinersHandler(2, (HOST, PORT))

    for i in range(5):
        chunks = ["hola", "como", "estas", i]

        handler.send(chunks)
        
        #handler.join()



if __name__ == "__main__":
    main()