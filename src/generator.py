import beatsaber
import music_loader
import random
import math

_EASY_RAND_VALUES= {
  'col' : [(0.05, 0), (0.5, 1), (0.95, 2), (1, 3)],
  'row' : [(0.1, 0), (0.9, 1), (1, 2)],
  'bomb' : 0.00,
  'inversion' : 0.07,
  'dir_break' : 0,
  'two_blocks' : 0.1,
  'tb_same_col' : 0.3,
  'tb_vertical' : 0.4,
  'tb_v_dir_up' : 0.5,
  'tb_h_dir_left' : 0.5,
  'target_beat' : 50
}

_NORMAL_RAND_VALUES = {
  'col' : [(0.1, 0), (0.5, 1), (0.9, 2), (1, 3)],
  'row' : [(0.15, 0), (0.85, 1), (1, 2)],
  'bomb' : 0.05,
  'inversion' : 0.07,
  'dir_break' : 0.1,
  'two_blocks' : 0.1,
  'tb_same_col' : 0.3,
  'tb_vertical' : 0.4,
  'tb_v_dir_up' : 0.5,
  'tb_h_dir_left' : 0.5,
  'target_beat' : 60
}

_HARD_RAND_VALUES = {
  'col' : [(0.15, 0), (0.5, 1), (0.85, 2), (1, 3)],
  'row' : [(0.2, 0), (0.8, 1), (1, 2)],
  'bomb' : 0.07,
  'inversion' : 0.1,
  'dir_break' : 0.15,
  'two_blocks' : 0.3,
  'tb_same_col' : 0.15,
  'tb_vertical' : 0.4,
  'tb_v_dir_up' : 0.5,
  'tb_h_dir_left' : 0.5,
  'target_beat' : 70
}

_EXPERT_RAND_VALUES = {
  'col' : [(0.25, 0), (0.5, 1), (0.75, 2), (1, 3)],
  'row' : [(0.3, 0), (0.7, 1), (1, 2)],
  'bomb' : 0.15,
  'inversion' : 0.3,
  'dir_break' : 0.15,
  'two_blocks' : 0.3,
  'tb_same_col' : 0.15,
  'tb_vertical' : 0.4,
  'tb_v_dir_up' : 0.5,
  'tb_h_dir_left' : 0.5,
  'target_beat' : 80
}

_DIFFICULTIES = [
  (beatsaber.Difficulty.EASY, _EASY_RAND_VALUES),
  (beatsaber.Difficulty.NORMAL, _NORMAL_RAND_VALUES),
  (beatsaber.Difficulty.HARD, _HARD_RAND_VALUES),
  (beatsaber.Difficulty.EXPERT, _EXPERT_RAND_VALUES)
]

_DIRECTIONS = [
  [[6], [1], [1], [7]],
  [[2], [0, 1, 2, 3, 4, 5, 6, 7, 8], [0, 1, 2, 3, 4, 5, 6, 7, 8], [3]],
  [[4], [0], [0], [5]]
]

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
    song.input_path = inp.input_file
    song.song_name = inp.name
    song.beats_per_minute = inp.bpm

    for difficulty, probabilities in _DIFFICULTIES:
      level = song.add_difficulty_level(difficulty)
      level.beats_per_minute = song.beats_per_minute

      prob_col = probabilities['col']
      prob_row = probabilities['row']

      prob_bomb = probabilities['bomb']
      prob_inversion = probabilities['inversion']
      prob_dir_break = probabilities['dir_break']
      prob_two_blocks = probabilities['two_blocks']
      prob_tb_same_col = probabilities['tb_same_col']
      prob_tb_vertical = probabilities['tb_vertical']
      prob_tb_v_dir_up = probabilities['tb_v_dir_up']
      prob_tb_h_dir_left = probabilities['tb_h_dir_left']

      target_beat = probabilities['target_beat']
      prob_create_note = min(1, target_beat / level.beats_per_minute)

      # Generate the notes
      rand = random.Random()
      pos = float(inp.beats[0])
      step = 60 / level.beats_per_minute 
      # we remember the last type and direction to avoid akward sweeps most
      # of the time.
      # when the same color appears twice
      last_type = None 
      last_direction = None 
      while pos < inp.length:
        if rand.random() > prob_create_note:
          last_type = None
          pos += step
          continue

        # choose a random position
        col_r = rand.random()
        row_r = rand.random()
        for p, i in prob_col:
          if col_r < p:
            col = i
            break
        for p, i in prob_row:
          if row_r < p:
            row= i
            break

        # Determine the color based upon the position (red left blue right).
        # Invert with a certain probability
        invert = rand.random() < prob_inversion 
        type = beatsaber.BeatObjectType.RED if col < 2 and not invert else beatsaber.BeatObjectType.BLUE
        # Replace the block with a bomb
        if rand.random() < prob_bomb:
          type = beatsaber.BeatObjectType.BOMB

        # Determine the direction. Try to avoid akward movements
        # with a single saber most of the time by inverting the direction
        is_centered = (col == 1 or col == 2) and row == 1
        if is_centered and type == last_type and rand.random() < prob_dir_break:
          direction = beatsaber.invert_direction(last_direction)
        else:
          # compute a direction but apply the _DIR_BITMASK
          direction = beatsaber.CutDirection(random.choice(_DIRECTIONS[row][col]))
        last_type = type


        #duplicate the block to create a two block construct
        two_blocks = rand.random() < prob_two_blocks 
        if two_blocks:
          # determine the color of the second block
          same_color = rand.random() < prob_tb_same_col 
          ntype = type if same_color else beatsaber.invert_color(type)
          # determine vertical or horizontak alignment
          vertical = rand.random() < prob_tb_vertical 
          ndir = direction
          if same_color:
            # ensure the bocks can be cut with a single sweep of one of the sabers
            if vertical:
              if rand.random() < prob_tb_v_dir_up: 
                ndir = beatsaber.CutDirection.UP
              else:
                ndir = beatsaber.CutDirection.DOWN
            else:
              if rand.random()  < prob_tb_h_dir_left:
                ndir = beatsaber.CutDirection.LEFT
              else:
                ndir = beatsaber.CutDirection.RIGHT
          else:
            # avoid uncuttable combinations
            if vertical and ndir.value == 0 or ndir.value == 1:
              if rand.random()  < prob_tb_h_dir_left:
                ndir = beatsaber.CutDirection.LEFT
              else:
                ndir = beatsaber.CutDirection.RIGHT
            elif vertical and ndir.value == 2 or ndir.value == 3:
              if rand.random() < prob_tb_v_dir_up: 
                ndir = beatsaber.CutDirection.UP
              else:
                ndir = beatsaber.CutDirection.DOWN
          if vertical:
            nrow = row - 1 if row > 0 else row + 1
            level.add_note(nrow, col, ntype, ndir, pos)
            level.add_note(row, col, type, ndir, pos)
          else:
            ncol = col - 1 if col > 0 else col + 1
            level.add_note(row, ncol, ntype, ndir, pos)
            level.add_note(row, col, type, ndir, pos)
        else:
          # add the node
          level.add_note(row, col, type, direction, pos)

        pos += step
    return song
