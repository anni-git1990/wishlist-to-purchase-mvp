"""
Myntra Wishlist Confidence Engine - Native Mobile App Visual Simulator (Port 8501)
Simulates native iOS & Android mobile user interface surfaces (Surface 1, Surface 2, Surface 3 & Surface 5)
inside an interactive smartphone frame in the browser.
"""

import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.fit_confidence_service import FitConfidenceService
from services.quality_digest_service import QualityDigestService
from mobile_views.fit_confidence_views import NativeMobileFitViewRenderer
from mobile_views.quality_digest_views import NativeMobileQualityViewRenderer

fit_service = FitConfidenceService()
quality_service = QualityDigestService()
fit_renderer = NativeMobileFitViewRenderer()
quality_renderer = NativeMobileQualityViewRenderer()


MOBILE_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Myntra Mobile Wishlist Confidence Simulator</title>
    <style>
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', Roboto, Helvetica, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
        .sim-header { text-align: center; margin-bottom: 20px; }
        .sim-header h1 { font-size: 24px; color: #ff3f6c; margin: 0 0 6px 0; }
        .sim-header p { font-size: 14px; color: #94a3b8; margin: 0; }
        
        /* Mobile Phone Container */
        .phone-frame {
            width: 375px; height: 740px; background: #000; border: 12px solid #334155;
            border-radius: 44px; position: relative; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
            overflow: hidden; display: flex; flex-direction: column;
        }
        .notch {
            width: 150px; height: 24px; background: #334155; border-bottom-left-radius: 14px;
            border-bottom-right-radius: 14px; margin: 0 auto; z-index: 100; position: absolute; top: 0; left: 100px;
        }
        .status-bar { height: 44px; background: #1e1e24; display: flex; justify-content: space-between; align-items: flex-end; padding: 0 20px 8px 20px; font-size: 12px; font-weight: 600; color: #fff; z-index: 90; }
        
        /* Mobile App Navigation Bar */
        .app-navbar { height: 50px; background: #ff3f6c; color: #fff; display: flex; align-items: center; justify-content: space-between; padding: 0 16px; font-weight: bold; font-size: 16px; }
        .app-content { flex: 1; background: #f4f4f6; color: #111; overflow-y: auto; padding: 12px; position: relative; }
        
        /* Wishlist Item Card */
        .wishlist-card { background: #fff; border-radius: 12px; padding: 12px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        .product-flex { display: flex; gap: 12px; }
        .product-img { width: 90px; height: 110px; background: #e2e8f0; border-radius: 8px; object-fit: cover; }
        .product-info { flex: 1; }
        .brand { font-size: 14px; font-weight: bold; color: #282c3f; margin: 0; }
        .title { font-size: 13px; color: #535766; margin: 2px 0 6px 0; }
        .price-row { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: bold; }
        .current-price { color: #282c3f; }
        
        /* Surface 1 Chips & Snippets */
        .fit-chip {
            display: inline-flex; align-items: center; gap: 6px; background: #f0fdf4; border: 1px solid #bbf7d0;
            color: #15803d; padding: 6px 10px; border-radius: 20px; font-size: 12px; font-weight: 600;
            margin-top: 8px; cursor: pointer; transition: transform 0.1s;
        }
        .fit-chip:active { transform: scale(0.96); }
        .quality-snippet {
            background: #f8fafc; border-left: 3px solid #ff3f6c; padding: 8px 10px; border-radius: 4px;
            font-size: 11px; color: #475569; margin-top: 8px; cursor: pointer;
        }
        
        /* Deep Link Push Banner */
        .push-banner {
            background: #1e293b; color: #fff; padding: 10px 14px; border-radius: 12px; margin-bottom: 12px;
            display: flex; align-items: center; justify-content: space-between; font-size: 12px; border: 1px solid #334155; cursor: pointer;
        }
        
        /* Native Bottom Sheet Drawer */
        .bottom-sheet-overlay {
            position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5);
            z-index: 200; display: none; justify-content: flex-end; flex-direction: column;
        }
        .bottom-sheet-overlay.active { display: flex; }
        .bottom-sheet {
            background: #fff; border-top-left-radius: 20px; border-top-right-radius: 20px;
            padding: 16px; max-height: 80%; overflow-y: auto; animation: slideUp 0.25s ease-out;
        }
        @keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
        .sheet-handle { width: 36px; height: 5px; background: #cbd5e1; border-radius: 3px; margin: 0 auto 12px auto; }
        .sheet-title { font-size: 16px; font-weight: bold; color: #0f172a; margin: 0 0 12px 0; }
        
        /* Fit Details & Bars */
        .metric-badge { background: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: bold; }
        .bar-container { margin: 10px 0; }
        .bar-label { display: flex; justify-content: space-between; font-size: 12px; color: #64748b; margin-bottom: 4px; }
        .bar-bg { height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
        .bar-fill { height: 100%; background: #ff3f6c; border-radius: 4px; }
        
        /* Peer Evidence Feed */
        .peer-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 10px; margin-bottom: 8px; font-size: 12px; }
        .peer-tag { color: #64748b; font-size: 11px; margin-bottom: 2px; }
        .btn-add-bag { background: #ff3f6c; color: #fff; width: 100%; border: none; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 14px; margin-top: 12px; cursor: pointer; }
        
        /* Controls */
        .sim-controls { margin-top: 20px; display: flex; gap: 10px; }
        .btn-ctl { background: #334155; color: #f8fafc; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; }
        .btn-ctl:hover { background: #475569; }
    </style>
</head>
<body>
    <div class="sim-header">
        <h1>Myntra Wishlist Confidence Engine</h1>
        <p>Native Mobile App Interface Simulator (iOS & Android Surface 1, 2, 3)</p>
    </div>

    <div class="phone-frame">
        <div class="notch"></div>
        <div class="status-bar">
            <span>9:41</span>
            <span>5G 100%</span>
        </div>
        
        <div class="app-navbar">
            <span>WISHLIST (1 Item)</span>
            <span style="font-size:12px;">Surface 1</span>
        </div>
        
        <div class="app-content">
            <!-- Simulated Push Notification -->
            <div class="push-banner" onclick="openFitSheet()">
                <div>
                    <div style="font-weight:bold; color:#ff3f6c;">🔔 Contextual Evidence Trigger</div>
                    <div>3 new similar-height reviews added for Roadster Shirt</div>
                </div>
                <span style="font-size:18px;">➔</span>
            </div>

            <!-- Surface 1 Wishlist Item Card -->
            <div class="wishlist-card">
                <div class="product-flex">
                    <img class="product-img" src="https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=300" alt="Roadster Shirt">
                    <div class="product-info">
                        <div class="brand">ROADSTER</div>
                        <div class="title">Men Pure Cotton Casual Shirt</div>
                        <div class="price-row">
                            <span class="current-price">₹1,299</span>
                        </div>
                        
                        <!-- Surface 1 Fit Recommendation Chip -->
                        <div class="fit-chip" onclick="openFitSheet()">
                            <span>✨ Rec. Size: <strong>M</strong></span>
                            <span style="font-size:10px; background:#bbf7d0; padding:2px 6px; border-radius:10px;">88% match</span>
                        </div>
                    </div>
                </div>
                
                <!-- Surface 1 Quality Digest Snippet Preview -->
                <div class="quality-snippet" onclick="openQualitySheet()">
                    <strong>Quality Digest:</strong> 100% combed cotton, soft feel, highly breathable for summer wear.
                    <span style="color:#ff3f6c; font-weight:bold; margin-left:4px;">View Digest ➔</span>
                </div>
            </div>
        </div>

        <!-- Native Bottom Sheet 1: Fit Confidence Detail (Surface 2) -->
        <div class="bottom-sheet-overlay" id="fitSheetOverlay" onclick="closeSheets(event)">
            <div class="bottom-sheet">
                <div class="sheet-handle"></div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="sheet-title">Personalized Fit Confidence</div>
                    <span class="metric-badge">HIGH CONFIDENCE</span>
                </div>
                
                <p style="font-size:13px; color:#475569; margin:0 0 12px 0;">
                    Based on 4 successful past purchases in size M from Roadster & 18 peer reviews.
                </p>
                
                <div class="bar-container">
                    <div class="bar-label"><span>Fit True to Size</span><strong>92%</strong></div>
                    <div class="bar-bg"><div class="bar-fill" style="width:92%;"></div></div>
                </div>
                <div class="bar-container">
                    <div class="bar-label"><span>Post-Wash Shrinkage Risk</span><strong>Low (2%)</strong></div>
                    <div class="bar-bg"><div class="bar-fill" style="width:15%; background:#22c55e;"></div></div>
                </div>

                <div style="font-weight:bold; font-size:13px; margin:14px 0 6px 0; color:#1e293b;">Verified Similar-Body Peer Feedback</div>
                <div class="peer-card">
                    <div class="peer-tag">Height: 5'9" • Weight: 72kg • Size Bought: M</div>
                    <div>"Fits perfectly across chest and shoulders. Length is ideal for untucked wear."</div>
                </div>
                <div class="peer-card">
                    <div class="peer-tag">Height: 5'10" • Weight: 74kg • Size Bought: M</div>
                    <div>"Fabric has good stretch. No tightness around armholes."</div>
                </div>

                <button class="btn-add-bag" onclick="addToBag()">Pre-Select Size M & Add to Bag</button>
            </div>
        </div>

        <!-- Native Bottom Sheet 2: Quality Digest Detail (Surface 3) -->
        <div class="bottom-sheet-overlay" id="qualitySheetOverlay" onclick="closeSheets(event)">
            <div class="bottom-sheet">
                <div class="sheet-handle"></div>
                <div class="sheet-title">Verified Quality Digest</div>
                
                <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:10px; border-radius:8px; font-size:12px; margin-bottom:12px;">
                    <strong>LLM Traceable Summary:</strong><br>
                    • 100% combed cotton, soft feel, highly breathable.<br>
                    • Color retention rated 4.8/5 across 42 post-wash reviews.<br>
                    • Reinforced double-stitching at collar and seams.
                </div>

                <div style="font-weight:bold; font-size:13px; margin-bottom:6px; color:#1e293b;">Verified Customer Photos (CNN Approved)</div>
                <div style="display:flex; gap:8px; overflow-x:auto; padding-bottom:8px;">
                    <img src="https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=200" style="width:90px; height:90px; border-radius:8px; object-fit:cover;">
                    <img src="https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=200" style="width:90px; height:90px; border-radius:8px; object-fit:cover;">
                </div>

                <button class="btn-add-bag" style="background:#0f172a;" onclick="closeSheetsDirect()">Close Quality Sheet</button>
            </div>
        </div>
    </div>

    <div class="sim-controls">
        <button class="btn-ctl" onclick="openFitSheet()">Open Fit Detail Sheet (Surface 2)</button>
        <button class="btn-ctl" onclick="openQualitySheet()">Open Quality Sheet (Surface 3)</button>
        <button class="btn-ctl" onclick="window.open('http://localhost:8080', '_blank')">Open Admin Dashboard (Surface 4)</button>
    </div>

    <script>
        function openFitSheet() {
            document.getElementById('fitSheetOverlay').classList.add('active');
            document.getElementById('qualitySheetOverlay').classList.remove('active');
        }
        function openQualitySheet() {
            document.getElementById('qualitySheetOverlay').classList.add('active');
            document.getElementById('fitSheetOverlay').classList.remove('active');
        }
        function closeSheets(e) {
            if (e.target.classList.contains('bottom-sheet-overlay')) {
                e.target.classList.remove('active');
            }
        }
        function closeSheetsDirect() {
            document.getElementById('fitSheetOverlay').classList.remove('active');
            document.getElementById('qualitySheetOverlay').classList.remove('active');
        }
        function addToBag() {
            closeSheetsDirect();
        }
    </script>
</body>
</html>
"""


class MobileSimulatorHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(MOBILE_HTML_TEMPLATE.encode('utf-8'))


def run_simulator_server(port: int = 9090):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MobileSimulatorHTTPHandler)
    print(f"Native Mobile App Visual Simulator running on http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_simulator_server()
