# 幣安 X API 監控器 - 設定說明

## 1. 安裝依賴套件

```bash
pip install requests python-dotenv flask line-bot-sdk
```

## 2. 環境變數設定

建立 `.env` 檔案並設定以下參數：

```
X_BEARER_TOKEN=你的X_API_Bearer_Token
LINE_BOT_TOKEN=你的LINE_Bot_Channel_Access_Token
LINE_CHANNEL_SECRET=你的LINE_Channel_Secret
LINE_GROUP_ID=你的LINE_Group_ID
```

## 3. 取得必要的 Token

### X API Token (免費版)
1. 前往 https://developer.twitter.com/
2. 申請開發者帳戶
3. 建立新的 App
4. 取得 Bearer Token

### LINE Bot Token 和 Group ID

#### 建立 LINE Bot
1. 前往 https://developers.line.biz/
2. 建立新的 Provider 和 Channel (選擇 **Messaging API**)
3. 取得 Channel Access Token
4. 在「Messaging API」頁面中開啟：
   - ✅ **Allow bot to join group chats（允許加入群組聊天）**
   - ✅ **Use webhooks**

#### 取得 LINE 群組 ID 完整流程

**步驟 1：安裝必要套件**
```bash
pip install flask line-bot-sdk
```

**步驟 2：設定環境變數**

在 `.env` 檔案中加入：
```
LINE_BOT_TOKEN=你的_Channel_Access_Token
LINE_CHANNEL_SECRET=你的_Channel_Secret
```

**步驟 3：安裝並設定 ngrok**
```bash
# macOS
brew install --cask ngrok

# 或手動下載
# https://ngrok.com/download
```

首次使用需要 authtoken：
1. 註冊帳號：https://dashboard.ngrok.com/signup
2. 取得 authtoken：https://dashboard.ngrok.com/get-started/your-authtoken
3. 執行指令：
```bash
ngrok config add-authtoken <你的_authtoken>
```

**步驟 4：啟動服務**

終端機 1 - 啟動 Flask：
```bash
python3 get_group_id.py
```

終端機 2 - 啟動 ngrok：
```bash
ngrok http 5000
```

你會看到類似：
```
Forwarding https://abc123.ngrok.io -> http://localhost:5000
```

**步驟 5：設定 LINE Webhook**
1. 回到 LINE Developers Console
2. 將 Webhook URL 設為：`https://abc123.ngrok.io/callback`
3. 點擊「Verify」測試連線
4. 啟用 Webhook（⚡ Turn ON）

**步驟 6：取得群組 ID**
1. 在 LINE 群組中「邀請」你的 bot
2. 在群組中輸入任何訊息
3. `get_group_id.py` 終端機會印出：
   ```
   ✅ 群組 ID：C4a1f79f3bcaxxxxxxxxxxxxxxxxx
   ```
4. 複製此 ID 到 `.env` 檔案：
   ```
   LINE_GROUP_ID=C4a1f79f3bcaxxxxxxxxxxxxxxxxx
   ```

**步驟 7：測試群組訊息**
```python
# 測試發送訊息到群組
monitor = BinanceTwitterMonitor()
monitor.send_line_message("🔧 測試群組訊息發送")
```

**📌 重要提醒：**
- 若沒人在群組中發言，LINE 不會送 webhook，請務必在群組中發言一次
- 免費版 ngrok 每次重啟網址會變動，如需固定網址需升級帳號
- 取得 Group ID 後就可以關閉 webhook 測試環境，專心執行監控程式

## 4. 免費版限制說明

### X API 免費版限制：
- 每月 10,000 次請求
- 每次最多 10 則推文
- 只能搜尋最近 7 天的推文
- 每 15 分鐘最多 300 次請求

### 建議設定：
- 監控間隔：15 分鐘
- 每次請求：10 則推文
- 每天約 96 次請求 (在限制範圍內)

## 5. 使用方法

### 基本執行：
```bash
python binance_monitor.py
```

### 後台執行 (Linux/Mac)：
```bash
nohup python binance_monitor.py &
```

### Windows 後台執行：
```bash
pythonw binance_monitor.py
```

## 6. 進階設定

### 修改監控關鍵字
在程式中修改 `keywords` 列表：
```python
self.keywords = ["幣安", "上線", "alpha", "TGE"]
```

### 關鍵字匹配策略
程式提供三種匹配策略，可在 `check_keywords_match()` 方法中選擇：

