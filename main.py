import requests
import xml.etree.ElementTree as ET
import os

# --- 設定區 ---
RSS_URL = "https://rss.app/feeds/jmiOmW3vDqw8aGgD.xml"  # 已經幫你填好你的專屬網址了！
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
LAST_TWEET_FILE = "last_tweet.txt"

def get_latest_tweet():
    # 簡單的偽裝
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        print(f"正在讀取 RSS: {RSS_URL}")
        response = requests.get(RSS_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            # RSS.app 的格式裡，貼文放在 <item> 裡面
            items = root.findall('./channel/item')
            if items:
                # 抓出最新一篇的連結
                link = items[0].find('link').text
                return link
            else:
                print("RSS 裡面目前沒有文章。")
        else:
            print(f"讀取失敗，狀態碼: {response.status_code}")
            
    except Exception as e:
        print(f"發生錯誤: {e}")
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
        data = {"content": f"📢 HaBEoxo 有新推文囉！\n{latest_tweet}"}
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
