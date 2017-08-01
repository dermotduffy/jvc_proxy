#!/usr/bin/python

import argparse
import logging
import socket
import socketserver
import time

RECV_SIZE = 1024

JVC_GREETING = b"PJ_OK"
JVC_ACK = b"PJACK"
JVC_REQ = b"PJREQ"

def read_n_bytes(sock, length):
  """Read exactly 'length' bytes from socket."""
  buff = b''
  try:
    while len(buff) < length:
      data = sock.recv(min(length - len(buff), RECV_SIZE))
      if data == b'':
        logging.warning("Short-read from: " + str(sock.getpeername()))
        return None 
      buff += data
  except socket.error as e:
    logging.exception("Socket exception whilst reading bytes: " + str(
        sock.getpeername()))
    return None
  return buff

def send_bytes(sock, data):
  """Send all data to socket."""
  try:
    sock.sendall(data)
  except socket.error as e:
    logging.exception("Socket exception whilst sending bytes: " + str(
        sock.getpeername()))
    return None
  return len(data)

def create_connected_JVC_socket(host, port, timeout, retries=0, retry_wait=0):
  """Create a socket connected and handshook to a JVC host."""
  attempt = 0
  while attempt <= retries:
    if attempt > 0:
      logging.info("Retrying in %i second(s)..." % retry_wait)
      time.sleep(retry_wait)
    attempt += 1

    try:
      jvc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      jvc_socket.settimeout(timeout)

      logging.info("Connecting to JVC (%s:%i) ..." % (host, port))
      jvc_socket.connect((host, port))
      logging.info("Connected to JVC (%s:%i), handshaking ..." % (host, port))
    except socket.error as e:
      logging.exception("Socket exception whilst connecting (%s:%i)" % (
          host, port))
      continue

    if read_n_bytes(jvc_socket, len(JVC_GREETING)) != JVC_GREETING:
      logging.warning("JVC protocol greeting was incorrect: " + str(
          jvc_socket.getpeername()))
      jvc_socket.close()
      continue

    if send_bytes(jvc_socket, JVC_REQ) != len(JVC_REQ):
      logging.warning("Could not send JVC request handshake: " + str(
          jvc_socket.getpeername()))
      jvc_socket.close()
      continue

    if read_n_bytes(jvc_socket, len(JVC_ACK)) != JVC_ACK:
      logging.warning("JVC protocol did not ACK request: " + str(
          jvc_socket.getpeername()))
      jvc_socket.close()
      continue

    logging.info("Successfully completed JVC handshake: " + str(
          jvc_socket.getpeername()))
    return jvc_socket 

  logging.info("Failed to connected after %i attempt(s) ..." % attempt)
  return None

class JVCProxyRequestHandler(socketserver.BaseRequestHandler):
  JVC_HOST = None
  JVC_PORT = None
  TIMEOUT = None
  RETRIES = 0
  RETRY_WAIT = 0

  def _proxy_sockets(self, socket_in, socket_out, debug_direction=">>"):
    """Proxy data between two sockets."""
    bytes_proxied = 0
    debug_buffer = b''
 
    while True:
      try:
        data = socket_in.recv(RECV_SIZE)
        if data == b'':
          break
      except socket.timeout as e:
        break

      send_bytes(socket_out, data)
      bytes_proxied += len(data)          
      if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
        debug_buffer += data

    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
      logging.info("Proxied %i bytes between %s and %s\n%s %s" % (
          bytes_proxied,
          str(socket_in.getpeername()), str(socket_out.getpeername()),
          debug_direction, 
          repr(debug_buffer)))
    else:
      logging.info("Proxied %i bytes between %s and %s" % (
          bytes_proxied,
          str(socket_in.getpeername()), str(socket_out.getpeername())))

  def handle(self):
    assert self.JVC_HOST is not None
    assert self.JVC_PORT is not None
    assert self.TIMEOUT is not None

    self.request.settimeout(self.TIMEOUT)

    jvc_socket = create_connected_JVC_socket(
        self.JVC_HOST, self.JVC_PORT, self.TIMEOUT,
        retries=self.RETRIES, retry_wait=self.RETRY_WAIT)
    if not jvc_socket:
      logging.warning(
          "Could not connect to JVC host (%s:%i). Cannot proxy." % (
          self.JVC_HOST, self.JVC_PORT))
      return

    self._proxy_sockets(self.request, jvc_socket)
    self._proxy_sockets(jvc_socket, self.request, debug_direction="<<")
    jvc_socket.close()

def main():
  parser = argparse.ArgumentParser()

  parser.add_argument("jvc_host", help="JVC host to proxy to. Default: 20554.")
  parser.add_argument("--jvc_port", default=20554, type=int,
      help="JVC port number to connect to.")
  parser.add_argument("--proxy_host", default="localhost",
      help="Proxy server host/IP to bind to. Default: localhost.")
  parser.add_argument("--proxy_port", default=20554, type=int,
      help="Proxy server port number to listen on. Default: 20554.")
  parser.add_argument("-t", "--timeout", default=2, type=int,
      help="Timeout for network operations (seconds). Default: 2.")
  parser.add_argument("-l", "--loglevel", default="ERROR",
      help="Logging level. Default: ERROR.",
      choices=["ERROR", "WARNING", "INFO", "DEBUG"])
  parser.add_argument("-r", "--retries", type=int, default=0,
      help="Number of retries to allow in connection to the JVC host. Default: 0")
  parser.add_argument("-w", "--retry_wait", type=int, default=5,
      help="Seconds to wait between connection retries. Default: 5.")

  args = parser.parse_args()

  logging.basicConfig(
      level=logging.getLevelName(args.loglevel),
      format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s",
      datefmt="%F %H:%M:%S")

  JVCProxyRequestHandler.JVC_HOST = args.jvc_host
  JVCProxyRequestHandler.JVC_PORT = args.jvc_port
  JVCProxyRequestHandler.TIMEOUT = args.timeout
  JVCProxyRequestHandler.RETRIES = args.retries
  JVCProxyRequestHandler.RETRY_WAIT = args.retry_wait

  tcp_server = socketserver.TCPServer(  
      (args.proxy_host, args.proxy_port),
      JVCProxyRequestHandler,
      bind_and_activate=False)
  tcp_server.allow_reuse_address = True
  tcp_server.server_bind()
  tcp_server.server_activate()

  tcp_server.serve_forever()

if __name__ == "__main__":
  main()
