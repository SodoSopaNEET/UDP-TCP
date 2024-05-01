import socket

HOST = "127.0.0.1"
PORT = 22222

#創建socket
tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#連接server
tcp_client.connect((HOST, PORT))

imgFile = open("test.png", "rb")
while True:
    imgData = imgFile.readline(1024)
    if not imgData:
        break  # 讀完檔案結束迴圈
    tcp_client.send(imgData)
imgFile.close()
print("傳送完畢")

tcp_client.close()