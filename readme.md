# 幣安 X API 監控器 - 設定說明

## 1. 安裝依賴套件

```bash
pip3 install requests python-dotenv
```

## 2. 環境變數設定

建立 `.env` 檔案並設定以下參數：

```
X_BEARER_TOKEN=你的X_API_Bearer_Token
LINE_BOT_TOKEN=你的LINE_Bot_Channel_Access_Token
LINE_USER_ID=你的LINE_User_ID
```

## 3. 取得必要的 Token

### X API Token (免費版)
1. 前往 https://developer.twitter.com/
2. 申請開發者帳戶
3. 建立新的 App
4. 取得 Bearer Token

### LINE Bot Token
1. 前往 https://developers.line.biz/
2. 建立新的 Provider 和 Channel
3. 取得 Channel Access Token
4. 取得你的 User ID (可透過 LINE Bot 發送訊息給自己來取得)

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

### Q: 如何測試 LINE Bot？
A: 可以手動調用 `send_line_message()` 方法：
```python
monitor = BinanceTwitterMonitor()
monitor.send_line_message("測試訊息")
```

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