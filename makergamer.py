import pygame
from glob import glob
from json import loads as json
from runpy import run_path
from os import system, chdir
from os.path import isfile
from shutil import rmtree
from requests import get as request
import texteditor
#from webbrowser import open as webopen
pygame.init()
myfont = pygame.font.SysFont("Ubuntu", 20, bold=True)

pygame.mouse.set_visible(False)
# Comment out for debugging purposes (writing this on Ubuntu laptop)

WIDTH = 480
HEIGHT = 272
DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MakerGamer")

third = int(WIDTH / 3)
half = int(HEIGHT / 2)
top_padding = 10
bottom_padding = 50
offset = int((third - half + top_padding + bottom_padding) / 2)
image_length = half - top_padding - bottom_padding
text_padding = 10

wallpaper = pygame.image.load("wallpaper.jpg").convert()
wallpaper = pygame.transform.scale(wallpaper, (WIDTH, HEIGHT))

mode = "home"
currentGame = ""

class Tile:
    def __init__(self, icon_src, title, mode="home", currentGame=""):
        self.image = pygame.image.load(icon_src).convert_alpha()
        self.image = pygame.transform.scale(self.image, (image_length, image_length))
        self.title = title
        self.titleSurf = myfont.render(self.title, 1, (255, 255, 255))
        self.titleWidth = myfont.size(self.title)[0]
        self.titleOffset = (third - self.titleWidth) / 2
        self.mode = mode
        self.currentGame = currentGame

tiles = []
tiles.append(Tile("icons/download.png", "Download", "download"))
tiles.append(Tile("icons/play.png", "Play", "play"))
tiles.append(Tile("icons/edit.png", "Edit", "edit"))
tiles.append(Tile("icons/person.png", "Friends"))
tiles.append(Tile("icons/upload.png", "Upload"))
tiles.append(Tile("icons/settings.png", "Settings"))

numToXy = {0:(0, 0), 1:(third, 0), 2:(2*third, 0),
           3:(0, half), 4:(third, half), 5:(2*third, half)}

halfNumToXy = {0:(0, half), 1:(third, half), 2:(2*third, half)}

class TileMenu:
    def __init__(self, tiles, left=False, right=False): # Left, right refer to presence of arrows
        self.tiles = tiles
        self.rightArrow = pygame.image.load("icons/arrow.png").convert_alpha()
        self.leftArrow = pygame.transform.flip(self.rightArrow, True, False)
        self.left = left
        self.right = right

    def draw(self):
        for i, tile in enumerate(self.tiles):
            x, y = numToXy[i]
            DISPLAY.blit(tile.image, (x+offset, y+top_padding))
            #print("Blitting text "+tile.title+" to "+str((x-tile.titleOffset, y-bottom_padding)))
            DISPLAY.blit(tile.titleSurf, (x+tile.titleOffset, y+(half-bottom_padding)+text_padding))
        arrow_h = (HEIGHT / 2) - 32
        if self.left:
            DISPLAY.blit(self.leftArrow, (0, arrow_h))
        if self.right:
            DISPLAY.blit(self.rightArrow, (WIDTH-40, arrow_h))

    def handleMouse(self, pos):
        global mode, currentGame
        x, y = pos
        t = None
        if x < 40:
            return -1
        if x > (WIDTH - 40):
            return 1
        if x < third:
            if y < half:
                t = 0
            else:
                t = 3
        elif x < 2*third:
            if y < half:
                t = 1
            else:
                t = 4
        else:
            if y < half:
                t = 2
            else:
                t = 5
        if t >= len(self.tiles):
            return 0 # No tile there!
        mode = self.tiles[t].mode
        currentGame = self.tiles[t].currentGame
        return 0

menu = TileMenu(tiles)

class HalfMenu:
    def __init__(self, tiles):
        self.tiles = tiles

    def draw(self):
        for i, tile in enumerate(self.tiles):
            x, y = halfNumToXy[i]
            DISPLAY.blit(tile.image, (x+offset, y+top_padding))
            #print("Blitting text "+tile.title+" to "+str((x-tile.titleOffset, y-bottom_padding)))
            DISPLAY.blit(tile.titleSurf, (x+tile.titleOffset, y+(half-bottom_padding)+text_padding))


    def handleMouse(self, pos):
        global mode, currentGame
        x, y = pos
        t = None
        if y < half:
            return
        if x < third:
            t = 0
        elif x < 2*third:
            t = 1
        else:
            t = 2
        if t >= len(self.tiles):
            return 0 # No tile there!
        mode = self.tiles[t].mode
        currentGame = self.tiles[t].currentGame
        return 0

