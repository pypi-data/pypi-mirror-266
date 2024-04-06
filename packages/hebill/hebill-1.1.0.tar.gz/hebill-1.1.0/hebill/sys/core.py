import socket


class Sys:
    @staticmethod
    def local_ips(self):
        ips = set()
        # 获取当前主机名
        hostname = socket.gethostname()  # 获取主机的所有地址信息
        addr_info = socket.getaddrinfo(hostname, None)
        for addr in addr_info:
            ip_address = addr[4][0]  # 提取IP地址
            ips.add(ip_address)
        return ips
