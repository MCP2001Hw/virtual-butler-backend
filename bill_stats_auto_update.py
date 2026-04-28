import bill_stats_update_database
import database_execute
import time
import threading
import datetime

PAYMENT_STATUS = {
    "unpaid": 0,
    "paid": 1
}

schedule_update_time = (0, 0, 1, 0)  # (days, hours, minutes, seconds)
schedule_update_time_in_seconds = (
    schedule_update_time[0] * 86400 +
    schedule_update_time[1] * 3600 +
    schedule_update_time[2] * 60 +
    schedule_update_time[3]
)

last_updated_time = datetime.datetime.now()

initial_dictionary_for_payment_status = {}

def get_house_id_list():
    try:
        return [row[0] for row in database_execute.execute_SQL("SELECT houseID FROM House ORDER BY houseID")]
    except Exception as e:
        print(f"Error fetching house IDs: {e}")
        return []

def get_bill_id_and_paid_status_list():
    try:
        return [(row[0], row[1]) for row in database_execute.execute_SQL("SELECT billID, paidStatus FROM BillStats ORDER BY billID")]
    except Exception as e:
        print(f"Error fetching bill IDs: {e}")
        return []

def get_houseID(billID):
    result = database_execute.execute_SQL("SELECT houseID FROM BillStats WHERE BillID = %s", (billID,))
    return result[0][0] if result else None

def get_bill_amount(date1, date2):
    result = database_execute.execute_SQL("""
        SELECT COALESCE(SUM(costsOfEnergy), 0) 
        FROM DeviceStats 
        WHERE timestamp BETWEEN %s AND %s
        AND deviceStatus = 'conclusion'
    """, (date1, date2))
    return result[0][0] if result else 0

def initialise_bill_stats():
    house_id_list = get_house_id_list()
    for house_id in house_id_list:
        current_time = datetime.datetime.now()
        bill_stats_update_database.update_bill_stats(house_id, 0, current_time)

def routine_update():
    house_id_list = get_house_id_list()
    current_time = datetime.datetime.now()

    for house_id in house_id_list:
        bill_amount = get_bill_amount(last_updated_time, current_time)
        bill_stats_update_database.update_bill_stats(house_id, bill_amount, current_time)

def routine_update_helper():
    global last_updated_time

    while True:
        current_time = datetime.datetime.now()
        if current_time - last_updated_time >= datetime.timedelta(seconds=schedule_update_time_in_seconds):
            routine_update()
            last_updated_time = current_time
        time.sleep(1)


# Start threads
thread1 = threading.Thread(target=routine_update_helper, daemon=True)
thread1.start()

initialise_bill_stats()

while True:
        time.sleep(1)