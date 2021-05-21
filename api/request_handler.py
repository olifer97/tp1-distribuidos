import socket
import logging
import json
import threading
import datetime
import queue
from constants import *
from custom_socket.server_socket import ServerSocket

'''
Request format

{"type": "POTS_CHUNK/GET_STATS/GET_BLOCK/GET_BLOCKS", "parameter": if necessary }

POTS_CHUNK -> Save chunk in blockchain. Parameter: chunk

GET_STATS -> Get miners stats. Parameter: -

GET_BLOCK -> Get bloch by hash. Parameter: hash

GET_BLOCKS -> Get blocks in a minute interval. Parameter: timestamp in "%m-%d-%Y, %H:%M:%S" format

'''

class RequestHandler:
    def __init__(self, port, listen_backlog, chunks_queue, query_queue, response_queue, n_workers):

        self.socket = ServerSocket('', port, listen_backlog)
        self.chunks_queue = chunks_queue
        self.query_queue = query_queue
        self.response_thread = threading.Thread(target=self.hearResponses)
        self.response_queue = response_queue

        self.response_thread.start()
        self.requests_queue = queue.Queue()

        self.workers = [threading.Thread(target=self.hearClientRequests, args=(self.requests_queue,)) for i in range(n_workers)]
    
    def hearResponses(self):
        while True:
            response = self.response_queue.get()
            response['socket'].send_with_size(json.dumps(response['info']))
            response['socket'].close()
        

    def hearClientRequests(self, requests_queue):
        while True:
            client_sock = self.requests_queue.get()
            self.__handle_client_connection(client_sock)

    def run(self):
        for worker in self.workers:
            worker.start()

        while True:
            client_sock = self.socket.accept()
            self.requests_queue.put(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            req = client_sock.recv_with_size()
            logging.info('Request received from connection: {}'.format(req))

            op = req['type']
            
            if op == POST_CHUNK: #send chunk
                chunk = req['parameter']
                logging.info('Received chunk: {}'.format(chunk))
                self.chunks_queue.put(chunk, block=False)
                msg = {'response': 'Chunk {} will be proccesed'.format(chunk)}
                client_sock.send_with_size(json.dumps(msg))
                client_sock.close()
            elif op == GET_STATS: #request stats
                self.query_queue.put({"socket": client_sock, "query": {"type": "st"}})
                logging.info('Query Stats')
            elif op == GET_BLOCK: #request block by hash
                hash = req['parameter']
                self.query_queue.put({"socket": client_sock, "query": {"type": "gh", "hash": hash}})
                logging.info('Query Block by hash: {}'.format(hash))
            elif op == GET_BLOCKS: #request blocks in a minute
                string_timestamp = req['parameter']
                timestamp = datetime.datetime.strptime(string_timestamp, TIMESTAMP_FORMAT)
                self.query_queue.put({"socket": client_sock, "query": {"type": "gm", "timestamp": string_timestamp}})
                logging.info('Request for blocks in minute: {}'.format(string_timestamp))
            else:
                logging.info("Unknown operation")
                msg = {'response': 'Unknown operation: {}'.format(op)}
                client_sock.send_with_size(json.dumps(msg))
                client_sock.close()
        except queue.Full:
            logging.info("Queue full")
            msg = {'response': 'System overload try sending chunk later'}
            client_sock.send_with_size(json.dumps(msg))
            client_sock.close()
        except Exception as e:
            logging.info("Error with request")
            logging.info(e)
            msg = {'response': 'System overload try sending chunk later'}
            client_sock.send_with_size(json.dumps(msg))
            client_sock.close()