shifts = {"`":"~",
          "1":"!", "2":"@", "3":"#", "4":"$", "5":"%", "6":"^", "7":"&", "8":"*", "9":"(", "0":")",
          "-":"_", "=":"+",
          "[":"{", "]":"}", "\\":"|",
          ";":":", "'":'"',
          ",":"<", ".":">", "/":"?"}

class Textbox:
    def __init__(self):
        self.x = 100
        self.y = half/2 - 10
        self.width = WIDTH - 200
        self.height = 20
        self.text = ""
        self.shift = False

    def draw(self):
        pygame.draw.rect(DISPLAY, (255, 255, 255), (self.x, self.y, self.width, self.height), 4)
        pygame.draw.rect(DISPLAY, (0, 0, 0), (self.x, self.y, self.width, self.height))
        textSurf = myfont.render(self.text, 1, (255, 255, 255))
        DISPLAY.blit(textSurf, (self.x, self.y))

    def addch(self, ch):
        if not self.shift:
            self.text += ch
        else:
            try:
                self.text += shifts[ch]
            except KeyError:
                self.text += ch.upper()

    def delete(self):
        self.text = self.text[:-1]

class GameInfo:
    def __init__(self, icon, title, description):
        self.icon = pygame.image.load(icon).convert_alpha()
        self.icon_l = sorted((int(WIDTH/2-20), int(half-20)))[0]
        self.icon = pygame.transform.scale(self.icon, (self.icon_l, self.icon_l))
        self.title = myfont.render(title, True, (255, 255, 255))

        self.descriptions = []
        
        d = ""
        description = description.split(" ")
        maxW = WIDTH-(self.icon_l+40)
        # This basically just keeps adding words to a line until it is too long,
        # then starts a new line.
        for i in range(len(description)):
            #print(d)
            if myfont.size(d+description[i]+" ")[0] > maxW:
                # If the current string plus the next word is too big...
                self.descriptions.append(myfont.render(d, True, (255, 255, 255)))
                d = ""
            d += description[i]+" "
        self.descriptions.append(myfont.render(d, True, (255, 255, 255)))

    def draw(self):
        global DISPLAY
        DISPLAY.blit(self.icon, (10, 10))
        DISPLAY.blit(self.title, (self.icon_l+20, 10))
        for i, d in enumerate(self.descriptions):
            DISPLAY.blit(d, (self.icon_l+20, 30+20*i))
        

def handleQuit(event):
    if event.type == pygame.QUIT:
        return True
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return True
    return False

clock = pygame.time.Clock()

def makePlayMenu():
    games = glob("games/*/")
    tiles = [Tile("icons/back.png", "Back")]
    for game in games:
        gamedir = game.split("/")[1]
        try:
            with open(game+"manifest.json") as manifestFile:
                manifest = json(manifestFile.read())
        except:
            # Probably a Scratch project
            # Make up a manifest on the fly
            manifest = {"title":gamedir, "description":"No Description Provided"}
        if isfile(game+"favicon.png"):
            icon = game+"favicon.png"
        else:
            icon = "icons/play.png"
        title = manifest["title"]
        tiles.append(Tile(icon, title, mode="play", currentGame=gamedir))
    menus = []
    for x in range(0, len(tiles), 6):
        menus.append(TileMenu(tiles[x:x+6]))
    for num, menu in enumerate(menus):
        if not num == 0:
            menu.left = True
        if not num == len(menus) - 1:
            menu.right = True
    return menus

def makeEditMenu():
    games = glob("games/*/")
    tiles = [Tile("icons/back.png", "Back")]
    for game in games:
        gamedir = game.split("/")[1]
        try:
            with open(game+"manifest.json") as manifestFile:
                manifest = json(manifestFile.read())
        except:
            # Probably a Scratch project
            # Make up a manifest on the fly
            manifest = {"title":gamedir, "description":"No Description Provided"}
        if isfile(game+"favicon.png"):
            icon = game+"favicon.png"
        else:
            icon = "icons/play.png"
        title = manifest["title"]
        tiles.append(Tile(icon, title, mode="edit", currentGame=gamedir))
    menus = []
    for x in range(0, len(tiles), 6):
        menus.append(TileMenu(tiles[x:x+6]))
    for num, menu in enumerate(menus):
        if not num == 0:
            menu.left = True
        if not num == len(menus) - 1:
            menu.right = True
    return menus

