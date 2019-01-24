#!/usr/bin/env python3
import beatsaber
import music_loader
import sys
import getopt

class Settings:
  def __init__(self):
    self.song_file = ''
    self.cover_file = None
    self.generator = 'basic_generator'
    self.output_file = ''

def print_usage():
  print("Usage: " + sys.argv[0] + '[options] <out-directory>')
  print("Creates a beat saber song loader compatible song.")
  print()
  print("Options:")
  print("i,input           The input song file")
  print("c,cover           The input cover file")


def parse_settings():
  s = Settings()
  longopts = [
      'input=',
      'cover='
      ]
  optlist, args = getopt.getopt(sys.argv[1:], 'i:c:', longopts)
  if len(args) != 1:
    print_usage()
    sys.exit(1)
  s.output_file = args[0]
  for var, val in optlist:
    if var == 'i' or var == 'input':
      s.song_file = val
    elif var == 'c' or var == 'cover':
      s.cover_file = val
  return s

if __name__ == '__main__':
  settings = parse_settings()
  inp_song = music_loader.MusicLoader.load(settings.song_file)
  beat_song = generator.BasicGenerator.generate(inp_song)
  beat_song.save(settings.output_file)
