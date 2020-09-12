from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, VideoSendMessage
from requests_oauthlib import OAuth1Session
import os, json, requests, random, pykakasi

CHANNEL_ACCESS_TOKEN = os.environ['CHANNEL_ACCESS_TOKEN']
CHANNEL_SECRET = os.environ['CHANNEL_SECRET']
COTOGOTO_APPKEY = os.environ['COTOGOTO_APPKEY']
TWITTER_CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
TWITTER_CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
twitter = OAuth1Session(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)

# レスポンスを生成する
def response(status_code, body):
    body = json.dumps(body)
    return {'statusCode': status_code, 'body': body}

# 動画が見たいかどうか判定する
def want_video(text):
    words = ['douga', 'eizou', 'bideo', 'muubii', 'hamusuta', 'hamuchan']
    kakasi = pykakasi.kakasi()
    kakasi.setMode('H', 'a')
    kakasi.setMode('K', 'a')
    kakasi.setMode('J', 'a')
    converter = kakasi.getConverter()
    converted_text  = converter.do(text)
    for word in words:
        if word in converted_text: return True
    return False

# 語尾を修正する
def modify_text_end(text):
    idx = 0
    symbols = ['。', '、', '！', '？', 'ー', '.', ',']
    for i in range(len(text), 0, -1):
        if text[i-1] not in symbols:
            idx = i
            break
    text = text[:idx] + 'でち' + text[idx:] + '🐹'
    return text

# リプライを取得する
def get_reply(text):
    url = 'https://app.cotogoto.ai/webapi/noby.json'
    params = {'appkey': COTOGOTO_APPKEY, 'text': text}
    try:
        res = requests.get(url, params = params, timeout = 10)
        res = json.loads(res.text)
        text = res['text']
        text = modify_text_end(text)
    except:
        text = '応答できないでち🐹'
    return text

# ツイートを検索する
def search_tweets(query, result_type):
    url = 'https://api.twitter.com/1.1/search/tweets.json'
    params = {
        'q': query,
        'lang': 'ja',
        'result_type': result_type,
        'count': 100
    }
    res = twitter.get(url, params = params)
    if res.status_code != 200: return []
    tweets = json.loads(res.text)['statuses']
    return tweets

# ランダムに動画を取得する
def get_video(query):
    recent_tweets = search_tweets(query, 'recent')
    popular_tweets = search_tweets(query, 'popular')
    tweets = recent_tweets + popular_tweets
    random.shuffle(tweets)
    for tweet in tweets:
        try:
            tweet = tweet.get('retweeted_status', tweet)
            variants = tweet['extended_entities']['media'][0]['video_info']['variants']
            variants = [variant for variant in variants if variant.get('bitrate')]
            video_url = max(variants, key = lambda variant: variant['bitrate'])['url']
            video_url = video_url.split('?')[0]
            preview_url = tweet['extended_entities']['media'][0]['media_url_https']
            return video_url, preview_url
        except:
            pass
    return '', ''

# メッセージイベント
@handler.add(MessageEvent, message = TextMessage)
def message(event):
    text = event.message.text
    if want_video(text):
        text = '僕の仲間を呼ぶでち🐹'
        query = '#ハムスターのいる生活 OR #ハムスター好きと繋がりたい filter:videos'
        video_url, preview_url = get_video(query)
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text = text),
                VideoSendMessage(original_content_url = video_url, preview_image_url = preview_url)
            ]
        )
    else:
        text = get_reply(text)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))

def lambda_handler(event, context):
    signature = event['headers']['X-Line-Signature']
    body = event['body']
    try:
        handler.handle(body, signature)
    except Exception as error:
        print(error)
        return response(400, 'ERROR')
    return response(200, 'OK')
