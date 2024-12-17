from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

def do_ping_sweep(ip, num_of_hosts):
    active_hosts = []
    base_ip = ".".join(ip.split('.')[:-1])  # Получаем базовый IP без последней части
    for i in range(1, num_of_hosts + 1):
        current_ip = f"{base_ip}.{i}"
        response = os.system(f"ping -c 1 {current_ip}" if os.name != 'nt' else f"ping -n 1 {current_ip}")
        if response == 0:
            active_hosts.append(current_ip)
    return active_hosts

def send_http_request(target, method, headers=None, payload=None):
    import requests
    headers_dict = {}
    if headers:
        for header in headers:
            name, value = header.split(':', 1)
            headers_dict[name.strip()] = value.strip()
    if method.upper() == "GET":
        response = requests.get(target, headers=headers_dict)
    elif method.upper() == "POST":
        response = requests.post(target, headers=headers_dict, json=payload)
    else:
        raise ValueError("Unsupported HTTP method")

    return {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "content": response.text
    }

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/sendhttp":
            content_length = int(self.headers["Content-Length"])
            post_data = json.loads(self.rfile.read(content_length))

            target = post_data.get("Target")
            method = post_data.get("Method")
            headers = post_data.get("Headers")
            payload = post_data.get("Payload")

            if not target or not method:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing target or method in request")
                return

            response = send_http_request(target, method, headers, payload)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        elif self.path == "/scan":
            content_length = int(self.headers["Content-Length"])
            post_data = json.loads(self.rfile.read(content_length))

            ip = post_data.get("target")
            num_of_hosts = post_data.get("count")

            if not ip or not num_of_hosts:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing IP or number of hosts in request")
                return

            active_hosts = do_ping_sweep(ip, int(num_of_hosts))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"active_hosts": active_hosts}).encode())

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"API is running!")

if __name__ == "__main__":
    server_address = ("", 3000)
    httpd = HTTPServer(server_address, RequestHandler)
    print("Server is running on port 3000...")
    httpd.serve_forever()