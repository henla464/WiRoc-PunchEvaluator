__author__ = 'henla464'

import datetime
import math
import socketserver
from struct import unpack
import os.path
from startWebServer import startFlaskServer


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.

    iwconfig wlan0 power off
    iw wlan0 set power_save off
    """

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.data = None

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("Received from {}:".format(self.client_address[0]))
        print(self.data)
        #byteArr = bytearray(
        #    pack("<cHIII", bytes([punch]), siMessage.GetStationNumber(), siMessage.GetSICardNumber(), codeDay, time))
        (dataType, stationNumber, SINo, codeDay, time) = unpack("<bHIII", self.data)
        # codeDay is no used
        print(dataType)
        if dataType == 0:
            # this is a punch
            print(f"stationNumber {stationNumber}")
            print(f"SINo {SINo}")
            print(f"time tenths of second {time}")
            print(f"current time: {datetime.datetime.now()}")
            print(datetime.datetime.now())
            self.printToFile(stationNumber, SINo, time)

        # just send back the same data, but upper-cased
        #self.request.sendall(self.data.upper())

    def printToFile(self, stationNumber, siNo, time):
        currentDateTime = datetime.datetime.now()
        currentDate = str(currentDateTime)[0:10]
        addHeader = not os.path.isfile(currentDate + ".txt")

        with open(currentDate + ".txt", "a") as logFile:
            if addHeader:
                logFile.write("Control;Card no;Time;TimeTenthOfSeconds;ReceivedTime\n")
            timeS = time / 10
            timeM = math.floor(timeS / 60)
            timeSRemaining = timeS - (timeM * 60)
            logFile.write(str(stationNumber))
            logFile.write(";")
            logFile.write(str(siNo))
            logFile.write(";")
            logFile.write(str(int(timeM)))
            logFile.write(":")
            logFile.write(str(int(timeSRemaining)))
            logFile.write(";")
            logFile.write(str(int(time)))
            logFile.write(";")
            logFile.write(str(currentDateTime))
            logFile.write("\n")

def getIpAddress():
    ipAddressStr = os.popen("hostname -I").read().strip("\n")
    ipAddresses = ipAddressStr.split(' ')
    for ip in ipAddresses:
        if not ip.startswith("169"):
            return ip

def startTCPServer():
    HOST, PORT = getIpAddress(), 10000
    print(HOST)
    print(str(PORT))

    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()


if __name__ == '__main__':
    startTCPServer()


