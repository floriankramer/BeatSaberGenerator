from enum import Enum
import os
import shutil
import json

class BeatObjectType(Enum):
  RED = 0
  BLUE = 1
  BOMB = 3

def invert_color(t):
  if t == BeatObjectType.RED:
    return BeatObjectType.BLUE
  elif t == BeatObjectType.BLUE:
    return BeatObjectType.RED
  return t

class BeatObstacleType(Enum):
  WALL = 0
  CEILING = 1

class CutDirection(Enum):
  UP = 0
  DOWN = 1
  LEFT = 2
  RIGHT = 3
  UP_LEFT = 4
  UP_RIGHT = 5
  DOWN_LEFT = 6
  DOWN_RIGHT = 7
  ANY = 8

def invert_direction(d):
  if  d == CutDirection.UP:
    return CutDirection.DOWN
  elif  d == CutDirection.DOWN:
    return CutDirection.UP
  elif  d == CutDirection.LEFT:
    return CutDirection.RIGHT
  elif  d == CutDirection.RIGHT:
    return CutDirection.LEFT
  elif  d == CutDirection.UP_LEFT:
    return CutDirection.DOWN_RIGHT
  elif  d == CutDirection.UP_RIGHT:
    return CutDirection.DOWN_LEFT
  elif  d == CutDirection.DOWN_LEFT:
    return CutDirection.UP_RIGHT
  elif  d == CutDirection.DOWN_RIGHT:
    return CutDirection.UP_LEFT
  return CutDirection.ANY

class BeatObject:
  def __init__(self):
    """
    _time : The time at which the object will pass the player
    _column: The column of the 3 x 4 grid
    _row: The row of the 3 x 4 grid
    """
    self._type = BeatObjectType.RED 
    self._time = 0.0
    self._column = 0
    self._row = 0
    self._cut_direction = CutDirection.ANY

  def to_json(self):
    l = ['{']
    l.append('"_lineLayer": ')
    l.append(self._row)
    l.append('"_lineIndex": ')
    l.append(self._col)
    l.append('"_type": ')
    l.append(self._type.value)
    l.append('"_time": ')
    l.append(self._time)
    l.append('"_cutDirection": ')
    l.append(self._cut_direction.value)
    return ''.join(l)

  def to_jsonable(self):
    tmp = {}
    tmp['_lineLayer'] = self._row
    tmp['_lineIndex'] = self._column
    tmp['_type'] = self._type.value
    tmp['_cutDirection'] = self._cut_direction.value
    tmp['_time'] = self._time
    return tmp

class BeatObstacle():
  def __init__(self):
    """
    _time : The time at which the object will pass the player
    _column: The column of the 3 x 4 grid
    _row: The row of the 3 x 4 grid
    """
    self._type = BeatObstacleType.WALL 
    self._time = 0.0
    self._column = 0
    self._width = 1
    self._duration = 1

  def to_json(self):
    return json.dumps(self.to_jsonable())

  def to_jsonable(self):
    tmp = {}
    tmp['_lineIndex'] = self._column
    tmp['_type'] = self._type.value
    tmp['_duration'] = self._duration
    tmp['_time'] = self._time
    tmp['_width'] = self._width
    return tmp

class Difficulty(Enum):
  EASY = 'easy'
  NORMAL = 'normal'
  HARD = 'hard'
  EXPERT = 'expert'

_DIFFICULTY_RANKS = {
  Difficulty.EASY.value : 1,
  Difficulty.NORMAL.value : 2,
  Difficulty.HARD.value : 3,
  Difficulty.EXPERT.value : 4
}

class DifficultyLevel():
  def __init__(self):
    self.version = '1.5.0'
    self.beats_per_minute = 60
    self.beats_per_bar = 4
    self.note_jump_speed = 10
    self.shuffle = 1
    self.shuffle_period = 0.2
    self.events = []
    self.notes = []
    self.obstacles = []

  def to_jsonable(self):
    tmp = {}
    tmp['_version'] = self.version
    tmp['_beatsPerMinute'] = self.beats_per_minute
    tmp['_beatsPerBar'] = self.beats_per_bar
    tmp['_noteJumpSpeed'] = self.note_jump_speed
    tmp['_shuffle'] = self.shuffle
    tmp['_shufflePeriod'] = self.shuffle_period
    l = []
    tmp['_events'] = l
    l = []
    for note in self.notes:
      l.append(note.to_jsonable())
    tmp['_notes'] = l
    l = []
    for obstacle in self.obstacles:
      l.append(obstacle.to_jsonable())
    tmp['_obstacles'] = l
    return tmp

  def to_json(self):
    return json.dumps(self.to_jsonable()) 

  def add_note(self, row, col, type, cut_direction, time):
    """
    Args:
      row(int): the row from [0:2] with 0 being the bottom row
      col(int): the col from [0:3] with 0 being the leftmost column
      type(BeatObjectType): the objects type
      cut_direction(CutDirection): The cut direction (use any for a bomb)
      time(float): the timestamp at which the object should pass the player
    """
    n = BeatObject()
    n._row = row
    n._column = col
    n._type = type
    n._cut_direction = cut_direction
    n._time = time
    self.notes.append(n)

  def add_obstacle(self, col, type, width, time, duration):
    o = BeatObstacle()
    o._column = col
    o._type = type
    o._width = width
    o._time = time
    o._duration = duration
    self.obstacles.append(o)


