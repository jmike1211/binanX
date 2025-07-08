from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv


import os

app = Flask(__name__)

load_dotenv()

# 設定你的 Channel Access Token 與 Secret
LINE_BOT_TOKEN = os.getenv('LINE_BOT_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_BOT_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print("Received body:", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.source.type == 'group':
        group_id = event.source.group_id
        print(f"🔍 收到群組訊息，Group ID 為：{group_id}")

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"這個群組的 ID 是：\n{group_id}")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請將我加入群組中，我可以回覆群組 ID 😄")
        )

if __name__ == "__main__":
    app.run()
