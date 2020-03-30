import threading
import json
import re
import time
import Graphic
import SuperChatData
import httplib2
from tkinter import messagebox
from collections import deque
from oauth2client import tools
from oauth2client import client
from oauth2client.file import Storage

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

class HandleYoutubeAPI:
    def __init__(self, graphic):
        self.videoId = ""
        self.chatId = ""
        self.ItemList = deque()
        self.lock = threading.Lock()

        credentials_path = "credentials.json"
        store = Storage(credentials_path)
        credentials = store.get()

        if credentials is None or credentials.invalid:
            f = "YoutubeClientId.json"
            flow = client.flow_from_clientsecrets(f, scopes)
            flow.user_agent = "text"
            credentials = tools.run_flow(flow, Storage(credentials_path))

        self.http = credentials.authorize(httplib2.Http())

        result = re.findall('\?v=([^&]+)', graphic.URLInput.get())
        if (len(result) > 0):
            self.videoId = result[0]    
            url = "https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id=" + self.videoId 
            res, data = self.http.request(url)
            data = json.loads(data.decode())
        else:
            messagebox.showerror("エラー", "ビデオID取得失敗")
            return

        if 'items' not in data.keys():
            messagebox.showerror("エラー", "チャットチャットID取得失敗")
        elif 'actualEndTime' in data["items"][0]["liveStreamingDetails"].keys():
            messagebox.showerror("エラー", "終了した生放送です")
        else:
            self.chatId = data["items"][0]["liveStreamingDetails"]["activeLiveChatId"]
            #スレッド作成
            self.getItemsThread = threading.Thread(target = self.getItems)
            self.getItemsThread.start()

    def getItems(self):
        isEnd = False        
        nextPageToken = ""

        while isEnd == False:
            interval = 0

            url = "https://www.googleapis.com/youtube/v3/liveChat/messages?liveChatId=" + self.chatId
            url += "&part=authorDetails,snippet&hl=ja&maxResults=2000"

            if (nextPageToken != ""):
                url += "&pageToken=" + nextPageToken
                print (nextPageToken)

            res, data = self.http.request(url)
            data = json.loads(data.decode())

            if 'error' in data.keys():
                print(data["error"]["message"])
                isEnd = True
            else:
                interval = data["pollingIntervalMillis"]
                nextPageToken = data["nextPageToken"]
                for item in data["items"]:
                    if item["snippet"]["type"] == "superChatEvent":
                        name = item["authorDetails"]["displayName"]
                        imageURL = item["authorDetails"]["profileImageUrl"]
                        moneyString = item["snippet"]["superChatDetails"]["amountDisplayString"]
                        comment = item["snippet"]["superChatDetails"]["userComment"]
                        superChatData = SuperChatData.SuperChatData(name, imageURL, moneyString, comment)
                        #配列に排他処理
                        self.lock.acquire()
                        self.ItemList.append(superChatData)
                        self.lock.release()
            time.sleep(interval * 0.001)

    def getData(self):
        self.lock.acquire()
        #コメントを格納する配列が空のとき
        if not self.ItemList:
            superChatData = ""
        else:
            superChatData = self.ItemList.popleft()
            print (superChatData)
        self.lock.release()
        return superChatData
