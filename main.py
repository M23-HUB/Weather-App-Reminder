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

#---------API Request---------#

param = {
  "lat": MY_LAT,
  "lon": MY_LNG,
  "cnt": 5, # Number of intervals returned
  "appid": APPID
}

response = requests.get(url="https://api.openweathermap.org/data/2.5/forecast", params=param)
response.raise_for_status()
data = response.json()
print(data["list"])

#------Weather Conditions-----#

weather_conditions = {
    'sunny': {'active': False, 'label': '☀️ Sunny', 'count': 0},
    'partly cloudy': {'active': False, 'label': '⛅ Partly Cloudy', 'count': 0},
    'cloudy': {'active': False, 'label': '☁️ Cloudy', 'count': 0},
    'overcast': {'active': False, 'label': '☁️ Snow', 'count': 0},
    'rain': {'active': False, 'label': '🌧️ Rain', 'count': 0},
    'drizzle': {'active': False, 'label': '🌧️ Drizzle', 'count': 0},
    'snow': {'active': False, 'label': '❄️ Snow', 'count': 0},
    'sleet': {'active': False, 'label': '🌨️ Sleet', 'count': 0},
    'hail': {'active': False, 'label': '🌨 Hail', 'count': 0},
    'mist': {'active': False, 'label': '🌫️ Mist', 'count': 0},
    'thunderstorm': {'active': False, 'label': '⛈️ Thunderstorm', 'count': 0},
    'turnado': {'active': False, 'label': '🌪️ Thunderstorm', 'count': 0},
    'blizzard': {'active': False, 'label': '🌨️ Blizzard', 'count': 0},
    'harricane': {'active': False, 'label': '🌀 Hurricane', 'count': 0},
    'windy': {'active': False, 'label': '༄ Thunderstorm', 'count': 0},
    'fog': {'active': False, 'label': '🌫️ Thunderstorm', 'count': 0},
    'humid': {'active': False, 'label': '♒︎ Thunderstorm', 'count': 0} 
}

#  Check for rain

# for hour_data in data["list"]:
#     condition_code = hour_data["weather"][0]["id"]
    
#     if 700 <= int(condition_code) < 790:
#         weather_conditions['mist']['active'] = True
#         weather_conditions['mist']['count'] += 1
#     elif 600 <= int(condition_code) < 630:
#         weather_conditions['snow']['active'] = True
#         weather_conditions['snow']['count'] += 1
#     elif 500 <= int(condition_code) < 540:
#         weather_conditions['rain']['active'] = True
#         weather_conditions['rain']['count'] += 1
#     elif 300 <= int(condition_code) < 330:
#         weather_conditions['drizzle']['active'] = True
#         weather_conditions['drizzle']['count'] += 1
#     elif 200 <= int(condition_code) < 240:
#         weather_conditions['thunder']['active'] = True
#         weather_conditions['thunder']['count'] += 1

#------Active Weather Conditions-----#

time_report = []
for data in data["list"]:
    weather_now = data["weather"][0]["main"].low()    
    if weather_now in weather_conditions:
        weather_conditions[weather_now]['active'] = True
        weather_conditions[weather_now]['count'] += 1
        time = data['list']['dt_txt'].split("")[1][:-3]
        time_report.append(time)

active_conditions = []
for key, value in weather_conditions.items():
    if value['active']:
        active_conditions.append(f"{value['label']} (in {value['count']} forecast periods)")      

#-------------Tips-------------#

def tips():
    # Consider carrying an umbrella and dressing appropriately for the weather conditions
    pass

#------Send Email-----#

if active_conditions:
    
    alert_items = ''.join(f"<strong>{condition}</strong> at {time}<br>" for condition, time in zip(active_conditions, time_report))
    # weather_icon = [i for i in active_conditions["label"].split("")[0]]
                  
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
                <div class="weather-icon"></div>
                <h1>⚠️ Weather Alert</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">
                    Weather conditions for the next few hours
                </p>
            </div>
            
            <div style="margin: 20px 0;">
                <p style="font-size: 14px; color: #666;">
                    <strong>📅 Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
            
            <h3 style="color: #333;">⚠️ Active Weather Alerts</h3>
            
            <div class="alert-item">
                {alert_items}
            </div>
            
            <div style="background: #e7f3ff; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; color: #004085;">
                    <strong>💡 Tip:</strong> {tips()}
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
    msg['Subject'] = "Weather Alert - Action Required"
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL
    
    # Plain text version (for email clients that don't support HTML)
    
    plain_text = "Weather Alert for the next few hours:\n\n"
    plain_text += alert_items
    msg.set_content(plain_text)
    
    # HTML version
    
    msg.add_alternative(html_body, subtype='html')
    
    # Send the email
    
    with sm.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=PASSWORD)
        connection.send_message(msg)