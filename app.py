from __future__ import print_function
from flask import Flask, render_template, request, redirect,g,session,jsonify
import requests
import json
from api import spotify #e kom kriju nji package me emrin api e ne ta eshte nji klase me emrin spotify e metodave te saj iu qasemi per me arr te dhena
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = "super secret key"
Bootstrap(app)

#route e tregon pathin e webit (psh www.emri.com/) - te drejton ten metoda index, www.webi.com/getauth te drejton tek metoda getAuth etj.

@app.route('/')
def index():
    return render_template('index.html')#render template kthen te dergon ne html(shfaq html)

@app.route('/getauth')
def getAuth():
    return redirect(spotify.getAuth()) #metoda redirect te ben redirect ne linkun qe ti e jep

@app.route('/authresponse/')
def authresponse(): #pas marrjes se autorizimit webi vazhdon ekzekutimin ne kete metod ke fut ne session token e gjeneruar
    auth_token = request.args['code']
    token = spotify.authresponse(auth_token)
    session['token'] = token
    return render_template('authresponse.html',token=session['token'])

@app.route('/authresponse/getTracks') #metod qe gjeneron kenget e userit duke thirrur ne metoden get_playlists() qe gjendet ne klasen spotify
def getTracks():
    return jsonify(spotify.get_playlists())


if __name__ == '__main__':
    app.run(debug=True)
