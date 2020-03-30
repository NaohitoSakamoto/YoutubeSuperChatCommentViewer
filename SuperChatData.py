class SuperChatData:
    def __init__(self, name, imgURL, moneyString, comment):
        self.name = name
        self.imgURL = imgURL
        self.moneyString = moneyString
        self.comment = comment

    def GetName(self):
        return self.name

    def GetImgURL(self):
        return self.imgURL

    def GetMoneyString(self):
        return self.moneyString

    def GetComment(self):
        return self.comment

