import tkinter
import HandleYoutubeAPI
import SuperChatData
import threading
import time
import textwrap
from urllib import request
from PIL import Image, ImageTk

class Graphic:
    def __init__(self):
        self.insertURL = ""

        self.mainFrame = tkinter.Tk()
        self.mainFrame.title("YoutubeLiveSuperChatCommentViewer")
        self.mainFrame.geometry("450x600")
        self.mainFrame.attributes("-topmost", True)

        self.URLLabel = tkinter.Label(self.mainFrame, text = "URL")
        self.URLLabel.place(x = 10, y = 14)

        self.URLInput = tkinter.Entry(self.mainFrame, width = 55)
        self.URLInput.insert(tkinter.END, self.insertURL)
        self.URLInput.place(x = 50, y = 14)

        self.ConnectButton = tkinter.Button(self.mainFrame, text = "接続", command=self.InputURLButtonClick)
        self.ConnectButton.place(x = 390, y = 10)

        self.superChatAreaFrameUnder = tkinter.Frame(self.mainFrame, height = 540, width = 430, bg = "white")
        self.superChatAreaFrameUnder.place(x = 10, y = 45)
        self.superChatAreaFrameUnder.propagate(0)

        self.superChatAreaCanvas = tkinter.Canvas(self.superChatAreaFrameUnder, height = 540, width = 410, bg = "black")
        self.superChatAreaScrollBar = tkinter.Scrollbar(self.superChatAreaFrameUnder, orient=tkinter.VERTICAL, command = self.superChatAreaCanvas.yview)

        self.superChatAreaCanvas['yscrollcommand'] = self.superChatAreaScrollBar.set
        self.superChatAreaCanvas['scrollregion'] = (0, 0, 0, 540)

        self.superChatAreaCanvas.xview_moveto(0)
        self.superChatAreaCanvas.yview_moveto(0)

        self.superChatAreaCanvas.pack(anchor = tkinter.NW, side = tkinter.LEFT)
        self.superChatAreaScrollBar.pack(anchor = tkinter.NE, side = tkinter.RIGHT, fill = tkinter.Y)

        self.superChatAreaCanvas.bind_all("<MouseWheel>", self.MouseWheelCallBack)

        self.mainFrame.mainloop()

    #マウスをスクロールした時のコールバック関数
    def MouseWheelCallBack(self, event):
        self.superChatAreaCanvas.yview_scroll(-1 * (event.delta // 120), "units")

    #接続ボタンを押したときのイベント関数
    def InputURLButtonClick(self):
        handleYoutubeAPI = HandleYoutubeAPI.HandleYoutubeAPI(self)
        #定期的にコメントを取得しコメントを作成するスレッドを作成
        makeSuperChatThread = threading.Thread(target = self.MakeSuperChat, args = ([handleYoutubeAPI]))
        makeSuperChatThread.start()

    #定期的にコメントを取得しコメントを作成するスレッド関数
    def MakeSuperChat(self, handleYoutubeAPI):
        isEnd = False
        superChatYCoordinate = 10 #コメントのY座標
        imgs = []
        superChatDataBase = []

        while isEnd == False:
            #コメントを格納している配列を確認
            superChatData = handleYoutubeAPI.getData()

            #コメントが取得できたとき
            if superChatData != "":
                superChatDataBase.append(superChatData)

                imgURL = superChatData.GetImgURL()
                name = superChatData.GetName()
                moneyString = superChatData.GetMoneyString()
                comment = superChatData.GetComment()

                #サムネイルを作成
                request.urlretrieve(imgURL, 'test.jpg')
                img = Image.open(open('test.jpg', 'rb'))
                img.thumbnail((50, 50), Image.ANTIALIAS)
                img = ImageTk.PhotoImage(img)
                imgs.append(img)

                #コメントを改行し、コメントラベル、キャンバスの高さを決定
                comment = textwrap.fill(comment, 37)
                newLineCount = comment.count('\n')
                commentCanvasHeight = 100 + (13 * newLineCount)

                #コメントを作成
                commentCanvas = tkinter.Canvas(self.superChatAreaCanvas, height = commentCanvasHeight, width = 390, bg = "orange")

                #コメントキャンバスにサムネイルを追加
                commentCanvas.create_image(10, 10, image = img, anchor=tkinter.NW)

                #コメントキャンパスに名前を追加
                nameLabel = tkinter.Label(commentCanvas, text = name, fg = 'black')
                commentCanvas.create_window(70, 10, window = nameLabel, anchor = tkinter.NW)

                #コメントキャンバスにお金を追加
                moneyStringLabel = tkinter.Label(commentCanvas, text = moneyString, fg = 'black')
                commentCanvas.create_window(70, 40, window = moneyStringLabel, anchor = tkinter.NW)

                #コメントキャンパスにコメントを追加
                commentLabel = tkinter.Label(commentCanvas, text = comment, fg = 'black', justify = 'left')
                commentCanvas.create_window(10, 70, window = commentLabel, anchor = tkinter.NW)
             
                #スーパチャットを作成
                self.superChatAreaCanvas.create_window(10, superChatYCoordinate, window = commentCanvas, anchor = tkinter.NW)

                superChatYCoordinate += commentCanvasHeight + 10
                scrollBarPosition = self.superChatAreaScrollBar.get()[1]

                #コメントの一番下がフレームの一番下より下になった場合スクロール
                if (superChatYCoordinate > 540) :
                    self.superChatAreaCanvas['scrollregion'] = (0, 0, 0, superChatYCoordinate)
                    if (scrollBarPosition > 0.99):
                        scrollBarLength = 540
                        self.superChatAreaCanvas.yview_moveto((superChatYCoordinate - scrollBarLength) / superChatYCoordinate)
            
        time.sleep(1)
