import socket
import sys
from socket import timeout
from check import ip_checksum
import threading
import time

class Client:
    def __init__(self, host, port):
        self.host = host  # 設定client連接的server主機地址
        self.port = port  # 設定client連接的server port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 創建UDP socket
        self.s.settimeout(3)  # 設置socket超時時間為3秒
        self.window_size = 4  # 設置窗口大小為4
        self.base = 0  # 窗口的基序列號
        self.next_seq_num = 0  # 下一個要發送的封包序列號
        self.lock = threading.Lock()  # 創建thread lock以保護共享資源
        self.acknowledged = set()  # 記錄已確認的封包序列號
        self.timers = {}  # 用於保存每個封包的定時器

    def send(self, msg, seq):
        try:
            print(f'send: SENDING PKT {seq}')
            checksum = ip_checksum(msg).to_bytes(2, byteorder='big')  # 計算封包的檢查和
            packet = checksum + seq.to_bytes(1, byteorder='big') + msg  # 構造封包
            self.s.sendto(packet, (self.host, self.port))  # 發送封包
        except socket.error as msg:
            print('Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

    def start_timer(self, seq):
        if seq in self.timers:
            self.timers[seq].cancel()  # 取消已有的定時器
        timer = threading.Timer(3, self.timeout, [seq])  # 為封包設置超時定時器
        self.timers[seq] = timer
        timer.start()

    def timeout(self, seq):
        with self.lock:
            if seq not in self.acknowledged:  # 如果封包未被確認
                print(f'TIMEOUT: Resending {seq}')
                self.send(self.data[seq], seq)  # 重發封包
                self.start_timer(seq)  # 重啟定時器

    def send_messages(self, data):
        self.data = [data[i:i+1024] for i in range(0, len(data), 1024)]  # 將數據切分為1024位元組的塊
        while self.base < len(self.data):
            with self.lock:
                while self.next_seq_num < self.base + self.window_size and self.next_seq_num < len(self.data):  # 確保窗口內有空位並且還有數據要發送
                    self.send(self.data[self.next_seq_num], self.next_seq_num)  # 發送封包
                    self.start_timer(self.next_seq_num)  # 啟動定時器
                    self.next_seq_num += 1

            try:
                reply, addr = self.s.recvfrom(1024)  # 接收ACK
                ack = int.from_bytes(reply, byteorder='big')  # 解析ACK
                with self.lock:
                    if self.base <= ack < self.base + self.window_size:
                        print(f'ACK received: {ack}')
                        self.acknowledged.add(ack)  # 標記ACK已接收
                        self.timers[ack].cancel()  # 取消定時器
                        while self.base in self.acknowledged:  # 移動窗口
                            self.base += 1
            except timeout:
                continue
            except ConnectionResetError:
                print("Connection was reset. Retrying...")
                time.sleep(1)

        self.send(b'END', self.next_seq_num)  # 發送結束信號
        print('send: SENDING END')

if __name__ == "__main__":
    with open('test.png', 'rb') as f:  # 讀取要傳輸的文件
        data = f.read()

    client = Client('localhost', 2163)
    client.send_messages(data)
