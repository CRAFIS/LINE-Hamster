from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, VideoSendMessage
from requests_oauthlib import OAuth1Session
import os, requests, json, random

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]
COTOGOTO_APPKEY = os.environ["COTOGOTO_APPKEY"]
TWITTER_CONSUMER_KEY = os.environ["TWITTER_CONSUMER_KEY"]
TWITTER_CONSUMER_SECRET = os.environ["TWITTER_CONSUMER_SECRET"]
TWITTER_ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
TWITTER_ACCESS_SECRET = os.environ["TWITTER_ACCESS_SECRET"]

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
    if want_video(text):
        query = "#ハムスターのいる生活 filter:videos"
        video_url, preview_url = get_video(query)
        line_bot_api.reply_message(
            event.reply_token,
            VideoSendMessage(original_content_url=video_url, preview_image_url=preview_url))
    else:
        reply_text = get_reply(text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text))

def want_video(text):
    words = ['動画', '映像', 'ビデオ', 'ムービー']
    return True in [word in text for word in words]

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

def get_video(query):
    twitter = OAuth1Session(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    url = "https://api.twitter.com/1.1/search/tweets.json"
    params = {
        "q": query,
        "lang": "ja",
        "result_type": "mixed",
        "count": 100
    }
    res = twitter.get(url, params = params)
    tweets = json.loads(res.text)["statuses"]
    random.shuffle(tweets)
    for tweet in tweets:
        try:
            tweet = tweet.get("retweeted_status", tweet)
            variants = tweet["extended_entities"]["media"][0]["video_info"]["variants"]
            variants = [variant for variant in variants if variant.get("bitrate")]
            video_url = max(variants, key = lambda x: x["bitrate"])["url"]
            video_url = video_url.split('?')[0]
            preview_url = tweet["extended_entities"]["media"][0]["media_url_https"]
            return video_url, preview_url
        except:
            pass

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
