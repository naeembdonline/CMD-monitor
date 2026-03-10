@echo off
==================================================
Fiverr Monitor - Chrome Debug Mode Launcher
==================================================
বিদ্যমান Chrome বন্ধ হচ্ছে...
taskkill /F /IM chrome.exe 2>nul
timeout /t 2 /nobreak >nul
ডিবাগ মোডে Chrome শুরু হচ্ছে...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:/chrome-debug"
✅ Chrome ডিবাগ মোডে চালু হয়েছে!
echo Fiverr-এ লগইন করুন (একবারের জন্য)
pause
