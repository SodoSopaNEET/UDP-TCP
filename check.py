def ip_checksum(data):
    pos = len(data)  # 獲取數據的長度
    if pos & 1:  # 如果數據長度是奇數
        pos -= 1
        cksum = data[pos]  # 最後一個位元作為初始檢查和
    else:
        cksum = 0  # 初始化檢查和為0
    while pos > 0:
        pos -= 2
        cksum += (data[pos + 1] << 8) + data[pos]  # 將兩個位元組合為16位整數並加到檢查和
    cksum = (cksum >> 16) + (cksum & 0xffff)  # 將高16位加到低16位
    cksum += (cksum >> 16)  # 確保再次將高16位加到低16位
    return (~cksum) & 0xffff  # 返回檢查和的補碼，確保是16位