class Song:
  def __init__(self):
    """
    This info is copied straight from https://github.com/xyonico/BeatSaberSongLoader
    "songName" - Name of your song
    "songSubName" - Text rendered in smaller letters next to song name. (ft. Artist)
    "beatsPerMinute" - BPM of the song you are using
    "previewStartTime" - How many seconds into the song the preview should start
    "previewDuration" - Time in seconds the song will be previewed in selection screen
    "coverImagePath" - Cover image name
    "environmentName" - Game environment to be used
    "songTimeOffset" - Time in seconds of how early a song should start. Negative numbers for starting the song later
    "shuffle" - Time in number of beats how much a note should shift
    "shufflePeriod" - Time in number of beats how often a note should shift. Don't ask me why this is a feature, I don't know
    "oneSaber" - true or false if it should appear in the one saber list

    All possible environmentNames:
    -DefaultEnvironment
    -BigMirrorEnvironment
    -TriangleEnvironment
    -NiceEnvironment

    "difficultyLevels": [
      {
        "difficulty": This can only be set to Easy, Normal, Hard, Expert or ExpertPlus,
        "difficultyRank": Currently unused whole number for ranking difficulty,
        "jsonPath": The name of the json file for this specific difficulty
      }
      ]
    """
    self.input_path = None
    self.cover_path = None
    self.song_name = 'Custom Song'
    self.song_sub_name = 'Ft. Nobody'
    self.song_author_name = 'Author'
    self.beats_per_minute = 60
    self.preview_start_time = 10
    self.preview_duration = 20
    self.song_time_offset = -5
    self.shuffle = 1
    self.shuffle_period = 0.2
    self.one_saber = False 
    self.difficulty_levels = {}
    
  def add_difficulty_level(self, difficulty):
    if not difficulty in self.difficulty_levels.keys():
      self.difficulty_levels[difficulty] = DifficultyLevel() 
    return self.difficulty_levels[difficulty]

  def save(self, dest):
    if not os.path.exists(dest):
      os.mkdir(dest)
    # copy the song
    tmp_song_path = os.path.join(dest, os.path.basename(self.input_path))
    shutil.copy(self.input_path, tmp_song_path)

    # copy the cover
    if self.cover_path is not None:
      tmp_cover_path = os.path.join(dest, os.path.basename(self.cover_path))
      shutil.copy(self.input_path, tmp_cover_path)

    # write the info.json
    tmp_info_path = os.path.join(dest, 'info.json')
    with open(tmp_info_path, 'w') as f:
      print(self.to_json(), file=f)

    for difficulty, level in self.difficulty_levels.items():
      tmp_level_path = os.path.join(dest, difficulty.value + '.json')
      with open(tmp_level_path, 'w') as f:
        print(level.to_json(), file=f)

  def to_jsonable(self):
    audio_path = 'audio.ogg'
    cover_image_path = 'cover.jpg'
    if self.input_path is not None:
      audio_path = os.path.basename(self.input_path)
    if self.cover_path is not None:
      cover_image_path = os.path.basename(self.cover_path)
    tmp = {}
    tmp['songName'] = self.song_name
    tmp['songSubName'] = self.song_sub_name
    tmp['authorName'] = self.song_author_name
    tmp['beatsPerMinute'] = self.beats_per_minute
    tmp['previewStartTime'] = self.preview_start_time
    tmp['previewDuration'] = self.preview_duration
    tmp['coverImagePath'] = cover_image_path
    tmp['environmentName'] = audio_path 
    l = []
    for difficulty, level in self.difficulty_levels.items():
      tmp2 = {}
      tmp2['difficulty'] = difficulty.value
      tmp2['difficultyRank'] = _DIFFICULTY_RANKS[difficulty.value] 
      tmp2['audioPath'] = audio_path
      tmp2['jsonPath'] = difficulty.value + '.json'
      tmp2['offset'] = 0
      tmp2['oldOffset'] = 0
      l.append(tmp2)
    tmp['difficultyLevels'] = l
    return tmp

  def to_json(self):
    return json.dumps(self.to_jsonable()) 

