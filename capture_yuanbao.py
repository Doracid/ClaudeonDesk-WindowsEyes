"""
元宝 API 抓包工具
启动后在本机 :8888 开一个代理，所有经过的请求都会打印出来
然后用元宝的设置把代理指向 127.0.0.1:8888 即可
"""
import socket
import ssl
import threading
import logging
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("capture")

def handle_client(client):
    """处理客户端连接"""
    try:
        # 读取HTTP请求行
        request_line = b""
        while b"\r\n" not in request_line:
            chunk = client.recv(1)
            if not chunk:
                return
            request_line += chunk

        line = request_line.decode("utf-8", errors="replace").strip()
        parts = line.split(" ")
        method = parts[0]

        if method == "CONNECT":
            # HTTPS: 只记录目标地址，然后透传
            target = parts[1]  # host:port
            log.info(f"[HTTPS] CONNECT {target}")
            client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            # 获取原始socket的对端地址
            log.info(f"[HTTPS] 隧道建立: {target}")
            # 透传 - 读取后续数据直到连接关闭
            try:
                while True:
                    data = client.recv(65536)
                    if not data:
                        break
            except:
                pass
        else:
            # HTTP: 读取完整请求并记录
            headers = b""
            while b"\r\n\r\n" not in headers:
                chunk = client.recv(1)
                if not chunk:
                    return
                headers += chunk

            # 提取Host和路径
            header_text = headers.decode("utf-8", errors="replace")
            first_line = header_text.split("\r\n")[0]
            host = ""
            for h in header_text.split("\r\n"):
                if h.lower().startswith("host:"):
                    host = h.split(":", 1)[1].strip()
                    break

            log.info(f"[HTTP] {method} http://{host}{first_line.split()[1]}")

            # 如果有Content-Length，读取body
            content_length = 0
            for h in header_text.split("\r\n"):
                if h.lower().startswith("content-length:"):
                    content_length = int(h.split(":")[1].strip())
                    break

            body = b""
            if content_length > 0:
                body = client.recv(min(content_length, 65536))

            if body:
                log.info(f"[HTTP] Body({len(body)} bytes): {body[:500]}")

            client.sendall(b"HTTP/1.1 502 Not Proxied\r\nContent-Length: 2\r\n\r\nOK")
    except Exception as e:
        log.error(f"处理连接出错: {e}")
    finally:
        try:
            client.close()
        except:
            pass

def start_proxy(port=8888):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(50)
    log.info(f"=" * 50)
    log.info(f"代理已启动: 127.0.0.1:{port}")
    log.info(f"请将元宝的代理设置为 127.0.0.1:{port}")
    log.info(f"所有API请求会在这里显示")
    log.info(f"按 Ctrl+C 停止")
    log.info(f"=" * 50)

    while True:
        client, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(client,), daemon=True)
        t.start()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    try:
        start_proxy(port)
    except KeyboardInterrupt:
        log.info("已停止")
