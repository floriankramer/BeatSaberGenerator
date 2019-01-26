# BeatSaberGenerator
This python program creates [Song Loader](https://github.com/xyonico/BeatSaberSongLoader/releases) compatible songs from arbitrary ogg input files.
Currently it does so using [essentia](https://essentia.upf.edu/) to automatically detect the songs beat and then simply
generates random notes mines and walls (although there are further constraints to make the result playable). More algorithms
for level generation are planned, but might never make it to the ligth of day due to the usual constraints of time and 
motivation.

## Installation
The entire generator is written in python3 with the following dependencies, which can be installed using pip:
 - essentia
 - pytaglib
With everything installed you can start the generator using either the `generator.py` command line interface or `gui.py` for
a minimalistic graphical user interface.

### Windows
These instructions for windows are currently untested and may not work. If you get these working and had to change anything please
create an issue or a pull request.
Install python 3 from [python.org](https://www.python.org/downloads/). If the installer asks you if you want to add python to your path
say yes. Open the powershell / cmd with administrative rights and run `pip3 install essentia pytaglib`.
You should now be able to double click `gui.py` to open the generators gui.

### Linux
Install python3 using you distributions package manager:  
 - Ubuntu / debian : `sudo apt install python3 python3-pip`
 - ArchLinux : `sudo pacman -S python python-pip`
Now install the required dependencies:  
`pip3 install essentia pytaglib`  
Thats it. You should now be able to start the generator using either `generator.py` or `gui.py`

## Using the generator
If you want to play the generated songs be sure to select the CustomSongs folder in your BeatSaber installation folder as the output folder,
or copy the songs folders there manually after generating them. You can find your installation Folder by right clicking
the game in your steam library, going into the preferences and selecting `Open in explorer` under the local files tab.
### GUI
Select a song or folder as the input file (When selecting a folder you might currently have to select a song in that folder and
then remove the file name from the input text field). Then select your output folder (e.g. The CustomSongs folder) and press
generate. The ui will hang for a while now (Using a second thread to keep the ui from blocking is planned). On my
system with an i7 it takes 5-7 seconds per song, so depending on the input size this might take a while. There currently
is no progress bar. If you want to monitor the progress check the output folder manually.

### Command Line
Run `generate.py -i <input-folder> <OutputFolder>`. You can pass multiple input folders / files by repeatedly using the -i flag.
Thescript will recurse through any folders passed as input and process any .ogg files it finds inside.
