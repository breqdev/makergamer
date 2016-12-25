import pygame
from time import time
from math import ceil
pygame.init()

shifts = {"`":"~",
          "1":"!", "2":"@", "3":"#", "4":"$", "5":"%", "6":"^", "7":"&", "8":"*", "9":"(", "0":")",
          "-":"_", "=":"+",
          "[":"{", "]":"}", "\\":"|",
          ";":":", "'":'"',
          ",":"<", ".":">", "/":"?"}

class TextEditor:
    def __init__(self, display, width, height, font, file, text=""):
        self.width = width
        self.height = height
        self.font = font
        self.cellW, self.cellH = self.font.size("8")
        self.display = display
        self.text = text.split("\n")
        self.shift = False
        self.cursorY = 0
        self.cursorX = 0
        self.drawnX = 0
        self.clicked = False
        self.highlightX = self.cursorX
        self.highlightY = self.cursorY
        self.undo = [self.text]
        self.ctrl = False
        self.redo = self.text
        self.file = file
        self.scroll = 0

    def draw(self):
        if self.cursorY > len(self.text) - 1:
            self.cursorY = len(self.text) - 1
        currentLine = self.text[self.cursorY]
        if len(currentLine) < self.cursorX:
            self.drawnX = len(currentLine)
        else:
            self.drawnX = self.cursorX
        if self.highlightY > len(self.text) - 1:
            self.highlightY = len(self.text) - 1
        currentLine = self.text[self.highlightY]
        if len(currentLine) < self.highlightX:
            self.highlightX = len(currentLine)

        visibleStart = self.scroll/self.cellH
        visibleEnd = (self.height+self.scroll)/self.cellH - 1
        while self.cursorY < visibleStart:
            self.scroll -= 10
            visibleStart = self.scroll/self.cellH
        while self.cursorY > visibleEnd:
            self.scroll += 10
            visibleEnd = (self.height+self.scroll)/self.cellH - 1
        
        display = self.display
        for y in range(len(self.text)):
            for x in range(len(self.text[y])):
                #print("blitting char "+str(x)+" line "+str(y)+
                      #" at pos "+str(x*self.cellW)+", "+str(y*self.cellH))
                if 0 <= (y*self.cellH - self.scroll) <= self.height:
                    text = self.font.render(self.text[y][x], 1, (255, 255, 255))
                    display.blit(text, (x*self.cellW, y*self.cellH - self.scroll))
        if self.cursorX < 0:
            self.cursorX = 0
        if self.drawnX < 0:
            self.drawnX = 0
        if self.cursorY < 0:
            self.cursorY = 0
        if self.highlightX < 0:
            self.highlightX = 0
        if self.highlightY < 0:
            self.highlightY = 0
        pygame.draw.line(display, (255, 255, 255), (self.drawnX*self.cellW, ((self.cursorY+1)*self.cellH)-self.scroll),
                         (self.drawnX*self.cellW, self.cursorY*self.cellH - self.scroll))

        highlightedLines = abs(self.cursorY - self.highlightY) + 1
        lesser = sorted((self.cursorY, self.highlightY))[0]
        lesserX, greaterX = sorted(((self.cursorY, self.cursorX), (self.highlightY, self.highlightX)))
        lesserYX, greaterYX = lesserX[1], greaterX[1]
        for i in range(highlightedLines):
            if i == 0:
                rectX1 = lesserYX*self.cellW
            else:
                rectX1 = 0
            rectY1 = (lesser+i+1)*self.cellH
            if i == highlightedLines-1:
                rectX2 = greaterYX*self.cellW
            else:
                rectX2 = self.width
            rectY2 = (lesser+i)*self.cellH
            rectX1, rectX2 = sorted((rectX1, rectX2))
            rectY1, rectY2 = sorted((rectY1, rectY2))
            rectSurf = pygame.Surface((rectX2-rectX1, rectY2-rectY1))
            rectSurf.set_alpha(128)
            rectSurf.fill((255, 255, 255))
            display.blit(rectSurf, (rectX1, rectY1))
        
    def addch(self, ch):
        self.undo.append(self.text[:])
        if self.highlightX != self.cursorX or self.highlightY != self.cursorY:
            self.highlightDel()
        global shifts
        self.cursorX = self.drawnX
        if self.shift:
            try:
                ch = shifts[ch]
            except:
                ch = ch.upper()
        self.text[self.cursorY] = self.text[self.cursorY][:self.cursorX] \
                                  + ch + self.text[self.cursorY][self.cursorX:]
        self.cursorX += 1
        self.resetHighlight()

    def highlightDel(self):
        highlightedLines = abs(self.cursorY - self.highlightY)+1
        lesserY = sorted((self.cursorY, self.highlightY))[0]
        finalLine = ""
        linesToDel = []
        lesserX = 0
        for i in range(highlightedLines):
            currentLine = self.text[lesserY+i]
            linesToDel.append(lesserY+i)
            if i == 0:
                if self.cursorY == self.highlightY:
                    lesser = sorted((self.cursorX, self.highlightX))[0]
                elif self.cursorY < self.highlightY:
                    lesser = self.cursorX
                else:
                    lesser = self.highlightX
                lesserX = lesser
            else:
                lesser = 0
            if i == highlightedLines-1:
                if self.cursorY == self.highlightY:
                    greater = sorted((self.cursorX, self.highlightX))[1]
                elif self.cursorY > self.highlightY:
                    greater = self.cursorX
                else:
                    greater = self.highlightX
            else:
                greater = len(currentLine)
            #lesser, greater = sorted((self.cursorX, self.highlightX))
            #print(currentLine[:lesser] + currentLine[greater:])
            finalLine += currentLine[:lesser] + currentLine[greater:]
        #print(finalLine)
        least = sorted(linesToDel)[0]
        greatest = sorted(linesToDel)[-1]
        lesserY = sorted((self.cursorY, self.highlightY))[0]
        del self.text[least:greatest+1]
        self.text.insert(lesserY, finalLine)
        self.highlightX = lesserX
        self.highlightY = lesserY

    def backspace(self):
        self.undo.append(self.text[:])
        if self.highlightX != self.cursorX or self.highlightY != self.cursorY:
            self.highlightDel()
            return
        self.cursorX = self.drawnX
        if len(self.text[self.cursorY]) == 0:
            del self.text[self.cursorY]
            self.cursorY -= 1
            self.cursorX = len(self.text[self.cursorY])
        elif self.cursorX == 0:
            self.cursorX = len(self.text[self.cursorY-1])
            self.text[self.cursorY-1] += self.text[self.cursorY]
            del self.text[self.cursorY]
            self.cursorY -= 1
        else:
            self.text[self.cursorY] = self.text[self.cursorY][:self.cursorX-1] \
                                      + self.text[self.cursorY][self.cursorX:]
            self.cursorX -= 1
        self.resetHighlight()
            
    def delete(self):
        self.undo.append(self.text[:])
        if self.highlightX != self.cursorX or self.highlightY != self.cursorY:
            self.highlightDel()
            return
        self.cursorX = self.drawnX
        if self.cursorX == len(self.text[self.cursorY]):
            if not self.cursorY + 1 >= len(self.text):
                self.text[self.cursorY] += self.text[self.cursorY+1]
                del self.text[self.cursorY+1]
        else:
            self.text[self.cursorY] = self.text[self.cursorY][:self.cursorX] \
                                      + self.text[self.cursorY][self.cursorX+1:]
        self.resetHighlight()

    def newline(self):
        self.undo.append(self.text[:])
        before = self.text[self.cursorY][:self.cursorX]
        after = self.text[self.cursorY][self.cursorX:]
        self.text.insert(self.cursorY+1, after)
        self.text[self.cursorY] = before
        self.cursorY += 1
        self.cursorX = 0
        self.resetHighlight()

    def handleMouse(self, pos):
        x, y = pos
        x = int(round(x / self.cellW))
        y = int(y / self.cellH)
        self.cursorX = x
        self.cursorY = y
        if self.cursorY > len(self.text) - 1:
            self.cursorY = len(self.text) - 1
        currentLine = self.text[self.cursorY]
        if len(currentLine) < self.cursorX:
            self.cursorX = len(currentLine)
        self.highlightX = self.cursorX
        self.highlightY = self.cursorY

    def handleMotion(self, pos):
        if self.clicked:
            x, y = pos
            self.highlightX = int(round(x / self.cellW))
            self.highlightY = int(y / self.cellH)

    def resetHighlight(self):
        self.highlightX = self.cursorX
        self.highlightY = self.cursorY

    def ctrlZ(self):
        self.redo = self.text[:]
        try:
            self.text = self.undo[-1][:]
            del self.undo[-1]
        except:
            pass

    def ctrlY(self):
        self.undo.append(self.text[:])
        self.text = self.redo[:]

    def ctrlV(self):
        types = pygame.scrap.get_types()
        #print(types)
        chs = ""
        for t in types:
            if "string" in t.lower() or "text" in t.lower():
                get = pygame.scrap.get(t)
                if get:
                    if isinstance(get, bytes):
                        get = get.decode("UTF-8")
                    chs += get
                    break
        for ch in chs:
            self.addch(ch)
            if self.cursorY > len(self.text) - 1:
                self.cursorY = len(self.text) - 1
            currentLine = self.text[self.cursorY]
            if len(currentLine) < self.cursorX:
                self.drawnX = len(currentLine)
            else:
                self.drawnX = self.cursorX

    def ctrlC(self):
        highlightedLines = abs(self.cursorY - self.highlightY)+1
        lesserY = sorted((self.cursorY, self.highlightY))[0]
        finalLine = ""
        linesToCopy = []
        lesserX = 0
        for i in range(highlightedLines):
            currentLine = self.text[lesserY+i]
            if i == 0:
                if self.cursorY == self.highlightY:
                    lesser = sorted((self.cursorX, self.highlightX))[0]
                elif self.cursorY < self.highlightY:
                    lesser = self.cursorX
                else:
                    lesser = self.highlightX
                lesserX = lesser
            else:
                lesser = 0
            if i == highlightedLines-1:
                if self.cursorY == self.highlightY:
                    greater = sorted((self.cursorX, self.highlightX))[1]
                elif self.cursorY > self.highlightY:
                    greater = self.cursorX
                else:
                    greater = self.highlightX
            else:
                greater = len(currentLine)
            #lesser, greater = sorted((self.cursorX, self.highlightX))
            #print(currentLine[:lesser] + currentLine[greater:])
            if highlightedLines == 1:
                linesToCopy.insert(0, currentLine[lesser:greater])
            elif i == 0:
                linesToCopy.insert(0, currentLine[lesser:])
            elif i == highlightedLines - 1:
                linesToCopy.insert(-1, currentLine[:greater])
            else:
                linesToCopy.append(self.text[lesserY+i])
        #print(finalLine)
        least = lesserY
        greatest = len(linesToCopy)+lesserY
        lesserY = sorted((self.cursorY, self.highlightY))[0]
        print(linesToCopy)
        pygame.scrap.put("UTF8_STRING", ("\n".join(linesToCopy)).encode("UTF-8"))

    def ctrlX(self):
        self.ctrlC()
        self.highlightDel()

    def ctrlS(self):
        with open(self.file, "w") as myFile:
            myFile.write("\n".join(self.text))

        



