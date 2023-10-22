
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

    def order_complete(self,to_email=None,data):
        """
        發送訂單完成
        """
        if to_email == None :
            return(False)

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

    def order_send(self,to_email=None,data):
        """
        發送訂單資訊
        """
        if to_email == None :
            return(False)
        self.content['From'] = "robin92062574@gmail.com"
        self.content['To'] = to_email
        self.content['subject'] = "<Ecobao>_訂單傳送成功通知"
        data = {
            'subject': data['subject'],
            'name' : data['name'],
            'order_id' : data['order_id'],
            'order_time' : data['order_time'],
            'order_store' : data['order_store'],
            'order_complete_time' : data['order_complete_time'],
            'order_price' : data['order_total_price'],
            'data_food': data['data_food']
            }

    def order_cancel(self,to_email=None,data):
        """
        發送訂單取消
        """
        if to_email == None :
            return(False)
        self.content['From'] = "robin92062574@gmail.com"
        self.content['To'] = to_email
        self.content['subject'] = "<Ecobao>_訂單傳送取消通知"
        data = {
            'subject': data['subject'],
            'name' : data['name'],
            'order_id' : data['order_id'],
            'order_time' : data['order_time'],
            'order_store' : data['order_store'],
            'order_complete_time' : data['order_complete_time'],
            'order_price' : data['order_total_price'],
            'data_food': data['data_food']
            }
        if self.__template('order.html',data):
            html_part = MIMEText(rendered_template, 'html')
        else:
            return(False)

    def __template(self,path_data,backend_data):
        """
        html模板，使用jinja2進行輸出
        """
        from jinja2 import Template
        try:
            with open(path_data, "r") as template_file:
                email_template = template_file.read()

                template = Template(email_template)
                rendered_template = template.render(backend_data)
                return(rendered_template)
        except Exception as e :
            print(e)
            return(False)
