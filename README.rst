Overview of JVC Proxy
=====================

A tiny server that acts as a proxy between a client and a JVC projector such a
projector. JVC projectors insist on an additional 3-way handshake (PJ_OK,
PJREQ, PJACK) in addition to the normal TCP 3-way handshake. This means that
certain home automation appliances may have timing difficulties communicating
with the projector as they lack the protocol knowledge to implement the
additional handshake.

See `JVC Projector Control codes
<http://support.jvc.com/consumer/support/documents/DILAremoteControlGuide.pdf>`_
for the actual codes to effectively manage a JVC projector.

Using the server
----------------

Start the server, proxy between localhost and 'my-projector' on the usual JVC
control port number (20554).

::

    $ jvc_proxy -l DEBUG -r 2 -t 1 my-projector

Binds the server to an IP address / hostname that is accessible external to the
machine (i.e. not localhost). Set logging level to DEBUG (will log the actual
bytes proxied). Will retry failed connections to the projector twice. Allows 1
second timeout on network operations.

::

    $ jvc_proxy --proxy_host my-pc -l DEBUG -r 2 -t 1 my-projector

Available arguments:

::

    usage: jvc_proxy.py [-h] [--jvc_port JVC_PORT] [--proxy_host PROXY_HOST]
                        [--proxy_port PROXY_PORT] [-t TIMEOUT] [-v VERBOSE]
                        [-l {ERROR,WARNING,INFO,DEBUG}] [-r RETRIES]
                        [-w RETRY_WAIT]
                        jvc_host

    positional arguments:
      jvc_host              JVC host to proxy to. Default: 20554.

    optional arguments:
      -h, --help            show this help message and exit
      --jvc_port JVC_PORT   JVC port number to connect to.
      --proxy_host PROXY_HOST
                            Proxy server host/IP to bind to. Default: localhost.
      --proxy_port PROXY_PORT
                            Proxy server port number to listen on. Default: 20554.
      -t TIMEOUT, --timeout TIMEOUT
                            Timeout for network operations (seconds). Default: 2.
      -v VERBOSE, --verbose VERBOSE
                            Whether or not to output proxied data. Default: False.
      -l {ERROR,WARNING,INFO,DEBUG}, --loglevel {ERROR,WARNING,INFO,DEBUG}
                            Logging level. Default: ERROR.
      -r RETRIES, --retries RETRIES
                            Number of retries to allow in connection to the JVC
                            host. Default: 0
      -w RETRY_WAIT, --retry_wait RETRY_WAIT
                            Seconds to wait between connection retries. Default:
                            5.


Starting the server by default
------------------------------

Use the included jvc_proxy.service to start the server as a systemd
unit.
