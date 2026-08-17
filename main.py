import os
import requests
import smtplib as sm
from email.message import EmailMessage
from datetime import datetime

MY_LAT = 50.075539
MY_LNG = 14.437800
MY_EMAIL = os.environ.get("MY_EMAIL")
PASSWORD = os.environ.get("PASSWORD")
APPID = os.environ.get("APPID")

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
                <div class="weather-icon">🌧️</div>
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
            
            {''.join(f'<div class="alert-item">🌧️ <strong>{condition}</strong></div>' for condition in active_conditions)}
            
            <div style="background: #e7f3ff; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; color: #004085;">
                    <strong>💡 Tip:</strong> Consider carrying an umbrella and dressing appropriately for the weather conditions.
                </p>
            </div>
            
            <div class="footer">
                <p>Stay safe! ☔</p>
                <p>This is an automated weather alert from Weather App</p>
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
    plain_text += "\n".join(f"• {condition}" for condition in active_conditions)
    msg.set_content(plain_text)
    
    # HTML version
    
    msg.add_alternative(html_body, subtype='html')
    
    # Send the email
    
    with sm.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=PASSWORD)
        connection.send_message(msg)