# 🚀 Quick Setup Guide - Fiverr Remote Monitor

## ✅ যা যা তৈরি করা হয়েছে | What has been created

```
CMD-monitor/
├── agent/
│   ├── agent.py              ✅ প্রধান মনিটরিং এজেন্ট
│   ├── .env.example          ✅ এনভায়রনমেন্ট ভেরিয়েবল টেমপ্লেট
│   └── requirements_agent.txt ✅ পাইথন ডিপেন্ডেন্সি
├── server/
│   ├── server.py             ✅ ফ্লাস্ক + SocketIO সার্ভার
│   ├── .env.example          ✅ সার্ভার কনফিগারেশন
│   ├── requirements_server.txt ✅ সার্ভার ডিপেন্ডেন্সি
│   └── render.yaml           ✅ Render ডিপ্লয়মেন্ট কনফিগ
├── dashboard/
│   ├── dashboard.html        ✅ ওয়েব ইন্টারফেস
│   ├── manifest.json         ✅ PWA ম্যানিফেস্ট
│   ├── sw.js                 ✅ সার্ভিস ওয়ার্কার
│   ├── push_handler.js       ✅ পুশ নোটিফিকেশন
│   └── bubblewrap.config.json ✅ APK জেনারেশন
├── start-chrome-debug.bat    ✅ Chrome ডিবাগ লঞ্চার
├── .gitignore               ✅ Git ইগনোর ফাইল
├── README.md                ✅ মূল ডকুমেন্টেশন
└── SETUP_GUIDE.md           ✅ এই ফাইল
```

---

## ⚠️ প্রথমে করণীয় | First Things First

### 1️⃣ Python ইনস্টল করুন (আবশ্যিক!)

1. [Python 3.12 ডাউনলোড করুন](https://www.python.org/downloads/release/python-3120/)
2. ইনস্টল করার সময় **"Add Python to PATH"** চেকমার্ক করুন!
3. ইনস্টল করার পর CMD খুলে চেক করুন:
   ```cmd
   python --version
   ```

---

## 📋 ধাপে ধাপে সেটআপ | Step-by-Step Setup

### ধাপ ১: এজেন্ট সেটআপ | Step 1: Agent Setup

```cmd
# ফোল্ডারে যান
cd Desktop\CMD-monitor\agent

# ভার্চুয়াল এনভায়রনমেন্ট তৈরি করুন
python -m venv venv

# এক্টিভেট করুন
venv\Scripts\activate

# ডিপেন্ডেন্সি ইনস্টল করুন
pip install -r requirements_agent.txt
```

### ধাপ ২: .env ফাইল তৈরি করুন

```cmd
# এজেন্ট ফোল্ডারে
cd Desktop\CMD-monitor\agent
copy .env.example .env
notepad .env
```

নিচের মত করে পূরণ করুন:

```env
SERVER_URL=https://your-app.onrender.com  # পরে আপডেট করবেন
AGENT_TOKEN=আপনার_টোকেন
CHECK_INTERVAL=45
```

টোকেন জেনারেট করুন:
```cmd
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### ধাপ ৩: Chrome ডিবাগ মোড চালু করুন

```cmd
# মেইন ফোল্ডার থেকে
cd Desktop\CMD-monitor
start-chrome-debug.bat
```

Chrome খুললে **Fiverr-এ লগইন করুন** (একবারের জন্য)

---

## 🌐 ধাপ ৪: Render.com এ সার্ভার ডিপ্লয় করুন

### 4.1 সার্ভার ফোল্ডারে যান ও .env তৈরি করুন

```cmd
cd Desktop\CMD-monitor\server
copy .env.example .env
notepad .env
```

### 4.2 টোকেন জেনারেট করুন

```cmd
# AGENT_TOKEN (এজেন্টের সাথে একই হতে হবে!)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 4.3 Render.com এ ডিপ্লয় করুন

1. [render.com](https://render.com) এ সাইন আপ করুন (ফ্রি)
2. **New +** → **Web Service**
3. আপনার GitHub রিপো কানেক্ট করুন

| সেটিং | ভ্যালু |
|-------|--------|
| Name | `fiverr-monitor-server` |
| Environment | `Python 3` |
| Root Directory | `server` |
| Build Command | `pip install -r requirements_server.txt` |
| Start Command | `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT server:app` |

### 4.4 Environment Variables সেট করুন

Render ড্যাশবোর্ডে যান → **Environment** ট্যাব → এই ভেরিয়েবলগুলো যোগ করুন:

```
AGENT_TOKEN=আপনার_টোকেন
DASHBOARD_USER=admin
DASHBOARD_PASS=শক্তিশালী_পাসওয়ার্ড
SECRET_KEY=আপনার_সিক্রেট_কি
```

### 4.5 ডিপ্লয় হওয়ার পর

আপনার সার্ভার URL পাবেন যেমন: `https://fiverr-monitor-server.onrender.com`

এই URL টি কপি করে এজেন্টের `.env` ফাইলে `SERVER_URL` আপডেট করুন।

---

## 🖥️ ধাপ ৫: ড্যাশবোর্ড ব্যবহার করুন

1. `dashboard/dashboard.html` ফাইলটি ব্রাউজারে খুলুন
2. আপনার ড্যাশবোর্ড ইউজারনেম ও পাসওয়ার্ড দিয়ে লগইন করুন
3. এজেন্ট চালু করুন:
   ```cmd
   cd Desktop\CMD-monitor\agent
   venv\Scripts\activate
   python agent.py
   ```

---

## 📱 মোবাইল অ্যাপ

### PWA হিসেবে ইনস্টল করুন (সহজ পদ্ধতি)

1. মোবাইলে `dashboard.html` ফাইলটির URL খুলুন
2. Chrome মেনু (⋮) → **"Add to Home Screen"** বা **"Install App"**
3. নোটিফিকেশন অনুমতি দিন

---

## 🎉 সব কিছু রেডি!

| কম্পোনেন্ট | স্ট্যাটাস |
|----------|---------|
| Agent | ✅ তৈরি |
| Server | ✅ তৈরি |
| Dashboard | ✅ তৈরি |
| PWA | ✅ তৈরি |

**এখন আপনার করণীয়:**
1. Python ইনস্টল করুন
2. Render.com এ সার্ভার ডিপ্লয় করুন
3. এজেন্ট চালু করুন

---

## 🔧 ট্রাবলশুটিং | Troubleshooting

| সমস্যা | সমাধান |
|-------|---------|
| Chrome সংযোগ ব্যর্থ | `start-chrome-debug.bat` রান করুন |
| Agent চলছে না | `python agent.py` দিয়ে লগ চেক করুন |
| সার্ভার স্লিপ করছে | ফ্রি টিয়ার - এজেন্ট অটো-ওয়েক করবে |

---

**Sources:**
- [Fiverr Monitor GitHub](https://github.com/naeembdonline/CMD-monitor)
