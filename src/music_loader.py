import essentia
import essentia.standard
import taglib 
from enum import Enum
# import essentia.streaming
import os

class DataType(Enum):
  BEAT = 0


class Song():
  def __init__(self):
    self.input_file = ''
    self.name = 'unknown'
    self.artist = 'unknown'
    self.composer = 'unknown'
    self.album = 'unknown'
    self.bpm = None 
    self.length = 0
    self.beats = None

class MusicLoader():

  def __init__():
    pass

  @staticmethod
  def load(path, required_data):
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
    for t in required_data:
      if t == DataType.BEAT:
        beatTracker = essentia.standard.BeatTrackerMultiFeature()
        beats = beatTracker(audio)
        song.length = len(audio) / 44100.0
        song.beats = beats[0]
        song.bpm = 60 / ((song.beats[-1] - song.beats[0]) / len(song.beats))
    return song


def compute_segments(path):
    loader = essentia.standard.MonoLoader(filename=path)
    audio = loader()

  
