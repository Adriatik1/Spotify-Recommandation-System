from __future__ import print_function
from flask import Flask, render_template, request, redirect,g,session,jsonify
import requests
import json
from api import spotify #e kom kriju nji package me emrin api e ne ta eshte nji klase me emrin spotify e metodave te saj iu qasemi per me arr te dhena
from flask_bootstrap import Bootstrap
import pandas as pd

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
    #return jsonify(spotify.get_playlists())
    #songs = json.dumps(spotify.get_playlists())
    # marrim kenget si json
    songs = json.loads(json.dumps(spotify.get_playlists()))
    listaStr = ''
    for val in songs:
        listaStr += "ID: " + val['id'] + "<br/>"
    return render_template('yoursongs.html', value=listaStr)

@app.route('/authresponse/getSuggestions')
def getSuggestions():
    toSuggestStr = ''
    songs = json.loads(json.dumps(spotify.get_playlists()))
    songmax2 = pd.read_csv('association_track_rules_max_2.csv', sep=',')
    songmax3 = pd.read_csv('association_track_rules_custom_max_3.csv', sep=',')
    artistmax2 = pd.read_csv('association_artist_rules_custom_max_2.csv',sep=',')
    artistmax3 = pd.read_csv('association_artist_rules_custom_max_3.csv', sep=',')


    # i shtojme te gjitha id-te e kengeve te user ne nje liste
    userSongs = []
    userArtists = []
    for val in songs:
        userSongs.append(val['id'])
        userArtists.append(val['artistid'])

    userSongs = list(set(userSongs))
    userArtists = list(set(userArtists))

    songsToSuggest = []
    # per cdo ID te kengeve te shfrytezuesit shikojme se a ekziston ne csv fajll
    for val in userSongs:
        # per rregullat me 2 kenge -----------------------------------------------
        # nese jo, kalojme tutje te kenga tjeter
        if(len(songmax2[songmax2['trackID1'].astype(str).str.contains(val)]) == 0):
            continue
        # nese po, marrim te gjitha rregullat me ate ID dhe i shtojme ne songsToSuggest
        else:
            songmax2_temp = songmax2[songmax2['trackID1'].astype(str).str.contains(val)]
            for index, row in songmax2_temp.iterrows():
                if str(row['trackID2']) not in userSongs:
                    songsToSuggest.append(row['trackID2'])

        # per rregullat me 3 kenge -----------------------------------------------
        if(len(songmax3[songmax3['trackID1'].astype(str).str.contains(val)]) == 0):
            continue
        else:
            songmax3_temp = songmax3[songmax3['trackID1'].astype(str).str.contains(val)]
            for index, row in songmax3_temp.iterrows():
                if(str(row['trackID2'])) in userSongs:
                    if str(row['trackID3']) not in userSongs:
                        songsToSuggest.append(row['trackID3'])

    artistsToSuggest = []
    # per cdo ID te artisteve te shfrytezuesit shikojme se a ekziston ne csv fajll
    for val in userArtists:
        # per rregullat me 2 artiste -----------------------------------------------
        # nese jo, kalojme tutje te kenga tjeter
        if (len(artistmax2[artistmax2['artistID1'].astype(str).str.contains(val)]) == 0):
            continue
        # nese po, marrim te gjitha rregullat me ate ID dhe i shtojme ne songsToSuggest
        else:
            artistmax2_temp = artistmax2[artistmax2['artistID1'].astype(str).str.contains(val)]
            for index, row in artistmax2_temp.iterrows():
                if str(row['artistID2']) not in userArtists:
                    artistsToSuggest.append(row['artistID2'])

        # per rregullat me 3 kenge -----------------------------------------------
        if (len(artistmax3[artistmax3['artistID1'].astype(str).str.contains(val)]) == 0):
            continue
        else:
            artistmax3_temp = artistmax3[artistmax3['artistID1'].astype(str).str.contains(val)]
            for index, row in artistmax3_temp.iterrows():
                if (str(row['artistID2'])) in userArtists:
                    if str(row['artistID3']) not in userArtists:
                        artistsToSuggest.append(row['artistID3'])

    # permes set-it i zhdukim duplikatet dhe pastaj e kthejme ne liste
    songsToSuggest = list(set(songsToSuggest))
    artistsToSuggest = list(set(artistsToSuggest))

    allTracksdf = pd.read_csv('SpotifyAudioArtistsOK3.csv',sep=',')

    toSuggestStr += "<h1> Kenge </h1> <br />"
    for x in songsToSuggest:
        toSuggestStr += "ID: " + x + "<br />Emri: "
        allTracksdf_temp = allTracksdf[allTracksdf['trackID'] == x]
        for index, row in allTracksdf_temp.iterrows():
            toSuggestStr += str(row['track_name']) + "<br />====================================<br />"
    toSuggestStr += "Numri i kengeve te sugjeruara: " + str(len(songsToSuggest)) + "<br /><br />"

    toSuggestStr += "<h1> Artiste </h1> <br />"
    for x in artistsToSuggest:
        toSuggestStr += "ID: " + x + "<br />Emri: "
        allTracksdf_temp = allTracksdf[allTracksdf['artistID'] == x]
        for index, row in allTracksdf_temp.iterrows():
            toSuggestStr += str(row['artist_name']) + "<br />====================================<br />"
            break
    toSuggestStr += "Numri i artisteve te sugjeruar: " + str(len(artistsToSuggest)) + "<br /><br />"

    return render_template('suggestions.html', value=toSuggestStr)


if __name__ == '__main__':
    app.run(debug=True)
