import pymysql
from django.contrib.auth.hashers import make_password,check_password
connect = pymysql.connect(host='localhost',port=3306,user='root',passwd='',database='ecobao')
cursor = connect.cursor()
for i in range(2,500):
    sql = "INSERT INTO `data_maintenance_memberp` (`uid`, `account`, `password`, `is_active`, `is_staff`, `is_superuser`, `last_login`, `date_joined`) VALUES ('M{0:5d}', 'test{}', {}, '1', '0', '0', NULL, '2023-10-01 00:19:04.000000');".format(i,i,make_password('test{}'.format(i)))

    cursor.execute(sql)
    sql = "INSERT INTO `data_maintenance_member` (`uid_id`, `name`, `phone`, `gender`, `email`, `address`, `birth`, `allergen`) VALUES ('test{}', 'test{}', 'test{}', 'test{}', 'test{}', 'test{}', '2023-09-07', 'test{}');".format(i,i,i,i,i,i,i)

    cursor.execute(sql)
    connect.commit()
cursor.close()
connect.close()