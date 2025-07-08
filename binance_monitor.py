import requests
import json
import time
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
class BinanceTwitterMonitor:
    def __init__(self):
        # X API 設定 (免費版)
        self.bearer_token = os.getenv('X_BEARER_TOKEN')  # 你的 X API Bearer Token
        
        # LINE Bot 設定
        self.line_bot_token = os.getenv('LINE_BOT_TOKEN')  # 你的 LINE Bot Channel Access Token
        self.line_group_id = os.getenv('LINE_GROUP_ID')   # 你的 LINE Group ID
        
        # API 端點
        self.x_api_url = "https://api.twitter.com/2/tweets/search/recent"
        self.line_api_url = "https://api.line.me/v2/bot/message/push"
        
        # 搜尋參數 - 多關鍵字監控
        self.keywords = ["幣安", "上線", "alpha", "TGE"]
        self.search_query = self.build_search_query()
        self.last_tweet_id = None
        
    def build_search_query(self):
        """建立搜尋查詢字串"""
        # 方法1: 包含所有關鍵字 (AND 邏輯)
        # return " ".join(self.keywords)
        
        # 方法2: 包含任一關鍵字 (OR 邏輯)
        return " OR ".join(self.keywords)
    
    def check_keywords_match(self, text):
        """檢查推文是否符合關鍵字條件"""
        text_lower = text.lower()
        
        # 策略1: 必須包含所有關鍵字
        # return all(keyword.lower() in text_lower for keyword in self.keywords)
        
        # 策略2: 包含任一關鍵字即可
        return any(keyword.lower() in text_lower for keyword in self.keywords)
        
        # 策略3: 自定義組合邏輯
        # 例如：必須包含「幣安」且包含「上線」或「alpha」或「TGE」
        # has_binance = "幣安" in text_lower
        # has_others = any(keyword.lower() in text_lower for keyword in ["上線", "alpha", "tge"])
        # return has_binance and has_others
    
    def get_twitter_headers(self):
        """取得 X API 請求標頭"""
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "BinanceMonitorBot/1.0"
        }
    
    def get_line_headers(self):
        """取得 LINE API 請求標頭"""
        return {
            "Authorization": f"Bearer {self.line_bot_token}",
            "Content-Type": "application/json"
        }
    
    def search_tweets(self):
        """搜尋包含指定關鍵字的推文"""
        params = {
            "query": self.search_query,
            "tweet.fields": "created_at,author_id,text,public_metrics",
            "user.fields": "name,username",
            "expansions": "author_id",
            "max_results": 10,  # 免費版限制
            "sort_order": "recency"
        }
        
        # 如果有上次的推文ID，只取新的推文
        if self.last_tweet_id:
            params["since_id"] = self.last_tweet_id
        
        try:
            response = requests.get(
                self.x_api_url,
                headers=self.get_twitter_headers(),
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                logger.error(f"X API 錯誤: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"搜尋推文時發生錯誤: {str(e)}")
            return None
    
    def send_line_message(self, message):
        """發送訊息到 LINE 群組"""
        payload = {
            "to": self.line_group_id,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }
        
        try:
            response = requests.post(
                self.line_api_url,
                headers=self.get_line_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                logger.info("LINE 群組訊息發送成功")
                return True
            else:
                logger.error(f"LINE API 錯誤: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"發送 LINE 群組訊息時發生錯誤: {str(e)}")
            return False
    
    def process_tweets(self, data):
        """處理推文數據"""
        if not data or 'data' not in data:
            logger.info("沒有找到新推文")
            return
        
        tweets = data['data']
        users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
        
        for tweet in tweets:
            # 檢查推文內容是否包含目標關鍵字
            if self.check_keywords_match(tweet['text']):
                author_id = tweet['author_id']
                author = users.get(author_id, {})
                
                # 格式化訊息
                message = self.format_message(tweet, author)
                
                # 發送到 LINE
                if self.send_line_message(message):
                    logger.info(f"已發送推文通知: {tweet['id']}")
                
                # 更新最後處理的推文ID
                self.last_tweet_id = tweet['id']
    
    def format_message(self, tweet, author):
        """格式化要發送的訊息"""
        author_name = author.get('name', '未知用戶')
        author_username = author.get('username', '')
        tweet_text = tweet['text']
        created_at = tweet['created_at']
        tweet_id = tweet['id']
        
        # 找出匹配的關鍵字
        matched_keywords = [keyword for keyword in self.keywords 
                          if keyword.lower() in tweet_text.lower()]
        
        # 格式化時間
        try:
            dt = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_time = created_at
        
        message = f"""🚨 關鍵字監控通知！
        
🏷️ 匹配關鍵字: {', '.join(matched_keywords)}
👤 發布者: {author_name} (@{author_username})
📅 時間: {formatted_time}
📝 內容: {tweet_text}
🔗 連結: https://twitter.com/{author_username}/status/{tweet_id}
        """
        
        return message
    
    def run_monitor(self):
        """執行監控"""
        logger.info(f"開始監控關鍵字: {', '.join(self.keywords)}")
        logger.info(f"搜尋查詢: {self.search_query}")
        
        while True:
            try:
                # 搜尋推文
                data = self.search_tweets()
                
                if data:
                    self.process_tweets(data)
                
                # 休息 15 分鐘 (免費版有速率限制)
                logger.info("等待 15 分鐘後繼續監控...")
                time.sleep(15 * 60)
                
            except KeyboardInterrupt:
                logger.info("監控已停止")
                break
            except Exception as e:
                logger.error(f"監控過程中發生錯誤: {str(e)}")
                time.sleep(60)  # 發生錯誤時等待 1 分鐘後重試

def main():
    # 檢查環境變數
    required_vars = ['X_BEARER_TOKEN', 'LINE_BOT_TOKEN', 'LINE_GROUP_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"缺少必要的環境變數: {', '.join(missing_vars)}")
        return
    
    # 建立監控器並開始執行
    monitor = BinanceTwitterMonitor()
    monitor.send_line_message("測試訊息")
    # monitor.run_monitor()

if __name__ == "__main__":
    main()