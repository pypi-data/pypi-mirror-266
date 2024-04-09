import datetime
class sequence:
    def __init__(self,timestamp,data) -> None:
        self.timestamp:datetime.datetime = timestamp
        self.data: list = data
        pass
class sequence_manager:
    def __init__(self) -> None:
        self.__messages : dict = {}
    def delete_addr(self,address):
        if(address in self.__messages.keys()):
            del self.__messages[address]
    def add_addr(self,address):
        if(address not in self.__messages.keys()):
            self.__messages[address] = {}
    def add_seq(self,address,seqno,result,id):
        client_messages = self.__messages[address]
        if(seqno not in client_messages.keys()):
            client_messages[seqno] = sequence(datetime.datetime.now(),[(id,result)])
        else:
            client_messages[seqno].data.append((id,result))
    def get_result(self,address,seqno):
        try:
            seq: sequence = self.__messages[address][seqno]
            seq_data = seq.data
            seq_data = sorted(seq_data)
            result = b''.join(x[1] for x in seq_data)
            del self.__messages[address][seqno]
            return result
        except:
            return None