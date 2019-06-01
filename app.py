from __future__ import print_function
from flask import Flask, render_template, request, redirect,g,session,jsonify
import requests
import json
from api import spotify #e kom kriju nji package me emrin api e ne ta eshte nji klase me emrin spotify e metodave te saj iu qasemi per me arr te dhena
from flask_bootstrap import Bootstrap
import pandas as pd
import random

app = Flask(__name__)
app.secret_key = "super secret key"
Bootstrap(app)
songmax2 = pd.read_csv('association_track_rules_max_2.csv', sep=',')
songmax3 = pd.read_csv('association_track_rules_custom_max_3.csv', sep=',')
artistmax2 = pd.read_csv('association_artist_rules_custom_max_2.csv', sep=',')
artistmax3 = pd.read_csv('association_artist_rules_custom_max_3.csv', sep=',')
allTracksdf = pd.read_csv('SpotifyAudioArtistsOK3.csv',sep=',')
songs = ''
allListsong=[]
allListartist=[]

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
    global songs
    songs = json.loads(json.dumps(spotify.get_playlists()))
    listaStr = ''
    for val in songs:
        listaStr += "<tr class='text-white'><td> " + val['id']+"</td><td class='font-weight-bold'>"+val['name']+"</td><td>"+val['artist']+"</td></tr>"
    return render_template('yoursongs.html', value=listaStr)


@app.route('/authresponse/getSuggestions')
def getSuggestions():
    global songs
    songs = json.loads(json.dumps(spotify.get_playlists()))
    listaStr = ''
    for val in songs:
        listaStr += "ID: " + val['id'] + "<br/>"
    return render_template('suggestions.html')

@app.route('/testajax')
def testajax():
    return jsonify(
        emri="Adriatik",
        mbiemri="Ademi"
    )

@app.route('/getPlaylistsCombo')
def getPlaylistsCmb():
    data=spotify.get_playlists_combo();
    return jsonify(data)

@app.route('/addto_playlist')
def addto_playlist():
    playlistId = request.args.get('playlistId')
    songId = request.args.get('songId')
    spotify.add_track(playlistId,songId)
    return jsonify(success="Kenga u shtua me suksese!")

