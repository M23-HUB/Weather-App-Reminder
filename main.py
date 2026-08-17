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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            margin: 0;
            padding: 20px;
        }}
        .card {{
            max-width: 550px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            overflow: hidden;
        }}
        .card-header {{
            background: #1a1a2e;
            padding: 30px 30px 20px 30px;
            color: white;
        }}
        .card-header h1 {{
            margin: 0;
            font-size: 22px;
            font-weight: 600;
        }}
        .card-body {{
            padding: 30px;
        }}
        .alert {{
            background: #fff5f5;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 14px 18px;
            margin: 8px 0;
            color: #721c24;
        }}
        .alert::before {{
            content: "⚠️ ";
        }}
        .stat {{
            display: inline-block;
            background: #e9ecef;
            padding: 2px 12px;
            border-radius: 20px;
            font-size: 13px;
            color: #495057;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 15px 30px;
            text-align: center;
            color: #6c757d;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="card-header">
            <h1>🌧️ Weather Alert</h1>
            <p style="opacity: 0.8; margin: 5px 0 0 0; font-size: 14px;">
                Next few hours forecast
            </p>
        </div>
        <div class="card-body">
            <div style="text-align: center; padding: 10px 0;">
                <span class="stat">⚠️ {len(active_conditions)} alerts active</span>
            </div>
            
            {''.join(f'<div class="alert">{condition}</div>' for condition in active_conditions)}
            
            <hr style="border: none; border-top: 1px solid #e9ecef; margin: 25px 0;">
            
            <div style="font-size: 14px; color: #495057; line-height: 1.6;">
                <p><strong>📍 Location:</strong> Prague, Czech Republic</p>
                <p><strong>🕐 Time:</strong> {datetime.now().strftime('%H:%M')}</p>
            </div>
        </div>
        <div class="footer">
            Automated weather notification
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