import requests
import xml.etree.ElementTree as ET
import os

# --- 設定區 ---
TWITTER_USER = "HaBEoxo"  # 請把這裡換成你想追蹤的推特帳號 ID (不含 @)
# 使用 Nitter 鏡像站的 RSS，避免被 Twitter 官方阻擋
RSS_URL = f"https://nitter.poast.org/{TWITTER_USER}/rss" 
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
LAST_TWEET_FILE = "last_tweet.txt"

def get_latest_tweet():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(RSS_URL, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"無法讀取 RSS，狀態碼: {response.status_code}")
            return None
            
        root = ET.fromstring(response.content)
        # 抓取第一筆 item (也就是最新貼文)
        for item in root.findall('./channel/item'):
            link = item.find('link').text
            # 將 Nitter 網址替換回原本的 Twitter 網址，讓 Discord 能正常顯示預覽
            original_url = link.replace("nitter.poast.org", "twitter.com")
            return original_url
    except Exception as e:
        print(f"發生錯誤: {e}")
    return None

def main():
    latest_tweet = get_latest_tweet()
    if not latest_tweet:
        return

    # 讀取機器人上次推播的紀錄
    last_tweet = ""
    if os.path.exists(LAST_TWEET_FILE):
        with open(LAST_TWEET_FILE, "r") as f:
            last_tweet = f.read().strip()

    # 比對！如果是沒見過的新推文，就發送到 Discord
    if latest_tweet != last_tweet:
        data = {"content": f"📢 有新推文囉！\n{latest_tweet}"}
        requests.post(WEBHOOK_URL, json=data)

        # 把最新的推文網址寫入紀錄檔
        with open(LAST_TWEET_FILE, "w") as f:
            f.write(latest_tweet)
        print("推播成功！")
    else:
        print("目前沒有新推文。")

if __name__ == "__main__":
    main()
