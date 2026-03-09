# 🚀 Fiverr Remote Monitor System

**ফাইভার রিমোট মনিটর সিস্টেম - সম্পূর্ণ সেটআপ গাইড**

A complete, production-ready system for monitoring and replying to Fiverr messages remotely from your office or mobile device. All components run on **free tiers** with no paid services required.

---

## 📋 Table of Contents / সূচিপত্র

- [System Overview](#system-overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Step 1: Home PC Setup](#step-1-home-pc-setup)
- [Step 2: Server Deployment](#step-2-server-deployment-on-rendercom)
- [Step 3: Dashboard Access](#step-3-dashboard-access)
- [Step 4: Android App Setup](#step-4-android-app-setup)
- [Security Checklist](#security-checklist)
- [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview / সিস্টেম ওভারভিউ

The system consists of **5 components**:

1. **`agent.py`** - Runs on your home PC, monitors Fiverr inbox via Chrome
2. **`server.py`** - Secure bridge between agent and dashboard (hosted on Render)
3. **`dashboard.html`** - Web interface for desktop browsers
4. **PWA Files** - Progressive Web App for mobile devices
5. **Documentation** - Complete setup and usage guides

```
┌─────────────────┐         WebSocket          ┌─────────────────┐
│  Home PC        │ ◄─────────────────────────► │  Render Server  │
│  (agent.py)     │                             │  (server.py)    │
│  Chrome + Fiverr│                             │  Free Tier      │
└─────────────────┘                             └────────┬────────┘
                                                          │
                                                          ▼
                                              ┌─────────────────────┐
                                              │  Dashboard / PWA    │
                                              │  (Web + Mobile)     │
                                              └─────────────────────┘
```

---

## ✨ Features / বৈশিষ্ট্য

### Agent (Home PC)
- ✅ Attaches to existing Chrome session (no login required)
- ✅ Monitors Fiverr inbox every 45 seconds
- ✅ Detects and forwards new messages via WebSocket
- ✅ Sends replies naturally with human-like typing
- ✅ Auto-reconnects on connection drops
- ✅ Silent background operation (< 200MB RAM)

### Server (Render.com Free Tier)
- ✅ Real-time WebSocket communication
- ✅ Secure session-based authentication
- ✅ Rate limiting and IP blocking
- ✅ Push notifications (Web Push API)
- ✅ In-memory message storage (last 100 messages)
- ✅ Auto-wakes from free tier sleep

### Dashboard (Web + Mobile)
- ✅ Clean, professional "internal tool" design
- ✅ Real-time message updates (no refresh needed)
- ✅ Agent online/offline status indicator
- ✅ Send and receive messages
- ✅ Browser notifications
- ✅ PWA support (install as app on Android)
- ✅ Offline mode with cached messages

---

## 🏗️ Architecture / আর্কিটেকচার

```
fiverr-monitor/
├── agent/
│   ├── agent.py              # Main monitoring agent
│   ├── .env.example          # Environment variables template
│   └── requirements_agent.txt # Python dependencies
├── server/
│   ├── server.py             # Flask + SocketIO server
│   ├── .env.example          # Server configuration
│   ├── requirements_server.txt
│   └── render.yaml           # Render deployment config
├── dashboard/
│   ├── dashboard.html        # Single-file web interface
│   ├── manifest.json         # PWA manifest
│   ├── sw.js                 # Service worker (offline support)
│   ├── push_handler.js       # Push notification handler
│   └── bubblewrap.config.json # APK generation config
└── README.md                 # This file
```

---

## 📦 Prerequisites / প্রয়োজনীয় মান

### Home PC
- **Windows** (Task Scheduler setup) or **Linux/Mac**
- **Google Chrome** (already logged into Fiverr)
- **Python 3.10+**
- Internet connection (always on)

### Server Deployment
- **GitHub account** (free)
- **Render.com account** (free tier)

### Access Device
- Any modern web browser
- Android Chrome (for PWA)
- Optional: Bubblewrap CLI (for APK generation)

---

## 🚀 Step 1: Home PC Setup / ধাপ ১: হোম পিসি সেটআপ

### 1.1 Start Chrome with Remote Debugging

**উইন্ডোজ / Windows:**

Create a batch file `start-chrome-debug.bat`:

```batch
@echo off
taskkill /F /IM chrome.exe 2>nul
timeout /t 2 /nobreak >nul
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:/chrome-debug"
```

**লিনাক্স / Linux:**

```bash
#!/bin/bash
pkill -f "chrome" 2>/dev/null
sleep 2
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-debug" &
```

**ম্যাক / macOS:**

```bash
#!/bin/bash
pkill -f "Chrome" 2>/dev/null
sleep 2
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-debug" &
```

**Execute this script once to start Chrome in debug mode.**
**এই স্ক্রিপ্টটি একবার এক্সিকিউট করুন ডিবাগ মোডে ক্রোম শুরু করতে।**

### 1.2 Log in to Fiverr (One-time only)

1. Chrome will open with remote debugging enabled
2. Go to **fiverr.com** and log in to your account
3. Keep this Chrome window open (you can minimize it)

**এটি একবারের জন্য - আপনার সেশন সংরক্ষিত থাকবে**
**This is one-time only - your session will be saved**

### 1.3 Install Python Dependencies

```bash
cd agent
pip install -r requirements_agent.txt
```

### 1.4 Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your values
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Generate AGENT_TOKEN:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Your `.env` file should look like:**

```env
SERVER_URL=https://your-app.onrender.com
AGENT_TOKEN=your_generated_token_here
CHECK_INTERVAL=45
HEARTBEAT_INTERVAL=30
RECONNECT_INTERVAL=10
```

### 1.5 Test the Agent

```bash
python agent.py
```

You should see:
```
==================================================
Fiverr Remote Monitor Agent শুরু হচ্ছে | Starting...
==================================================
ক্রোমের সাথে সফলভাবে সংযুক্ত হয়েছে | Successfully connected to Chrome
```

If successful, close with `Ctrl+C` and proceed to silent mode setup.

### 1.6 Auto-start on Boot (Windows)

**Create a Scheduled Task:**

1. Open **Task Scheduler** (`taskschd.msc`)
2. Click **"Create Basic Task"**
3. Name: `Fiverr Monitor Agent`
4. Trigger: **"When I log on"**
5. Action: **"Start a program"**
6. Program/script: `pythonw.exe`
7. Arguments: `"C:\path\to\agent\agent.py"`
8. Start in: `"C:\path\to\agent"`

**Or use command line:**

```batch
schtasks /create /tn "Fiverr Monitor Agent" /tr "pythonw.exe C:\path\to\agent\agent.py" /sc onlogon /rl highest /f
```

**Verify:**
```batch
schtasks /query /tn "Fiverr Monitor Agent"
```

### 1.7 Run Agent Silently

```bash
# No console window
pythonw agent.py

# Or use the batch file
start /B pythonw agent.py
```

---

## 🌐 Step 2: Server Deployment on Render.com / ধাপ ২: রেন্ডারে সার্ভার ডিপ্লয়মেন্ট

### 2.1 Prepare GitHub Repository

```bash
# Initialize git repo
cd fiverr-monitor
git init

# Add files
git add server/
git commit -m "Add Fiverr Monitor server"
```

Create `.gitignore`:
```
.env
__pycache__/
*.pyc
*.log
.DS_Store
```

Push to GitHub:
```bash
git remote add origin https://github.com/yourusername/fiverr-monitor.git
git branch -M main
git push -u origin main
```

### 2.2 Create Render.com Account

1. Go to **[render.com](https://render.com)**
2. Sign up with GitHub (free)
3. Verify your email

### 2.3 Deploy Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `fiverr-monitor-server` |
| **Environment** | `Python 3` |
| **Branch** | `main` |
| **Root Directory** | `server` |
| **Build Command** | `pip install -r requirements_server.txt` |
| **Start Command** | `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT server:app` |

4. **Click "Deploy"**

### 2.4 Set Environment Variables

After deployment starts, go to your service dashboard:

1. Click **"Environment"** tab
2. Add the following variables:

```env
# Generate these with Python
AGENT_TOKEN=<same as agent's AGENT_TOKEN>
DASHBOARD_USER=admin
DASHBOARD_PASS=<secure_password_12+_chars>
SECRET_KEY=<64_char_random_string>

# Generate VAPID keys for push notifications
VAPID_PRIVATE_KEY=<your_vapid_private_key>
VAPID_PUBLIC_KEY=<your_vapid_public_key>
VAPID_CLAIM_EMAIL=mailto:your@email.com
```

**Generate secure strings:**

```bash
# AGENT_TOKEN and SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# VAPID Keys (use this Python script)
python3 << 'EOF'
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

key = ec.generate_private_key(ec.SECP256R1())
private_bytes = key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
public_bytes = key.public_key().public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)

private_key = base64.urlsafe_b64encode(private_bytes.split(b'\n')[-2]).decode().rstrip('=')
public_key = base64.urlsafe_b64encode(public_bytes).decode().rstrip('=')

print(f"VAPID_PRIVATE_KEY={private_key}")
print(f"VAPID_PUBLIC_KEY={public_key}")
EOF
```

### 2.5 Wait for Deployment

- Initial deploy takes **3-5 minutes**
- You'll get a URL like: `https://fiverr-monitor-server.onrender.com`
- Save this URL for agent configuration

### 2.6 Handle Free Tier Sleep

Render free tier spins down after 15 minutes of inactivity. The agent will auto-wake the server on the first connection attempt.

**To manually wake:**
```bash
curl https://your-app.onrender.com/health
```

---

## 🖥️ Step 3: Dashboard Access / ধাপ ৩: ড্যাশবোর্ড অ্যাক্সেস

### Option A: Direct File Access

Simply open `dashboard/dashboard.html` in your browser.

**Update the SERVER_URL in dashboard.html:**

```javascript
const CONFIG = {
    SERVER_URL: 'https://your-app.onrender.com',
    API_BASE: 'https://your-app.onrender.com'
};
```

### Option B: Host on GitHub Pages (Free)

1. Create a `gh-pages` branch or use `docs/` folder
2. Upload dashboard files
3. Enable GitHub Pages in repository settings
4. Access at `https://yourusername.github.io/fiverr-monitor/`

### Using the Dashboard

1. **Login:** Use credentials from `DASHBOARD_USER` and `DASHBOARD_PASS`
2. **Monitor Messages:** New messages appear in real-time
3. **Send Replies:** Select a conversation, type reply, click Send
4. **Check Status:** Green dot = agent online, Red dot = offline

---

## 📱 Step 4: Android App Setup / ধাপ ৪: অ্যান্ড্রয়েড অ্যাপ সেটআপ

### Option A: PWA (Simplest - Recommended)

1. **Open dashboard URL in Chrome on Android:**
   ```
   https://your-app.onrender.com/dashboard.html
   ```

2. **Add to Home Screen:**
   - Tap menu (⋮)
   - Select **"Add to Home Screen"** or **"Install App"**
   - Confirm installation

3. **Grant Permissions:**
   - Allow **Notifications** when prompted
   - App will request push notification subscription

4. **Use as Native App:**
   - Opens in fullscreen (no browser UI)
   - Works offline
   - Receives push notifications

### Option B: Generate Real APK (Advanced)

#### Install Bubblewrap CLI

```bash
npm install -g @bubblewrap/cli
```

#### Initialize Project

```bash
cd dashboard
bubblewrap init --manifest https://your-app.onrender.com/manifest.json
```

#### Generate APK

```bash
bubblewrap build
```

#### Install on Android

1. Transfer `app-release.apk` to your phone
2. Enable **"Install from Unknown Sources"** in settings
3. Open the APK file to install

### Using the Mobile App

**Bottom Navigation:**

| Tab | Function |
|-----|----------|
| 📥 Inbox | View all conversations |
| 💬 Chat | Active conversation view |
| 🟢 Status | Agent connection status |
| ⚙️ Settings | App preferences |

**Features:**
- Pull-to-refresh on inbox
- Swipe left for quick reply
- Offline message viewing
- Push notifications (even when app closed)

---

## 🔒 Security Checklist / নিরাপত্তা চেকলিস্ট

Before going live, ensure all items are checked:

- [ ] **AGENT_TOKEN** is minimum 32 characters, randomly generated
- [ ] **DASHBOARD_PASS** is minimum 12 characters, not common
- [ ] **SECRET_KEY** is minimum 64 characters, randomly generated
- [ ] VAPID keys properly generated (not placeholder values)
- [ ] All secrets stored in `.env` files (never committed to git)
- [ ] `.env` files added to `.gitignore`
- [ ] Dashboard login page is working
- [ ] Rate limiting is enabled on server
- [ ] IP blocking works after 3 failed logins
- [ ] WebSocket connections require authentication
- [ ] HTTPS enforced (Render provides this automatically)
- [ ] Agent runs as `pythonw` (no console window)
- [ ] Chrome debug profile is separate from main profile

---

## 🔧 Troubleshooting / সমস্যা সমাধান

### Agent Won't Connect to Chrome

**Problem:** `Failed to connect to Chrome`

**Solution:**
1. Verify Chrome is running with debug port:
   ```bash
   # Check if port 9222 is open
   netstat -an | findstr 9222  # Windows
   lsof -i :9222               # Linux/Mac
   ```

2. Start Chrome manually:
   ```bash
   chrome.exe --remote-debugging-port=9222 --user-data-dir="C:/chrome-debug"
   ```

3. Ensure only ONE Chrome instance is running with the debug profile

### Agent Can't Find Messages

**Problem:** `No conversations found`

**Solution:**
1. Check if Fiverr page structure changed (inspect elements)
2. Verify you're logged into Fiverr in the debug Chrome
3. Increase wait time in `agent.py`:
   ```python
   time.sleep(5)  # Increase from 2
   ```

### Server Keeps Sleeping

**Problem:** Server takes long to respond on first request

**Solution:**
1. This is normal on free tier (spins down after 15 min inactivity)
2. Agent will auto-wake on next connection attempt
3. To keep awake, use a cron job (not recommended - wastes free hours)

### Push Notifications Not Working

**Problem:** Notifications don't appear on mobile

**Solution:**
1. Verify VAPID keys are correctly set
2. Check browser notification permissions
3. Test with `testNotification()` in browser console
4. Ensure service worker is registered

### Dashboard Shows "Agent Offline"

**Problem:** Agent status always shows offline

**Solution:**
1. Check agent log file for errors
2. Verify AGENT_TOKEN matches on both sides
3. Test server endpoint directly:
   ```bash
   curl https://your-app.onrender.com/health
   ```

### High Memory Usage

**Problem:** Agent using more than 200MB RAM

**Solution:**
1. Reduce message history in server.py
2. Clear browser cache in debug profile
3. Restart agent daily via Task Scheduler

---

## 📊 Performance Tips / পারফরম্যান্স টিপস

### Agent Optimization
- Increase `CHECK_INTERVAL` to reduce CPU usage
- Use `pythonw` for silent operation
- Clear `last_seen.json` if it grows too large

### Server Optimization
- Free tier: 512MB RAM, 0.1 CPU (sufficient for this use case)
- Monitor Render dashboard for usage stats
- Upgrade to paid tier only if needed

### Mobile Optimization
- Use PWA instead of APK (smaller, updates automatically)
- Enable "Data Saver" in Chrome for slow connections
- Cache size is limited to 50 messages for offline

---

## 📝 Maintenance / রক্ষণাবেক্ষণ

### Daily
- Check agent.log for errors
- Verify agent status in dashboard

### Weekly
- Rotate agent.log (automatic after 1MB)
- Check Render dashboard for errors

### Monthly
- Update Python dependencies
- Rotate AGENT_TOKEN (requires updating both agent and server)
- Clear old messages from server memory

---

## 🆘 Support / সহায়তা

**Common Issues:**
1. Chrome updates may break selectors → Check Fiverr page structure
2. Render free tier sleep → Normal behavior
3. Network drops → Auto-reconnect handles this

**Debug Mode:**

Enable verbose logging in agent:
```python
logging.basicConfig(level=logging.DEBUG)
```

**Getting Help:**

When reporting issues, include:
- Agent OS and version
- Chrome version
- Python version
- Relevant log excerpts
- Steps to reproduce

---

## 📄 License / লাইসেন্স

This project is for personal use only. Ensure you comply with Fiverr's Terms of Service when using automation tools.

---

## 🎉 You're All Set!

Your Fiverr Remote Monitor System is now fully operational. You can:

✅ Monitor Fiverr messages from anywhere
✅ Reply to messages remotely
✅ Receive push notifications on mobile
✅ All running on free tiers

**আপনার ফাইভার রিমোট মনিটর সিস্টেম এখন সম্পূর্ণ কার্যকর।**

---

**Last Updated:** March 2026
**Version:** 1.0.0

---

**সফল হোক! / Good luck! 🚀**
