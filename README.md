# LINE-Hamster-Bot

## Deployment

```
$ heroku login
$ heroku create <App Name>
$ heroku config:set CHANNEL_SECRET="<Your Channel Secret>" --app <App Name>
$ heroku config:set CHANNEL_ACCESS_TOKEN="<Your Access Token>" --app <App Name>
$ heroku config:set COTOGOTO_APPKEY="<Your CotoGoto App Key>" --app <App Name>
$ git add .
$ git commit -m "<Commit Message>"
$ git push heroku master
```