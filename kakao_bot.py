import os
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask
import threading
import re

app = Flask(__name__)

# --- 設定區 ---
KAKAO_URL = "https://open.kakao.com/o/gU3wVbG"
TELEGRAM_BOT_TOKEN = "8977176422:AAGhPii3CcVElSm6KD1otLIsC9AXygTJnv4"
TELEGRAM_CHAT_ID = "8688789964"

last_count = None

def get_kakao_member_count():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:
        res = requests.get(KAKAO_URL, headers=headers, timeout=10)
        html_text = res.text
        
        # 1. 直接在整頁原始碼中搜尋類似 "900/900" 或帶斜線的人數格式
        match = re.search(r'(\d{1,4})\s*[/／]\s*(\d{1,4})', html_text)
        if match:
            current = match.group(1)
            max_limit = match.group(2)
            return f"{current}/{max_limit}人"

        # 2. 備用：尋找包含數字的文字
        numbers = re.findall(r'\b([1-9]\d{2,3})\b', html_text)
        if numbers:
            return f"{numbers[0]}人"

        return "無法解析"
    except Exception as e:
        print(f"抓取失敗: {e}")
        return "抓取錯誤"

def send_telegram_msg(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        r = requests.post(url, data=payload, timeout=10)
        print("Telegram 發送結果:", r.json())
    except Exception as e:
        print("Telegram 發送例外:", e)

# 背景定期監控任務 (每 3 分鐘檢查一次)
def background_monitor():
    global last_count
    while True:
        current_count = get_kakao_member_count()
        if current_count and current_count not in ["無法解析", "抓取錯誤"] and current_count != last_count:
            if last_count is not None:
                msg = f"🔔 KakaoTalk 群組人數變動！\n舊人數：{last_count}\n最新人數：{current_count}"
                send_telegram_msg(msg)
            last_count = current_count
        time.sleep(180)

# 啟動背景線程
threading.Thread(target=background_monitor, daemon=True).start()

@app.route("/")
def home():
    current_count = get_kakao_member_count()
    msg = f"🤖 KakaoTalk 監控小幫手連線正常！\n📊 當前群組人數為：{current_count}"
    send_telegram_msg(msg)
    return f"Kakao Monitor is running! Current count: {current_count}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
