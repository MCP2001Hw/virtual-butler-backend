import database_execute, datetime

def add_device(deviceName, deviceType, roomID, userID):
    # Check if the device already exists for the user
    result = database_execute.execute_SQL("""
        SELECT * FROM Devices WHERE deviceName = %s AND userID = %s
    """, (deviceName, userID))

    if result is None:
        data = (
            deviceName, 
            deviceType, 
            roomID, 
            userID, 
            "inactive",
        )

        # Insert the new device into the database
        rows_affected = database_execute.execute_SQL("""
            INSERT INTO Devices (deviceName, deviceType, roomID, userID, deviceStatus) 
            VALUES (%s, %s, %s, %s, %s)
        """, data)

        if rows_affected:
            print(f"Device '{deviceName}' added successfully!")
            return rows_affected
        else:
            print("Failed to add device.")
    else:
        print("Device already exists.")

def remove_device(deviceID):
    # Check if the device exists
    result = database_execute.execute_SQL("""
        SELECT * FROM Devices WHERE deviceID = %s
    """, (deviceID,))

    if result:
        # Delete the device from the database
        rows_deleted = database_execute.execute_SQL("""
            DELETE FROM Devices WHERE deviceID = %s;
        """, (deviceID,))

        if rows_deleted:
            print(f"Device with ID '{deviceID}' removed successfully!")
        else:
            print("Failed to remove device.")
    else:
        print("Device not found.")

def change_name(deviceID, newDeviceName):
    """ Updates the name of a device if it exists. """
    # Check if the device exists
    result = database_execute.execute_SQL("""
        SELECT * FROM Devices WHERE deviceID = %s
    """, (deviceID,))

    if result:
        # Update the device name in the database
        rows_updated = database_execute.execute_SQL("""
            UPDATE Devices
            SET deviceName = %s
            WHERE deviceID = %s;
        """, (newDeviceName, deviceID))

        if rows_updated:
            print(f"Device ID '{deviceID}' renamed to '{newDeviceName}' successfully!")
        else:
            print("Failed to update device name.")
    else:
        print("Device not found.")

def device_activate(deviceID):
    # Check if the device is inactive
    result = database_execute.execute_SQL("""
        SELECT deviceName FROM Devices WHERE deviceID = %s AND deviceStatus = 'inactive'
    """, (deviceID,))

    if result:
        # Activate the device
        rows_updated = database_execute.execute_SQL("""
            UPDATE Devices
            SET deviceStatus = %s
            WHERE deviceID = %s;
        """, ("active", deviceID))

        if rows_updated:
            print(f"Device ID '{deviceID}' activated successfully!")
        else:
            print(f"Failed to activate {result[0][0]}.")
    else:
        print("Device already active or not found.")

def device_deactivate(deviceID):
    # Check if the device is active
    result = database_execute.execute_SQL("""
        SELECT deviceName FROM Devices WHERE deviceID = %s AND deviceStatus = 'active'
    """, (deviceID,))

    if result:
        # Deactivate the device
        rows_updated = database_execute.execute_SQL("""
            UPDATE Devices
            SET deviceStatus = %s
            WHERE deviceID = %s;
        """, ("inactive", deviceID))

        if rows_updated:
            print(f"Device ID '{deviceID}' deactivated successfully!.")
        else:
            print(f"Failed to deactivate {result[0][0]}.")
    else:
        print("Device already deactivated or not found.")
