# makergamer
A fantasy console that can play Python 3, HTML/JS, and Scratch games.
### This is a work in progress! Currently, only Python games will work.
Developed on Ubuntu, but it will eventually be for [PocketCHIP](https://nextthing.co/pages/pocketchip). (I don't have a PocketCHIP yet.)  

Run makergamer.py with Python 3. That's all!  

To download code, go to the Download menu and type in a GitHub repo name (like ["wesleycha/mg-test-py"](https://github.com/wesleycha/mg-test-py). Press Download.  

To play games, go to the Play menu, and select the game.  

None of the other menus work yet.  

### Developing games
Games are stored in a folder with the Python code and any other files (images, sounds, etc.) needed, as well as a `manifest.json` file.  

The Python 3 code must be in a file named `index.py`.  

A suitable `manifest.json` file would look like:  
~~~~
{  
  "title":"A game"  
}  
~~~~
Obviously, replace `A game` with whatever your game is called.
