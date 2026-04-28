import database_execute

def add_room(roomName, userID, houseID):
    # Check if the room already exists for the user
    result = database_execute.execute_SQL("""
        SELECT * FROM Rooms WHERE roomName = %s AND userID = %s
    """, (roomName, userID))

    if result is None:
        data = (roomName, userID, houseID, "Free")

        # Insert the new room into the database
        rows_affected = database_execute.execute_SQL("""
            INSERT INTO Rooms (roomName, userID, houseID, occupation) 
            VALUES (%s, %s, %s, %s)
        """, data)

        if rows_affected:
            print(f"Room '{roomName}' added successfully!")
        else:
            print("Failed to add room.")
    else:
        print("Room already exists for this user.")

def remove_room(roomID):
    # Check if the room exists
    result = database_execute.execute_SQL("""
        SELECT * FROM Rooms WHERE roomID = %s
    """, (roomID,))

    if result:
        # Delete the room from the database
        rows_deleted = database_execute.execute_SQL("""
            DELETE FROM Rooms WHERE roomID = %s;
        """, (roomID,))

        if rows_deleted:
            print(f"Room with ID '{roomID}' removed successfully!")
        else:
            print("Failed to remove room.")
    else:
        print("Room not found.")

def change_room_name(roomID, newRoomName):
    # Check if the room exists
    result = database_execute.execute_SQL("""
        SELECT * FROM Rooms WHERE roomID = %s
    """, (roomID,))

    if result:
        # Update the room name in the database
        rows_updated = database_execute.execute_SQL("""
            UPDATE Rooms
            SET roomName = %s
            WHERE roomID = %s;
        """, (newRoomName, roomID))

        if rows_updated:
            print(f"Room ID '{roomID}' renamed to '{newRoomName}' successfully!")
        else:
            print("Failed to update room name.")
    else:
        print("Room not found.")

def change_room_status(roomID, newOccupation):
    # Validate the new occupation status
    if newOccupation not in ("Occupied", "Free"):
        print("Invalid status! Choose from 'Occupied' or 'Free'")
        return

    # Check if the room exists
    result = database_execute.execute_SQL("""
        SELECT * FROM Rooms WHERE roomID = %s
    """, (roomID,))

    if result:
        # Update the room occupation status in the database
        rows_updated = database_execute.execute_SQL("""
            UPDATE Rooms
            SET occupation = %s
            WHERE roomID = %s;
        """, (newOccupation, roomID))

        if rows_updated:
            print(f"Room ID '{roomID}' status changed to '{newOccupation}' successfully!")
        else:
            print("Failed to update room occupation.")
    else:
        print("Room not found.")