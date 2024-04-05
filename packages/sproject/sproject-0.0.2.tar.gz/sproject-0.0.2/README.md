# API for finding same type of files and copy in a specific path

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)                 
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)   

[Follow Doveloper](https://www.instagram.com/nicky_connects/?next=%2F)
## Functionality of the Music Player

- Better Optimization
- Pause/Play Supported
- Add/Delete songs from Playlist
- Previous/Next song function
- Time duration of song / next song displays
- List of all the songs.
- Adjust Volume
- Automatically Playing in Queue
- Play Selected song from Playlist

## Usage

- Make sure you have Python installed in your system.
- Run Following command in the CMD.
 ```
  pip install NTools
  ```
## Example

 ```
 #test.py
from NTools import copy_files

#Make sure you entered the correct file extension.
extension = '.pdf'

# enter the source and destination path as follows
s_path = "your source directory"
d_path = "your destination directory"

# Now the Function call should be like this
copy_files(s_path,d_path,extension)
  ```

## Run the following Script.
 ```
  python test.py
 ```

## Output 
- x files copied
- No files found with the extension

## Note 
- I have tried to implement all the functionality, it might have some bugs also. Ignore that or please try to solve that bug.
