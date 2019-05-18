from __future__ import print_function
from flask import Flask, render_template, request, redirect,g,session,jsonify
import requests
import json
from api import spotify
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = "super secret key"
Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getauth')
def getAuth():
    return redirect(spotify.getAuth())

@app.route('/authresponse/')
def authresponse():
    auth_token = request.args['code']
    token = spotify.authresponse(auth_token)
    session['token'] = token
    return render_template('authresponse.html',token=session['token'])

@app.route('/authresponse/getTracks')
def getTracks():
    return jsonify(spotify.get_playlists())


if __name__ == '__main__':
    app.run(debug=True)
