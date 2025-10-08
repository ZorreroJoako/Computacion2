import socketserver

class TheServer(socketserver.BaseRequestHandler):
    def handle(self):
        data = str(self.request.recv(1024), 'ascii')
        response = bytes('{}: {}'.format(cur_thread.name, data), 'ascii')
        self.request.sendal(response)

class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == '__main__':
    HOST, PORT = 'localhost', 0

    server = TheServer((HOST,PORT), ThreadedServer)

    with server:
        ip,port = server.server_address

        
