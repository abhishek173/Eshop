from datetime import datetime

def generateOrderId(index):
    current_date  = datetime.now()
    day = current_date.day
    month = current_date.month
    year = current_date.year
    order_id = f"OD{year}{month}{day}{index.zfill(5)}"
    print("generated Order_id : ",order_id)
    return order_id