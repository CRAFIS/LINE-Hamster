from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, VideoSendMessage
from requests_oauthlib import OAuth1Session
import os, requests, json, random, pykakasi

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ['CHANNEL_ACCESS_TOKEN']
CHANNEL_SECRET = os.environ['CHANNEL_SECRET']
COTOGOTO_APPKEY = os.environ['COTOGOTO_APPKEY']
TWITTER_CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
TWITTER_CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route('/callback', methods = ['POST'])
def callback():
    # Get X-Line-Signature Header Value
    signature = request.headers['X-Line-Signature']
    # Get Request Body as Text
    body = request.get_data(as_text = True)
    app.logger.info(f"Request body: {body}")
    # Handle Webhook Body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message = TextMessage)
def handle_message(event):
    text = event.message.text
    if want_video(text):
        reply_text = '僕の仲間を呼ぶでち🐹'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = reply_text))
        query = '#ハムスター OR #ハムスターのいる生活 OR #ハムスター好きと繋がりたい filter:videos'
        video_url, preview_url = get_video(query)
        line_bot_api.reply_message(
            event.reply_token,
            VideoSendMessage(original_content_url = video_url, preview_image_url = preview_url)
        )
    else:
        reply_text = get_reply(text)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = reply_text))

def want_video(text):
    words = ['douga', 'eizou', 'bideo', 'mu-bi-', 'hamusuta-', 'hamutyann']
    kakasi = pykakasi.kakasi()
    kakasi.setMode('H', 'a')
    kakasi.setMode('K', 'a')
    kakasi.setMode('J', 'a')
    conv = kakasi.getConverter()
    return True in [word in conv.do(text) for word in words]

def get_reply(text):
    url = 'https://app.cotogoto.ai/webapi/noby.json'
    params = {
        'appkey': COTOGOTO_APPKEY,
        'text': text
    }
    try:
        res = requests.get(url, params = params, timeout = 5.0)
        res = json.loads(res.text)
        text = res['text']
        idx = 0
        symbols = ['。', '、', '！', '？', 'ー', '.', ',']
        for i in range(len(text), 0, -1):
            if text[i-1] not in symbols:
                idx = i
                break
        text = text[:idx] + 'でち' + text[idx:]
        reply_text = text + '🐹'
    except:
        reply_text = '応答できないでち🐹'
    return reply_text

def get_video(query):
    twitter = OAuth1Session(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    url = 'https://api.twitter.com/1.1/search/tweets.json'
    params = {
        'q': query,
        'lang': 'ja',
        'result_type': 'mixed',
        'count': 100
    }
    res = twitter.get(url, params = params)
    tweets = json.loads(res.text)['statuses']
    random.shuffle(tweets)
    for tweet in tweets:
        try:
            tweet = tweet.get('retweeted_status', tweet)
            variants = tweet['extended_entities']['media'][0]['video_info']['variants']
            variants = [variant for variant in variants if variant.get('bitrate')]
            video_url = max(variants, key = lambda x: x['bitrate'])['url']
            video_url = video_url.split('?')[0]
            preview_url = tweet['extended_entities']['media'][0]['media_url_https']
            return video_url, preview_url
        except:
            pass

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host = '0.0.0.0', port = port)
