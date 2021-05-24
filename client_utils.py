import os
import json 
from common.custom_socket.client_socket import ClientSocket

BLOCKCHAIN_ADDRESS = ('127.0.0.1', 5000)

def send_and_recv(request, address):
    sock = ClientSocket(address = address)
    try:
      sock.send_with_size(json.dumps(request))
      response = sock.recv_with_size()
    except Exception as e:
      print(e)
      response = "Socket close"
    sock.close()
    return response 

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