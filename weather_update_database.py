import datetime
import weather_API
import database_execute

def update_weather(houseId):
    # Fetch the city for the given houseID
    city_result = database_execute.execute_SQL("SELECT city FROM House WHERE houseID = %s", (houseId,))
    if not city_result:
        return f"Error: No city found for houseID {houseId}"

    city = city_result[0][0]

    # Fetch the weather data for the city
    weather = weather_API.getWeatherData(city)
    if not weather:
        return "Error: Failed to fetch weather data."

    # Prepare the data for insertion
    data = (
        weather_API.getTemperature(weather),
        weather_API.getHumidity(weather),
        weather_API.getWind(weather),
        weather_API.getDescription(weather),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        houseId
    )

    # Insert the weather data into the database
    return database_execute.execute_SQL(
        "INSERT INTO Weather (temperature, humidity, windSpeed, weatherType, timestamp, houseID) VALUES (%s, %s, %s, %s, %s, %s)",
        data
    )