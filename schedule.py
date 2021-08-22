from flask import Flask, request, abort
import os
import requests
import json
import re

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
TIME_TREE_ACCESS_TOKEN = os.environ["TIME_TREE_ACCESS_TOKEN"]
USER_ID = os.environ["USER_ID"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

timezone = 9

def main():

  # header
  headers = {
   'Accept': 'application/vnd.timetree.v1+json',
   'Authorization': 'Bearer ' + TIME_TREE_ACCESS_TOKEN
   }

  URL = 'https://timetreeapis.com/calendars'
  
  #get json
  r = requests.get(URL, headers=headers)
  data = r.json()
  today = json.dumps(data, indent=4, ensure_ascii=False)
  
  #get calendar id
  p = r'"id": "(.*?)[,"]'
  r = re.findall(p, today)
  calendars=set(r)
  
  messages = "明日のスケジュールです。"
    
  #get schedule
  for calendar in calendars:
    URL = 'https://timetreeapis.com/calendars/'+calendar+'/upcoming_events?timezone=Asia/Tokyo&days=2'
    r = requests.get(URL, headers=headers)
    data = r.json()
    for event in data['data']:
      start=event['attributes']['start_at']
      end=event['attributes']['end_at']
      
      # change format
      start_date,start_time = start.split("T")
      end_date,end_time = end.split("T")
      _,start_month,start_day = start_date.split("-")
      _,end_month,end_day = end_date.split("-")
      start_hour,start_min,_ = start_time.split(":")
      end_hour,end_min,_ = end_time.split(":")

      s_hour = int(start_hour) + timezone
      e_hour = int(end_hour) + timezone

      message = start_month + "/" + start_day + " "+ str(s_hour) + ":" + start_min + "～" + end_month + "/" + end_day + " "+ str(e_hour) + ":" + end_min + "\n" + event['attributes']['title'] + "\n"
    messages += message
    line_bot_api.push_message(USER_ID,TextSendMessage(text=message))

if __name__ == "__main__":
    main()
