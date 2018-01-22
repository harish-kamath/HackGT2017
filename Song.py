import numpy as np
import pafy
import librosa
import ffmpy
import os
from numpy import genfromtxt
from matplotlib import pyplot as plt
import sounddevice as sd

def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]

class Song:

    def __init__(self, u):
        self.isLoaded = False
        self.url = u
        self.beat_frames = None
        self.y = None
        print("Creating new song: {}".format(self.url))
        video = pafy.new(self.url,basic = False, gdata=False,size=False)
        audio = video.getbestaudio(preftype="ogg")
        if(audio == None):
            audio = video.getbestaudio(preftype="m4a")


        m4a = os.path.isfile("audio/"+u+".m4a") or os.path.isfile(u+".m4a")
        ogg = os.path.isfile("audio/"+u+".ogg") or os.path.isfile(u+".ogg")

        filename = ""
        if(ogg):
            filename = u + ".ogg"
        elif(m4a):
            filename = u + ".m4a"
        else:
            filename = audio.download(quiet=False)
            if(os.path.isfile(filename[:-4] + ".m4a")):
                os.rename(filename[:-4] + ".m4a", u+".m4a")
                filename = u+".m4a"
            else:
                os.rename(filename[:-4] + ".ogg", u+".ogg")
                filename = u+".ogg"
        ogg = os.path.isfile("audio/"+u+".ogg") or os.path.isfile(u+".ogg")

        if(filename[-4:] is not ".ogg" and not (ogg)):
            ff = ffmpy.FFmpeg(inputs={filename: None},outputs={filename[:-4]+".ogg": None})
            ff.run()
            filename = filename[:-4]+".ogg"
        if(os.path.isfile(u+".m4a")):
            os.rename(u+".m4a","audio/"+u+".m4a")
        if(os.path.isfile(u+".ogg")):
            os.rename(u+".ogg","audio/"+u+".ogg")
        self.filename = filename
        print("New song created!")

    def loadSong(self):
        print("Loading file data...")
        if(not(os.path.isfile("txt/"+self.filename[:-4]+".txt"))):
            self.y,self.sr = librosa.load("audio/"+self.filename)
            print("Song has not been downloaded before")
            np.savetxt(self.filename[:-4]+".txt",self.y,delimiter=",")
            print("Saved Song features!")
            os.rename(self.filename[:-4]+'.txt',"txt/"+self.filename[:-4]+'.txt')
        else:
            print("Song already existed! Downloading features now...")
            self.y = np.loadtxt('txt/'+self.filename[:-4]+".txt")
            self.sr = 22050
        self.isLoaded = True

    def beats(self):
        if(not(self.isLoaded)):
            self.loadSong()
        print("Calculating beats and tempo...")
        self.tempo, self.beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sr)
        print('\nEstimated tempo of {}: {:.2f} beats per minute\n'.format(self.filename[:-4],self.tempo))
        beat_times = librosa.frames_to_time(self.beat_frames, sr=self.sr)
        beat_times = np.append(beat_times,[self.tempo])
        print('Saving output to csv...')
        librosa.output.times_csv(self.filename[:-4]+'_beat_times.csv', beat_times)
        os.rename(self.filename[:-4]+'_beat_times.csv',"csv/"+self.filename[:-4]+'_beat_times.csv')


    def getBeats(self):
        if(os.path.isfile("csv/"+self.filename[:-4]+'_beat_times.csv')):
            self.beat_frames = genfromtxt("csv/"+self.filename[:-4]+'_beat_times.csv', delimiter=',')
            self.tempo = self.beat_frames[-1]
        else:
            self.beats()
        return self.beat_frames

    def getTempo(self):
        if(not(self.beat_frames == None)):
            self.tempo = self.beat_frames[-1]
        else:
            self.getBeats()
        return self.tempo

    def play(self):
        if(self.y == None):
            self.loadSong()
        sd.play(self.y,self.sr,blocking=True)

    def getHype(self):
        if(self.y == None):
            self.loadSong()
        oenv = librosa.onset.onset_strength(y=self.y,sr=self.sr,hop_length=512)
        tempogram = librosa.feature.tempogram(onset_envelope=oenv,sr=self.sr,hop_length=512)
        tempogram[::-1].sort(axis=0)
        hypeTimes = tempogram[:,1]
        hypeTimes = np.delete(hypeTimes,0)
        return hypeTimes

    def getName(self):
        return self.url

    def getPartition(self,portion,point):
        if(self.y == None):
            self.loadSong()
        leng = self.y.size
        point *= leng
        lower = 0 if (point - portion*leng < 0)   else int(point - portion * leng)
        upper =  leng if (point + portion*leng > leng) else int(point + portion * leng)
        fLower = lower/float(leng)
        fUpper = upper/float(leng)

        beat_times = librosa.frames_to_time(self.beat_frames, sr=self.sr)

        ran = beat_times[-1] - beat_times[0]

        fLower *= ran
        fUpper *= ran

        fLower = find_nearest(beat_times, fLower)/ran
        fUpper = find_nearest(beat_times,fUpper) / ran


        return (fLower,fUpper)


    def getAudioPath(self):
        return "audio/" + self.filename[:-4]+".ogg"

    def getBeatsCSVPath(self):
        return self.filename[:-4]+"_beat_times.csv"

    def getTextPath(self):
        return self.filename[:-4]+".txt"
