#!/usr/bin/env python3
import os
import multiprocessing
import traceback

import ui.mainwindow
import beatsaber
import music_loader
import generators.beat
import generate

def process_dirs(indir, outdir):
  msgs = []
  try:
    print('processing ', indir, outdir)
    if not os.path.exists(outdir):
      os.makedirs(outdir, exist_ok=True)
    num_cores = max(1, multiprocessing.cpu_count() - 1)
    inputs = generate.find_input_files([indir])
    if len(inputs) == 0:
      msgs.append('No input files found.')
      return msgs
    print('Found', len(inputs), 'files')
    process_args = []
    for path in inputs:
      process_args.append((path, os.path.join(outdir, os.path.basename(path)), 'generators.beat'))
    with multiprocessing.Pool(num_cores) as pool:
      pool.starmap(generate.process_file, process_args)
  except Exception as e:
    traceback.print_exc()
    msgs.append(str(e))
  msgs.append('Done')
  return msgs

if __name__ == '__main__':
  print('Starting the gui')
  mainwindow = ui.mainwindow.MainWindow()
  mainwindow.generate_function = process_dirs
  mainwindow.mainloop()

