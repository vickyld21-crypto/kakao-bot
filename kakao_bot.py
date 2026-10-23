import os
import time
import requests
from flask import Flask, request
import threading

app = Flask(__name__)

# --- 設定區 ---
TELEGRAM_BOT_TOKEN = "8977176422:AAGhPii3CcVElSm6KD1otLIsC9AXygTJnv4"
TELEGRAM_CHAT_ID = "8688789964"

# 預設目前的群組人數狀態（小庭可以隨時在這邊修改，或者透過網頁更新）
current_status = "900/900人 (滿員)"
last_status = None

def send_telegram_msg(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        r = requests.post(url, data=payload, timeout=10)
        print("Telegram 發送結果:", r.json())
    except Exception as e:
        print("Telegram 發送例外:", e)

@app.route("/")
def home():
    global current_status
    # 檢查網址有沒有帶入自訂人數，例如: https://你的網址/?count=899/900
    new_count = request.args.get('count')
    if new_count:
        current_status = new_count
        
    msg = f"🤖 邊邊群組人數小幫手連線正常！\n📊 當前群組狀態：{current_status}"
    send_telegram_msg(msg)
    return f"""
    <h2>Kakao Monitor is running!</h2>
    <p>目前狀態：<b>{current_status}</b></p>
    <p>若要隨時更新並推送到 Telegram，請點擊：<br>
    <a href="/?count=900/900人">更新為 900/900人</a> | 
    <a href="/?count=899/900人 (有空位囉！)">更新為 899/900人 (有空位)</a></p>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
