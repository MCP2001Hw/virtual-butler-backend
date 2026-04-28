from flask import Flask, jsonify, request, session
import flask_cors
import flask_session
import database_execute, permissions_management, device_management, user_management
import datetime
import decimal
import bcrypt
# import device_stats_auto_update
# import weather_auto_update
# import bill_stats_auto_update

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)
flask_session.Session(app)
flask_cors.CORS(app, origins="*")

# User Authentication Functions
# -----------------------------

@app.route('/update_profile', methods=['POST'])
def update_profile():
    try:
        # Get JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract username and updated_info from the request
        username = data.get('username')
        updated_info = data.get('updated_info')

        if not username or not updated_info:
            return jsonify({"error": "Username and updated information are required"}), 400

        # Fetch the user from the database
        user = get_user_by_username(username)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Map frontend fields to backend database columns
        field_mapping = {
            "first name": "firstName",
            "last name": "lastName",
            "e_mail": "eMailAddress",
            "password": "password",
        }

        # Update user fields from updated_info
        for field, new_value in updated_info.items():
            if field == "password":
                # Hash the new password before saving it to the database
                new_value = bcrypt.hashpw(new_value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Check if the field exists in the user data and update accordingly
            if field in user:
                user[field] = new_value
                db_field = field_mapping.get(field)

                if db_field:
                    update_query = f"UPDATE Users SET {db_field} = %s WHERE userName = %s"
                    database_execute.execute_SQL(update_query, (new_value, username))

        # After updating, fetch the updated user from the database
        updated_user = get_user_by_username(username)

        return jsonify({"message": "Profile updated successfully", "user": updated_user})

    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

def get_house_id_by_username(username):
    query = """
        SELECT houseID 
        FROM Users
        WHERE username = %s
    """
    result = database_execute.execute_SQL(query, (username,))
    return result

def get_user_by_username(username):
    query = """
        SELECT firstName, lastName, userName, eMailAddress, password 
        FROM Users 
        WHERE userName = %s
    """
    result = database_execute.execute_SQL(query, (username,))
    
    # Assuming the result is a list of tuples, convert it to a dictionary
    if result:
        return {
            "first name": result[0][0],
            "last name": result[0][1],
            "user name": result[0][2],
            "e_mail": result[0][3],
            "password": result[0][4]
        }
    return None


# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({"error": "username and password are required"}), 400

    user = database_execute.execute_SQL("""
        SELECT userID, password FROM Users WHERE username = %s
    """, (username,))

    if user:
        stored_hashed_password = user[0][1].encode('utf-8')

        # Securely compare hashed passwords
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
            session['user_id'] = user[0][0]
            session.permanent = True
            return jsonify({"message": "Login successful"}), 200

    return jsonify({"error": "Invalid username or password"}), 401

# Route for user logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logout successful"}), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    role = data.get('role')

    if not all([username, password, email, first_name, last_name, role]):
        return jsonify({"error": "All fields are required"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        query = """
            INSERT INTO Users (username, password, eMailAddress, firstName, lastName, roles)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        params = (username, hashed_password, email, first_name, last_name, role)
        database_execute.execute_SQL(query, params)

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# User Management Functions
# -------------------------

def get_active_devices_count(house_id):
    query = """
        SELECT COUNT(*) 
        FROM Devices
        JOIN Rooms ON Devices.roomID = Rooms.roomID
        WHERE Devices.deviceStatus = 'active' AND Rooms.houseID = %s;
    """
    result = database_execute.execute_SQL(query, (house_id,))
    return result[0][0] if result else 0

# Function to get the count of occupied rooms in a house
def get_occupied_rooms_count(house_id):
    query = """
        SELECT COUNT(*) 
        FROM Rooms
        WHERE occupation = 'Occupied' AND houseID = %s;
    """
    result = database_execute.execute_SQL(query, (house_id,))
    return result[0][0] if result else 0

# Function to get the total energy cost since the last payment date for a house
def get_energy_cost_total(house_id, last_payment_date):
    query = """
        SELECT SUM(DeviceStats.costsOfEnergy) 
        FROM DeviceStats
        JOIN Devices ON DeviceStats.deviceID = Devices.deviceID
        JOIN Rooms ON Devices.roomID = Rooms.roomID
        WHERE Rooms.houseID = %s AND DeviceStats.timestamp > %s;
    """
    result = database_execute.execute_SQL(query, (house_id, last_payment_date))
    return result[0][0] if result and result[0][0] is not None else 0

# Function to get the latest weather information for a house
def get_latest_weather(house_id):
    query = """
        SELECT weatherType, temperature, humidity, windSpeed
        FROM Weather
        WHERE houseID = %s
        ORDER BY timestamp DESC
        LIMIT 1;
    """
    result = database_execute.execute_SQL(query, (house_id,))
    return result[0] if result else ("Unknown", None, None, None)

# Function to get the bill status for a house
def get_bill_status(house_id):
    query = """
        SELECT amount, paidStatus
        FROM BillStats
        WHERE houseID = %s
        ORDER BY timestamp DESC
        LIMIT 1;
    """
    result = database_execute.execute_SQL(query, (house_id,))
    if result:
        amount, paid_status = result[0]
        paid_status = "Paid" if paid_status == 1 else "Unpaid"
        return amount, paid_status
    return None, None, None, None

# Route to get home data
@app.route('/home', methods=['GET'])
def get_home():
    username = request.args.get('username')
    house_id_list = get_house_id_by_username(username)
    house_id = house_id_list[0][0]
    last_payment_date = request.args.get('last_payment_date')

    if not house_id:
        return jsonify({"error": "house_id is required"}), 400

    try:
        active_devices_count = get_active_devices_count(house_id)
        occupied_rooms_count = get_occupied_rooms_count(house_id)
        energy_cost_total = get_energy_cost_total(house_id, last_payment_date)
        weather_type, temperature, humidity, wind_speed = get_latest_weather(house_id)
        past_bill_amount, paid_status,= get_bill_status(house_id)
        current_amount = energy_cost_total

        inside_the_residence = {
            "Devices_Active": active_devices_count,
            "Rooms_Occupied": occupied_rooms_count
        }

        outside_the_residence = {
            "Weather_Description": weather_type,
            "Temperature": int(temperature / decimal.Decimal('0.5')) * 0.5,
            "Humidity": humidity,
            "Wind_Speed": wind_speed
        }

        energy_bill = {
            "Bill_Paid_Status": paid_status,
            "Past_Bill_Amount": past_bill_amount,
            "Current_Amount": current_amount
        }

        response_data = {
            "Inside_The_Residence": inside_the_residence,
            "Outside_The_Residence": outside_the_residence,
            "Energy_Bill": energy_bill
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def get_all_rooms(house_id):
    query = """
        SELECT r.roomID, r.roomName FROM Rooms r WHERE r.houseID = %s
    """
    return database_execute.execute_SQL(query, (house_id,))

def get_all_devices_in_this_room(room_id):
    query = """
        SELECT d.deviceName, d.deviceStatus FROM Devices d WHERE d.roomID = %s
    """
    return database_execute.execute_SQL(query, (room_id,))

@app.route('/rooms', methods=['GET'])
def get_rooms():
    username = request.args.get('username')
    house_id_list = get_house_id_by_username(username)
    house_id = 1 #house_id_list[0][0]


    if not house_id:
        return jsonify({"error": "house_id is required"}), 400

    try:
        rooms = get_all_rooms(house_id)
        device_list_in_this_room = {}
        for room in rooms:
            room_id = room[0]
            room_name = room[1]
            device_list = get_all_devices_in_this_room(room_id)
            if room_name not in device_list_in_this_room:
                device_list_in_this_room[room_name] = []
            for device in device_list:
                device_name = device[0]
                device_status = device[1]
                data = {
                    "device_name": device_name,
                    "device_status": device_status
                }
                device_list_in_this_room[room_name].append(data)
        
        return jsonify(device_list_in_this_room)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
# Function to get the past 24-hour energy consumption sorted by device type
def get_last_24_hours_energy_consumption_per_device(house_id):
    query = """
        SELECT 
            ds.deviceID, 
            d.deviceName, 
            r.roomName,
            SUM(ds.energyConsumption)
        FROM 
            DeviceStats ds
        JOIN 
            Devices d ON ds.deviceID = d.deviceID
        JOIN
            Rooms r ON d.roomID = r.roomID
        WHERE
            ds.timestamp BETWEEN NOW() - INTERVAL 1 DAY AND NOW() 
            AND r.houseID = %s
        GROUP BY 
            ds.deviceID, d.deviceName, r.roomName
        ORDER BY 
            SUM(ds.energyConsumption) DESC
    """
    result = database_execute.execute_SQL(query, (house_id,))
    return result

def get_total_energy_consumed_in_last_24_hours(house_id):
    query = """
        SELECT 
        SUM(ds.energyConsumption)
        FROM 
        DeviceStats ds
        JOIN 
        Devices d ON ds.deviceID = d.deviceID
        JOIN
        Rooms r ON d.roomID = r.roomID
        WHERE
        timestamp BETWEEN NOW() - INTERVAL 1 DAY AND NOW() 
        AND houseID = %s
        ORDER BY 
        ds.deviceID DESC
    """
    result = database_execute.execute_SQL(query, (house_id,))
    return result

def get_total_costs_of_energy_in_last_24_hours(house_id):
    query = """
        SELECT 
        SUM(ds.costsOfEnergy)
        FROM 
        DeviceStats ds
        JOIN 
        Devices d ON ds.deviceID = d.deviceID
        JOIN
        Rooms r ON d.roomID = r.roomID
        WHERE
        timestamp BETWEEN NOW() - INTERVAL 1 DAY AND NOW() 
        AND houseID = %s
        ORDER BY 
        ds.deviceID DESC
    """
    result = database_execute.execute_SQL(query, (house_id,))
    return result

def get_energy_consumption_by_time_interval(house_id, time1, time2):
    query = """
        SELECT 
        COALESCE(SUM(ds.energyConsumption), 0)
        FROM 
        DeviceStats ds
        JOIN 
        Devices d ON ds.deviceID = d.deviceID
        JOIN
        Rooms r ON d.roomID = r.roomID
        WHERE 
        timestamp BETWEEN NOW() - INTERVAL 1 DAY AND NOW()
        AND TIME(ds.timestamp) BETWEEN %s AND %s
        AND r.houseID = %s
        ORDER BY 
        ds.deviceID DESC
    """
    result = database_execute.execute_SQL(query, (time1, time2, house_id))
    return result

def get_last_completed_jobs(house_id):
    query = """
        SELECT 
            d.deviceName, 
            SUM(ds.energyConsumption) AS totalEnergyConsumption
        FROM 
            DeviceStats ds
        JOIN 
            Devices d ON ds.deviceID = d.deviceID
        JOIN
            Rooms r ON d.roomID = r.roomID
        WHERE 
            ds.timestamp BETWEEN NOW() - INTERVAL 1 DAY AND NOW()
            AND r.houseID = %s
        GROUP BY 
            d.deviceName
        ORDER BY 
            totalEnergyConsumption DESC;
    """
    result = database_execute.execute_SQL(query, (house_id,))
    return result

def message_data(house_id):
    query = """
        SELECT 
            DATE_FORMAT(ds.timestamp, '%h:%i %p') AS formatted_timestamp,               
            d.deviceName,
            ds.deviceStatus
        FROM 
            DeviceStats ds
        JOIN 
            Devices d ON ds.deviceID = d.deviceID
        JOIN
            Rooms r ON d.roomID = r.roomID
        WHERE 
            r.houseID = %s
            AND ds.deviceStatus IN ('active', 'conclusion')
        ORDER BY 
            ds.timestamp DESC;
    """
    result = database_execute.execute_SQL(query, (house_id,))
    return result

# Route to get dashboard data
@app.route('/dashboard', methods=['GET'])
def get_dashboard():
    username = request.args.get('username')
    house_id_list = get_house_id_by_username(username)
    house_id = house_id_list[0][0]

    if not house_id:
        return jsonify({"error": "house_id is required"}), 400

    try:
        total_energy_consumed_in_last_24_hours = get_total_energy_consumed_in_last_24_hours(house_id)
        total_costs_of_energy_in_last_24_hours = get_total_costs_of_energy_in_last_24_hours(house_id)
        last_24_hours_energy_consumption_per_device = get_last_24_hours_energy_consumption_per_device(house_id)

        device_list = last_24_hours_energy_consumption_per_device

        Last_24_hours = {
            "total_energy_consumed": total_energy_consumed_in_last_24_hours[0][0],
            "total_costs_of_energy": total_costs_of_energy_in_last_24_hours[0][0]
        }

        Most_energy_used_by = {}

        if device_list:
            if len(device_list) > 0:
                Most_energy_used_by["device 1"] = {
                    "device_id": device_list[0][0],
                    "device_name": device_list[0][1],
                    "room_name": device_list[0][2],
                    "energy_consumed": device_list[0][3],
                }

            if len(device_list) > 1:
                Most_energy_used_by["device 2"] = {
                    "device_id": device_list[1][0],
                    "device_name": device_list[1][1],
                    "room_name": device_list[1][2],
                    "energy_consumed": device_list[1][3],
                }

            if len(device_list) > 2:
                Most_energy_used_by["device 3"] = {
                    "device_id": device_list[2][0],
                    "device_name": device_list[2][1],
                    "room_name": device_list[2][2],
                    "energy_consumed": device_list[2][3],
                }
        else:
            Most_energy_used_by = {"device_id": "None",
            "device_name": "None",
            "room_name": "None",
            "energy_consumed": "None"
            }


        Consumption = {
            "12am to 6am": get_energy_consumption_by_time_interval(house_id, '00:00:00', '06:00:00'),
            "6am to 12pm": get_energy_consumption_by_time_interval(house_id, '06:00:00', '12:00:00'),
            "12pm to 4pm": get_energy_consumption_by_time_interval(house_id, '12:00:00', '16:00:00'),
            "4pm to 8pm": get_energy_consumption_by_time_interval(house_id, '16:00:00', '20:00:00'),
            "8pm to 12am": get_energy_consumption_by_time_interval(house_id, '20:00:00', '00:00:00')
        }

        pie_chart = {
            "devices": get_last_completed_jobs(house_id)
        }

        messages = message_data(house_id)

        response_data = {
        "Last_24_hours": Last_24_hours,
        "Most_energy_used_by": Most_energy_used_by,
        "Consumption": Consumption,
        "pie_chart": pie_chart,
        "messages": messages  # Add messages to the response data
    }


        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def get_all_devices(house_id):
    query = """
        SELECT Devices.deviceID, Devices.deviceName, Devices.deviceType, Devices.deviceStatus
        FROM Devices
        JOIN Rooms ON Devices.roomID = Rooms.roomID
        WHERE Rooms.houseID = %s;
    """
    result = database_execute.execute_SQL(query, (house_id,))
    return result if result else []

# Route to get all devices for a house
@app.route('/devices', methods=['GET'])
def get_devices():
    username = request.args.get('username')
    house_id_list = get_house_id_by_username(username)
    house_id = house_id_list[0][0]

    if not house_id:
        return jsonify({"error": "house_id is required"}), 400

    try:
        devices = get_all_devices(house_id)
        return jsonify({"devices": devices}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def get_energy_data(house_id, start_interval=None, 
                    end_interval=None):
    interval_condition = ""

    if start_interval is not None:
        if end_interval is not None:
            interval_condition = f"AND timestamp >= NOW() - INTERVAL {start_interval} DAY AND timestamp < NOW() - INTERVAL {end_interval} DAY"
        else:
            interval_condition = f"AND timestamp >= NOW() - INTERVAL {start_interval} DAY"

    query = f"""
        SELECT d.deviceName, 
               SUM(energyConsumption), 
               SUM(energyGeneration), 
               SUM(deviceUsage), 
               d.deviceStatus,
               SUM(costsOfEnergy), 
               r.roomName
        FROM DeviceStats ds
        JOIN Devices d ON ds.deviceID = d.deviceID
        JOIN Rooms r ON r.roomID = d.roomID
        WHERE r.houseID = %s
        {interval_condition}
        AND ds.deviceStatus = 'conclusion'
        GROUP BY r.roomName, d.deviceName, d.deviceStatus
    """

    result = database_execute.execute_SQL(query, (house_id,))
    return result if result else []

def process_energy_data(house_id, start_days, end_days=None):
    data1 = {}
    data2 = {}

    # Fetch energy data
    data_list_1 = get_energy_data(house_id, start_days)
    data_list_2 = get_energy_data(house_id, end_days, start_days) if end_days else []

    # Process primary data
    for data in data_list_1:
        device_name = data[0]
        entry = {
            "device_name": device_name,
            "energy_consumption": data[1],
            "energy_generation": data[2],
            "device_usage": data[3],
            "device_status": data[4],
            "costs_of_energy": data[5],
            "room_name": data[6]
        }
        data1.setdefault(device_name, []).append(entry)

    # Process comparison data
    for data in data_list_2:
        device_name = data[0]
        entry = {
            "device_name": device_name,
            "energy_consumption": data[1],
            "energy_generation": data[2],
            "device_usage": data[3],
            "device_status": data[4],
            "costs_of_energy": data[5],
            "room_name": data[6]
        }
        data2.setdefault(device_name, []).append(entry)

    return {"data_1": data1, "data_2": data2}

def get_total_energy_data(house_id, start_interval=None, 
                    end_interval=None):
    interval_condition = ""

    if start_interval is not None:
        if end_interval is not None:
            interval_condition = f"AND timestamp >= NOW() - INTERVAL {start_interval} DAY AND timestamp < NOW() - INTERVAL {end_interval} DAY"
        else:
            interval_condition = f"AND timestamp >= NOW() - INTERVAL {start_interval} DAY"

    query = f"""
        SELECT sum(ds.energyConsumption), sum(ds.energyGeneration), sum(ds.deviceUsage), sum(ds.costsOfEnergy)
        FROM DeviceStats ds
        JOIN Devices d ON d.deviceID = ds.deviceID
        JOIN Rooms r ON r.roomID = d.roomID
        WHERE r.houseID = %s
        {interval_condition}
    """

    result= database_execute.execute_SQL(query, (house_id,))
    return result if result else []

def process_total_energy_data(house_id, start_days, end_days=None):
    data1 = {}
    data2 = {}

    # Fetch energy data
    data_list_1 = get_total_energy_data(house_id, start_days)
    data_list_2 = get_total_energy_data(house_id, end_days, start_days) if end_days else []

    # Process primary data
    for data in data_list_1:
        result1 = {
            "total_energy_consumption": data[0],
            "total_energy_generation": data[1],
            "total_device_usage": data[2],
            "total_cost": data[3]
        }

    # Process comparison data
    for data in data_list_2:
        result2 = {
            "total_energy_consumption": data[0],
            "total_energy_generation": data[1],
            "total_device_usage": data[2],
            "total_cost": data[3]
        }

    return {"result_1": result1, "result_2": result2}

@app.route('/stats', methods=['GET'])
def get_stats():
    username = request.args.get('username')
    intervals = request.args.get('intervals')
    house_id_list = get_house_id_by_username(username)
    house_id = house_id_list[0][0]

    
    try:
        top_data = {}
        bottom_data = {}

        if intervals == "Day":
            top_data = process_energy_data(house_id, 1, 2)
            bottom_data = process_total_energy_data(house_id, 1, 2)
        elif intervals == "Week":
            top_data = process_energy_data(house_id, 7, 14)
            bottom_data = process_total_energy_data(house_id, 7, 14)
        elif intervals == "Month":
            top_data = process_energy_data(house_id, 30, 60)
            bottom_data = process_total_energy_data(house_id, 30, 60)
        elif intervals == "Year":
            top_data = process_energy_data(house_id, 365, 730)
            bottom_data = process_total_energy_data(house_id, 365, 730)
        result = {
            "top_data": top_data,
            "bottom_data": bottom_data
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Function to get all users
def get_all_users(house_id):
    query = """
    SELECT username, roles
    FROM Users
    WHERE houseID = %s
    """
    result = database_execute.execute_SQL(query, (house_id,))
    return result if result else []

# Route to get all users
@app.route('/users', methods=['GET'])
def get_users():
    username = request.args.get('username')
    house_id_list = get_house_id_by_username(username)
    house_id = house_id_list[0][0]
    try:
        users = get_all_users(house_id)
        return jsonify({"users": users}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def get_user_info(user_id):
    query = """
        SELECT firstName, lastName, userName, eMailAddress, password 
        FROM Users 
        WHERE userID = %s
    """
    result = database_execute.execute_SQL(query, (user_id,))
    return result

def get_house_address(house_id):
    query = """
        SELECT postcode, street, city
        FROM House 
        WHERE houseID = %s
    """
    result = database_execute.execute_SQL(query, (house_id,))
    return result

def get_user_id_by_username(username):
    query = """
        SELECT userID
        FROM Users
        WHERE username = %s
    """
    result = database_execute.execute_SQL(query, (username,))
    return result
    
@app.route('/my_profiles', methods=['GET'])
def get_my_profiles():
    username = request.args.get('username')
    house_id_list = get_house_id_by_username(username)
    house_id = house_id_list[0][0]
    user_id_list = get_user_id_by_username(username)
    user_id = user_id_list[0][0]
    try:
        profile_list = get_user_info(user_id)
        profile = profile_list[0]
        first_name = profile[0]
        last_name = profile[1]
        username = profile[2]
        e_mail = profile[3]
        password = profile[4]

        nick_name = first_name + "'s House"
        address_info_list = get_house_address(house_id)
        address_info = address_info_list[0]
        address = address_info[0] + " " + address_info[1]

        user_info = {
            "first name": first_name,
            "last name": last_name,
            "username": username,
            "e_mail": e_mail,
            "password": password
        }

        residence = {
            "nick name": nick_name,
            "address": address
        }

        my_profile = {
            "user_info": user_info,
            "residence": residence
        }
        return jsonify({"my_profile": my_profile}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to update the role of a user
@app.route('/update_user_role', methods=['POST'])
def update_user_role():
    username = request.args.get('username')
    changedUsername = request.args.get('changedUsername')
    user_id_list = get_user_id_by_username(changedUsername)
    user_id = user_id_list[0][0]
    new_role = request.args.get('new_role')
    requester_id_list = get_user_id_by_username(username)
    requester_id = requester_id_list[0][0]

    if not all([user_id, new_role, requester_id]):
        return jsonify({"error": "user_id, new_role, and requester_id are required"}), 400

    try:
        if permissions_management.has_permission(requester_id, user_id) == False:
            return jsonify({"error": "Requester does not have permission to update this user"}), 403
        rows_affected = permissions_management.set_role(user_id, new_role)

        if rows_affected:
            return jsonify({"message": "User role updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update user role"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_permissions', methods=['POST'])
def update_permissions():
    data = request.get_json()

    user_id = data.get('user_id')
    device_management = data.get('device_management')
    stat_view = data.get('stat_view')

    if not all([user_id, device_management, stat_view]):
        return jsonify({"error": "user_id, device_management, and stat_view are required"}), 400

    try:
        permissions_management.allow_device_management(user_id, device_management)
        permissions_management.allow_statView(user_id, stat_view)

        return jsonify({"message": "User permissions updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to add a new device
@app.route('/add_device', methods=['POST'])
def add_device():
    data = request.get_json()

    device_name = data.get('device_name')
    device_type = data.get('device_type')
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    energy_consumption = data.get('energy_consumption')
    energy_generation = data.get('energy_generation')

    if not all([device_name, device_type, room_id, user_id, energy_consumption, energy_generation]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        params = (device_name, device_type, room_id, user_id, energy_consumption, energy_generation, 'inactive', 0)
        rows_affected = device_management.add_device(params)

        if rows_affected:
            return jsonify({"message": "Device added successfully"}), 201
        else:
            return jsonify({"error": "Failed to add device"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/remove_device', methods=['POST'])
def remove_device():
    data = request.get_json()

    device_ID = data.get('device_ID')

    if not device_ID:
        return jsonify({"error": "Device not found"}), 400

    try:
        rows_affected = device_management.remove_device(device_ID)

        if rows_affected:
            return jsonify({"message": "Device removed successfully"}), 201
        else:
            return jsonify({"error": "Failed to remove device"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/change_name', methods=['POST'])
def change_device_name():
    data = request.get_json()

    device_ID = data.get('device_ID')
    new_device_name = data.get('new_device_name')

    if not device_ID or not new_device_name:
        return jsonify({"error": "Device ID and new device name are required"}), 400

    try:
        rows_affected = device_management.change_name(device_ID, new_device_name)

        if rows_affected:
            return jsonify({"message": "Device name changed successfully"}), 200
        else:
            return jsonify({"error": "Failed to change device name"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to update the status of a device
@app.route('/update_device_status', methods=['POST'])
def update_device_status():
    data = request.get_json()
    device_id = data.get('device_id')

    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    try:
        query = "SELECT deviceStatus FROM Devices WHERE deviceID = %s"
        result = database_execute.execute_SQL(query, (device_id,))

        if not result:
            return jsonify({"error": "Device not found"}), 404

        current_status = result[0][0]
        new_status = "active" if current_status == "inactive" else "inactive"

        if new_status == "active":
            rows_affected = device_management.device_activate(device_id)
        else:
            rows_affected = device_management.device_deactivate(device_id)

        if rows_affected:
            return jsonify({"message": f"Device status updated to {new_status}"}), 200
        else:
            return jsonify({"error": "Failed to update device status"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_users', methods=['POST'])
def delete_users():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Incorrect username or password"}), 400
    try:
        user = database_execute.execute_SQL("""
            SELECT userID, password FROM Users WHERE username = %s
        """, (username,))

        if user:
            stored_hashed_password = user[0][1].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                rows_affected = user_management.remove_user(username)
                if rows_affected:
                    return jsonify({"message": "User deleted successfully"}), 200
                else:
                    return jsonify({"error": "User deleted successfully"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5000)