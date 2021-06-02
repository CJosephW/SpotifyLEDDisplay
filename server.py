from flask import Flask, render_template, redirect, request, session, make_response,session,redirect
import requests
import threading
from threading import Event
import urllib.request
import time
from urllib.parse import urlencode
import base64
import smtplib
import os
from dotenv import load_dotenv
from SpotifyDisplayLED import SpotifyDisplayLED

load_dotenv()
oauthEvent = Event()

CLIENTID = os.environ.get("CLIENTID")
CLIENTSECRET = os.environ.get("CLIENTSECRET")
SPOTIFY_GET_TRACK_URL = 'https://api.spotify.com/v1/me/player/currently-playing'
REDIRECT_URI = os.environ.get("REDIRECT_URI")
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_EMAIL_PASS = os.environ.get("SMTP_EMAIL_PASS")
MOBILE_SMS_GATEWAY = os.environ.get("MOBILE_SMS_GATEWAY")
provider_url = "https://accounts.spotify.com/authorize"

params = urlencode({
    'client_id': CLIENTID,
    'scope':'user-read-currently-playing', 
    'redirect_uri': REDIRECT_URI,
    'response_type': 'code'
})

url = provider_url + '?' + params

app = Flask(__name__)

print(CLIENTID)

basicAuthString = CLIENTID + ":" + CLIENTSECRET
base64AuthBytes = base64.b64encode(bytes(basicAuthString, 'utf-8'))
base64Auth = base64AuthBytes.decode("utf-8")                                                            

@app.route("/spotify/callback")
def spotify_callback():
    code = request.args.get('code')
    response = requests.post('https://accounts.spotify.com/api/token',
        headers={
            "Authorization": f"Basic {base64Auth}"
        },
        data={
        'redirect_uri': 'http://192.168.50.199:5000/spotify/callback',
        'grant_type':'authorization_code', 
        'code': code
        }
        )
    json = response.json()
    auth_code = json["access_token"]
    global oAuth
    oAuth = auth_code
    oauthEvent.set()
    return "HELLO"

def get_playback():
    time.sleep(2)
    Display = SpotifyDisplayLED()
    while True: 
        if oauthEvent.is_set():
            response = requests.get(

            SPOTIFY_GET_TRACK_URL,
                headers={
                    "Authorization": f"Bearer {oAuth}"
                }
            )
            
            try:
                resp_json = response.json()
            
                print(resp_json)
                track_id = resp_json['item']['id']
                track_name = resp_json['item']['name']
                track_progress = resp_json['progress_ms']
                track_duration = resp_json['item']['duration_ms']
                track_image = resp_json['item']['album']['images'][2]['url']
                current_track_info = {
                    'id': track_id,
                    "name" : track_name,

                }
                progress = (track_progress/track_duration) 
            
                print(resp_json)
                print(track_name)
                Display.startDisplay(track_image, progress, track_name)
            except ValueError:
                Display.startDisplay()
                print("looks like you're not playing anything at the moment")
                time.sleep(5)
            
    return

def start_email_server():
    #your sms gateway email
    sms_email = MOBILE_SMS_GATEWAY
    #your smtp email
    smtp = "smtp.gmail.com"
    port = 587 

    server = smtplib.SMTP(smtp, port)
    server.starttls()

    server.login(SMTP_EMAIL,SMTP_EMAIL_PASS)

    server.sendmail(SMTP_EMAIL, sms_email, '\n'+url)

    server.quit()
        
playback = threading.Thread(target = get_playback)
sms_email = threading.Thread(target = start_email_server)

try:
    playback.start()
    sms_email.start()
except:
    print("oop")
app.run(host="0.0.0.0")

