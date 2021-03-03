# LINE-Hamchin-Bot

![LINE](https://user-images.githubusercontent.com/25927185/109787539-ace7ce00-7c51-11eb-8758-523ba582a619.png)

## Lambda Function

| Attribute | Content |
| - | - |
| Name | LineHamchinBot |
| Runtime | Python 3.8 |
| Memory | 128 MB |
| Timeout | 10 seconds |
| File | lambda_function.py |

### Role

| Attribute | Content |
| - | - |
| Name | LambdaAccess2CloudWatchLogs |
| Policy | CloudWatchLogsFullAccess |

### Environmental Variable

| Key |
| - |
| CHANNEL_ACCESS_TOKEN |
| CHANNEL_SECRET |
| COTOGOTO_APPKEY |
| TWITTER_CONSUMER_KEY |
| TWITTER_CONSUMER_SECRET |
| TWITTER_ACCESS_TOKEN |
| TWITTER_ACCESS_SECRET |

## Lambda Layer

| Attribute | Content |
| - | - |
| Name | LineHamchinBot |
| Runtime | Python 3.8 |

To create zip file:

```
$ pip3 install -t ./python -r requirements.txt
$ zip -r package.zip ./python
```

## API Gateway

### POST /

- Use Lambda Proxy Integration.
- Use Default Timeout.

#### HTTP Request Header

| Key | Required |
| - | :-: |
| X-Line-Signature | ○ |
