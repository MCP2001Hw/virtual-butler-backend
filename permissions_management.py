import database_execute

# Define user roles and their hierarchy
USER_ROLES = {
    "Homeowner": 3,
    "User": 1,
    "Admin": 2
}

def get_user_role(user_id):
    query = """
        SELECT roles FROM Users WHERE userID = %s
    """
    result = database_execute.execute_SQL(query, (user_id,))
    return result[0][0] if result else None

def has_permission(requester_id, target_user_id):
    requester_role = get_user_role(requester_id)
    target_user_role = get_user_role(target_user_id)

    if requester_role and target_user_role:
        if USER_ROLES[requester_role] > USER_ROLES[target_user_role]:
            return True
        else:
            return False
    else:
        print(f"Invalid roles: requester_role={requester_role}, target_user_role={target_user_role}")
        return False

def can_modify_user(requester_id, target_user_id):
    if not has_permission(requester_id, target_user_id):
        raise PermissionError("Requester does not have permission to modify this user")

def get_user_permissions(user_id):
    query = """
        SELECT deviceManagement, statView FROM Permissions WHERE userID = %s
    """
    result = database_execute.execute_SQL(query, (user_id,))
    return result[0] if result else None

def set_role(user_id, role):
    # Ensure the role is valid before proceeding
    valid_roles = ['Admin', 'User', 'Guest']  # Adjust based on your system roles
    if role not in valid_roles:
        print(f"Invalid role: {role}")
        return  # Early exit if the role is invalid

    print(f"Updating role for user {user_id} to {role}")

    # SQL query to update the user's role
    query = """
        UPDATE Users SET roles = %s WHERE userID = %s
    """
    
    try:
        # Execute the query with the provided parameters
        database_execute.execute_SQL(query, (role, user_id))
        print(f"Role updated successfully for user {user_id} to {role}")
    except Exception as e:
        # Handle potential errors during the database update
        print(f"Error updating role for user {user_id}: {str(e)}")


def allow_device_management(user_id, device_management):
    query = """
        UPDATE Permissions SET deviceManagement = %s WHERE userID = %s
    """
    database_execute.execute_SQL(query, (device_management, user_id))

def allow_statView(user_id, statView):
    query = """
        UPDATE Permissions SET statView = %s WHERE userID = %s
    """
    database_execute.execute_SQL(query, (statView, user_id))