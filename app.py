#!/usr/bin/env python3
"""
Focus 2.1 - Self-hosted start page with widget system, wallpaper support, and more
"""

from flask import Flask, render_template, jsonify, request, send_from_directory, redirect
from datetime import datetime
from html.parser import HTMLParser
import json
import os
import re
import base64
import hashlib
import urllib.request
import urllib.error

app = Flask(__name__, static_folder='static', template_folder='templates')

DATA_FILE = 'data/bookmarks.json'
WALLPAPER_CACHE = 'data/wallpaper_cache'

def ensure_data_dir():
    os.makedirs('data', exist_ok=True)
    os.makedirs(WALLPAPER_CACHE, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        default_data = {
            "settings": {
                "name": "",
                "showGreeting": True,
                "showTime": True,
                "showSearch": True,
                "searchEngine": "brave",
                "theme": "dark",
                "wallpaper": {
                    "type": "none",
                    "blur": 0,
                    "dim": 30
                }
            },
            "categories": [],
            "favorites": []
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(default_data, f, indent=2)

def load_data():
    ensure_data_dir()
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    # Ensure required fields exist
    if 'categories' not in data:
        data['categories'] = []
    if 'favorites' not in data:
        data['favorites'] = []
    if 'wallpaper' not in data.get('settings', {}):
        data['settings']['wallpaper'] = {"type": "none", "blur": 0, "dim": 30}
    return data

def save_data(data):
    ensure_data_dir()
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

class BookmarkHTMLParser(HTMLParser):
    """Parse Chrome/Firefox bookmark HTML exports"""
    def __init__(self):
        super().__init__()
        self.bookmarks = []
        self.folder_stack = []
        self.current_folder = None
        self.in_a = False
        self.current_link = {}
        
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h3':
            self.current_folder = ''
        elif tag == 'a':
            self.in_a = True
            self.current_link = {'url': attrs.get('href', ''), 'name': ''}
        elif tag == 'dl':
            if self.current_folder is not None:
                self.folder_stack.append(self.current_folder)
                self.current_folder = None
                
    def handle_endtag(self, tag):
        if tag == 'h3':
            if self.current_folder:
                self.folder_stack.append(self.current_folder)
            self.current_folder = None
        elif tag == 'a':
            self.in_a = False
            if self.current_link.get('url') and self.current_link.get('name'):
                self.current_link['folder'] = '/'.join(self.folder_stack) if self.folder_stack else 'Imported'
                self.bookmarks.append(self.current_link)
            self.current_link = {}
        elif tag == 'dl':
            if self.folder_stack:
                self.folder_stack.pop()
                
    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
        if self.current_folder is not None or (self.folder_stack and self.current_folder == ''):
            self.current_folder = data
        elif self.in_a:
            self.current_link['name'] = data

def parse_browser_bookmarks(html_content):
    """Parse browser bookmark HTML and convert to categories"""
    parser = BookmarkHTMLParser()
    parser.feed(html_content)
    
    folders = {}
    for bm in parser.bookmarks:
        folder = bm['folder'] or 'Imported'
        top_folder = folder.split('/')[0] if folder else 'Imported'
        if top_folder not in folders:
            folders[top_folder] = []
        folders[top_folder].append({
            'id': f"link_{datetime.now().timestamp()}_{len(folders[top_folder])}",
            'name': bm['name'],
            'url': bm['url']
        })
    
    colors = ['#22c55e', '#6366f1', '#f59e0b', '#ef4444', '#f97316', '#14b8a6', '#8b5cf6', '#ec4899']
    categories = []
    for idx, (name, links) in enumerate(folders.items()):
        categories.append({
            'id': f"cat_{datetime.now().timestamp()}_{idx}",
            'name': name[:30],
            'color': colors[idx % len(colors)],
            'subfolders': [],
            'links': links
        })
    
    return categories

def parse_bonjour_import(bonjour_data):
    """Parse Bonjour export format with categories and folders"""
    result = {
        "settings": {
            "name": bonjour_data.get("greeting", ""),
            "showGreeting": not bonjour_data.get("hide", {}).get("greetings", False),
            "showTime": bonjour_data.get("time", True),
            "showSearch": bonjour_data.get("searchbar", {}).get("on", True),
            "searchEngine": bonjour_data.get("searchbar", {}).get("engine", "brave"),
            "theme": "dark" if bonjour_data.get("dark", "auto") == "dark" else "auto",
            "wallpaper": {"type": "none", "blur": 0, "dim": 30}
        },
        "categories": [],
        "favorites": []
    }
    
    groups = bonjour_data.get("linkgroups", {}).get("groups", [])
    links = {}
    folders = {}
    
    for key, value in bonjour_data.items():
        if key.startswith("links") and isinstance(value, dict) and "_id" in value:
            if value.get("folder", False):
                folders[value["_id"]] = value
            elif "url" in value:
                links[value["_id"]] = value
    
    colors = ['#22c55e', '#6366f1', '#f59e0b', '#ef4444', '#f97316', '#14b8a6', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
    
    for idx, group_name in enumerate(groups):
        category = {
            "id": f"cat_{idx}",
            "name": group_name,
            "color": colors[idx % len(colors)],
            "subfolders": [],
            "links": []
        }
        
        # Get folders in this group
        group_folders = []
        for folder_id, folder in folders.items():
            if folder.get("parent") == group_name:
                subfolder = {
                    "id": folder_id,
                    "name": folder.get("title", "Untitled"),
                    "order": folder.get("order", 999),
                    "links": []
                }
                # Get links in this folder
                folder_links = []
                for link_id, link in links.items():
                    if link.get("parent") == folder_id:
                        folder_links.append({
                            "id": link_id,
                            "name": link.get("title", "Untitled"),
                            "url": link.get("url", ""),
                            "order": link.get("order", 999)
                        })
                folder_links.sort(key=lambda x: x.get("order", 999))
                subfolder["links"] = folder_links
                group_folders.append(subfolder)
        
        group_folders.sort(key=lambda x: x.get("order", 999))
        category["subfolders"] = group_folders
        
        # Get links directly in the group (not in folders)
        group_links = []
        for link_id, link in links.items():
            if link.get("parent") == group_name:
                group_links.append({
                    "id": link_id,
                    "name": link.get("title", "Untitled"),
                    "url": link.get("url", ""),
                    "order": link.get("order", 999)
                })
        group_links.sort(key=lambda x: x.get("order", 999))
        category["links"] = group_links
        result["categories"].append(category)
    
    return result

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(load_data())

@app.route('/api/data', methods=['POST'])
def update_data():
    save_data(request.json)
    return jsonify({"status": "success"})

@app.route('/api/import/bonjour', methods=['POST'])
def import_bonjour():
    try:
        parsed = parse_bonjour_import(request.json)
        save_data(parsed)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/import/browser', methods=['POST'])
def import_browser():
    try:
        html_content = request.json.get('html', '')
        categories = parse_browser_bookmarks(html_content)
        data = load_data()
        if 'categories' not in data:
            data['categories'] = []
        data['categories'].extend(categories)
        save_data(data)
        return jsonify({"status": "success", "imported": len(categories)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/wallpaper/upload', methods=['POST'])
def upload_wallpaper():
    """Handle custom wallpaper upload"""
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No file selected"}), 400
        
        # Save to cache
        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
            return jsonify({"status": "error", "message": "Invalid file type"}), 400
        
        filename = f"custom_{datetime.now().timestamp()}.{ext}"
        filepath = os.path.join(WALLPAPER_CACHE, filename)
        file.save(filepath)
        
        return jsonify({"status": "success", "filename": filename})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/wallpaper/cache/<filename>')
def serve_cached_wallpaper(filename):
    """Serve cached wallpaper"""
    return send_from_directory(WALLPAPER_CACHE, filename)

@app.route('/api/export', methods=['GET'])
def export_data():
    return jsonify(load_data())

@app.route('/api/wallpaper/bing')
def bing_wallpaper():
    """Proxy for Bing daily wallpaper to avoid CORS"""
    try:
        url = 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('images') and len(data['images']) > 0:
                image_url = 'https://www.bing.com' + data['images'][0]['url']
                return jsonify({"url": image_url})
        return jsonify({"error": "No image found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wallpaper/picsum')
def picsum_wallpaper():
    """Get random wallpaper from Lorem Picsum (Unsplash alternative)"""
    try:
        # Lorem Picsum provides random images - we redirect to their service
        # Categories are simulated by using seed based on category name
        category = request.args.get('category', 'nature')
        # Use a daily seed so image changes once per day but stays consistent during the day
        from datetime import date
        seed = hash(category + str(date.today())) % 1000
        # Return the direct Picsum URL - it handles redirects automatically
        return jsonify({"url": f"https://picsum.photos/seed/{seed}/1920/1080"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===================== WIDGET API ENDPOINTS =====================

# Cache for weather and finance data
_cache = {
    'weather': {'data': None, 'timestamp': 0, 'key': None},
    'finance': {}
}
CACHE_DURATION_WEATHER = 600  # 10 minutes
CACHE_DURATION_FINANCE = 300  # 5 minutes

@app.route('/api/weather')
def get_weather():
    """Proxy for Open-Meteo weather API (free, no API key required)"""
    import time
    
    lat = request.args.get('lat', '38.98')
    lon = request.args.get('lon', '-94.67')
    unit = request.args.get('unit', 'F')
    
    cache_key = f"{lat},{lon}"
    now = time.time()
    
    # Check cache
    if (_cache['weather']['key'] == cache_key and 
        _cache['weather']['data'] and 
        now - _cache['weather']['timestamp'] < CACHE_DURATION_WEATHER):
        cached = _cache['weather']['data'].copy()
        # Convert temperature if needed
        if unit == 'C' and 'temp_f' in cached:
            cached['temp'] = round((cached['temp_f'] - 32) * 5/9, 1)
            cached['unit'] = '°C'
        else:
            cached['temp'] = cached.get('temp_f', 0)
            cached['unit'] = '°F'
        return jsonify(cached)
    
    try:
        # Open-Meteo API - free, no key required
        url = (f"https://api.open-meteo.com/v1/forecast?"
               f"latitude={lat}&longitude={lon}"
               f"&current=temperature_2m,weather_code,is_day"
               f"&temperature_unit=fahrenheit"
               f"&timezone=auto")
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Focus/2.1'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            current = data.get('current', {})
            temp_f = current.get('temperature_2m', 0)
            weather_code = current.get('weather_code', 0)
            is_day = current.get('is_day', 1)
            
            # Map weather codes to descriptions and icons
            weather_map = {
                0: ('Clear', '☀️', '🌙'),
                1: ('Mostly Clear', '🌤️', '🌙'),
                2: ('Partly Cloudy', '⛅', '☁️'),
                3: ('Overcast', '☁️', '☁️'),
                45: ('Foggy', '🌫️', '🌫️'),
                48: ('Icy Fog', '🌫️', '🌫️'),
                51: ('Light Drizzle', '🌧️', '🌧️'),
                53: ('Drizzle', '🌧️', '🌧️'),
                55: ('Heavy Drizzle', '🌧️', '🌧️'),
                61: ('Light Rain', '🌧️', '🌧️'),
                63: ('Rain', '🌧️', '🌧️'),
                65: ('Heavy Rain', '🌧️', '🌧️'),
                66: ('Freezing Rain', '🌨️', '🌨️'),
                67: ('Heavy Freezing Rain', '🌨️', '🌨️'),
                71: ('Light Snow', '❄️', '❄️'),
                73: ('Snow', '🌨️', '🌨️'),
                75: ('Heavy Snow', '🌨️', '🌨️'),
                77: ('Snow Grains', '🌨️', '🌨️'),
                80: ('Light Showers', '🌦️', '🌧️'),
                81: ('Showers', '🌦️', '🌧️'),
                82: ('Heavy Showers', '🌧️', '🌧️'),
                85: ('Light Snow Showers', '🌨️', '🌨️'),
                86: ('Snow Showers', '🌨️', '🌨️'),
                95: ('Thunderstorm', '⛈️', '⛈️'),
                96: ('Thunderstorm + Hail', '⛈️', '⛈️'),
                99: ('Heavy Thunderstorm', '⛈️', '⛈️'),
            }
            
            desc, icon_day, icon_night = weather_map.get(weather_code, ('Unknown', '❓', '❓'))
            icon = icon_day if is_day else icon_night
            
            result = {
                'temp_f': round(temp_f, 1),
                'temp': round(temp_f, 1) if unit == 'F' else round((temp_f - 32) * 5/9, 1),
                'unit': '°F' if unit == 'F' else '°C',
                'description': desc,
                'icon': icon,
                'is_day': bool(is_day)
            }
            
            # Cache the result
            _cache['weather'] = {
                'data': result,
                'timestamp': now,
                'key': cache_key
            }
            
            return jsonify(result)
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'temp': '--',
            'unit': '°F' if unit == 'F' else '°C',
            'description': 'Unavailable',
            'icon': '❓'
        }), 500

@app.route('/api/finance')
def get_finance():
    """Proxy for stock/crypto data using Yahoo Finance"""
    import time
    
    symbol = request.args.get('symbol', 'SPY').upper()
    now = time.time()
    
    # Check cache
    if (symbol in _cache['finance'] and 
        now - _cache['finance'][symbol].get('timestamp', 0) < CACHE_DURATION_FINANCE):
        return jsonify(_cache['finance'][symbol]['data'])
    
    try:
        # Use Yahoo Finance v8 API (unofficial but widely used)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d"
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            chart = data.get('chart', {}).get('result', [{}])[0]
            meta = chart.get('meta', {})
            
            current_price = meta.get('regularMarketPrice', 0)
            previous_close = meta.get('previousClose', meta.get('chartPreviousClose', current_price))
            
            # Calculate change
            change = current_price - previous_close
            change_pct = (change / previous_close * 100) if previous_close else 0
            
            # Market state
            market_state = meta.get('marketState', 'REGULAR')
            is_market_open = market_state in ['REGULAR', 'PRE', 'POST']
            
            result = {
                'symbol': symbol,
                'price': round(current_price, 2),
                'change': round(change, 2),
                'changePercent': round(change_pct, 2),
                'previousClose': round(previous_close, 2),
                'marketState': market_state,
                'isMarketOpen': is_market_open,
                'currency': meta.get('currency', 'USD'),
                'name': meta.get('shortName', symbol)
            }
            
            # Cache the result
            _cache['finance'][symbol] = {
                'data': result,
                'timestamp': now
            }
            
            return jsonify(result)
            
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return jsonify({
                'error': f'Symbol "{symbol}" not found',
                'symbol': symbol,
                'price': 0,
                'change': 0,
                'changePercent': 0
            }), 404
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({
            'error': str(e),
            'symbol': symbol,
            'price': 0,
            'change': 0,
            'changePercent': 0
        }), 500

if __name__ == '__main__':
    ensure_data_dir()
    app.run(host='0.0.0.0', port=5000, debug=True)
