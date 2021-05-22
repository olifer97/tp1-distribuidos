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
    def __init__(self, port, listen_backlog, chunks_queue, query_queue, response_queue, n_workers, stop_event):
        self.stop_event = stop_event
        self.socket = ServerSocket('', port, listen_backlog)
        self.chunks_queue = chunks_queue
        self.query_queue = query_queue
        self.response_thread = threading.Thread(target=self._hear_responses)
        self.response_queue = response_queue

        self.response_thread.start()
        self.requests_queue = queue.Queue()

        self.workers = [threading.Thread(target=self._hear_client_requests, args=(self.requests_queue,)) for i in range(n_workers)]
    
    def _send_and_close(self, socket, response):
        socket.send_with_size(json.dumps(response))
        socket.close()
    
    def _hear_responses(self):
        while not self.stop_event.is_set():
            try:
                response = self.response_queue.get(timeout=TIMEOUT_WAITING_MESSAGE)
                self.response_queue.task_done()
                self._send_and_close(response['socket'], response['info'])
            except queue.Empty:
                if self.stop_event.is_set():
                    break
        

    def _hear_client_requests(self, requests_queue):
        logging.info("[WORKER] Starts")
        while not self.stop_event.is_set():
            try:
                client_sock = self.requests_queue.get(timeout=TIMEOUT_WAITING_MESSAGE)
                self.requests_queue.task_done()
                self._handle_client_connection(client_sock)
            except queue.Empty:
                if self.stop_event.is_set():
                    logging.info("[WORKER] Finishes")
                    break

    def run(self):
        try:
            for worker in self.workers:
                worker.start()

            logging.info("[REQUEST HANDLER] Starts")
            while not self.stop_event.is_set():
                client_sock = self.socket.accept()
                if client_sock == None:
                    continue
                self.requests_queue.put(client_sock)
        except SystemExit:
            self.requests_queue.join()
            self.stop_event.set()

    def _handle_client_connection(self, client_sock):
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
                self._send_and_close(client_sock, msg)
            elif op == GET_STATS: #request stats
                self.query_queue.put({"socket": client_sock, "query": {"type": "st"}})
                logging.info('Query Stats')
            elif op == GET_BLOCK: #request block by hash
                hash = req['parameter']
                if not hash.isdigit():
                    msg = {'response': 'Hash must be all digits'}
                    self._send_and_close(client_sock, msg)
                else:
                    self.query_queue.put({"socket": client_sock, "query": {"type": "gh", "hash": hash}})
                logging.info('Query Block by hash: {}'.format(hash))
            elif op == GET_BLOCKS: #request blocks in a minute
                string_timestamp = req['parameter']
                try:
                    datetime.datetime.strptime(string_timestamp, TIMESTAMP_FORMAT)
                    self.query_queue.put({"socket": client_sock, "query": {"type": "gm", "timestamp": string_timestamp}})
                except:
                    msg = {'response': 'Timestamp format incorrect. Expecting: {}'.format(TIMESTAMP_FORMAT)}
                    self._send_and_close(client_sock, msg)
                logging.info('Request for blocks in minute: {}'.format(string_timestamp))
            else:
                logging.info("Unknown operation")
                msg = {'response': 'Unknown operation: {}'.format(op)}
                self._send_and_close(client_sock, msg)
        except queue.Full:
            logging.info("Queue full")
            msg = {'response': 'System overload try sending chunk later'}
            self._send_and_close(client_sock, msg)
        except Exception as e:
            logging.info("Error with request")
            logging.info(e)
            msg = {'response': 'Error with request'}
            self._send_and_close(client_sock, msg)