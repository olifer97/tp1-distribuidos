import threading
import json
import socket
import sys, getopt

from common.constants import *
from common.custom_socket.client_socket import ClientSocket

BLOCKCHAIN_ADDRESS = ('127.0.0.1', 5000)
RESPONSE_SIZE = 1024

OPTIONS = 'client.py [--chunk <chunk>] [--block <hash>] [--timestamp <timestamp>] [--stats]'


def send_and_recv(request, address):
    sock = ClientSocket(address = address)
    sock.send_with_size(json.dumps(request))
    response = sock.recv_with_size()
    sock.close()
    return response 


def saveChunk(chunk):
    request = {"type": POST_CHUNK, "parameter": chunk}
    return send_and_recv(request, BLOCKCHAIN_ADDRESS)

def getBlock(hash):
    request = {"type": GET_BLOCK, "parameter": hash}
    return send_and_recv(request, BLOCKCHAIN_ADDRESS)

def getBlocks(timestamp):
    request = {"type": GET_BLOCKS, "parameter": timestamp}
    return send_and_recv(request, BLOCKCHAIN_ADDRESS)

def getStats():
    request = {"type": GET_STATS}
    return send_and_recv(request, BLOCKCHAIN_ADDRESS)


def main(argv):
   try:
      opts, args = getopt.getopt(argv,"hc:b:t:s",["chunk=","block=", "timestamp="])
   except getopt.GetoptError:
      print(OPTIONS)
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print(OPTIONS)
         sys.exit()
      elif opt in ("-c", "--chunk"):
         print(saveChunk(arg))
         sys.exit()
      elif opt in ("-b", "--block"):
         print(getBlock(arg))
         sys.exit()
      elif opt in ("-t", "--timestamp"):
         print(getBlocks(arg))
         sys.exit()
      elif opt in ("-s", "--stats"):
         print(getStats())
         sys.exit()
    


if __name__ == "__main__":
    main(sys.argv[1:])
