import beatsaber
import music_loader
import random
import math

_EASY_RAND_VALUES= {
  'col' : [(0.05, 0), (0.5, 1), (0.95, 2), (1, 3)],
  'row' : [(0.7, 0), (0.9, 1), (1, 2)],
  'bomb' : 0.00,
  'inversion' : 0.07,
  'dir_break' : 0,
  'two_blocks' : 0.1,
  'tb_same_col' : 0.3,
  'tb_vertical' : 0.4,
  'tb_v_dir_up' : 0.5,
  'tb_h_dir_left' : 0.5,
  'wall' : 0.005,
  'target_beat' : 70,
  'min_headheight_dist' : 5
}

_NORMAL_RAND_VALUES = {
  'col' : [(0.1, 0), (0.5, 1), (0.9, 2), (1, 3)],
  'row' : [(0.55, 0), (0.85, 1), (1, 2)],
  'bomb' : 0.05,
  'inversion' : 0.07,
  'dir_break' : 0.1,
  'two_blocks' : 0.15,
  'tb_same_col' : 0.3,
  'tb_vertical' : 0.4,
  'tb_v_dir_up' : 0.5,
  'tb_h_dir_left' : 0.5,
  'wall' : 0.01,
  'target_beat' : 80,
  'min_headheight_dist' : 3
}

_HARD_RAND_VALUES = {
  'col' : [(0.15, 0), (0.5, 1), (0.85, 2), (1, 3)],
  'row' : [(0.4, 0), (0.8, 1), (1, 2)],
  'bomb' : 0.1,
  'inversion' : 0.15,
  'dir_break' : 0.15,
  'two_blocks' : 0.25,
  'tb_same_col' : 0.15,
  'tb_vertical' : 0.4,
  'tb_v_dir_up' : 0.5,
  'tb_h_dir_left' : 0.5,
  'wall' : 0.015,
  'target_beat' : 95,
  'min_headheight_dist' : 1.5
}

_EXPERT_RAND_VALUES = {
  'col' : [(0.25, 0), (0.5, 1), (0.75, 2), (1, 3)],
  'row' : [(0.1, 0), (0.7, 1), (1, 2)],
  'bomb' : 0.15,
  'inversion' : 0.3,
  'dir_break' : 0.15,
  'two_blocks' : 0.3,
  'tb_same_col' : 0.15,
  'tb_vertical' : 0.4,
  'tb_v_dir_up' : 0.5,
  'tb_h_dir_left' : 0.5,
  'wall' : 0.02,
  'target_beat' : 110,
  'min_headheight_dist' : 1
}

_DIFFICULTIES = [
  (beatsaber.Difficulty.EASY, _EASY_RAND_VALUES),
  (beatsaber.Difficulty.NORMAL, _NORMAL_RAND_VALUES),
  (beatsaber.Difficulty.HARD, _HARD_RAND_VALUES),
  (beatsaber.Difficulty.EXPERT, _EXPERT_RAND_VALUES)
]

# allow all directions for the two central columns in the bottom and center row
# Only allow outward directions in all other fields
_DIRECTIONS = [
  [[6], [0, 1, 2, 3, 4, 5, 6, 7, 8], [0, 1, 2, 3, 4, 5, 6, 7, 8], [7]],
  [[2], [0, 1, 2, 3, 4, 5, 6, 7, 8], [0, 1, 2, 3, 4, 5, 6, 7, 8], [3]],
  [[4], [0], [0], [5]]
]

