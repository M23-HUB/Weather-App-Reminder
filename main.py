import os
import requests
import smtplib as sm

MY_LAT = 50.075539
MY_LNG = 14.437800
MY_EMAIL = os.environ.get("MY_EMAIL")
PASSWORD = os.environ.get("PASSWORD")
APPID = os.environ.get("APPIS")

param = {
  "lat": MY_LAT,
  "lon": MY_LNG,
  "cnt": 5, # Number of intervals returned
  "appid": APPID
}

response = requests.get(url="https://api.openweathermap.org/data/2.5/forecast", params=param)
response.raise_for_status()
data = response.json()

weather_conditions = {
    'thunder': {'active': False, 'label': '⛈️ Thunderstorm', 'count': 0},
    'drizzle': {'active': False, 'label': '🌧️ Drizzle', 'count': 0},
    'rain': {'active': False, 'label': '🌧️ Rain', 'count': 0},
    'mist': {'active': False, 'label': '🌫️ Mist', 'count': 0},
    'snow': {'active': False, 'label': '❄️ Snow', 'count': 0}
}

#  Check for rain

for hour_data in data["list"]:
    condition_code = hour_data["weather"][0]["id"]
    
    if 700 <= int(condition_code) < 790:
        weather_conditions['mist']['active'] = True
        weather_conditions['mist']['count'] += 1
    elif 600 <= int(condition_code) < 630:
        weather_conditions['snow']['active'] = True
        weather_conditions['snow']['count'] += 1
    elif 500 <= int(condition_code) < 540:
        weather_conditions['rain']['active'] = True
        weather_conditions['rain']['count'] += 1
    elif 300 <= int(condition_code) < 330:
        weather_conditions['drizzle']['active'] = True
        weather_conditions['drizzle']['count'] += 1
    elif 200 <= int(condition_code) < 240:
        weather_conditions['thunder']['active'] = True
        weather_conditions['thunder']['count'] += 1

# Collect active conditions with counts
active_conditions = []
for key, value in weather_conditions.items():
    if value['active']:
        active_conditions.append(f"{value['label']} (in {value['count']} forecast periods)")      

#  Send Email

if active_conditions:
  email_body = "Weather Alert for the next few hours:\n\n"
  email_body += "\n".join(f"• {condition}" for condition in active_conditions)
  
  with sm.SMTP("smtp.gmail.com") as connection:
      connection.starttls()
      connection.login(user= MY_EMAIL, password=PASSWORD)
      connection.sendmail(
        from_addr=MY_EMAIL,
        to_addrs=MY_EMAIL,
        msg=f"Subject: Weather Alert\n\n{email_body}"
      )
