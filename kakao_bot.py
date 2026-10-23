import os
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask
import threading

app = Flask(__name__)

# --- 設定區 ---
KAKAO_URL = "https://open.kakao.com/o/gU3wVbG"
TELEGRAM_BOT_TOKEN = "8977176422:AAGhPii3CcVElSm6KD1otLIsC9AXygTJnv4"
TELEGRAM_CHAT_ID = "8688789964"

last_count = None

def get_kakao_member_count():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(KAKAO_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 抓取 KakaoTalk 人數標籤
        count_element = soup.select_one("span.txt_num") or soup.select_one(".num_user") or soup.select_one(".count")
        if count_element:
            return count_element.text.strip()
        
        # 備用抓取法
        for span in soup.find_all(["span", "p"]):
            text = span.text.strip()
            if text.isdigit() and len(text) <= 4:
                return text
        return "未知"
    except Exception as e:
        print(f"抓取失敗: {e}")
        return None

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
        if current_count and current_count != last_count:
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
    msg = f"🤖 KakaoTalk 監控小幫手連線正常！\n📊 當前群組人數為：{current_count} 人"
    send_telegram_msg(msg)
    return f"Kakao Monitor is running! Current count: {current_count}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