class BasicGenerator():

  def __init__(self):
    pass

  @staticmethod
  def _compute_wall_probs(wall_rows, wall_cols, wall_prob_row, wall_prob_col, prob_row, prob_col):
    """
    This updates the probabilities in wall_prob_* to match those in prob_*
    without the rows and columns in wall_rows and wall_cols. To ensure
    that the probabilities still sum to one the removed probability
    is evenly distributed among the remaining rows or columns
    """
    # adjust the row probabilities
    total_new_row = 0
    for row in wall_rows:
      if row == 0:
        total_new_row += prob_row[row][0]
      else:
        total_new_row += prob_row[row][0] - prob_row[row - 1][0]
    if len(wall_rows) < 3:
      total_new_row /= 3 - len(wall_rows)
    # set the probability for all rows in wall_rows to 0,
    # for all other rows increase it by total_new_row
    for row in range(0, 3):
      if row in wall_rows:
        if row == 0:
          wall_prob_row[row] = (0, 0)
        else:
          wall_prob_row[row] = (wall_prob_row[row - 1][0], row)
      else:
        if row == 0:
          wall_prob_row[row] = (prob_row[0][0] + total_new_row, 0)
        else:
          prob_old = prob_row[row][0] - prob_row[row - 1][0]
          wall_prob_row[row] = (wall_prob_row[row - 1][0] + prob_old + total_new_row, row)

    # adjust the col probabilities
    total_new_col = 0
    for col in wall_cols:
      if col == 0:
        total_new_col += prob_col[col][0]
      else:
        total_new_col += prob_col[col][0] - prob_col[col - 1][0]
    if len(wall_cols) < 4:
      total_new_col /= 4 - len(wall_cols)
    # set the probability for all cols in wall_cols to 0,
    # for all other cols increase it by total_new_col
    for col in range(0, 4):
      if col in wall_cols:
        if col == 0:
          wall_prob_col[col] = (0, 0)
        else:
          wall_prob_col[col] = (wall_prob_col[col - 1][0], col)
      else:
        if col == 0:
          wall_prob_col[col] = (prob_col[0][0] + total_new_col, 0)
        else:
          prob_old = prob_col[col][0] - prob_col[col - 1][0]
          wall_prob_col[col] = (wall_prob_col[col - 1][0] + prob_old + total_new_col, col)
    


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
    song.song_sub_name = inp.album
    song.song_author_name = inp.artist
    song.beats_per_minute = inp.bpm

    time_to_beats = inp.bpm / 60 

    for difficulty, probabilities in _DIFFICULTIES:
      level = song.add_difficulty_level(difficulty)
      level.beats_per_minute = song.beats_per_minute

      prob_col = probabilities['col']
      prob_row = probabilities['row']
      wall_prob_col = [0, 0, 0, 0]
      wall_prob_row = [0, 0, 0]
      

      prob_bomb = probabilities['bomb']
      prob_inversion = probabilities['inversion']
      prob_dir_break = probabilities['dir_break']
      prob_two_blocks = probabilities['two_blocks']
      prob_tb_same_col = probabilities['tb_same_col']
      prob_tb_vertical = probabilities['tb_vertical']
      prob_tb_v_dir_up = probabilities['tb_v_dir_up']
      prob_tb_h_dir_left = probabilities['tb_h_dir_left']
      prob_wall = probabilities['wall']

      target_beat = probabilities['target_beat']
      min_headheight_dist= probabilities['min_headheight_dist']

      prob_create_note = min(1, target_beat / level.beats_per_minute)

      # Generate the notes
      rand = random.Random()
      # wait at least five seconds or until the first beat was detected
      pos = 2
      for i in inp.beats:
        if i > pos:
          pos = i
          break;
      step = 60 / level.beats_per_minute 
      # we remember the last type and direction to avoid akward sweeps most
      # of the time.
      # when the same color appears twice
      last_type = None 
      last_direction = None 
      last_block_headheight = -50
      # this stores when the current wall will end. This is used
      # to toggle wall based effect on and off
      wall_end = 0
      # These store which rows and cols are entirely blocked by a wall
      wall_cols = []
      wall_rows = []
      while pos < inp.length:
        if rand.random() > prob_create_note:
          last_type = None
          pos += step
          continue

        # convert the timestamp to beats
        t = pos * time_to_beats

        # generate walls
        if pos > wall_end and rand.random() < prob_wall:
          # create a wall with a length between 3 and 6 seconds
          length = math.ceil((3 + rand.random() * 3) * time_to_beats)
          # update the wall end timestamp
          wall_end = pos + length / time_to_beats
          wall_rows.clear()
          wall_cols.clear()
          if rand.random() < 0.2:
            # crate a ceiling
            level.add_obstacle(0, beatsaber.BeatObstacleType.CEILING, 4, t, length)
            wall_rows = [2]
          else:
            col = rand.randint(0, 3)
            if col == 0:
              level.add_obstacle(0, beatsaber.BeatObstacleType.WALL, 1, t, length)
              wall_cols = [0]
            elif col == 1:
              level.add_obstacle(0, beatsaber.BeatObstacleType.WALL, 2, t, length)
              wall_cols = [0, 1]
            elif col == 2:
              level.add_obstacle(2, beatsaber.BeatObstacleType.WALL, 2, t, length)
              wall_cols = [2, 3]
            elif col == 3:
              level.add_obstacle(3, beatsaber.BeatObstacleType.WALL, 1, t, length)
              wall_cols = [3]
          # Compute new probabilities that don't place objects into walls
          BasicGenerator._compute_wall_probs(wall_rows, wall_cols, wall_prob_row, wall_prob_col, prob_row, prob_col)


        # choose a random position, avoid crowding
        # the headspace in row 1
        while True: 
          col_r = rand.random()
          row_r = rand.random()
          pc = prob_col if wall_end < pos else wall_prob_col
          pr = prob_row if wall_end < pos else wall_prob_row
          for p, i in pc:
            if col_r < p:
              col = i
              break
          for p, i in pr:
            if row_r < p:
              row= i
              break
          if pos - last_block_headheight > min_headheight_dist or not ((col == 1 or col == 2) and row == 1):
            break
        if (col == 1 or col == 2) and row == 1:
          last_block_headheight = pos


        # Determine the color based upon the position (red left blue right).
        # Invert with a certain probability
        invert = rand.random() < prob_inversion 
        color_bool = col < 2
        if invert:
          color_bool = not color_bool
        type = beatsaber.BeatObjectType.RED if color_bool else beatsaber.BeatObjectType.BLUE
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


        # Duplicate the block to create a two block construct if we are not
        # in a wall
        two_blocks = pos > wall_end and rand.random() < prob_two_blocks 
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
            if vertical and (ndir.value == 0 or ndir.value == 1):
              if rand.random()  < prob_tb_h_dir_left:
                ndir = beatsaber.CutDirection.LEFT
              else:
                ndir = beatsaber.CutDirection.RIGHT
            elif not vertical and (ndir.value == 2 or ndir.value == 3):
              if rand.random() < prob_tb_v_dir_up: 
                ndir = beatsaber.CutDirection.UP
              else:
                ndir = beatsaber.CutDirection.DOWN
          if vertical:
            nrow = row - 1 if row > 0 else row + 1
            level.add_note(nrow, col, ntype, ndir, t)
            level.add_note(row, col, type, ndir, t)
          else:
            ncol = col - 1 if col > 0 else col + 1
            level.add_note(row, ncol, ntype, ndir, t)
            level.add_note(row, col, type, ndir, t)
        else:
          # add the node
          level.add_note(row, col, type, direction, t)

        pos += step
    return song
