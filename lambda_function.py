import json
import sys
import os
import random
from datetime import datetime as dt
from datetime import timedelta
import boto3
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerSendMessage
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)

#(1)Amazon REKOGNITION
rekognition_label = boto3.client('rekognition')
rekognition_face = boto3.client('rekognition')

#(2)LINE Messaging API
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', None)
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if LINE_CHANNEL_SECRET is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if LINE_CHANNEL_ACCESS_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

#(3)Messaging API Handler
@handler.add(MessageEvent)
def message(event):
    #(4)LINE message information
    event_type = event.type
    message_type = event.message.type
    message_id = event.message.id
    #msg = 'event_type: ' + event_type + ', user_id: ' + user_id + ', message_type: ' + message_type + ', message_id:' + message_id

    if message_type == 'image':
        #(5)Get image data from LINE
        message_content = line_bot_api.get_message_content(message_id)
        content = bytes()
        for chunk in message_content.iter_content():
            content += chunk
        
        #(6)Recognize image by Rekognition
        labels = detect_labels(content)
        print(labels)
        msg_label = ''
        baby_flag = False
        human_flag = False
        for label in labels['Labels']:
            msg_label += label['Name'] + ':' + str(round(label['Confidence'],1)) + '%\n'
            if label['Name'] == 'Baby':
                baby_flag = True
                print('Here is a baby.')
            if label['Name'] == 'Baby' or label['Name'] == 'Person' or label['Name'] == 'Human' or label['Name'] == 'Newborn':
                human_flag = True
                print('Here is a Human.')
        msg_label = msg_label[:-1]
        
        #(7)Detect face in image by Rekognition
        if human_flag == True:  #When a human is detected
            FaceDetails = detect_faces(content)
            print(FaceDetails)
            if len(FaceDetails['FaceDetails']) == 0: #When a face is not detected
                human_flag = False
            else:
                age_min = FaceDetails['FaceDetails'][0]['AgeRange']['Low']
                age_max = FaceDetails['FaceDetails'][0]['AgeRange']['High']
                msg_face = 'Age:' + str(age_min) + '-' + str(age_max) + 'years old'
                if age_max < 5:
                    baby_flag = True

        #(8)Ask LINE bot to reply messages
        text = []
        if baby_flag == True: #There is a baby
            msg_approval = ['可愛い!', '天使!', '偉い!', '育児して偉い！', '最高!', 'すごい！', 'キャワワ!', '天才!', '【大当たり】おめでとうございます！']
            text.append(TextSendMessage(text=random.choice(msg_approval)))
            text.append(StickerSendMessage(package_id='11537', sticker_id=str(52000000+random.choice(range(2734,2774)))))
        else: #There is no baby
            text.append(TextSendMessage(text='No baby.'))
        text.append(TextSendMessage(text=msg_label))
        if human_flag == True: #There is a face
            text.append(TextSendMessage(text=msg_face))
        line_bot_api.reply_message(event.reply_token, text)
    
def detect_labels(image_bytes):
    try:
        res = rekognition_label.detect_labels(
            Image={
                'Bytes': image_bytes
            },
            MaxLabels=6,
            MinConfidence=50
        )
        return res
    except Exception as ex:
        print("fail to detect labels. error = " + ex.message)
        
def detect_faces(image_bytes):
    try:
        res = rekognition_face.detect_faces(
            Image={
                'Bytes': image_bytes
            },
            Attributes=[
                'ALL',
            ]
        )
        return res
    except Exception as ex:
        print("fail to detect faces. error = " + ex.message)


def send_line_bot(signature, body):
    ok_json = {"isBase64Encoded": False,
               "statusCode": 200,
               "headers": {},
               "body": ""}
    error_json = {"isBase64Encoded": False,
                  "statusCode": 403,
                  "headers": {},
                  "body": "Error"}
            
    try:
        #print(body)
        #print(signature)
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        return error_json
    except InvalidSignatureError:
        return error_json

    return ok_json
        
def lambda_handler(event, context):
    
    signature = event["headers"]["x-line-signature"]
    body = event["body"]
    res = send_line_bot(signature, body)
    print(res)
    
    return res