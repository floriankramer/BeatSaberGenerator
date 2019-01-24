import beatsaber
import music_loader

class BasicGenerator():

  def __init__(self):
    pass

  @staticmethod
  def generate(inp):
    """
    This generator uses the beats of the input song and a randomizer for
    generation. No further input is used.
    Args:
      inp(music_loader.Song): The song for which the beatsaber song should be
                              generated .
    Returns:
    A beatsaber.Song object generated from inp.
    """
    song = beatsaber.Song() 
    song.song_name = inp.name
    song.beats_per_minute = inp.bpm
    normal = song.add_difficulty_level(beatsaber.Difficulty.NORMAL)
    for t in inp.beats:
      normal.add_note(0, 0, beatsaber.BeatObjectType.RED, beatsaber.CutDirection.ANY, t)
    return song
