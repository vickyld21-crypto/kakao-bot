import os
import time
import re
import asyncio
import threading
import requests
from flask import Flask
from playwright.async_api import async_playwright

app = Flask(__name__)

# --- 設定區 ---
KAKAO_URL = "https://open.kakao.com/o/gU3wVbG"
TELEGRAM_BOT_TOKEN = "8977176422:AAGhPii3CcVElSm6KD1otLIsC9AXygTJnv4"
TELEGRAM_CHAT_ID = "8688789964"

current_status = "監控中..."

def send_telegram_msg(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram 發送例外:", e)

async def check_kakao_slots():
    """使用 Playwright 載入動態頁面並檢查人數"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15"
        )
        page = await context.new_page()
        try:
            await page.goto(KAKAO_URL, wait_until="networkidle", timeout=25000)
            content = await page.content()
            await browser.close()
            
            # 搜尋類似 900/900 或 899/900 的格式
            match = re.search(r'(\d{1,4}\s*[/／]\s*\d{1,4})', content)
            if match:
                return match.group(1).replace(" ", "")
            
            return "無資料"
        except Exception as e:
            print("抓取失敗:", e)
            await browser.close()
            return "抓取錯誤"

def monitor_task():
    """每 30 秒自動檢查一次，只有『不是 900/900』時才發 Telegram"""
    global current_status
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    while True:
        try:
            count_str = loop.run_until_complete(check_kakao_slots())
            if count_str not in ["無資料", "抓取錯誤"]:
                current_status = count_str
                
                # 🎯 核心判斷：只要抓到的數字「不是 900/900」，立刻發 Telegram 警報！
                if count_str != "900/900":
                    msg = f"🚨 **邊邊群組有空位囉！** 🚨\n\n當前群組人數：**{count_str}**\n快點進去搶名額：\n{KAKAO_URL}"
                    send_telegram_msg(msg)
        except Exception as e:
            print("監控執行異常:", e)
            
        time.sleep(30) # 每 30 秒自動檢查一次

# 啟動背景自動監控線程
threading.Thread(target=monitor_task, daemon=True).start()

@app.route("/")
def home():
    return f"Kakao Monitor is active! Current status: {current_status}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
