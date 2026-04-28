import database_execute

def add_user(username, password, eMailAddress, firstName, lastName, roles):
    # Check if the username already exists
    result = database_execute.execute_SQL("""
        SELECT * FROM Users WHERE username = %s
    """, (username,))

    if result is None:
        data = (username, password, eMailAddress, firstName, lastName, roles)
        
        # Insert the new user into the database
        rows_affected = database_execute.execute_SQL("""
            INSERT INTO Users (username, password, eMailAddress, firstName, lastName, roles)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, data)

        if rows_affected:
            print(f"User '{username}' added successfully!")
            return rows_affected
        else:
            print("Failed to add user.")
    else:
        print("Duplicate username! User already exists.")

def remove_user(username):
    # Check if the user exists
    result = database_execute.execute_SQL("""
        SELECT * FROM Users WHERE username = %s
    """, (username,))

    if result:
        # Delete the user from the database
        rows_deleted = database_execute.execute_SQL("""
            DELETE FROM Users WHERE username = %s
        """, (username,))

        if rows_deleted:
            print(f"User '{username}' removed successfully!")
        else:
            print("Failed to remove user.")
    else:
        print("User not found.")