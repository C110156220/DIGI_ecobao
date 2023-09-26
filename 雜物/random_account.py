import pymysql
connect = pymysql.connect(host='localhost',port=3306,user='root',passwd='',database='ecobao')
cursor = connect.cursor()
for i in range(2,500):
    sql = "INSERT INTO `data_maintenance_member` (`uid`, `name`, `phone`, `gender`, `email`, `address`, `birth`, `allergen`) VALUES ('test{}', 'test{}', 'test{}', 'test{}', 'test{}', 'test{}', '2023-09-07', 'test{}');".format(i,i,i,i,i,i,i)
    cursor.execute(sql)
    sql = "INSERT INTO `data_maintenance_memberp` (`last_login`, `upid_id`, `account`, `password`, `is_verified`) VALUES ('2023-09-01 22:00:04.000000', 'test{}', 'test{}', 'test{}', '0');".format(i,i,i)
    cursor.execute(sql)
    connect.commit()
cursor.close()
connect.close()