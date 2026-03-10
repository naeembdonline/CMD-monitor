# 🌐 Render.com Deployment Guide

## এই প্রজেক্ট GitHub-এ আপলোড হয়ে গেছে!

**🔗 Repository:** https://github.com/naeembdonline/CMD-monitor

---

## 🚀 Render.com এ ডিপ্লয় করুন

### ধাপ ১: Render.com এ সাইন আপ করুন

1. যান: https://render.com
2. **Sign Up** ক্লিক করুন
3. GitHub দিয়ে সাইন আপ করুন (ফ্রি)
4. Email ভেরিফাই করুন

---

### ধাপ ২: নতুন Web Service তৈরি করুন

1. **New +** বাটনে ক্লিক করুন
2. **Web Service** সিলেক্ট করুন
3. **Connect GitHub** ক্লিক করুন
4. `CMD-monitor` রিপোজিটরি খুঁজুন ও কানেক্ট করুন

---

### ধাপ ৩: কনফিগারেশন সেট করুন

| ফিল্ড | ভ্যালু |
|-------|--------|
| **Name** | `fiverr-monitor-server` |
| **Environment** | `Python 3` |
| **Branch** | `main` |
| **Root Directory** | `server` |
| **Build Command** | `pip install -r requirements_server.txt` |
| **Start Command** | `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT server:app` |

---

### ধাপ ৪: Environment Variables যোগ করুন

ডিপ্লয় শুরু হওয়ার পর, আপনার সার্ভিস ড্যাশবোর্ডে যান → **Environment** ট্যাব

নিচের ভেরিয়েবলগুলো যোগ করুন:

```
AGENT_TOKEN=UU05osvenV7JqGnfvsWO16A8887pr3T4iij5i5dnf_A
DASHBOARD_USER=admin
DASHBOARD_PASS=Fiverr@Monitor2026
SECRET_KEY=RUA1TvsgIztFiaxZFDkbANmrme1V4cWETkrAUZtV-6gNJyq0s45D-0svG0OiVx5Nc12e352Pw1eGDE-hCttZKQ
```

---

### ধাপ ৫: ডিপ্লয় সম্পন্ন হওয়ার পর

- ৩-৫ মিনিট অপেক্ষা করুন
- আপনি একটি URL পাবেন যেমন: `https://fiverr-monitor-server.onrender.com`

---

## 🔄 আপনার Agent .env আপডেট করুন

Render থেকে পাওয়া URL দিয়ে agent `.env` আপডেট করুন:

```env
SERVER_URL=https://fiverr-monitor-server.onrender.com
```

---

## 🧪 টেস্ট করুন

### 1. সার্ভার হেলথ চেক
```bash
curl https://your-app.onrender.com/health
```

### 2. ড্যাশবোর্ড খুলুন
```
https://your-app.onrender.com/dashboard.html
```

### 3. লগইন করুন
- Username: `admin`
- Password: `Fiverr@Monitor2026`

---

## 📱 মোবাইল অ্যাপ ইনস্টল করুন

1. মোবাইলে ড্যাশবোর্ড URL খুলুন
2. Chrome মেনু (⋮) → **"Add to Home Screen"**
3. নোটিফিকেশন অনুমতি দিন

---

## ✅ এজেন্ট চালু করুন

```cmd
cd Desktop\CMD-monitor\agent
venv\Scripts\activate
python agent.py
```

---

**সব কিছু রেডি! এখন Fiverr মেসেজ মনিটর করতে পারবেন! 🎉**
