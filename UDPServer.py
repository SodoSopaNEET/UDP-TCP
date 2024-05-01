import socket
import sys
import time

HOST = ''  # Symbolic name meaning all available interfaces
PORT = 2163  # Arbitrary non-privileged port

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
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket created')
except socket.error as msg:
    print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

print('Socket bind complete')

expect_seq = 0
timeout_test = True

# now keep talking with the client
while 1:
    # receive data from client (data, addr)
    data, addr = s.recvfrom(1024)

    checksum = data[:2]
    seq = data[2]
    pkt = data[3:]

    if not data:
        break
    # print(str(ip_checksum(pkt) == checksum))

    if ip_checksum(pkt) == checksum and seq == str(expect_seq):
        print('recv: Good Data Sending ACK' + str(seq))
        print('recv pkt: ' + str(pkt))
        # Test timeout on message 4
        if str(pkt) == 'Message 4':
            time.sleep(5)
        s.sendto(str(seq), addr)
        expect_seq = 1 - expect_seq
    else:
        # Check seq and send according ACK
        if seq == str(expect_seq):
            print('recv: Bad Checksum Not Sending')
        else:
            print('recv: Bad Seq Sending ACK' + str(1 - expect_seq))
            s.sendto(str(1 - expect_seq), addr)
s.close()