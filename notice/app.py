
class Email:
    def __init__(self,content=None):
        from email.mime.multipart import MIMEMultipart

        # 信件內容
        self.mail_info = MIMEMultipart()
        self.content = content
        # 寄信伺服器
        self.account = "robin92062574@gmail.com"
        self.password = "ajuv lppx jrfu wjsl"

    def send(self):
        import smtplib
        server=smtplib.SMTP("smtp.gmail.com",587) #建立gmail連驗
        server.ehlo()
        server.starttls()
        server.login(self.account,self.password)
        status = server.send_message(self.mail_info)
        print(status)
        server.quit()

    def order_complete(self,to_email="C110156220@nkust.edu.tw"):
        """
        發送訂單完成
        """
        from email.mime.text import MIMEText
        from pathlib import Path
        from string import Template
        self.mail_info['From'] = "robin92062574@gmail.com"
        self.mail_info['To'] = to_email
        self.mail_info['subject'] = "<Ecobao>_訂單完成通知"
        html = Template(Path("template_notice.html").read_text(encoding='utf-8'))
        html = html.substitute()
        self.mail_info.attach(MIMEText(html,"html",'utf-8'))
        self.send()

    def order_send(self,to_email):
        """
        發送訂單資訊
        """
        self.content['From'] = "robin92062574@gmail.com"
        self.content['To'] = "C110156220@nkust.edu.tw"
        self.content['subject'] = "<Ecobao>_訂單傳送成功通知"

def test():
    tmp = Email()
    tmp.order_complete()
    print('ok')

test()