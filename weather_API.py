import requests

APIKey = "05f9f314f71d9d69f947eeffac9a4a1d"

def getWeatherData(cityName):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cityName}&appid={APIKey}"
    response = requests.get(url)
    return response.json()

def getTemperature(weatherData):
    # Convert temperature from Kelvin to Celsius and round it
    return round(weatherData['main']['temp'] - 273.15)

def getDescription(weatherData):
    return weatherData['weather'][0]['description']

def getHumidity(weatherData):
    return str(weatherData['main']['humidity'])

def getWind(weatherData):
    # Convert wind speed from m/s to mph
    return str(weatherData['wind']['speed'] * 2.236936)