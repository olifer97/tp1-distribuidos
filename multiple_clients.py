import threading
import json
import socket
import sys
import getopt
import queue

from common.utils import *
from common.constants import *

BLOCKCHAIN_ADDRESS = ('127.0.0.1', 5000)
RESPONSE_SIZE = 1024

OPTIONS = 'client.py [--clients <number>] [--size <number>] [--requests <number>]'

stop_threads = False


def send_and_recv(request, address):
    sock = connect_send(json.dumps(request), address)
    return recv_and_cut(sock, RESPONSE_SIZE)


class Client(threading.Thread):
    def __init__(self, address, request_queue):
      threading.Thread.__init__(self)
      self.address = address
      self.request_queue = request_queue

    def run(self):
      while True:
        request = self.request_queue.get()
        self.request_queue.task_done()
        print(send_and_recv(request, self.address))
        global stop_threads
        if stop_threads:
            break
        # close(sock)



def main(argv):
  requests_queue = queue.Queue()
  try:
    opts, args = getopt.getopt(argv,"hc:r:s:")
  except getopt.GetoptError:
    print(OPTIONS)
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print(OPTIONS)
      sys.exit()
    elif opt in ("-c", "--clients"):
      clients = arg
    elif opt in ("-r", "--requests"):
      requests = arg
    elif opt in ("-s", "--chunk_size"):
      chunk_size = arg

  clients_threads = [Client(BLOCKCHAIN_ADDRESS, requests_queue) for i in range(int(clients))]
  for client in clients_threads:
      client.start()

  for i in range(int(requests)):
      chunk = str(i) * int(chunk_size)
      request = {"type": 'POST_CHUNK', "parameter": chunk}
      requests_queue.put(request)

  requests_queue.join()

  global stop_threads
  stop_threads = True
  for client in clients_threads:
      client.join()
  print("Finished")
  sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
