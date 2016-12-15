import pygame
from glob import glob
from json import loads as json
from runpy import run_path
pygame.init()
myfont = pygame.font.SysFont("Ubuntu", 20, bold=True)

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
tiles.append(Tile("icons/download.png", "Download"))
tiles.append(Tile("icons/play.png", "Play", "play"))
tiles.append(Tile("icons/edit.png", "Edit", "edit"))
tiles.append(Tile("icons/person.png", "Friends"))
tiles.append(Tile("icons/upload.png", "Upload"))
tiles.append(Tile("icons/settings.png", "Settings"))

numToXy = {0:(0, 0), 1:(third, 0), 2:(2*third, 0),
           3:(0, half), 4:(third, half), 5:(2*third, half)}

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
            manifest = {"title":gamedir}
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
            manifest = {"title":gamedir}
        icon = "icons/edit.png"
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
            if event.type == pygame.QUIT:
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
            if event.type == pygame.QUIT:
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
    global currentGame, DISPLAY
    try:
        run_path("games/"+currentGame+"/index.py")
    except Exception as e:
        print(e)
    pygame.init()
    DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("MakerGamer")
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
            if event.type == pygame.QUIT:
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
    print("You can't edit "+currentGame+"'s code yet, sorry")
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
            if event.type == pygame.QUIT:
                pygame.quit()
                mode == "quit"
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                menu.handleMouse(event.pos)
        menu.draw()
        pygame.display.update()
        clock.tick(30)

modes = {"home":home, "play":playSwitch, "edit":editSwitch,
         "editCode":editCode, "editImages":editImages, "editSounds":editSounds}

while True:
    if mode == "quit":
        break
    elif mode in modes:
        modes[mode]()
    
