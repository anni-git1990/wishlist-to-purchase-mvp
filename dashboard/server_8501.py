"""
Myntra Wishlist Confidence Engine - Port 8501 Redirect / Server
Ensures port 8501 also serves the UX-Enhanced Mobile Application and Admin Telemetry.
"""

import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from dashboard.app import UX_ENHANCED_HTML_TEMPLATE, DashboardMetricsBackend

class Port8501HTTPHandler(BaseHTTPRequestHandler):
    backend = DashboardMetricsBackend()

    def do_GET(self):
        if self.path == "/api/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            metrics = self.backend.get_dashboard_summary()
            self.wfile.write(json.dumps(metrics).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(UX_ENHANCED_HTML_TEMPLATE.encode('utf-8'))

def run_8501_server(port: int = 8501):
    server_address = ('', port)
    httpd = HTTPServer(server_address, Port8501HTTPHandler)
    print(f"Server 8501 running on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_8501_server()