1. **任一關鍵字匹配 (OR 邏輯，預設)**：
   ```python
   return any(keyword.lower() in text_lower for keyword in self.keywords)
   ```

2. **所有關鍵字必須匹配 (AND 邏輯)**：
   ```python
   return all(keyword.lower() in text_lower for keyword in self.keywords)
   ```

3. **自定義組合邏輯**：
   ```python
   # 例如：必須包含「幣安」且包含其他任一關鍵字
   has_binance = "幣安" in text_lower
   has_others = any(keyword.lower() in text_lower for keyword in ["上線", "alpha", "tge"])
   return has_binance and has_others
   ```

### 修改搜尋查詢策略
在 `build_search_query()` 方法中可選擇：

1. **OR 邏輯搜尋 (預設)**：
   ```python
   return " OR ".join(self.keywords)
   ```

2. **AND 邏輯搜尋**：
   ```python
   return " ".join(self.keywords)
   ```

### 修改監控間隔
在 `run_monitor()` 方法中修改：
```python
time.sleep(15 * 60)  # 15 分鐘
```

### 修改推文數量
在 `search_tweets()` 方法中修改：
```python
"max_results": 10,  # 最多 10 則推文
```

## 7. 日誌監控

程式會自動記錄運行狀態，包括：
- 成功發送的通知
- API 錯誤
- 網路連線問題

## 8. 常見問題

### Q: 收不到通知怎麼辦？
A: 檢查以下項目：
1. 環境變數是否設定正確
2. X API 額度是否用完
3. LINE Bot Token 是否有效
4. 網路連線是否正常

### Q: 如何取得 LINE Group ID？
A: 
1. 建立 LINE Bot 並開啟群組功能
2. 使用 Flask + ngrok 建立 Webhook 接收環境
3. 把 Bot 加入目標群組
4. 在群組中發送任何訊息
5. 從 webhook 輸出中取得 Group ID

### Q: ngrok 網址一直變動怎麼辦？
A: 
1. 免費版 ngrok 每次重啟網址會變動
2. 取得 Group ID 後就可以關閉 ngrok
3. 如需固定網址可升級 ngrok 帳號

### Q: 機器人需要什麼權限？
A: 確保在 LINE Bot 設定中開啟：
- ✅ Use webhooks
- ✅ Allow bot to join group chats
- ✅ Auto-reply messages (可選)

### Q: Webhook 沒有收到訊息怎麼辦？
A: 檢查以下項目：
1. ngrok 是否正在運行
2. Webhook URL 是否正確設定
3. LINE Bot 是否已加入群組
4. 群組中是否有人發言（必須有人發言才會觸發 webhook）
5. Channel Secret 是否正確設定

### Q: 如何測試群組訊息？
A: 取得 Group ID 後，可以手動測試：
```python
monitor = BinanceTwitterMonitor()
monitor.send_line_message("🔧 測試群組訊息發送")
```

### Q: 取得 Group ID 後還需要 Webhook 嗎？
A: 不需要！取得 Group ID 後：
1. 可以關閉 `get_group_id.py` 和 ngrok
2. 在 LINE Console 中可以關閉 Webhook (Turn OFF)
3. 監控程式只需要 `LINE_BOT_TOKEN` 和 `LINE_GROUP_ID` 就能發送訊息

### Q: 如何調整關鍵字匹配策略？
A: 在 `check_keywords_match()` 方法中有三種策略：
1. **任一匹配**：推文包含任一關鍵字就通知
2. **全部匹配**：推文必須包含所有關鍵字才通知
3. **自定義邏輯**：例如必須包含「幣安」加上其他任一關鍵字

### Q: 會收到太多通知怎麼辦？
A: 可以調整策略：
1. 使用 AND 邏輯，要求包含更多關鍵字
2. 增加更具體的關鍵字
3. 添加排除關鍵字邏輯

## 9. 優化建議

1. **使用資料庫**：儲存已處理的推文ID，避免重複處理
2. **錯誤重試**：增加API調用失敗的重試機制
3. **多關鍵字監控**：擴展為監控多個關鍵字
4. **推文過濾**：增加更精確的內容過濾條件

## 10. 注意事項

- 請遵守 X API 使用條款
- 不要過度頻繁地調用 API
- 妥善保管 API Token
- 定期檢查 API 額度使用情況