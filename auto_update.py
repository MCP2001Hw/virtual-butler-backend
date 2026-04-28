import weather_auto_update, bill_stats_auto_update, device_stats_auto_update
import threading
import time

weather_auto_update.routine_update()
bill_stats_auto_update.routine_update()

thread1 = threading.Thread(target=weather_auto_update.routine_update_helper, daemon=True)
thread2 = threading.Thread(target=bill_stats_auto_update.routine_update_helper, daemon=True)
thread3 = threading.Thread(target=device_stats_auto_update.routine_update_helper, daemon=True)
thread4 = threading.Thread(target=device_stats_auto_update.monitor_state_changes, daemon=True)
thread5 = threading.Thread(target=device_stats_auto_update.clear_cache, daemon=True)

thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()

while True:
    time.sleep(1)