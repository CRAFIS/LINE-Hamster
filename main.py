from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, VideoSendMessage
import os, requests, json

app = Flask(__name__)

#環境変数取得
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]
COTOGOTO_APPKEY = os.environ["COTOGOTO_APPKEY"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if '動画' in text or 'ビデオ' in text:
        video_url = "https://video.twimg.com/ext_tw_video/1145316011974877190/pu/vid/1280x720/RdiweV650PpxBqH8.mp4"
        preview_url = "https://pbs.twimg.com/ext_tw_video_thumb/1145316011974877190/pu/img/iL6-Bzc-Z4EygSlZ.jpg"
        line_bot_api.reply_message(
            event.reply_token,
            VideoSendMessage(original_content_url=video_url, preview_image_url=preview_url))
    else:
        reply_text = get_reply(text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text))

def get_reply(text):
    url = "https://app.cotogoto.ai/webapi/noby.json"
    params = {
        "appkey": COTOGOTO_APPKEY,
        "text": text
    }
    try:
        res = requests.get(url, params = params, timeout = 5.0)
        res = json.loads(res.text)
        reply_text = res['text'] + "🐹"
    except:
        reply_text = "🐹💨🐹💨🐹💨"
    return reply_text


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
