__author__ = 'henla464'

import socket
import time
from struct import unpack, pack

class SendToSirapAdapter(object):
    def __init__(self):
        self.sock = None

    def OpenConnection(self):
        if self.sock is None:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = ("192.168.1.123", 10000)
                self.sock.settimeout(1)
                self.sock.connect(server_address)
                return True
            except socket.gaierror as msg:
                if self.sock is not None:
                    self.sock.close()
                self.sock = None
                return False
            except socket.error as msg:
                if self.sock is not None:
                    self.sock.close()
                self.sock = None
                return False
        return True

    def SendData(self, messageData: bytearray) -> bool:
        try:
            # Send data
            if not self.OpenConnection():
                self.sock = None
                return False

            self.sock.sendall(messageData)
            print("Sent")
            self.sock.close()
            self.sock = None
            return True
        except socket.error as msg:
            if self.sock is not None:
                self.sock.close()
            self.sock = None
            print(msg)
            return False
        except Exception as ex:
            if self.sock is not None:
                self.sock.close()
            self.sock = None
            print(ex)
            return False


def send():
    sendSirap = SendToSirapAdapter()
    punch = 0  # type of data
    codeDay = 0  # obsolete
    byteArr = bytearray(
        pack("<cHIII", bytes([punch]), 0, 12345678, codeDay, 1200))

    for i in range(100):
        time.sleep(0.5)
        print(str(i))
        byteArr[1] = i
        sendSirap.SendData(byteArr)


if __name__ == '__main__':
    send()


