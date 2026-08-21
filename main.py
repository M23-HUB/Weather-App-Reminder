import os
import requests
import smtplib as sm
from email.message import EmailMessage
from datetime import datetime

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
                weather_conditions['Rain']['label'] = '.../Weather-App-Reminder/images/13d.png'
            elif description in ['light intensity shower rain','shower rain','heavy intensity shower rain','ragged shower rain']:
                weather_conditions['Rain']['label'] = '.../Weather-App-Reminder/images/09d.png'            
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

def greetings():
    time_now = datetime.now()
    if time_now.hour < 12:
        return "Good Morning"
    elif 12 <= time_now.hour < 18:
        return "Good Afternoon"
    elif 18 <= time_now.hour:
        if time_now.hour > sunset_hour:
            weather_conditions['Clear']['label'] = '../Weather-App-Reminder/images/01n.png' 
            weather_conditions['Clouds']['few clouds']['label'] = '../Weather-App-Reminder/images/02n.png' 
        return "Good Evening"
     
def tips():
    """Return practical advice based on the currently active conditions."""
    active = {condition for condition, values in weather_conditions.items()
              if values.get('active')}

    if {'Rain', 'Drizzle', 'Thunderstorm'} & active:
        return "Consider carrying an umbrella and wearing waterproof clothing."
    if 'Snow' in active:
        return "Dress warmly and take care on slippery roads and sidewalks."
    if 'Clear' in active:
        return "Wear sunscreen and stay hydrated if you will be outside."
    if 'Atmosphere' in active:
        return "Visibility may be reduced, so travel carefully."
    return "Dress comfortably and check the forecast before heading out."

#---------API Request---------#

param_1 = {
  "lat": MY_LAT,
  "lon": MY_LNG,
  "cnt": 6, # Number of intervals returned
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

time_now = datetime.now()
sunset = data['results']['sunset']
sunset_hour = int(sunset.split("T")[1].split(':')[0])
temp = round(int(weather_now['main']['temp']),0)
feel_like = round(int(weather_now['main']['feels_like']),0)
min_temp = round(int(weather_now['main']['temp_min']),0)
max_temp = round(int(max([i['main']['temp'] for i in forecast['list']])), 0)

#------Weather Conditions-----#

weather_conditions = {
    'Clear':{'clear sky':{'active': False, 'label':('../Weather-App-Reminder/images/01d.png')}},
    'Clouds':{'few clouds': {'active': False, 'label':('../Weather-App-Reminder/images/02d.png')},
              'scattered clouds': {'active': False, 'label':('../Weather-App-Reminder/images/03d.png')}, 
              'broken clouds': {'active': False, 'label':('../Weather-App-Reminder/images/04d.png')}}, 
    'Drizzle':{'drizzle':{'active': False, 'label':('../Weather-App-Reminder/images/09d.png')}}, 
    'Rain':{'rain':{'active': False, 'label':('../Weather-App-Reminder/images/10d.png')}}, 
    'Thunderstorm':{'thunderstorm':{'active': False, 'label':('../Weather-App-Reminder/images/11d.png')}}, 
    'Snow':{'snow':{'active': False, 'label':('../Weather-App-Reminder/images/13d.png')}}, 
    'Atmosphere': {'atmosphere':{'active': False, 'label':('../Weather-App-Reminder/images/50d.png')}}, 
}

#------Active Weather Conditions-----#

for data in weather_now['weather']:
    main = data["main"].title()    
    description = data["description"].lower()    
    active_conditions(main, description)

active = []
for key, value in weather_conditions.items():
    for k, v in value.items():
        if v['active']:
            active.append(f"{v['label']}")      

#-----------Send Email-----------#

if active:
    
    alert_items = ''.join(f"<strong>The forecast is {description}.<br>Feels like {feel_like}<br>Minimun Temperature: {min_temp}<br>Maximun Temperature: {max_temp}</strong><br>")
    weather_icon = active[0]
                  
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
                <div class="weather-icon">f"<img src={weather_icon} alt='Weather icon'>"</div>
                <h1>f'{temp}'</h1>
                <h3>f'Feels like {feel_like}'</h3>
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
            </div>
            
            <div style="background: #e7f3ff; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; color: #004085;">
                    <strong>💡 Tip:</strong> f'{tips()}'
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
    msg['Subject'] = f"Weather Report: {greetings()} - {temp}"
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
