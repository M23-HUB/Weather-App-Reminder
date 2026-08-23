import os
import requests
import smtplib as sm
from email.message import EmailMessage
from datetime import datetime
import pytz

#----------CONSTANTS----------#

MY_LAT = 50.075539
MY_LNG = 14.437800
MY_EMAIL = os.environ.get("MY_EMAIL")
PASSWORD = os.environ.get("PASSWORD")
APPID = os.environ.get("APPID")

#---------Functions---------#

def active_conditions(main, description):
    
    if main in weather_conditions:
        if main == 'Clouds':
            if description == 'few clouds':
                weather_conditions['Clouds']['few clouds']['active'] = True                
            elif description == 'scattered clouds':
                weather_conditions['Clouds']['scattered clouds']['active'] = True
            elif description == 'broken clouds':
                weather_conditions['Clouds']['broken clouds']['active'] = True
        elif main == 'Rain':
            weather_conditions['Rain']['active'] = True
            if description == "freezing rain":
                weather_conditions['Rain']['label'] = '.13d'
            elif description in ['light intensity shower rain','shower rain','heavy intensity shower rain','ragged shower rain']:
                weather_conditions['Rain']['label'] = '.09d'            
        elif main == "Clear":
            weather_conditions['Clear']['active'] = True
        elif main == 'Drizzle':
            weather_conditions['Drizzle']['active'] = True
        elif main == 'Thunderstorm':
            weather_conditions['Thunderstorm']['active'] = True
        elif main == 'Snow':
            weather_conditions['Snow']['active'] = True
        else:
            weather_conditions['Atmosphere']['active'] = True

def expected_change():
    current_weather = weather_now['weather'][0]['description'].lower()
    
    changes = {}
    
    for interval in forecast['list']:
        forecast_time = interval['dt_txt']
        forecast_weather = interval['weather'][0]['description'].lower()
        forecast_temp = round(interval['main']['temp'])
        
        # Check if weather is different from current
        if forecast_weather != current_weather:            
            time_str = forecast_time[:8].split("T")[1].split(":")[0]
            hour = int(time_str)
            
            if hour == 0:
                formatted_time = "Midnight"
            elif hour < 12:
                formatted_time = f"{hour}:00 AM"
            elif hour == 12:
                formatted_time = "12:00 PM"
            else:
                formatted_time = f"{hour-12}:00 PM"
                        
            if forecast_weather not in changes:
                changes[forecast_weather] = {
                    'time': formatted_time,
                    'temperature': forecast_temp,
                    'hour': hour
                }
    
    return changes, current_weather

def greetings():
    cest = pytz.timezone('Europe/Berlin')
    time_now = datetime.now(cest)
    if time_now.hour < 12:
        return "Good Morning"
    elif 12 <= time_now.hour < 18:
        return "Good Afternoon"
    elif 18 <= time_now.hour:
        if time_now.hour > sunset_hour:
            weather_conditions['Clear']['clear sky']['label'] = '01n' 
            weather_conditions['Clouds']['few clouds']['label'] = '02n' 
        return "Good Evening"
     
def tips():
    """Return practical advice based on the currently active conditions."""
    active = {condition for condition, values in weather_conditions.items()
              if values.get('active')}
    
    tip_list = []

    if {'Rain', 'Drizzle', 'Thunderstorm'} & active:
        tip_list.append("Consider carrying an umbrella and wearing waterproof clothing.")
    if 'Snow' in active:
        tip_list.append("Dress warmly and take care on slippery roads and sidewalks.")
    if 'Clear' in active:
        tip_list.append("Wear sunscreen and stay hydrated if you will be outside.")
    if 'Atmosphere' in active:
        tip_list.append("Visibility may be reduced, so travel carefully.")
    if not tip_list:
        tip_list.append("Dress comfortably and don't forget to check the forecast before heading out.")
    return tip_list

#---------API Request---------#

param_1 = {
  "lat": MY_LAT,
  "lon": MY_LNG,
  "cnt": 9, # Number of intervals returned
  "appid": APPID,
  "units": "metric"
}

param_2 = {
 'lat': MY_LAT,
 'lng': MY_LNG,
 'formatted': 0
}

# 3 hour Report

response = requests.get(url="https://api.openweathermap.org/data/2.5/forecast", params=param_1)
response.raise_for_status()
forecast = response.json()

# Current weather repost

response = requests.get(url="https://api.openweathermap.org/data/2.5/weather", params=param_1)
response.raise_for_status()
weather_now = response.json()

#  Sunrise - Sunset hours

response = requests.get(url="http://api.sunrise-sunset.org/json", params= param_2)
response.raise_for_status()
data = response.json()

#------Veriables-----#

cest = pytz.timezone('Europe/Berlin')
time_now = datetime.now(cest)
sunset = data['results']['sunset']
sunset_hour = int(sunset.split("T")[1].split(':')[0])
temp = round(int(weather_now['main']['temp']),0)
feel_like = round(int(weather_now['main']['feels_like']),0)
min_temp = round(int(min([i['main']['temp_min'] for i in forecast['list']])), 0)
max_temp = round(int(max([i['main']['temp_max'] for i in forecast['list']])), 0)