@app.route('/authresponse/getSuggestionsRequest')
def getSuggestionsRequest():
    toSuggestStr = ''
    #songs = json.loads(json.dumps(spotify.get_playlists()))

    # i shtojme te gjitha id-te e kengeve te user ne nje liste dhe id te artisteve te user ne
    # nje liste tjeter
    userSongs = []

    for val in songs:
        userSongs.append(val['id'])

    # permes set-it i zhdukim duplikatet dhe pastaj e kthejme ne liste
    userSongs = list(set(userSongs))

    # bejme shuffle
    random.shuffle(userSongs)

    songsToSuggest = []
    # per cdo ID te kengeve te shfrytezuesit shikojme se a ekziston ne csv fajll
    for val in userSongs:
        if len(songsToSuggest) > 7:
            break
        # per rregullat me 2 kenge -----------------------------------------------
        # nese jo, kalojme tutje te kenga tjeter
        if(len(songmax2[songmax2['trackID1'].astype(str).str.contains(val)]) == 0):
            continue
        # nese po, marrim te gjitha rregullat me ate ID dhe i shtojme ne songsToSuggest
        else:
            songmax2_temp = songmax2[songmax2['trackID1'].astype(str).str.contains(val)]
            for index, row in songmax2_temp.iterrows():
                # kontrollojme mos kete kenge vecse e pelqen ky shfrytezues
                if str(row['trackID2']) not in userSongs:
                    songsToSuggest.append(row['trackID2'])

        # per rregullat me 3 kenge -----------------------------------------------
        if(len(songmax3[songmax3['trackID1'].astype(str).str.contains(val)]) == 0):
            continue
        # nese ekziston kjo kenge ne nje rregull
        else:
            songmax3_temp = songmax3[songmax3['trackID1'].astype(str).str.contains(val)]
            for index, row in songmax3_temp.iterrows():
                # shikojme kenga e dyte ne rregull, a ekziston ne playlistat e userit, nese po
                # atehere plotesohet kushti kenga1 && kenga2 -> kenga3
                if(str(row['trackID2'])) in userSongs:
                    # kontrollojme nese kenga3 vec eshte ne playlistat e userit
                    if str(row['trackID3']) not in userSongs:
                        songsToSuggest.append(row['trackID3'])


    # zhdukim duplikatet
    songsToSuggest = list(set(songsToSuggest))
    songsToSuggestNames = []


    random.shuffle(songsToSuggest)

    #toSuggestStr += "<h1> Kenge </h1> <br />"
    for x in songsToSuggest:
        #toSuggestStr += "ID: " + x + "<br />Emri: "
        allTracksdf_temp = allTracksdf[allTracksdf['trackID'] == x]
        for index, row in allTracksdf_temp.iterrows():
            #toSuggestStr += str(row['track_name']) + "<br />====================================<br />"
            songsToSuggestNames.append(str(row['track_name']))

    #toSuggestStr += "Numri i kengeve te sugjeruara: " + str(len(songsToSuggest)) + "<br /><br />"

    global allListsong
    songsToSuggest = songsToSuggest[:7]
    songsToSuggestNames = songsToSuggestNames[:7]

    i=0

    songImages = spotify.get_several_tracks_req(songsToSuggest)

    for i in range(0,6):
        allListsong.append({'id':songsToSuggest[i],'name':songsToSuggestNames[i],'img':songImages[i]})

    #allLists.append({'id':songsToSuggest})
    #allLists.append({'name':songsToSuggestNames})
    #allLists.append({'img':songImages})
    #allLists.append(artistsToSuggest)
    #allLists.append(artistsToSuggestNames)
    #allLists.append(artistImages)
    #print(allLists)
    #return jsonify({'data': render_template('AJAXresponse.html', myList=allLists)})
    return jsonify(allListsong)

@app.route('/authresponse/getSuggestionsRequestArtist')
def getSuggestionsRequestArtist():
    toSuggestStr = ''
    #songs = json.loads(json.dumps(spotify.get_playlists()))

    # nje liste tjeter
    userArtists = []
    for val in songs:
        userArtists.append(val['artistid'])

    # permes set-it i zhdukim duplikatet dhe pastaj e kthejme ne liste
    userArtists = list(set(userArtists))

    # bejme shuffle
    random.shuffle(userArtists)

    artistsToSuggest = []
    # per cdo ID te artisteve te shfrytezuesit shikojme se a ekziston ne csv fajll
    for val in userArtists:
        if len(artistsToSuggest) > 7:
            break
        # ngjashem si te kenget
        if (len(artistmax2[artistmax2['artistID1'].astype(str).str.contains(val)]) == 0):
            continue
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
    # zhdukim duplikatet
    artistsToSuggest = list(set(artistsToSuggest))
    artistsToSuggestNames = []

    random.shuffle(artistsToSuggest)

    #toSuggestStr += "<h1> Artiste </h1> <br />"
    for x in artistsToSuggest:
        #toSuggestStr += "ID: " + x + "<br />Emri: "
        allTracksdf_temp = allTracksdf[allTracksdf['artistID'] == x]
        for index, row in allTracksdf_temp.iterrows():
            #toSuggestStr += str(row['artist_name']) + "<br />====================================<br />"
            artistsToSuggestNames.append(str(row['artist_name']))
            break
    toSuggestStr += "Numri i artisteve te sugjeruar: " + str(len(artistsToSuggest)) + "<br /><br />"

    global allListartist

    artistsToSuggest = artistsToSuggest[:7]
    artistsToSuggestNames = artistsToSuggestNames[:7]
    i=0

    artistImages = spotify.get_several_artists(artistsToSuggest)

    for i in range(0, 6):
         allListartist.append({'id': artistsToSuggest[i], 'name': artistsToSuggestNames[i], 'img': artistImages[i]})

    return jsonify(allListartist)

if __name__ == '__main__':
    port = int(5000)
    app.run(debug=True)
