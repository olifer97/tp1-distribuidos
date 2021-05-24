import threading
import sys
import getopt
import queue

from common.constants import *
from client_utils import *

OPTIONS = 'client.py [--clients <number>] [--size <number>] [--requests <number>]'

stop_threads = False

class Client(threading.Thread):
    def __init__(self, address, request_queue):
      threading.Thread.__init__(self)
      self.address = address
      self.request_queue = request_queue

    def run(self):
      global stop_threads
      while True:
        try:
          request = self.request_queue.get()
          self.request_queue.task_done()
          print(send_and_recv(request, self.address))
          if stop_threads:
            break
        except queue.Empty:
          if stop_threads:
            break

def main(argv):
  config = parse_config_params()
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

  clients_threads = [Client((config['host'], config['port']), requests_queue) for i in range(int(clients))]
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