def playSwitch():
    if currentGame == "":
        play()
    else:
        playGame()

def editSwitch():
    if currentGame == "":
        edit()
    else:
        editGame()

##class SwipeDetector: # Untested, get back to this later...
##    def __init__(self):
##        self.x = 0
##        self.y = 0
##        self.down = False
##    def mousedown(self, x, y): # Call at each mousedown event
##        self.x = x
##        self.y = y
##        self.down = True
##    def mouseup(self, x, y): # 1 is right, -1 is left, 0 is not a swipe
##        if x > self.x + 80:
##            return 1
##        if x < self.x - 80:
##            return -1
##        return 0

def play():
    global mode, currentGame
    playMenus = makePlayMenu()
    currentMenu = 0
    while mode == "play" and currentGame == "":
        DISPLAY.blit(wallpaper, (0, 0))
        for event in pygame.event.get():
            if handleQuit(event):
                pygame.quit()
                mode == "quit"
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                currentMenu += playMenus[currentMenu].handleMouse(event.pos)
                if currentMenu < 0: currentMenu = 0
                if currentMenu >= len(playMenus): currentMenu = len(playMenus+1)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    currentMenu -= 1
                    if currentMenu < 0:
                        currentMenu = 0
                elif event.key == pygame.K_RIGHT:
                    currentMenu += 1
                    if currentMenu >= len(playMenus):
                        currentMenu = len(playMenus) - 1
        playMenus[currentMenu].draw()
        pygame.display.update()
        clock.tick(30)

def edit():
    global mode, currentGame
    editMenus = makeEditMenu()
    currentMenu = 0
    while mode == "edit" and currentGame == "":
        DISPLAY.blit(wallpaper, (0, 0))
        for event in pygame.event.get():
            if handleQuit(event):
                pygame.quit()
                mode == "quit"
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                currentMenu += editMenus[currentMenu].handleMouse(event.pos)
                if currentMenu < 0: currentMenu = 0
                if currentMenu >= len(editMenus): currentMenu = len(editMenus+1)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    currentMenu -= 1
                    if currentMenu < 0:
                        currentMenu = 0
                elif event.key == pygame.K_RIGHT:
                    currentMenu += 1
                    if currentMenu >= len(editMenus):
                        currentMenu = len(editMenus) - 1
        editMenus[currentMenu].draw()
        pygame.display.update()
        clock.tick(30)

def playGame():
    global currentGame
    myGame = currentGame
    tiles = [Tile("icons/back.png", "Back", "play"), Tile("icons/play.png", "Play", "run", currentGame),
             Tile("icons/trash.png", "Delete", "delete", currentGame)]
    menu = HalfMenu(tiles)
    if isfile("games/"+currentGame+"/favicon.png"):
        icon = "games/"+currentGame+"/favicon.png"
    else:
        icon = "icons/play.png"
    try:
        with open("games/"+currentGame+"/manifest.json") as manifestFile:
            manifest = json(manifestFile.read())
    except:
        # Probably a Scratch project
        # Make up a manifest on the fly
        manifest = {"title":currentGame, "description":"No Description Provided"}
    if "title" not in manifest.keys():
        manifest["title"] = currentGame
    if "description" not in manifest.keys():
        manifest["description"] = "No Description Provided"
    info = GameInfo(icon, manifest["title"], manifest["description"])
    while mode == "play" and currentGame == myGame:
        DISPLAY.blit(wallpaper, (0, 0))
        for event in pygame.event.get():
            if handleQuit(event):
                pygame.quit()
                mode == "quit"
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                menu.handleMouse(event.pos)
        menu.draw()
        info.draw()
        pygame.display.update()
        clock.tick(30)

def runGame():
    global currentGame, mode, DISPLAY
    files = glob("games/"+currentGame+"/*")
    if "games/"+currentGame+"/index.py" in files:
        playPY()
    else:
        system("surf file:///home/chip/makergamer/games/"+currentGame+"/index.html")
    currentGame = ""
    mode = "home"

def playPY():
    global currentGame, DISPLAY
    try:
        chdir("games/"+currentGame+"/")
        run_path("index.py")
    except Exception as e:
        print(e)
    chdir("../..")
    pygame.init()
    DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("MakerGamer")

def delete():
    global currentGame, mode
    rmtree("games/"+currentGame+"/")#, ignore_errors=True)
    mode = "home"
    currentGame = ""

