from .constants import *
from .server import *
from .client import *
from .protocol import *
from datetime import timedelta

__version__ = constants.VERSION
server = server
client = client
protocol = protocol
tcp_msg = tcp_msg
udp_msg = udp_msg
udp_storetime: timedelta = timedelta(minutes=5)