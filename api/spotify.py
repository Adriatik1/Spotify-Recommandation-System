from __future__ import print_function
from flask import Flask, render_template, request, redirect,g,session, jsonify
import requests
import json
from urllib.parse import quote


#variablat me shkronja te medha jane perdorur per api url e keso gjerash (jane self descriptive)

#  Client Keys
CLIENT_ID = "24f7961ebf634777bb21227b44e49c73"
CLIENT_SECRET = "fb2d923b0369464a9c23a85943559e98"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "127.0.0.1"
PORT = 5000
REDIRECT_URI = "http://localhost:5000/authresponse/"
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "state=&scope": SCOPE,
    # "state": STATE,
    "show_dialog": "true"
}

#TRACKS ARRAY
tracksList=[]

def getHeader(): #gjeneron headerin me token pasi qe duhet per cdo request me u dergu edhe tokeni :)
    auth_header = {"Authorization": "Bearer {}".format(session['token'])}
    return auth_header

def getAuth(): #authenticohet (kjo metod thirret nga klasa app.py)
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return auth_url

def authresponse(auth_token): #response nga authorizimi (thirret nga klasa app.py)
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    return access_token

#endpoint per playlists(duhet me ja u gjeneru cdo playliste kenget(id perkatesisht))
GET_PLAYLISTS_ENDPOINT="{}/{}/{}".format(SPOTIFY_API_URL,'me','playlists')

def get_playlists(): #cdo playliste merr kjo metod dhe per cdo playlist thirr metodet get_several_tracks ku gjenerohen tgjitha kenget dhe futen ne listen tracksList
    url=GET_PLAYLISTS_ENDPOINT
    resp=requests.get(url,headers=getHeader())
    resp=resp.json()
    for item in resp['items']:
        print(item['id'])
        print("kenget")
        print(get_several_tracks(item['id']))
    return tracksList

#endpoint per tracks
GET_PLAYLIST_TRACKS_ENDPOINT = "{}/{}".format(SPOTIFY_API_URL, 'tracks')

def get_several_tracks(playlistID):
    url = "{}/{}/{}/{}".format(SPOTIFY_API_URL, 'playlists',playlistID,'tracks')
    resp = requests.get(url,headers=getHeader())
    resp = resp.json()
    item=0
    for item in resp['items']:
        print(item['track']['name'])
        tracksList.append({"id":item['track']['id'],"name":item['track']['name'],"artist":item['track']['artists'][0]['name']})
        #tracksList.append({'id':item['track']['id'],'artists':item['track']['artists']['name'],'name':item['track']['name']})
    return tracksList