def editGame():
    global mode, currentGame
    startingGame = currentGame
    tiles = []
    tiles.append(Tile("icons/back.png", "Back", "edit"))
    tiles.append(Tile("icons/edit.png", "Edit Code", "editCode", currentGame))
    tiles.append(Tile("icons/images.png", "Edit Images", "editImages", currentGame))
    tiles.append(Tile("icons/sounds.png", "Edit Sounds", "editSounds", currentGame))
    editMenu = TileMenu(tiles)
    while mode == "edit" and currentGame == startingGame:
        DISPLAY.blit(wallpaper, (0, 0))
        for event in pygame.event.get():
            if handleQuit(event):
                pygame.quit()
                mode == "quit"
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                editMenu.handleMouse(event.pos)
        editMenu.draw()
        pygame.display.update()
        clock.tick(30)

def editCode():
    global mode
    files = glob("games/"+currentGame+"/*")
    if "games/"+currentGame+"/index.py" in files:
        texteditor.load("games/"+currentGame+"/index.py")
    elif "games/"+currentGame+"/index.html" in files:
        texteditor.load("games/"+currentGame+"/index.html")
    else:
        print("No editable code found")
    mode = "edit"

def editImages():
    global mode
    print("You can't edit "+currentGame+"'s images yet, sorry")
    mode = "edit"

def editSounds():
    global mode
    print("You can't edit "+currentGame+"'s sounds yet, sorry")
    mode = "edit"

def home():
    while mode == "home":
        DISPLAY.blit(wallpaper, (0, 0))
        for event in pygame.event.get():
            if handleQuit(event):
                pygame.quit()
                mode == "quit"
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                menu.handleMouse(event.pos)
        menu.draw()
        pygame.display.update()
        clock.tick(30)

