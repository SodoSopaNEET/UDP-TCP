import socket  # for sockets
import sys  # for exit
from socket import timeout
def ip_checksum(data):  # Form the standard IP-suite checksum
    pos = len(data)
    if pos & 1:  # If odd...
        pos -= 1
        sum = ord(data[pos])  # Prime the sum with the odd end byte
    else:
        sum = 0

    # Main code: loop to calculate the checksum
    while pos > 0:
        pos -= 2
        sum += (ord(data[pos + 1]) << 8) + ord(data[pos])

    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)

    result = (~ sum) & 0xffff  # Keep lower 16 bits
    result = result >> 8 | ((result & 0xff) << 8)  # Swap bytes
    return chr(result / 256) + chr(result % 256)
# Datagram (udp) socket
# create dgram udp socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print('Failed to create socket')
    sys.exit()

host = 'localhost'
port = 2163

s.settimeout(3)
seq = 0

checksum_test = True

# Send 7 test messages
for i in range(7):
    msg = 'Message ' + str(i)
    ack_received = False
    while not ack_received:
        try:
            # Test bad checksum on message 3
            if i == 3 and checksum_test:
                print('send: TESTING BAD CHECKSUM')
                s.sendto(ip_checksum("wrong") + str(seq) + msg, (host, port))
                checksum_test = False
            # Send good package
            else:
                print('send: SENDING PKT')
                s.sendto(ip_checksum(msg) + str(seq) + msg, (host, port))
        except socket.error as msg:
            print('Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

        try:
            # receive data from client (data, addr)
            print('send: GETTING ACK')
            reply, addr = s.recvfrom(1024)
            ack = reply[0]
        except timeout:
            print('send: TIMEOUT')
        else:
            print('Checking for ACK ' + str(seq))
            if ack == str(seq):
                ack_received = True
    print('ACK FOUND, CHANGING SEQ')
    seq = 1 - seq