def load(filename):
    DISPLAY = pygame.display.set_mode((480, 272))
    pygame.scrap.init()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Ubuntu Mono", 20)

    with open(filename, "r") as myFile:
        start_str = myFile.read()

    te = TextEditor(DISPLAY, 480, 272, font, filename, start_str)

    controls = {"z":te.ctrlZ, "y":te.ctrlY, "v":te.ctrlV, "c":te.ctrlC, "x":te.ctrlX, "s":te.ctrlS}

    banned_keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
    pressed_at = [-1, -1, -1, -1]

    def glideR():
        te.cursorX = te.drawnX
        te.cursorX += 1
        if te.cursorX > len(te.text[te.cursorY]) and len(te.text)-1 > te.cursorY:
            te.cursorX = 0
            te.cursorY += 1
        te.resetHighlight()

    def glideL():
        te.cursorX = te.drawnX
        te.cursorX -= 1
        if te.cursorX < 0 and te.cursorY > 0:
            te.cursorY -= 1
            te.cursorX = len(te.text[te.cursorY])
        te.resetHighlight()

    q = False
    while not q:
        pygame.draw.rect(DISPLAY, (0, 0, 0), (0, 0, 480, 272))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                q = True
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    q = True
                    break
                elif event.key in (pygame.K_RCTRL, pygame.K_LCTRL):
                    te.ctrl = True
                elif te.ctrl:
                    try:
                        func = controls[chr(event.key)]
                    except:
                        pass
                    else:
                        func()
                        continue
                elif event.key == pygame.K_BACKSPACE:
                    te.backspace()
                elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    te.shift = True
                    print(te.scroll)
                elif event.key == pygame.K_RETURN:
                    te.newline()
                elif event.key == pygame.K_DELETE:
                    te.delete()
    ##            elif event.key == pygame.K_LEFT:
    ##                te.cursorX -= 1
    ##            elif event.key == pygame.K_RIGHT:
    ##                te.cursorX += 1
    ##            elif event.key == pygame.K_UP:
    ##                te.cursorY -= 1
    ##            elif event.key == pygame.K_DOWN:
    ##                te.cursorY += 1
                elif event.key == pygame.K_PAGEUP:
                    te.scroll += te.cellH
                elif event.key == pygame.K_PAGEDOWN:
                    te.scroll -= te.cellH
                elif event.key not in banned_keys:
                    try:
                        ch = chr(event.key)
                    except:
                        pass
                    else:
                        te.addch(ch)
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    te.shift = False
                elif event.key in (pygame.K_RCTRL, pygame.K_LCTRL):
                    te.ctrl = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                te.handleMouse(event.pos)
                te.clicked = True
            elif event.type == pygame.MOUSEMOTION:
                te.handleMotion(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                te.clicked = False
        if q:
            break
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if pressed_at[0] == -1:
                pressed_at[0] = time()
                glideL()
            elif (time() - pressed_at[0]) > 0.5:
                glideL()
        else:
            pressed_at[0] = -1
        if keys[pygame.K_RIGHT]:
            if pressed_at[1] == -1:
                pressed_at[1] = time()
                glideR()
            elif (time() - pressed_at[1]) > 0.5:
                glideR()
        else:
            pressed_at[1] = -1
        if keys[pygame.K_UP]:
            if pressed_at[2] == -1:
                pressed_at[2] = time()
                te.cursorY -= 1
                te.resetHighlight()
            elif (time() - pressed_at[2]) > 0.5:
                te.cursorY -= 1
                te.resetHighlight()
        else:
            pressed_at[2] = -1
        if keys[pygame.K_DOWN]:
            if pressed_at[3] == -1:
                pressed_at[3] = time()
                te.cursorY += 1
                te.resetHighlight()
            elif (time() - pressed_at[3]) > 0.5:
                te.cursorY += 1
                te.resetHighlight()
        else:
            pressed_at[3] = -1
        te.draw()
        pygame.display.update()
        clock.tick(30)



if __name__ == "__main__":
    load("testfile.txt")
