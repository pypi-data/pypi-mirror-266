import socket
import select
from threading import Thread
from .protocol import *
from .sequence_manager import sequence_manager
from .utils import *

class server:
    def __init__(self,port : int) -> None:
        self.port : int = port
        self.on_receive = None
        self.on_connect = None
        self.on_disconnect = None

        self.__tcp_socket: socket.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.__tcp_socket.bind(('',port))

        self.__udp_socket: socket.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.__udp_socket.bind(('',port))

        self.__tcp_thread: Thread = None
        self.__udp_thread: Thread = None

        self.__clients: list = []
        self.__seq_manager: sequence_manager = sequence_manager()
        self.__addr_to_sock: dict = {}
        self.__udp_seq = 0
        self.__is_running = False

    def run(self):
        self.__is_running = True
        self.__tcp_thread = Thread(target=self.__run_tcp)
        self.__tcp_socket.listen()
        self.__tcp_thread.start()

        self.__udp_thread = Thread(target=self.__run_udp)
        self.__udp_socket.settimeout(1)
        self.__udp_thread.start()
    def close(self):
        self.__is_running = False
        self.__tcp_socket.close()
        self.__tcp_thread.join()
        for client in self.__clients:
            self.__seq_manager.delete_addr(client.getpeername())
        self.__udp_thread.join()
        self.__udp_socket.close()
    def send_reliable(self,msg: bytes,address:tuple):
        utils.send_tcp(self.__addr_to_sock[address],msg)
    def __get_actual_address(self,address):
        return self.__addr_to_sock[address].getpeername()
    def send_unreliable(self,msg: bytes,address:tuple):
        msg_len = len(msg)
        if(msg_len <= utils.MAX_UDP_PACKET_SIZE):
            utils.send_udp(self.__udp_socket,self.__tcp_socket.getsockname()[1],self.__get_actual_address(address),msg,self.__udp_seq,0,True)
        else:
            parts = []
            while (len(msg) > utils.MAX_UDP_PACKET_SIZE):
                parts.append(msg[0:utils.MAX_UDP_PACKET_SIZE])
                msg = msg[utils.MAX_UDP_PACKET_SIZE:]
            parts.append(msg)
            for i in range(len(parts)):
                utils.send_udp(self.__udp_socket,self.__tcp_socket.getsockname()[1],self.__get_actual_address(address),parts[i],self.__udp_seq,i, i == len(parts) - 1)
        self.__udp_seq += 1
    def __has_client(self,address):
        for client in self.__clients:
            client_address = client.getpeername()
            if(address == client_address):
                return True
        return False
    
    def __delete_client(self,sock):
        self.__clients.remove(sock)
        socket_addr = sock.getpeername()
        self.__seq_manager.delete_addr(socket_addr)
        del self.__addr_to_sock[socket_addr]
        if(self.on_disconnect):
            self.on_disconnect(socket_addr)
    def __run_udp(self):
        while self.__is_running:
            try:
                message: udp_msg = utils.read_udp_msg(self.__udp_socket)
                if(not self.__has_client(message.address)):
                    continue
                self.__seq_manager.add_seq(message.address,message.seq_no,message.data,message.seq_id)
                if(message.is_end):
                    # TODO : move to logging
                    # print("UDP",)
                    data = self.__seq_manager.get_result(message.address,message.seq_no)
                    result_msg = udp_msg()
                    result_msg.data = data
                    result_msg.address = message.address
                    result_msg.length = len(data)
                    result_msg.port = message.port
                    result_msg.is_end = True
                    result_msg.seq_no = message.seq_no
                    if(self.on_receive):
                        self.on_receive(result_msg,protocol.UDP)
            except:
                continue
    def __run_tcp(self):
        while self.__is_running:
            try:
                sockets,_,_ = select.select(self.__clients + [self.__tcp_socket],[],[])
                for sock in sockets:
                    if(sock == self.__tcp_socket):
                        client_socket,_ = sock.accept()
                        self.__clients.append(client_socket)
                        client_addr = client_socket.getpeername()
                        self.__seq_manager.add_addr(client_addr)
                        self.__addr_to_sock[client_addr] = client_socket
                        if(self.on_connect):
                            self.on_connect(client_addr)
                    else:
                        try:
                            message: tcp_msg = utils.read_tcp_msg(sock)
                            # Remove the length of the is end byte to match udp length which is the data length
                            message.length -= 1
                            # TODO : move to logging
                            # print("TCP",message.data)
                            if(self.on_receive):
                                self.on_receive(message,protocol.TCP)
                            if(message.closing):
                                self.__delete_client(sock)
                        except:
                            self.__delete_client(sock)
            except:
                continue