import json
import sys
import getopt
import os

from common.constants import *
from common.custom_socket.client_socket import ClientSocket

BLOCKCHAIN_ADDRESS = ('127.0.0.1', 5000)

OPTIONS = 'client.py [--chunk <chunk>] [--block <hash>] [--timestamp <timestamp>] [--stats]'


def send_and_recv(request, address):
   sock = ClientSocket(address=address)
   sock.send_with_size(json.dumps(request))
   response = sock.recv_with_size()
   sock.close()
   return response


def saveChunk(chunk, config):
   request = {"type": POST_CHUNK, "parameter": chunk}
   return send_and_recv(request, (config['host'], config['port']))


def getBlock(hash, config):
   request = {"type": GET_BLOCK, "parameter": hash}
   return send_and_recv(request, (config['host'], config['port']))


def getBlocks(timestamp, config):
   request = {"type": GET_BLOCKS, "parameter": timestamp}
   return send_and_recv(request, (config['host'], config['port']))


def getStats(config):
   request = {"type": GET_STATS}
   return send_and_recv(request, (config['host'], config['port']))


def parse_config_params():
   config_params = {}
   try:
      config_params["host"] = os.environ["HOST"]
   except KeyError as e:
      config_params["host"] = BLOCKCHAIN_ADDRESS[0]

   try:
      config_params["port"] = int(os.environ["PORT"])
   except KeyError as e:
      config_params["port"] = BLOCKCHAIN_ADDRESS[1]
   return config_params

def main(argv):
   config = parse_config_params()
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
         print(saveChunk(arg, config))
         sys.exit()
      elif opt in ("-b", "--block"):
         print(getBlock(arg, config))
         sys.exit()
      elif opt in ("-t", "--timestamp"):
         print(getBlocks(arg, config))
         sys.exit()
      elif opt in ("-s", "--stats"):
         print(getStats(config))
         sys.exit()
    


if __name__ == "__main__":
   main(sys.argv[1:])