#------Weather Conditions-----#

weather_conditions = {
    'Clear':{'clear sky':{'active': False, 'icon':'01d'}},
    'Clouds':{'few clouds': {'active': False, 'icon':'02d'},
              'scattered clouds': {'active': False, 'icon':'03d'}, 
              'broken clouds': {'active': False, 'icon':'04d'}}, 
    'Drizzle':{'drizzle':{'active': False, 'icon':'09d'}}, 
    'Rain':{'rain':{'active': False, 'icon':'10d'}}, 
    'Thunderstorm':{'thunderstorm':{'active': False, 'icon':'11d'}}, 
    'Snow':{'snow':{'active': False, 'icon':'13d'}}, 
    'Atmosphere': {'atmosphere':{'active': False, 'icon':'50d'}}, 
}

#------Active Weather Conditions-----#

for data in weather_now['weather']:
    main = data["main"].title()    
    description = data["description"].lower()    
    active_conditions(main, description)

active_conditions_list = []
for key, value in weather_conditions.items():
    for k, v in value.items():
        if v.get('active', False):
            active_conditions_list.append({
                'description': k,
                'icon': v.get('icon', '01d')
            })
            print(f"Active: {k} - {v['icon']}")

# Build alert items

alert_items = ''
if active_conditions_list:
    for condition in active_conditions_list:
        alert_items += f'''
        <div class="alert-item">
            <strong>The forecast is {condition['description'].title()}.</strong><br>
            Feels like {feel_like}°C<br>
            Minimum Temperature: {min_temp}°C<br>
            Maximum Temperature: {max_temp}°C<br>
            {expected_change}
        </div>
        '''
else:
    alert_items = '<div class="alert-item">No active weather alerts</div>'
                
# Get the first active condition for the main icon

weather_icon = active_conditions_list[0]['icon'] if active_conditions_list else '01d'
icon_url = f"https://openweathermap.org/img/wn/{weather_icon}@2x.png" if weather_icon else "https://openweathermap.org/img/wn/01d@2x.png"

# Get weather change information

changes, current_weather = expected_change()

change_message = ""

if changes:
    
    first_change_weather = list(changes.keys())[0]
    first_change_data = changes[first_change_weather]
    
    change_message = f"""
    <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px 15px; margin: 10px 0; border-radius: 4px;">
        <strong>Weather Change Alert.</strong><br>
        Expect <strong>{first_change_weather}</strong> at approximately <strong>{first_change_data['time']}</strong>.<br>
        Temperature will be around <strong>{first_change_data['temperature']}°C</strong>.
    </div>
    """
    
    if len(changes) > 1:
        change_message += """
        <div style="font-size: 12px; color: #666; margin-top: 5px;">
            <em>Multiple weather changes expected throughout the day.</em>
        </div>
        """
else:
    change_message = f"""
    <div style="background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 10px 15px; margin: 10px 0; border-radius: 4px;">
        <strong>Weather Outlook.</strong><br>
        Stable weather conditions expected throughout the day.
    </div>
    """

tip_list = tips()
tip_text = '<br>• '.join(tip_list)  # Format as bullet points
if tip_text:
    tip_text = '• ' + tip_text

#-----------Send Email-----------#

if active_conditions_list:
                      
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px 10px 0 0;
                margin: -30px -30px 20px -30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .weather-icon {{
                font-size: 48px;
            }}
            .alert-item {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 12px 16px;
                margin: 10px 0;
                border-radius: 4px;
                font-size: 16px;
            }}
            .alert-item strong {{
                color: #856404;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                text-align: center;
                color: #666;
                font-size: 12px;
            }}
            .badge {{
                display: inline-block;
                background: #dc3545;
                color: white;
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="weather-icon">
                    <img src="{icon_url}" alt='Weather icon'>
                </div>
                <h1>{temp}°C</h1>
                <h3>Feels like {feel_like}°C</h3>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">
                    Here is your Weather report for the next few hours
                </p>
            </div>
            
            <div style="margin: 20px 0;">
                <p style="font-size: 14px; color: #666;">
                    <strong>📅 Date:</strong> {time_now.strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
            
            <h3 style="color: #333;">⚠️ Active Weather Alerts</h3>
            
            <div class="alert-item">
                {alert_items}
                {change_message}
            </div>            

            <div style="background: #e7f3ff; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; color: #004085;">
                    <strong>💡 Tips:</strong><br>{tip_text}
                </p>
            </div>
            
            <div class="footer">
                <p>Stay safe!</p>
                <p>This is an automated weather alert from My Weather Reminder App</p>
            </div>
        </div>
    </body>
    </html>
    """ 
    
    msg = EmailMessage()
    msg['Subject'] = f"{greetings()}. Weather Report For Today: {min_temp}° - {max_temp}°"
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL
    
    # Plain text version (for email clients that don't support HTML)
    
    plain_text = "Weather Report for the next few hours:\n\n"
    plain_text += alert_items
    msg.set_content(plain_text)
    
    # HTML version
    
    msg.add_alternative(html_body, subtype='html')
    
    # Send the email
    
    with sm.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=PASSWORD)
        connection.send_message(msg)
