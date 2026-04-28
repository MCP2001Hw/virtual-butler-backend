import database_execute

def add_house(postcode, street, city, userID):
    # Check if the house already exists
    result = database_execute.execute_SQL("""
        SELECT * FROM House WHERE postcode = %s
    """, (postcode,))
    
    if result is None:
        data = (postcode, street, city, userID)
        
        # Insert the new house into the database
        rows_affected = database_execute.execute_SQL("""
            INSERT INTO House (postcode, street, city, userID) 
            VALUES (%s, %s, %s, %s)
        """, data)

        if rows_affected:
            print("House added successfully!")
        else:
            print("Failed to add house.")
    else:
        print("Duplicate address found.")

def remove_house(postcode):
    # Check if the house exists
    result = database_execute.execute_SQL("""
        SELECT * FROM House WHERE postcode = %s
    """, (postcode,))

    if result:
        # Delete the house from the database
        rows_deleted = database_execute.execute_SQL("""
            DELETE FROM House WHERE postcode = %s;
        """, (postcode,))

        if rows_deleted:
            print(f"House with postcode '{postcode}' removed successfully!")
        else:
            print("Failed to remove house.")
    else:
        print("House not found.")

def change_house_data(userID, postcode, street, city):
    """ Updates house details if the house exists. """
    # Check if the house exists
    result = database_execute.execute_SQL("""
        SELECT houseID FROM House 
        WHERE userID = %s AND postcode = %s AND street = %s AND city = %s
    """, (userID, postcode, street, city))

    if result:
        house_id = result[0][0]
        data = (userID, postcode, street, city, house_id)

        # Update the house details in the database
        rows_updated = database_execute.execute_SQL("""
            UPDATE House
            SET userID = %s, postcode = %s, street = %s, city = %s
            WHERE houseID = %s;
        """, data)

        if rows_updated:
            print("House data updated successfully!")
        else:
            print("Failed to update house data.")
    else:
        print("Invalid details, house not found.")