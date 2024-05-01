import socket

HOST = "127.0.0.1" #本機
PORT = 22222

#創建socket
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#綁定位址
tcp_server.bind((HOST, PORT))
#開始Listen
tcp_server.listen()
print("Start")

#接受Client連接
conn, addr = tcp_server.accept()
print(addr, "已連接")

imgFile = open('tcp_save.png', 'wb')  # 開始寫入圖片檔
while True:
    imgData = conn.recv(1024)  # 接收遠端主機傳來的數據
    if not imgData:
        break  # 讀完檔案結束迴圈
    imgFile.write(imgData)

imgFile.close()
print("image save")
conn.close()
tcp_server.close()
