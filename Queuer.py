import argparse
import requests
import json
import Song as s
import numpy as np
from glob import glob
from pydub import AudioSegment


parser = argparse.ArgumentParser(description='Mix your playlist!')

parser.add_argument('--searchterm', help='The term we will search YouTube for a playlist of!')
parser.add_argument('--url', help='The direct link to the Youtube Playlist!')
parser.add_argument('--playlistId', help='The encoded string of letters/numbers that define a Youtube entry!')
args = parser.parse_args()

playlistID = ""
if(args.searchterm):
    parameters = {"part":"snippet","q":args.searchterm, "type":"playlist","key":"AIzaSyAe6wO_cOPMMnhWa2_lvspJhUhDGixkrJU", "maxResults":"3"}
    response = requests.get("https://www.googleapis.com/youtube/v3/search",params=parameters)
    playlistID = response.json()["items"][0]["id"]["playlistId"]
elif(args.url):
    print("ok")
elif(args.playlistId):
    playlistId = args.playlistId

parameters={"part":"snippet","playlistId":playlistID, "key":"AIzaSyAe6wO_cOPMMnhWa2_lvspJhUhDGixkrJU", "maxResults":"10"}
response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems",params=parameters)
playlistItems = response.json()["items"]
videoIDs = []
for item in playlistItems:
    videoIDs.append(item["snippet"]["resourceId"]["videoId"])

songList = []
count = 0
for i in videoIDs:
    count += 1
    print("Creating video: {}/{}".format(count,len(videoIDs)))
    try:
        songList.append(s.Song(i))
    except IOError:
        print("Song with id: "+i+" can not be loaded!")
    except OSError:
        print("Problem writing the song: "+i)
    except:
        print("Could not load "+i+" for unknown reason :(")

count = 0
"""
for song in songList:
    count += 1
    print("Parsing video: {}/{}".format(count,len(songList)))
    try:
        song.beats()
    except:
        print("Trouble loading song beats!")
"""

tempos = []
for song in songList:
    count += 1
    print("Getting video tempo: {}/{}".format(count,len(songList)))
    try:
        tempo = song.getTempo()
        print("Video: "+song.getName()+" Tempo: "+str(tempo))
        tempos.append(tempo)
    except:
        print("Trouble loading song tempos!")

songAndTempo = zip(songList,tempos)
songAndTempo.sort(key=lambda x:x[1])

playlist_songs = [AudioSegment.from_file(x[0].getAudioPath(),format="ogg") for x in songAndTempo]
beginning_of_song = playlist_songs[0][:30*1000]
playlist = beginning_of_song

for i in range(0,len(songList)):
    ind = i
    partition = np.random.randint(low=5,high=10)/float(30)
    hypeVal = np.random.randint(low=0,high=15)
    print("Playing Song: {} at a partition of: {}".format(songList[ind].getName(),partition))
    l = songAndTempo[ind][0].getHype()
    m = songList[ind].getPartition(partition,l[hypeVal])
    begTime = m[0]*len(playlist_songs[ind])
    endTime = m[1]*len(playlist_songs[ind])
    playlist = playlist.append(playlist_songs[ind][int(begTime):int(endTime)],crossfade=(10*1000))

playlist = playlist.fade_out(100)
out_f = open("my_playlist.ogg", 'wb')

playlist.export(out_f, format='ogg')
