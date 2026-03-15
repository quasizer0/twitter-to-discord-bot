import requests
import xml.etree.ElementTree as ET
import os
import time

# --- 設定區 ---
TWITTER_USER = "HaBEoxo"  # 你要追蹤的帳號
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
LAST_TWEET_FILE = "last_tweet.txt"

# 準備多個備用鏡像站，防止單一網站 403 被擋
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.catsarch.com",
    "https://nitter.salastil.com",
    "https://nitter.poast.org",
    "https://nitter.woodland.cafe"
]

def get_latest_tweet():
    # 偽裝成一般的 Google Chrome 瀏覽器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for instance in NITTER_INSTANCES:
        rss_url = f"{instance}/{TWITTER_USER}/rss"
        print(f"嘗試連線: {rss_url}")
        
        try:
            response = requests.get(rss_url, headers=headers, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall('./channel/item')
                
                if items:
                    # 抓取最新貼文的連結
                    link = items[0].find('link').text
                    # 提取推文 ID 並組合成官方 X (Twitter) 網址，讓 Discord 預覽更漂亮
                    tweet_id = link.split('/')[-1].replace('#m', '')
                    return f"https://x.com/{TWITTER_USER}/status/{tweet_id}"
            else:
                print(f"連線失敗，狀態碼: {response.status_code}，切換下一個...")
                
        except Exception as e:
            print(f"發生錯誤: {e}，切換下一個...")
            
        time.sleep(2) # 稍微等待2秒再試下一個網站，避免被視為惡意攻擊
        
    print("所有鏡像站都無法連線。")
    return None

def main():
    latest_tweet = get_latest_tweet()
    if not latest_tweet:
        return

    last_tweet = ""
    if os.path.exists(LAST_TWEET_FILE):
        with open(LAST_TWEET_FILE, "r") as f:
            last_tweet = f.read().strip()

    if latest_tweet != last_tweet:
        data = {"content": f"📢 有新推文囉！\n{latest_tweet}"}
        # 發送至 Discord Webhook
        response = requests.post(WEBHOOK_URL, json=data)
        
        if response.status_code in [200, 204]:
            with open(LAST_TWEET_FILE, "w") as f:
                f.write(latest_tweet)
            print("推播成功！已發送到 Discord。")
        else:
            print(f"發送到 Discord 失敗，狀態碼: {response.status_code}")
    else:
        print("目前沒有新推文。")

if __name__ == "__main__":
    main()
