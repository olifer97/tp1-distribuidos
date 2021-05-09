import socket
import logging

CHUNK_SIZE = 65536

class RequestHandler:
    def __init__(self, port, listen_backlog, chunks_queue):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.chunks_queue = chunks_queue

    def run(self):
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


    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg = client_sock.recv(2).rstrip()
            logging.info(
                'Request received from connection {}. Operation: {}'
                    .format(client_sock.getpeername(), msg))
            
            response = ""
            if msg == b"CH": #send chunk
                chunk = client_sock.recv(CHUNK_SIZE).rstrip().decode()
                logging.info('Received chunk --> {}'.format(chunk))
                self.chunks_queue.put(chunk)
                self.chunks_queue.join()
                response = "Se estaria guardando tu bloque"
            elif msg == b"ST": #request stats
                logging.info('Asking stats to Mining Logic!')
                response = "Miners: 3\nSuccesful: 1"
            elif msg == b"GH": #request block by hash
                logging.info('Asking for hash block!')
                response = "\{ hash:asd123 \}"
            elif msg == b"GM": #request blocks in a minute
                logging.info('Asking for hashes in minute!')
                response = "asd123,qwe345"
            else:
                logging.info('Unknown operation')
                response = "Invalid operation"

            client_sock.send("{}\n".format(response).encode('utf-8'))
        except OSError:
            logging.info("Error while reading socket {}".format(client_sock))
        finally:
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