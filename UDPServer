import socket
import threading
from check import ip_checksum

class Server:
    def __init__(self, host, port):
        self.host = host  # 設定server的主機地址
        self.port = port  # 設定server的port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 創建UDP socket
        self.s.bind((self.host, self.port))  # 綁定socket到指定地址和port
        self.buffer = {}  # 用於儲存接收的封包
        self.expected_seq = 0  # 期望接收到的封包序列號
        self.lock = threading.Lock()  # 創建線程鎖以保護共享資源
        self.file_data = bytearray()  # 用於保存接收的文件數據
        self.running = True  # 服務器運行狀態標誌

    def start(self):
        print('Server started')
        while self.running:  # 持續運行直到接收到結束信號
            data, addr = self.s.recvfrom(1027)  # 接收封包，最大為1027位元組
            checksum = data[:2]  # 提取檢查和字段
            seq = int.from_bytes(data[2:3], byteorder='big')  # 提取序列號字段
            pkt = data[3:]  # 提取數據

            if pkt == b'END':  # 如果接收到結束信號
                print('recv: END')
                with self.lock:  # 獲取鎖來修改共享狀態
                    self.running = False
                self.s.sendto(seq.to_bytes(1, byteorder='big'), addr)  # 回傳ACK
                break

            if ip_checksum(pkt) == int.from_bytes(checksum, byteorder='big'):  # 校驗檢查和
                print(f'recv: Good Data {seq}')
                with self.lock:
                    if seq == self.expected_seq:  # 如果接收到期望的封包
                        print(f'Sending ACK {seq}')
                        self.s.sendto(seq.to_bytes(1, byteorder='big'), addr)  # 發送ACK
                        self.file_data.extend(pkt)  # 添加數據到文件
                        self.expected_seq += 1  # 更新期望序列號
                        while self.expected_seq in self.buffer:  # 處理buffer中的後續封包
                            self.file_data.extend(self.buffer.pop(self.expected_seq))
                            self.expected_seq += 1
                    elif seq > self.expected_seq:  # 如果接收到的封包序列號大於期望序列號
                        print(f'Buffering packet {seq}')
                        self.buffer[seq] = pkt  # 暫時儲存封包
                        print(f'Sending ACK {seq}')
                        self.s.sendto(seq.to_bytes(1, byteorder='big'), addr)  # 發送ACK
                    else:
                        print(f'Duplicate packet {seq}, ACK {seq} again')  # 重複封包
                        self.s.sendto(seq.to_bytes(1, byteorder='big'), addr)  # 重新發送ACK
            else:
                print('recv: Bad Checksum')  # 檢查和錯誤

        with open('udp_received.png', 'wb') as f:  # 將接收的數據寫入文件
            f.write(self.file_data)
        print("Server shutdown and image saved.")

if __name__ == "__main__":
    server = Server('', 2163)  # 創建Server，監聽所有地址上的2163端口
    server.start()  # 啟動Server
