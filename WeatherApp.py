import requests


api_key = input('Enter API_Key: ')
zip = input('Enter your Zip: ')
#city = input('Enter city name: ')

url = f'https://api.openweathermap.org/data/2.5/weather?zip={zip},us&appid={api_key}'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    temp_kelvin = data['main']['temp']
    temp_celsius = temp_kelvin - 273.15
    temp_fahrenheit = (temp_celsius * 9/5) + 32
    desc = data['weather'][0]['description']
    print(f'Temperature: {temp_fahrenheit:.2f} F')  # Display temperature rounded to 2 decimal places
    print(f'Description: {desc}')
else:
    print('Error fetching weather data')