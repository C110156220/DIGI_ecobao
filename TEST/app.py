
class Email:
    def __init__(self, content=None):
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        # 信件內容
        self.mail_info = MIMEMultipart()
        # self.content = content
        # 寄信伺服器
        self.account = "robin92062574@gmail.com"
        self.password = "ajuv lppx jrfu wjsl"

    def send(self, email):

        import smtplib
        server = smtplib.SMTP("smtp.gmail.com", 587)  # 建立gmail連驗
        server.ehlo()
        server.starttls()
        server.login(self.account, self.password)
        status = server.send_message(self.mail_info, self.account, email)
        print(status)
        server.quit()

    def order(self,status:str,data:dict) -> None:
        """
        status =
            "Complete":"<Ecobao>_訂單完成通知",
            "Success":"<Ecobao>_訂單傳送成功通知",
            "FoodReady":"<Ecobao>_餐點準備完成，請取餐",
            "Cencel":"<Ecobao>_訂單取消通知"

        """
        s = {
            "Complete":"<Ecobao>_訂單完成通知",
            "Success":"<Ecobao>_訂單傳送成功通知",
            "FoodReady":"<Ecobao>_餐點準備完成，請取餐",
            "Cencel":"<Ecobao>_訂單取消通知"
        }
        from email.mime.text import MIMEText
        self.mail_info['From'] = "robin92062574@gmail.com"
        self.mail_info['To'] = data['email']
        self.mail_info['subject'] = s[status]
        mail_data = {
            'subject': s[status],
            'name': data['uid'],
            'order_id': data['oid'],
            'order_time': data['order_time'],
            'order_store': data['orderfoods'][0]["store_name"],
            'order_complete_time': data['complete_time'],
            'order_price': data['total'],
            'data_food': data['orderfoods'],
            'status': data['status']
        }
        try:
            self.mail_info.attach(
                MIMEText(self.__template('order.html', mail_data), 'html'))
            self.send(data['email'])
            print('ok')
        except Exception as e:
            raise SystemError(f'內容加入出問題，{e}')


    def __template(self, path_data, backend_data):
        """
        html模板，使用jinja2進行輸出
        """
        from jinja2 import Template
        try:
            with open(path_data, "r", encoding='utf8') as template_file:
                email_template = template_file.read()

                template = Template(email_template)
                rendered_template = template.render(backend_data)
                return (rendered_template)
        except Exception as e:
            raise SystemError(e)
            print('jinja Error')
            return (False)
