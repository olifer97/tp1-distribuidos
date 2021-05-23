import threading
import json
import os
import sys
import getopt
import queue

from common.constants import *
from common.custom_socket.client_socket import ClientSocket

BLOCKCHAIN_ADDRESS = ('127.0.0.1', 5000)

OPTIONS = 'client.py [--clients <number>] [--size <number>] [--requests <number>]'

stop_threads = False

def send_and_recv(request, address):
    sock = ClientSocket(address = address)
    try:
      sock.send_with_size(json.dumps(request))
      response = sock.recv_with_size()
    except:
      response = "Socket close"
    sock.close()
    return response 


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
