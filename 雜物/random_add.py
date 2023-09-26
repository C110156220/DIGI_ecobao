import pymysql , random
upid = 'test'
area = ["臺北市","新北市","桃園市","臺中市","臺南市","高雄市"]
lat,lng =22.772558362730198, 120.40022782571859
type = ['素食','速食','日式','中式','滷味','宵夜','西式']
str_1 = ['美味','好吃','測試','好味','高興','蕭蕭']
str_2 = ['店','小吃店','專賣店','直營店','加盟店','小吃攤']
intro = "test"
address = "test"
link = "nope"
on_business = 1
connect = pymysql.connect(database='ecobao',host='localhost',port=3306,user='root',passwd='')
cursor = connect.cursor()
for i in range(2,500):
    sql = "INSERT INTO `data_maintenance_store` (`sid`, `upid_id`, `type`, `name`, `intro`, `area`, `address`, `lng`, `lat`, `link`, `on_business`) VALUES ('test{}', 'test{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(i,i,random.choice(type),random.choice(str_1)+random.choice(str_2),intro,random.choice(area),address,lng,lat,link,on_business)
    cursor.execute(sql)
    connect.commit()
connect.close()