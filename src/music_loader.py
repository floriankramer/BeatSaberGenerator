import essentia
import essentia.standard
import taglib 
# import essentia.streaming
import os

class Song():
  def __init__(self):
    self.input_file = ''
    self.name = 'unknown'
    self.artist = 'unknown'
    self.composer = 'unknown'
    self.album = 'unknown'
    self.bpm = 60
    self.length = 0
    self.beats = None

class MusicLoader():

  def __init__():
    pass

  @staticmethod
  def load(path):
    song = Song()
    song.input_file = path
    song.name = os.path.basename(path)[:-4]

    tagfile = taglib.File(path)
    tags = tagfile.tags
    if 'TITLE' in tags:
      song.name = str(tags['TITLE'][0])
    if 'ARTIST' in tags:
      song.artist = str(tags['ARTIST'][0])
    if 'COMPOSER' in tags:
      song.composer = str(tags['COMPOSER'][0])
    if 'ALBUM' in tags:
      song.album = str(tags['ALBUM'][0])

    loader = essentia.standard.MonoLoader(filename=path)
    audio = loader()
    beatTracker = essentia.standard.BeatTrackerMultiFeature()
    beatTracker(audio)
    beats = beatTracker(audio)
    song.length = len(audio) / 44100.0
    song.beats = beats[0]
    song.bpm = 0.0
    for i in range(1, len(song.beats)):
      song.bpm += song.beats[i] - song.beats[i - 1]
    song.bpm /= len(song.beats)
    song.bpm = 60 / song.bpm
    return song
