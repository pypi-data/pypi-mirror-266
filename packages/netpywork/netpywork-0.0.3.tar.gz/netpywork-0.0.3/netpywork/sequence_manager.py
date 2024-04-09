import datetime
import netpywork

class sequence:
    def __init__(self,data) -> None:
        self.data: list = data
    def get_amount(self) -> int:
        return len(self.data)
class sequence_manager:
    def __init__(self) -> None:
        self.__messages : dict = {}
        self.__messages_in_process: dict = {}
        self.__is_running = True
        # self.__clear_thread = Thread(target=self.__clear_old)
        # self.__clear_thread.start()
    def delete_addr(self,address):
        if(address in self.__messages.keys()):
            del self.__messages[address]
    def add_addr(self,address):
        if(address not in self.__messages.keys()):
            self.__messages[address] = {}
    def add_seq(self,address,seqno,result,id):
        client_messages = self.__messages[address]
        if(seqno not in client_messages.keys()):
            client_messages[seqno] = sequence([(id,result)])
            self.__messages_in_process[(address,seqno)] = datetime.datetime.now()
        else:
            client_messages[seqno].data.append((id,result))
        self.__clear_old()
    def get_amount(self,address,seqno):
        try:
            seq: sequence = self.__messages[address][seqno]
            return seq.get_amount()
        except:
            return -1
    def stop(self):
        self.__is_running = False
    def get_result(self,address,seqno):
        try:
            seq: sequence = self.__messages[address][seqno]
            seq_data = seq.data
            seq_data = sorted(seq_data)
            result = b''.join(x[1] for x in seq_data)
            del self.__messages[address][seqno]
            del self.__messages_in_process[(address,seqno)]
            return result
        except:
            return None
    def __clear_old(self):
        try:
            for address in self.__messages.keys():
                for seqno in self.__messages[address].keys():
                    timestamp = self.__messages_in_process[(address,seqno)]
                    if(timestamp + netpywork.udp_storetime < datetime.datetime.now()):
                        del self.__messages_in_process[(address,seqno)]
                        del self.__messages[address][seqno]
        except:
            pass