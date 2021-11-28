# HighsoApprovalBot

赤ん坊の画像を送ると「育児してて偉い！」と返してくれる「育児応援LINEボット」です。
詳細は以下のページにて。
https://highso.hatenablog.com/entry/2019/09/29/180000

## 機能
- (1)LINEで写真を送ったら、すぐに返事をしてくれるLINEボット。
- (2)写真が幼児の写真だったら「偉い！」と褒める。関係の無い写真だったら、褒めない。

![デモ](https://cdn-ak.f.st-hatena.com/images/fotolife/h/highso/20190929/20190929192530.png)

## 使ったもの
- AWS：Amazon Rekognition、Lambda、API Gateway
- LINE関連：Messaging API
- 開発環境：Windows10、Python 3.7
## アーキテクチャ
![アーキテクチャ](https://cdn-ak.f.st-hatena.com/images/fotolife/h/highso/20190929/20190929152858.png)

## AWS Lambdaへのアップロード
ライブラリをzipにまとめてアップロードします。

```
$ cd HighsoApprovalBot
$ sudo pip3 install requests -t ./
$ sudo pip3 install line-bot-sdk -t ./
$ sudo rm *.dist-info -r
$ sudo zip -r HighsoLineBot.zip ./*
```

HighsoLineBot.zipをLambdaにアップロードします。

## Lambdaの設定
タイムアウトの設定、トークンの設定、Rekognitionを使うIAMの設定など必要です。
詳細はブログ記事を参照。