def download():
    global mode
    tiles = []
    tiles.append(Tile("icons/back.png", "Back"))
    tiles.append(Tile("icons/download.png", "Download", "download", ""))
    downMenu = HalfMenu(tiles)
    textbox = Textbox()
    while mode == "download" and currentGame == "":
        DISPLAY.blit(wallpaper, (0, 0))
        for event in pygame.event.get():
            if handleQuit(event):
                pygame.quit()
                mode == "quit"
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                downMenu.handleMouse(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    textbox.delete()
                elif event.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
                    textbox.shift = True
                else:
                    try:
                        textbox.addch(chr(event.key))
                    except:
                        pass
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
                    textbox.shift = False
        downMenu.draw()
        textbox.draw()
        downMenu.tiles[1].currentGame = textbox.text
        pygame.display.update()
        clock.tick(30)

def downloadSwitch():
    global currentGame
    if currentGame == "":
        download()
    else:
        downloadGame()

def downloadGame():
    global currentGame, mode
    scratch = False
    try:
        int(currentGame)
    except:
        scratch = False
    else:
        scratch = True
    if scratch:
        with open("../phosphorus/app.html", "w") as myFile:
            myFile.write(r'''
<!doctype html>
<meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name=apple-mobile-web-app-capable content=yes>
<meta name=apple-mobile-web-app-status-bar-style content=black>
<title>phosphorus</title>
<link rel=stylesheet href=app.css>
<div class=player></div>
<div class=splash>
<div>
  <h1>phosphorus</h1>
  <p>by nathan</p>
  <div class=progress><div class=progress-bar></div></div>
</div>
</div>
<div class=error>
<div>
  <h1>phosphorus</h1>
  <p>An error has occurred. <a id=bug-link href=https://github.com/nathan/phosphorus/issues/new>Click here</a> to file a bug report on GitHub.</p>
</div>
</div>
<script src=fonts.js></script>
<script src=lib/jszip.js></script>
<script src=lib/rgbcolor.js></script>
<script src=lib/StackBlur.js></script>
<script src=lib/canvg.js></script>
<script src=phosphorus.js></script>
<script>

(function () {
  'use strict';

  if (location.protocol === 'https:') {
    location.replace(('' + location).replace(/^https:/, 'http:'));
  }

  var stage;

  var projectId = '''+currentGame+r''';
  var projectTitle = '';
  var turbo = false;
  var fullScreen = true;

  var params = location.search.substr(1).split('&');
  params.forEach(function(p) {
    var parts = p.split('=');
    if (parts.length > 1) {
      switch (parts[0]) {
        case 'id':
          projectId = Number(parts[1]);
          break;
        case 'turbo':
          turbo = parts[1] !== 'false';
          break;
        case 'full-screen':
          fullScreen = parts[1] !== 'false';
          break;
      }
    }
  });

  var splash = document.querySelector('.splash');
  var progressBar = document.querySelector('.progress-bar');
  var error = document.querySelector('.error');
  var bugLink = document.querySelector('#bug-link');
  var player = document.querySelector('.player');

  var stage;

  function layout() {
    if (!stage) return;
    var w = Math.min(window.innerWidth, window.innerHeight / .75);
    if (!fullScreen) w = Math.min(w, 480);
    var h = w * .75;
    player.style.left = (window.innerWidth - w) / 2 + 'px';
    player.style.top = (window.innerHeight - h) / 2 + 'px';
    stage.setZoom(w / 480);
    stage.draw();
  }

  function showError(e) {
    error.style.display = 'table';
    bugLink.href = 'https://github.com/nathan/phosphorus/issues/new?title=' + encodeURIComponent(projectTitle || '') + '&body=' + encodeURIComponent('\n\n\nhttp://scratch.mit.edu/projects/' + projectId + '\nhttp://phosphorus.github.io/#' + projectId + (e.stack ? '\n\n```\n' + e.stack + '\n```' : ''));
    console.error(e.stack);
  }

  window.addEventListener('resize', layout);

  if (P.hasTouchEvents) {
    document.addEventListener('touchmove', function(e) {
      e.preventDefault();
    });
  }

  var request = P.IO.loadScratchr2Project(projectId);

  request.onload = function (s) {
    splash.style.display = 'none';

    stage = s;
    layout();

    s.isTurbo = turbo;
    s.start();
    s.triggerGreenFlag();

    player.appendChild(s.root);
    s.focus();
    s.handleError = showError;
  };
  request.onerror = showError;
  request.onprogress = function (e) {
    progressBar.style.width = (10 + e.loaded / e.total * 90) + '%';
  };

  P.IO.loadScratchr2ProjectTitle(projectId, function(title) {
    document.title = projectTitle = title;
  });

}());

</script>
''')
        system("surf file:///home/chip/phosphorus/app.html")
    else:
        if not "/" in currentGame:
            mode = "scratch"
            print("currentGame is a Scratch uname. Switching to Scratch mode.")
            return
        else:
            repo_name = currentGame.split("/")[-1]
            system("git clone https://github.com/"+currentGame+"/ games/"+repo_name)
    currentGame = ""

def makeScratchMenu():
    global currentGame
    
    def getProjects(user, offset=0):
        r = request("https://api.scratch.mit.edu/users/"+user+"/projects?offset="+str(offset)).json()
        if len(r) == 20:
            r += getProjects(user, offset+20)
        return r

    projects = getProjects(currentGame)

    tiles = [Tile("icons/back.png", "Back")]

    for p in projects:
        title = p["title"]
        if len(title) > 15:
            title = title[:12]+"..."
        tiles.insert(1, Tile("icons/play.png", title, "download", str(p["id"])))

    menus = []
    for x in range(0, len(tiles), 6):
        menus.append(TileMenu(tiles[x:x+6]))
    for num, menu in enumerate(menus):
        if not num == 0:
            menu.left = True
        if not num == len(menus) - 1:
            menu.right = True
    return menus

    

def scratch():
    global mode, currentGame
    print("Scratch mode! currentGame: ", currentGame)
    user = currentGame

    menus = makeScratchMenu()
    currentMenu = 0
    
    while mode == "scratch" and currentGame == user:
        DISPLAY.blit(wallpaper, (0, 0))
        for event in pygame.event.get():
            if handleQuit(event):
                pygame.quit()
                mode == "quit"
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                currentMenu += menus[currentMenu].handleMouse(event.pos)
                if currentMenu < 0: currentMenu = 0
                if currentMenu >= len(menus): currentMenu = len(menus+1)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    currentMenu -= 1
                    if currentMenu < 0:
                        currentMenu = 0
                elif event.key == pygame.K_RIGHT:
                    currentMenu += 1
                    if currentMenu >= len(menus):
                        currentMenu = len(menus) - 1
        menus[currentMenu].draw()
        pygame.display.update()
        clock.tick(30)
    

modes = {"home":home, "play":playSwitch, "edit":editSwitch,
         "editCode":editCode, "editImages":editImages, "editSounds":editSounds,
         "download":downloadSwitch, "run":runGame, "delete":delete, "scratch":scratch}

while True:
    if mode == "quit":
        break
    elif mode in modes:
        modes[mode]()

pygame.mouse.set_visible(True)
