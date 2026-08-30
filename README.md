# Focus - Self-Hosted Start Page

A beautiful, feature-rich self-hosted browser start page with tab groups, folders, icon grid layout, wallpaper support, and responsive design optimized for desktop and mobile (including Samsung Fold devices).

## Screenshots

The interface displays bookmarks as a clean icon grid with rounded favicons and labels, organized into tab groups with optional subfolders. It adapts responsively from desktop (10 columns) to phone (5 columns).

---

## Features

### 🎯 Clean Icon Grid Layout
- **Large rounded icons** with site favicons (128px high-quality from Google)
- **Labels below icons** - Shows site name, wraps to 2 lines max
- **Auto-generated colors** - When favicon fails, shows colored placeholder with initial
- **Responsive grid** - Automatically adjusts columns based on screen width
- **Samsung Fold optimized** - Works on both inner and outer screens

### 📑 Organization
- **Tab Groups** - Organize bookmarks into color-coded categories
- **Subfolders** - Create folders within tabs for deeper organization
- **Favorites Bar** - Quick access to your most-used links at the top
- **Subfolder Chips** - Easy navigation between "All" and folder views

### 🔀 Drag & Drop
- **Reorder bookmarks** - Drag icons to rearrange within a tab
- **Create folders** - Hold a bookmark over another for 2.5 seconds to auto-create a folder
- **Move between tabs** - Drag bookmarks to other tab groups in the navigation bar
- **Scrollable tab bar** - Left/right arrows for many tabs, touch-drag on mobile

### 🖼️ Custom Icons
- **Upload custom images** - Replace any favicon with your own icon
- **Base64 encoded** - Icons stored in data, fully portable
- **Refresh favicon** - Re-fetch the original favicon anytime
- **Preserved in exports** - Custom icons included in JSON backups

### 🎨 Wallpaper System
| Source | Description |
|--------|-------------|
| **Bing Daily** | Microsoft's curated wallpaper (server-proxied for CORS) |
| **NASA APOD** | Astronomy Picture of the Day |
| **Random Photos** | Lorem Picsum random images (daily rotation by category) |
| **Custom URL** | Any direct image URL |
| **Solid Color** | Minimalist single-color background |
| **Gradient** | 12 presets + custom CSS gradient support |

**Visual Controls:**
- Blur slider (0-30px)
- Dim/overlay slider (0-70%)

### ⏰ Display Options
- **Configurable clock** - 12-hour or 24-hour format
- **Date display** - "Friday, January 16"
- **Personalized greeting** - "Good afternoon, Greg"
- **Toggle visibility** - Show/hide time, greeting, or search independently

### 🔍 Search Integration
| Engine | URL |
|--------|-----|
| Brave (default) | search.brave.com |
| Google | google.com |
| DuckDuckGo | duckduckgo.com |
| Bing | bing.com |
| Startpage | startpage.com |

- **Bookmark search** - Filter your links as you type (shows matches in dropdown)
- **Keyboard shortcut** - Press `/` to focus search

### 📥 Import/Export
- **Bonjour Import** - Full migration from Bonjourr JSON exports (preserves folder structure)
- **Browser Bookmarks** - Import Chrome/Firefox HTML bookmark exports
- **JSON Export** - Complete backup including custom icons
- **Data portability** - Simple JSON format, easy to edit manually

