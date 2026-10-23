import time
import requests
from bs4 import BeautifulSoup

TOKEN = "8977176422:AAGhPii3CcVElSm6KD1otLIsC9AXygTJnv4"
CHAT_ID = "8688789964"
URL = "https://open.kakao.com/o/gU3wVbG"
CHECK_INTERVAL = 300

PROXIES = {
    'http': 'http://proxy.server:3128',
    'https': 'http://proxy.server:3128'
}

def send_telegram_message(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(api_url, data=payload, proxies=PROXIES, timeout=10)
    except Exception as e:
        print(f"發送失敗: {e}")

def get_group_member_count(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            elem = soup.find('span', class_='num') or soup.find('em', class_='count')
            if elem:
                return int(elem.text.strip().replace(',', ''))
            og = soup.find('meta', property='og:description')
            if og and '名' in og.get('content', ''):
                import re
                m = re.search(r'(\d+)名', og['content'])
                if m:
                    return int(m.group(1))
        return None
    except:
        return None

def main():
    print("=== 雲端 Kakao 監控小幫手啟動 ===")
    last_count = None
    send_telegram_message("🤖 您的 KakaoTalk 雲端監控小幫手已成功啟動！開始為您盯哨...")
    while True:
        count = get_group_member_count(URL)
        if count is not None:
            if last_count is None:
                last_count = count
                send_telegram_message(f"📊 目前監控中的群組人數為: {count} 人")
            elif count != last_count:
                diff = count - last_count
                diff_str = f"+{diff}" if diff > 0 else f"{diff}"
                msg = f"🚨 【Kakao 聊天室人數變動】\n先前人數: {last_count}\n目前人數: {count} 人 ({diff_str})"
                send_telegram_message(msg)
                last_count = count
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
