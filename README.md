where to go from here:

we successfullly got all of this onto vercel, so now what?
Guess the main next step is to get chinese merged into here
and then get the ids data merged in
and then get the rendering working

# Kiokun SSG

A static site generated version of kiokun

## Project Structure

### databases

OUTDATEED:

this is where we will put all of the dictionary files that we have to download from the Internet periodically so that they're all in one place and it's easy to write a script to automatically download the latest version of these are so often and extract it and everything

e.g. jmdict, kanjidict, ids database, dong chinese words and characters, etc

### data

This is the main source folder for all of my work on manipulating the data into eventually getting the individual word and character files that power the site

this is like src for the python

#### main.py

called with `python data/main.py`

this file does the following:

1. calls all of the respective japanese and chinese processing scripts
2. takes the outputs from these functions and writes it to the files in dictionary/

#### jp folder

This folder contains all of the source code for all of the data manipulation python files for the Japanese language. Part of Kun this folder should have one main file that orchestrates everything else. It'll also have a file that cleans up every entry in a way that is specific to the JM dictionary

The main file is jmdict2entries
input: jmdict
output: entries object {'word/character' -> entry}

##### jmdict / jmnedict / kanjidic / kradfile / radkfile

So initially I tried making a centralized "databases" folder work, but it requires too much code jockeying so instead I will colocate the json dictionary files with their processors to make using them easier

### dictionary

This is the output folder that contains all of the individual word and character json files that power the site. Don't try opening this folder. It's huge. It will crash vs code or make it hang.

### src

This is the source folder for all of the web development files like svelte

## Notes

looks like quicktype.io is better than make_types (https://jvilk.com/MakeTypes/) so I will use that for the types for the chinese stuff