### 🌗 Themes
| Theme | Description |
|-------|-------------|
| **Dark** (default) | Dark background (#0a0a0a) with light text |
| **Light** | Light background (#f5f5f5) with dark text |
| **Auto** | Follows system preference via `prefers-color-scheme` |

### 📱 Context Menus
**Right-click on bookmark:**
- Open in new tab
- Copy URL to clipboard
- Add/remove from favorites
- Edit (name, URL, custom icon)
- Delete

**Right-click on tab:**
- Edit tab (name, color)
- Add new link
- Delete tab

**Right-click on folder chip:**
- Edit folder name
- Delete folder

---

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone or download the focus folder
cd focus

# Start the container (builds automatically)
docker-compose up -d

# Open http://localhost:5000
```

**Your data is stored in `./data/` folder** - this persists your bookmarks, settings, and custom icons.

### Option 2: Docker Run

```bash
# Build the image
docker build -t focus .

# Run with a local folder for data persistence (REQUIRED)
docker run -d \
  --name focus \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e TZ=America/Chicago \
  --restart unless-stopped \
  focus

# Open http://localhost:5000
```

### Option 3: Docker with Named Volume

```bash
# Run with a Docker-managed volume
docker run -d \
  --name focus \
  -p 5000:5000 \
  -v focus_data:/app/data \
  -e TZ=America/Chicago \
  --restart unless-stopped \
  focus

# Open http://localhost:5000
```

### Option 4: Python (Development)

```bash
cd focus
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

---

## Data Persistence (Important!)

Focus stores all your data in a single folder that **must be mapped** for Docker installations:

| Path | Contents | Purpose |
|------|----------|---------|
| `/app/data/bookmarks.json` | Settings, tabs, folders, bookmarks, favorites | Main data file |
| `/app/data/wallpaper_cache/` | Uploaded images | Custom wallpapers |

### Volume Mapping Examples

**Docker Compose** (in docker-compose.yml):
```yaml
volumes:
  - ./data:/app/data          # Local folder (recommended)
  # OR
  - focus_data:/app/data     # Named volume
```

**Docker Run**:
```bash
# Local folder - easy to backup/inspect
-v /home/user/focus-data:/app/data

# Named volume - Docker managed
-v focus_data:/app/data

# Current directory
-v $(pwd)/data:/app/data
```

### Backup & Restore

**Backup:**
```bash
# Copy the data folder
cp -r ./data ./focus-backup-$(date +%Y%m%d)

# Or just the main file
cp ./data/bookmarks.json ./bookmarks-backup.json
```

**Restore:**
```bash
# Replace the data folder and restart
cp -r ./focus-backup-20240116 ./data
docker-compose restart
```

**Export from UI:**
- Settings → Export Data → Downloads complete JSON with all custom icons

### First Run

On first start, Focus automatically creates:
```
data/
├── bookmarks.json      # Default empty configuration
└── wallpaper_cache/    # Empty folder for uploads
```

No manual setup required - just ensure the volume is mapped.

---

## Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | Python 3.9+ / Flask 3.0 | REST API, wallpaper proxies, data persistence |
| Frontend | Vanilla JavaScript (ES6+) | Single-page application, no framework |
| Styling | CSS3 Grid + Flexbox + Custom Properties | Responsive layout, theming |
| Storage | JSON file | Simple, portable, human-readable |
| Fonts | Google Fonts (Inter) | Clean, modern typography |
| Icons | Google Favicon Service | 128px high-quality favicons |

### Design Principles

1. **Single File Frontend** - All HTML/CSS/JS in one file (~700 lines)
2. **No Build Step** - No webpack, no npm, no compilation
3. **No External JS Dependencies** - Pure vanilla JavaScript
4. **Mobile-First Responsive** - Works on all screen sizes
5. **Progressive Enhancement** - Core features work without JavaScript errors
6. **Server-Side Proxies** - CORS-free wallpaper fetching

### File Structure

```
focus/
├── app.py                 # Flask REST API (320 lines)
│   ├── Data endpoints     # GET/POST /api/data
│   ├── Import parsers     # Bonjour JSON, Browser HTML
│   ├── Wallpaper proxies  # Bing, Picsum endpoints
│   └── File uploads       # Custom wallpaper support
├── requirements.txt       # Python dependencies (just Flask)
├── Dockerfile            # Python 3.11-slim + gunicorn
├── docker-compose.yml    # Volume mapping, health checks
├── README.md             # This documentation
├── templates/
│   └── index.html        # Complete frontend (HTML + CSS + JS)
└── data/                  # ⬅️ PERSIST THIS FOLDER (Docker volume)
    ├── bookmarks.json     # All user data - settings, categories, bookmarks, favorites
    └── wallpaper_cache/   # Uploaded custom wallpaper images
```

### Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│  Flask API  │────▶│  JSON File  │
│  (Vanilla   │◀────│  (Python)   │◀────│  (Storage)  │
│     JS)     │     └─────────────┘     └─────────────┘
└─────────────┘            │
                           ▼
                  ┌─────────────────┐
                  │ External APIs   │
                  │ • Bing (proxy)  │
                  │ • NASA (direct) │
                  │ • Picsum(proxy) │
                  └─────────────────┘
```

---

## API Reference

### Data Endpoints

#### GET /api/data
Returns complete application state.

#### POST /api/data
Saves complete application state.

### Import Endpoints

#### POST /api/import/bonjour
Import from Bonjourr JSON export. Preserves folder structure.

**Request Body:** Raw Bonjourr export JSON

#### POST /api/import/browser
Import from browser HTML bookmarks.

**Request Body:**
```json
{ "html": "<DL>...</DL>" }
```

### Wallpaper Proxy Endpoints

#### GET /api/wallpaper/bing
Proxies Bing Image of the Day API (bypasses CORS).

**Response:**
```json
{ "url": "https://www.bing.com/th?id=..." }
```

#### GET /api/wallpaper/picsum?category=nature
Returns Lorem Picsum random image URL. Category affects daily seed for variety.

**Response:**
```json
{ "url": "https://picsum.photos/seed/123/1920/1080" }
```

### File Endpoints

#### POST /api/wallpaper/upload
Upload custom wallpaper image.

**Request:** multipart/form-data with `file` field

#### GET /api/wallpaper/cache/{filename}
Serve uploaded wallpaper.

#### GET /api/export
Returns JSON data (same as GET /api/data).

---

## Data Format

### Complete Structure

```javascript
{
  "settings": {
    "name": "Greg",                    // For greeting
    "showGreeting": true,
    "showTime": true,
    "showSearch": true,
    "searchEngine": "brave",           // brave|google|duckduckgo|bing|startpage
    "theme": "dark",                   // dark|light|auto
    "clockFormat": "24",               // 12|24
    "wallpaper": {
      "type": "bing",                  // none|bing|nasa|unsplash|custom|solid|gradient
      "url": "",                       // For custom type
      "unsplashCategory": "nature",    // For unsplash/picsum type
      "color": "#1a1a2e",              // For solid type
      "gradient": "linear-gradient(...)", // For gradient type
      "blur": 0,                       // 0-30
      "dim": 30                        // 0-70
    }
  },
  "categories": [
    {
      "id": "cat_0",
      "name": "StartPage",
      "color": "#22c55e",
      "links": [
        {
          "id": "link_123",
          "name": "GitHub",
          "url": "https://github.com",
          "customIcon": "data:image/png;base64,..."  // Optional
        }
      ],
      "subfolders": [
        {
          "id": "folder_456",
          "name": "Social",
          "links": [...]
        }
      ]
    }
  ],
  "favorites": [
    {
      "id": "link_123",      // Same ID as in categories
      "name": "GitHub",
      "url": "https://github.com",
      "customIcon": "..."
    }
  ]
}
```

### Category Colors (Presets)

```javascript
['#22c55e', '#6366f1', '#f59e0b', '#ef4444', '#f97316', 
 '#14b8a6', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
```

### Gradient Presets

| Name | CSS Value |
|------|-----------|
| Sunset | `linear-gradient(135deg, #ff6b6b 0%, #feca57 100%)` |
| Ocean | `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` |
| Forest | `linear-gradient(135deg, #11998e 0%, #38ef7d 100%)` |
| Night | `linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)` |
| Aurora | `linear-gradient(135deg, #00c6ff 0%, #0072ff 100%)` |
| And 7 more... | |

---

## Responsive Breakpoints

| Screen Width | Grid | Icon Size | Target Device |
|--------------|------|-----------|---------------|
| > 600px | `auto-fill, minmax(80px, 1fr)` | 56×56px | Desktop, tablets |
| ≤ 600px | `auto-fill, minmax(75px, 1fr)` | 46×46px | Phones |
| ≤ 400px | Fixed 5 columns | 42×42px | Samsung Fold outer screen |

---

## CSS Custom Properties (Theming)

### Dark Theme (Default)
```css
:root {
  --bg-primary: #0a0a0a;
  --bg-glass: rgba(255, 255, 255, 0.06);
  --bg-glass-hover: rgba(255, 255, 255, 0.12);
  --bg-card: rgba(255, 255, 255, 0.04);
  --text-primary: #ffffff;
  --text-secondary: rgba(255, 255, 255, 0.7);
  --text-muted: rgba(255, 255, 255, 0.4);
  --border-color: rgba(255, 255, 255, 0.08);
  --accent: #6366f1;
  --radius: 14px;
  --radius-sm: 10px;
}
```

### Light Theme
```css
.light-theme {
  --bg-primary: #f5f5f5;
  --bg-glass: rgba(255, 255, 255, 0.8);
  --bg-glass-hover: rgba(255, 255, 255, 0.95);
  --text-primary: #1a1a1a;
  --text-secondary: rgba(0, 0, 0, 0.7);
  --text-muted: rgba(0, 0, 0, 0.4);
  --border-color: rgba(0, 0, 0, 0.08);
}
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `/` | Focus search bar |
| `Escape` | Close modal, blur search, hide context menu |
| `Enter` | Execute web search (when in search bar) |

---

## Troubleshooting

### Links not appearing
- Check browser console (F12) for JavaScript errors
- Verify `data/bookmarks.json` exists and is valid JSON
- Ensure you have at least one category/tab created

### Wallpaper not loading
- **Bing**: Should work via server proxy; check Flask console for errors
- **NASA**: Uses DEMO_KEY with rate limits; may fail if exceeded
- **Random Photos**: Uses Lorem Picsum; verify internet connectivity
- Try "None" to confirm app works without wallpaper

### Icons showing letters instead of favicons
- Normal behavior when Google's favicon service doesn't have the icon
- Colored placeholder uses first letter of site name
- Upload a custom icon for better appearance

### Mobile scroll buttons not showing
- Ensure many tabs exist (enough to overflow)
- Buttons appear only when content is scrollable
- Touch-drag also works on mobile tab bar

### Import not working
- **Bonjour**: Must be raw JSON export, not settings backup
- **Browser**: Must be HTML format (Bookmarks → Export)
- Check console for parsing errors

---

## Migration from Bonjourr

1. In Bonjourr extension, go to **Settings** → **Export all settings**
2. Save the JSON file
3. In Focus, click **Settings** (gear icon) → **Import Bonjour Backup**
4. Select the JSON file
5. All links and folders will be imported, preserving structure

**What transfers:**
- All bookmarks with names and URLs
- Folder organization within groups
- Link groups become Focus tabs
- Greeting name
- Display preferences (time, search, greeting toggles)

**What doesn't transfer:**
- Weather settings (not supported in Focus)
- Notes (not supported in Focus)
- Custom CSS (different styling system)
- Exact visual positioning

---

## Comparison with Bonjourr

| Feature | Focus | Bonjourr |
|---------|:------:|:--------:|
| Self-hosted | ✅ | ❌ (Chrome extension) |
| Icon grid layout | ✅ | ✅ |
| Tab groups | ✅ | ✅ |
| Folders/Subfolders | ✅ | ✅ |
| Favorites bar | ✅ | ❌ |
| Wallpapers | ✅ | ✅ |
| Custom icons | ✅ | ❌ |
| Drag & drop | ✅ | ✅ |
| Weather widget | ❌ | ✅ |
| Notes widget | ❌ | ✅ |
| Offline/PWA | ❌ | ✅ |
| Custom domains | ✅ | ❌ |
| Data portability | ✅ JSON | ✅ JSON |
| No account required | ✅ | ✅ |

---

## Development

### Running in Development

```bash
cd focus
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Validating Changes

After modifying `index.html`, validate JavaScript:
```bash
cat templates/index.html | sed -n '/<script>/,/<\/script>/p' | \
  sed '1d;$d' > /tmp/test.js && node --check /tmp/test.js
```

After modifying `app.py`, validate Python:
```bash
python -m py_compile app.py
```

### Code Conventions

- **Python**: PEP 8, type hints optional
- **JavaScript**: ES6+, string concatenation for HTML (avoids template literal issues)
- **CSS**: Custom properties, mobile-first media queries
- **HTML IDs**: camelCase (`tabNav`, `searchInput`)

---

## Deployment

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Set to `development` for debug mode |
| `TZ` | `UTC` | Timezone for greeting (e.g., `America/Chicago`, `Europe/London`) |

### Custom Port

```bash
# Map to port 8080 instead of 5000
docker run -d -p 8080:5000 -v ./data:/app/data focus
```

### Reverse Proxy (nginx)

```nginx
server {
    listen 80;
    server_name focus.example.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### With HTTPS (Caddy)

```
focus.example.com {
    reverse_proxy localhost:5000
}
```

### Synology NAS / Unraid / TrueNAS

1. Create a folder for data: `/volume1/docker/focus/data`
2. Map the volume: `-v /volume1/docker/focus/data:/app/data`
3. Set timezone to match your NAS
4. Expose port 5000 (or remap to desired port)

---

## License

MIT License - Feel free to modify and self-host.

---

## Credits

- **Font**: [Inter](https://rsms.me/inter/) by Rasmus Andersson
- **Inspiration**: [Bonjourr](https://bonjourr.fr/)
- **Wallpapers**: Microsoft Bing, NASA APOD, Lorem Picsum
- **Favicon Service**: Google S2 Favicons

---

## Changelog

### v2.1.0 (Current)
- Added tab groups (categories) with color coding
- Added subfolders within tabs
- Added favorites bar for quick access
- Added custom icon upload for bookmarks
- Added drag-to-create-folder functionality
- Added server-side wallpaper proxies (fixes Bing CORS)
- Replaced Unsplash with Lorem Picsum (Unsplash API deprecated)
- Added gradient wallpaper presets
- Fixed mobile tab scroll buttons
- Improved responsive design
- Full Bonjour import with folder structure preservation

### v2.0.0 (Bonjourr Style)
- Complete redesign with icon grid layout
- Wallpaper system with multiple sources
- Search integration with 5 engines
- Light/dark/auto themes
- Responsive breakpoints for mobile

### v1.0.0
- Initial release
