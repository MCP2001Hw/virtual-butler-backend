import database_execute
import datetime
import device_stats_update_database
import time
import threading

# Track device status
initial_dictionary_for_device_status = {}
recently_updated_device = {}
cache_lock = threading.Lock()
last_updated_time = datetime.datetime.now()

schedule_update_time = (0, 0, 0, 1) # Schedule update time: (days, hours, minutes, seconds)
schedule_update_time_in_seconds = schedule_update_time[0] * 24 * 60 * 60 + schedule_update_time[1] * 60 * 60 + schedule_update_time[2] * 60 + schedule_update_time[3]
print(f"Scheduled device statistic update time: {schedule_update_time[0]} days {schedule_update_time[1]} hours {schedule_update_time[2]} minutes {schedule_update_time[3]} seconds, ")


def get_device_id_list():
    device_ids = database_execute.execute_SQL("SELECT deviceID FROM Devices ORDER BY deviceID")
    device_ids = [row[0] for row in device_ids]
    print("Device IDs Retrieved:", device_ids)  # Debugging print
    return device_ids

def get_device_type(device_id):
    result = database_execute.execute_SQL("""SELECT deviceType FROM Devices WHERE deviceID = %s""", (device_id,))
    return result[0][0] if result else None  # Ensure safe access

def get_device_status(device_id):
    result = database_execute.execute_SQL("""SELECT deviceStatus FROM Devices WHERE deviceID = %s""", (device_id,))
    return result[0][0] if result else None

def get_latest_device_usage_and_timestamp(device_id):
    return database_execute.execute_SQL("""
    SELECT deviceUsage, timestamp FROM DeviceStats 
    WHERE deviceID = %s ORDER BY timestamp DESC LIMIT 1
    """, (device_id,))

def get_device_ID_and_type_and_status():
    return database_execute.execute_SQL("""SELECT deviceID, deviceType, deviceStatus FROM Devices""")

def get_device_usage(device_id):
    result = database_execute.execute_SQL("""
    SELECT deviceUsage 
    FROM DeviceStats 
    WHERE deviceID = %s 
    ORDER BY timestamp DESC
    LIMIT 1
    """, (device_id,))
    return result[0][0] if result else 0  # Ensure safe access

def routine_update():
    """ Updates device stats every 30 seconds. """
    device_id_list = get_device_id_list()
    current_time = datetime.datetime.now()

    for device_id in device_id_list:
        # Query database before locking
        device_status = get_device_status(device_id)
        print("Device Status:", device_status)
        device_type = get_device_type(device_id)
        print("Device Type:", device_type)

        # Check last update time before locking
        last_update_time = recently_updated_device.get(device_id, 0)
        print("Last Update Time:", last_update_time)
        usage_data = get_latest_device_usage_and_timestamp(device_id)
        if usage_data == None:
            usage_data = [(0, current_time)]
        print("Usage Data:", usage_data)
        if device_status == "active":
            last_usage, last_timestamp = usage_data[0]
            current_time = datetime.datetime.now()
            print("current time:", current_time)
            print("last timestamp:", last_timestamp)
            time_difference = current_time - last_timestamp
            print("last usage:", last_usage)
            print("time difference:", time_difference.total_seconds)
            new_device_usage = last_usage + time_difference.total_seconds()
            device_stats_update_database.update_device_stats(device_id, device_type, new_device_usage, device_status)
        elif device_status == "inactive":
            device_stats_update_database.update_device_stats(device_id, device_type, 0, device_status)

def routine_update_helper():
    """ Periodically calls routine_update() every 30 seconds. """
    global last_updated_time

    routine_update()

    while True:
        current_time = datetime.datetime.now()
        
        if current_time - last_updated_time >= datetime.timedelta(seconds=schedule_update_time_in_seconds):
            routine_update()  # Call routine update
            last_updated_time = current_time  # Update timestamp
        
        time.sleep(1)  # Prevent CPU overload

def monitor_state_changes():
    while True:
        for device_id, device_type, device_status in get_device_ID_and_type_and_status():
            previous_status = initial_dictionary_for_device_status.get(device_id)

            if previous_status is None:
                initial_dictionary_for_device_status[device_id] = device_status
            elif previous_status != device_status:
                with cache_lock:  # Ensure safe modification
                    if device_status == "active":
                        device_stats_update_database.update_device_stats(device_id, device_type, 0, device_status)
                        recently_updated_device[device_id] = datetime.datetime.now().timestamp()
                    elif device_status == "inactive":
                        new_device_status = "conclusion"
                        
                        # Ensure we do not access an empty result set
                        device_usage = get_device_usage(device_id)
                        
                        device_stats_update_database.update_device_stats(device_id, device_type, device_usage, new_device_status)
                    
                    elif device_status == "conclusion":
                        device_stats_update_database.update_device_stats(device_id, device_type, 0, "inactive")

                    initial_dictionary_for_device_status[device_id] = device_status  # Update tracked status

        time.sleep(1)  # Adjust polling frequency

def clear_cache():
    """ Clears recently_updated_device cache every 10 seconds. """
    while True:
        with cache_lock:
            recently_updated_device.clear()
        time.sleep(10)

# Start functions in parallel
thread1 = threading.Thread(target=routine_update_helper, daemon=True)
thread2 = threading.Thread(target=monitor_state_changes, daemon=True)
thread3 = threading.Thread(target=clear_cache, daemon=True)

thread1.start()
thread2.start()
thread3.start()

# Keep main program running
while True:
    time.sleep(1)  # Prevent CPU overload