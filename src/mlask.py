import os
import socket
import log
import gc
from array import array

def _parse_url_args(args_raw):
    args_dict = {}
    if args_raw:
        for assignment in args_raw.split('&'):
            key, value = assignment.split('=', 1)
            args_dict[key] = value
    return args_dict

class HttpRequest:
    
    @classmethod
    def new(cls, conn):
        self = cls()
        http_start_line = conn.readline().decode().strip()
        http_method, url, _http_version = http_start_line.split(' ', 2)
        self.method = http_method
        self.path, *args = url.split('?', 1)
        if args:
            self._args_raw = args[0]
        else:
            self._args_raw = ''
            
        self.headers = {}
        
        while True:
            line = conn.readline().decode().strip()
            if not line:
                break
            key, value = line.split(':', 1)
            self.headers[key.strip()] = value.strip()

        try:
            body_len = int(self.headers['Content-Length'])
            if body_len:
                self.body = conn.recv(body_len).decode().strip()
            else:
                self.body = None    
        except KeyError:
            self.body = None
            
        return self
    
    def get_url_args(self):
        return _parse_url_args(self._args_raw)
    
    def get_form_args(self):
        if self.body is None:
            return {}
        else:
            return _parse_url_args(self.body)            

    @property
    def path_normalized(self):
        path = self.path.rstrip('/')
        return path if path else '/'


class LocalFile:
    def __init__(self, path):
        self.path = path
        
    def __len__(self):
        return os.stat(self.path)[6]

def _isiterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    return True

def _sendall_safe(conn, data):
    try:
        conn.sendall(data)
    except:
        return True
    return False
        
class HttpResponse:

    def __init__(self, status=200, reason='OK', headers=None, body=None, content_type=None, length=None):
        self.status = status
        self.reason = reason
        self.body = body # str or LocalFile
        self.headers = headers if headers else {}
        self.content_type = content_type
        self.length = length

    def send(self, conn):
        if self.length is None:
            body_len = len(self.body) if self.body else 0
        else:
            body_len = self.length 
        conn.send(f'HTTP/1.1 {self.status} {self.reason}\n')
        if self.content_type:
            conn.send(f'Content-Type: {self.content_type}\n')
        conn.send('Connection: close\n')
        conn.send(f'Content-Length: {body_len}\n')
        
        for key, value in self.headers.items():
            conn.send(f'{key}: {value}\n')
        
        conn.send('\n')
        if isinstance(self.body, str):
            _sendall_safe(conn, self.body)
        elif _isiterable(self.body):
            for chunk in self.body:
                if _sendall_safe(conn, chunk):
                    break
        elif isinstance(self.body, LocalFile):
            with open(self.body.path) as fh:
                while True:
                    chunk = fh.read(1024)
                    if not chunk:
                        break
                    if _sendall_safe(conn, chunk):
                        break
                    del chunk

    @classmethod
    def from_file(cls, path, content_type='text/html'):
        return cls(body=LocalFile(path), content_type=content_type)

    @classmethod
    def from_iterable(cls, obj, length, content_type='text/html'):
        return cls(body=obj, content_type=content_type, length=length)

    @classmethod
    def redirect(cls, url):
        return cls(status=302, reason='Found', headers={'Location': url})

class Mlask:
 
    def __init__(self):
        self._routes = {}
 
    def add_route(self, method, path, callback):
        self._routes[(method, path)] = callback
        
    def route_get(self, path):
        def wrapper(callback):
            self.add_route('GET', path, callback)
            return callback
        return wrapper
    
    def route_post(self, path):
        def wrapper(callback):
            self.add_route('POST', path, callback)
            return callback
        return wrapper
    
    def route_put(self, path):
        def wrapper(callback):
            self.add_route('PUT', path, callback)
            return callback
        return wrapper
    
    def route_delete(self, path):
        def wrapper(callback):
            self.add_route('DELETE', path, callback)
            return callback
        return wrapper

    def _process_req(self, req):
        try:
            callback = self._routes[(req.method, req.path_normalized)]
        except KeyError:
            return HttpResponse(status=404, reason='Not Found')
        
        try:
            retval = callback(req)
        except Exception as exc:
            msg = str(exc)
            log.info(f'Error: {msg}')
            return HttpResponse(status=500, reason=msg)

        if isinstance(retval, str):
            return HttpResponse(body=retval, content_type="text/plain")
        elif isinstance(retval, int):
            return HttpResponse(status=retval, reason="")
        elif isinstance(retval, HttpResponse):
            return retval

        if retval:
            raise RuntimeError('Missing response')
        else:
            raise RuntimeError('Invalid response')        

    def run(self, host='', port=80):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(True)
        sock.bind((host, port))
        sock.listen(5)

        while True:
            log.info('Waiting for connection...')
            conn, addr = sock.accept()
            
            log.info(f'Connection from {addr}')
            try:
                req = HttpRequest.new(conn)
            except Exception as exc:
                log.info(f'Error: {exc}')

            log.info(f'{req.method} {req.path}')
            #log.info(req.headers)
            #log.info(req.body)
            #log.info(req.get_url_args())
            #log.info(req.get_form_args())

            resp = self._process_req(req)
            resp.send(conn)
            conn.close()
