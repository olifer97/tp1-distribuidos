import sys
import getopt

from common.constants import *
from client_utils import *

OPTIONS = 'client.py [--chunk <chunk>] [--block <hash>] [--timestamp <timestamp>] [--stats]'


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
