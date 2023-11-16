from app import *

data = {
        "oid": "OD000019",
        "orderfoods": [
            {
                "id": 29,
                "store_name": "彬彬炸雞",
                "sid": "S00003",
                "goods_price": "40",
                "goods_name": "薯條(小)",
                "quantity": 1,
                "discount": 0,
                "subtotal": 40,
                "oid": "OD000019",
                "gid": "G00002"
            }
        ],
        "orderpayments": [
            {
                "id": 7,
                "method": "到店取付",
                "credit_number": None,
                "credit_private": None,
                "credit_date_year": None,
                "credit_date_month": None,
                "oid": "OD000019"
            }
        ],
        "order_time": "2023-11-02T07:50:17.618432Z",
        "complete_time": None,
        "total": "40.00",
        "status": "未接單",
        "uid": "admin01",
        "email": "C110156220@nkust.edu.tw",
    }
ob = Email()
ob.order(status="Success",data=data)
