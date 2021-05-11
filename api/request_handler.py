import socket
import logging
import time
import json
import threading
import datetime
import queue
from utils_sock import *
from constants import *

QUERY_SIZE = 1024
OP_SIZE = 2

class RequestHandler:
    def __init__(self, port, listen_backlog, chunks_queue, query_queue, response_queue, n_workers):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.chunks_queue = chunks_queue
        self.query_queue = query_queue
        self.response_thread = threading.Thread(target=self.hearResponses)
        self.response_queue = response_queue

        self.response_thread.start()

        self.workers = [threading.Thread(target=self.hearConnections) for i in range(n_workers)]

    
    def hearResponses(self):
        while True:
            response = self.response_queue.get()
            response['socket'].send(str.encode(json.dumps(response['info']), 'utf-8'))
            response['socket'].close()
            self.response_queue.task_done()
            


    def hearConnections(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
        while True:
            client_sock = self.__accept_new_connection()
            self.__handle_client_connection(client_sock)

    def run(self):
        for worker in self.workers:
            worker.start()


    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg = recv_and_cut(client_sock, OP_SIZE, decode=False)
            logging.info('Request received from connection. Operation: {}'.format(msg))
            
            response = ""
            if msg == b"CH": #send chunk
                chunk = recv_and_cut(client_sock, CHUNK_SIZE)
                logging.info('Received chunk --> {}'.format(chunk))
                self.chunks_queue.put(chunk, block=False)
                client_sock.send("{'response': 'Chunk will be proccesed'}".encode('utf-8'))
                client_sock.close()
            elif msg == b"ST": #request stats
                self.query_queue.put({"socket": client_sock, "query": {"type": "st"}})
                logging.info('Query Stats')
            elif msg == b"GH": #request block by hash
                hash = int(recv_and_cut(client_sock, QUERY_SIZE))
                self.query_queue.put({"socket": client_sock, "query": {"type": "gh", "hash": hash}})
                logging.info('Query Block by hash: {}'.format(hash))
            elif msg == b"GM": #request blocks in a minute
                string_timestamp = recv_and_cut(client_sock, QUERY_SIZE)
                timestamp = datetime.datetime.strptime(string_timestamp, TIMESTAMP_FORMAT)
                self.query_queue.put({"socket": client_sock, "query": {"type": "gm", "timestamp": string_timestamp}})
                logging.info('Request for blocks in minute: {}'.format(string_timestamp))
            else:
                logging.info("Unknown operation")
                client_sock.send("{'response': 'Unknown operation'}".encode('utf-8'))
                client_sock.close()
        except queue.Full:
            logging.info("Queue full")
            client_sock.send("{'response': 'System overload try sending chunk later'}".encode('utf-8'))
            client_sock.close()
        except:
            logging.info("Error with request")
            client_sock.send("{'response': 'Error processing request'}".encode('utf-8'))
            client_sock.close()




    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info("Proceed to accept new connections")
        c, addr = self._server_socket.accept()
        logging.info('Got connection from {}'.format(addr))
        return c