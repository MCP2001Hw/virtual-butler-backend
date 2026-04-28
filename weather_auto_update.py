import database_execute
import weather_update_database
import datetime
import time
import threading

last_updated_time = datetime.datetime.now()

schedule_update_time = (0, 0, 0, 30) # Schedule update time: (days, hours, minutes, seconds)
schedule_update_time_in_seconds = schedule_update_time[0] * 24 * 60 * 60 + schedule_update_time[1] * 60 * 60 + schedule_update_time[2] * 60 + schedule_update_time[3]
print(f"Scheduled weather update time: {schedule_update_time[0]} days {schedule_update_time[1]} hours {schedule_update_time[2]} minutes {schedule_update_time[3]} seconds, ")

def get_house_id_list():
    try:
        return [row[0] for row in database_execute.execute_SQL("SELECT houseID FROM House ORDER BY houseID")]
    except Exception as e:
        print(f"Error fetching house IDs: {e}")
        return []


def routine_update():
    house_id_list = get_house_id_list()
    for house_id in house_id_list:
        weather_update_database.update_weather(house_id)

def routine_update_helper():
    global last_updated_time

    while True:
        current_time = datetime.datetime.now()
        if current_time - last_updated_time >= datetime.timedelta(seconds=schedule_update_time_in_seconds):
            routine_update()
            last_updated_time = current_time
        time.sleep(1)
    
threadW = threading.Thread(target=routine_update_helper, daemon=True)

threadW.start()

# Keep main program running
while True:
    time.sleep(1)  # Prevent CPU overload