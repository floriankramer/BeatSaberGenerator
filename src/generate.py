#!/usr/bin/env python3
import sys
import getopt
import os
import threading
import multiprocessing
import math

import beatsaber
import music_loader
import generators.beat


class Settings:
  def __init__(self):
    self.inputs = [] 
    self.cover_file = None
    self.generator = 'basic_generator'
    self.output_file = ''

def print_usage():
  print("Usage: " + sys.argv[0] + '[options] <out-directory>')
  print("Creates a beat saber song loader compatible song.")
  print()
  print("Options:")
  print("i,input           An input song file or folder. Multiple inputs can be specified.")
  print("c,cover           The input cover file")


def parse_settings():
  s = Settings()
  longopts = [
      'input=',
      'cover='
      ]
  optlist, args = getopt.getopt(sys.argv[1:], 'i:c:', longopts)
  if len(args) != 1:
    print('Wrong number of arguments. Expected one but got ' + str(len(args)))
    print_usage()
    sys.exit(1)
  s.output_file = args[0]
  for var, val in optlist:
    if var == '-i' or var == '--input':
      s.inputs.append(val)
    elif var == '-c' or var == '--cover':
      s.cover_file = val
  if len(s.inputs) == 0:
    print('An input file is required.')
    print_usage()
    sys.exit(1)
  return s

def find_input_files(l, endings_in=['ogg']):
  """
  Finds a list of inputs from all files in l and all files contained in folder
  in l.
  """
  candidates = [i for i in l]
  files = []
  endings = frozenset(endings_in)
  while len(candidates) > 0:
    path = candidates.pop()
    if os.path.isdir(path):
      # add all contens to the candidate, effectively
      # crawling through the folder structure
      for name in os.listdir(path):
        candidates.append(os.path.join(path, name))
    elif os.path.isfile(path):
      # determine the file ending
      p = path.find('.')
      p = max(p, 0)
      p = min(p + 1, len(path))
      end = path[p:]
      if end in endings:
        files.append(path)
  return files

def process_file(inpath, outpath, generator_name):
    inp_song = music_loader.MusicLoader.load(inpath, generators.beat.required_data())
    beat_song = generators.beat.generate(inp_song)
    beat_song.save(outpath)

if __name__ == '__main__':
  settings = parse_settings()
  if not os.path.exists(settings.output_file):
    os.mkdir(settings.output_file)
  if not os.path.isdir(settings.output_file):
    print('The output has to be a folder.')
    sys.exit(1)
  inputs = find_input_files(settings.inputs)

  process_args = []
  for path in inputs:
    process_args.append((path, os.path.join(settings.output_file, os.path.basename(path)), 'generators.beat'))


  # leave one core unused to help keep the system running smoothly
  num_cores = max(1, multiprocessing.cpu_count() - 1)
  # avoid spawning more workers than we have input files
  num_cores = min(num_cores, len(inputs))

  with multiprocessing.Pool(num_cores) as pool:
    pool.starmap(process_file, process_args)
