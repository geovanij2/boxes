import pygame
import math
# importing needed PodSixNet libraries and timing 
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep

# class BoxesGame extends ConnectionLIstener
class BoxesGame(ConnectionListener):

    def __init__(self):
        pass
        #1
        pygame.init()
        pygame.font.init() # not actually necessary, pygame.init() does it for me
        width = 389
        height = 489
        #2
        # initialize the screen
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Boxes")
        #3
        # initialize pygame clock
        self.clock=pygame.time.Clock()
        # creates list of horizontal pairs of points that makes a line
        self.boardh = [[False for x in range(6)] for y in range(7)]
        # same thing but vertical
        self.boardv = [[False for x in range(7)] for y in range(6)]
        # initialize Graphics
        self.initGraphics()
        # initialize sound
        self.initSound()

        self.turn = True
        self.me = 0
        self.otherplayer = 0
        self.didiwin = False
        # variable to make the player wait for 10 frames before placing another line
        self.justplaced = 10
        # array that keeps track of the owner of the squares
        self.owner = [[0 for x in range(6)] for y in range(6)]
        
        self.gameid = None
        self.num = None

        # initialize PodSixNet client
        # self.Connect()

        # allows user to connect to a different server other than the one on the local machine 
        address = input('Address of Server: ')
        try:
            if not address:
                host, port = 'localhost', 8000
            else:
                host, port = address.split(':')
            self.Connect((host, int(port)))
        except:
            print('Error Connecting to Server')
            print('Usage:', 'host:port')
            print('e.g.', 'localhost:31425')
            exit()
        print("Boxes client started")


        # wait until receive the message to start the game
        self.running = False
        while not self.running:
            self.Pump()
            connection.Pump()
            sleep(0.01)
        # determine attributes from player #
        if self.num == 0:
            self.turn == True
            self.marker = self.greenplayer
            self.othermarker = self.blueplayer
        else:
            self.turn = False
            self.marker = self.blueplayer
            self.othermarker = self.greenplayer


    def Network_startgame(self, data):
        self.running = True
        self.num = data["player"]
        self.gameid = data["gameid"]

    def Network_place(self, data):
        # get attributes
        self.placeSound.play()
        x = data['x']
        y = data['y']
        hv = data['is_horizontal']
        # horizontal or vertical
        if hv:
            self.boardh[y][x] = True
        else:
            self.boardv[y][x] = True

    def Network_yourturn(self, data):
        # torf = short for true of false
        self.turn = data["torf"]

    def Network_win(self, data):
        self.winSound.play()
        self.owner[data['x']][data['y']] = 'win'
        # actually useless
        self.boardh[data["y"]][data["x"]]=True
        self.boardv[data["y"]][data["x"]]=True
        self.boardh[data["y"]+1][data["x"]]=True
        self.boardv[data["y"]][data["x"]+1]=True
        #add one point to my score
        self.me+=1
    def Network_lose(self, data):
        self.loseSound.play()
        self.owner[data["x"]][data["y"]]="lose"
        # actually uselles
        self.boardh[data["y"]][data["x"]]=True
        self.boardv[data["y"]][data["x"]]=True
        self.boardh[data["y"]+1][data["x"]]=True
        self.boardv[data["y"]][data["x"]+1]=True
        #add one to other players score
        self.otherplayer+=1

    def Network_close(self, data):
        exit()

    
    def initGraphics(self):
        # loads the line images
        self.normallinev = pygame.image.load("normalline.png")
        self.normallineh = pygame.transform.rotate(pygame.image.load("normalline.png"), -90)

        self.bar_donev = pygame.image.load("bar_done.png")
        self.bar_doneh = pygame.transform.rotate(pygame.image.load("bar_done.png"), -90)
        
        self.hoverlinev = pygame.image.load("hoverline.png")
        self.hoverlineh = pygame.transform.rotate(pygame.image.load("hoverline.png"), -90)

        self.separators = pygame.image.load("separators.png")

        self.redindicator = pygame.image.load("redindicator.png")
        
        self.greenindicator = pygame.image.load("greenindicator.png")
        
        self.greenplayer = pygame.image.load("greenplayer.png")
        
        self.blueplayer = pygame.image.load("blueplayer.png")
        
        self.winningscreen = pygame.image.load("youwin.png")
        
        self.gameover = pygame.image.load("gameover.png")
        
        self.score_panel = pygame.image.load("score_panel.png")

    def initSound(self):
        pygame.mixer.music.load('music.wav')
        self.winSound = pygame.mixer.Sound('win.wav')
        self.loseSound = pygame.mixer.Sound('lose.wav')
        self.placeSound = pygame.mixer.Sound('place.wav')
        pygame.mixer.music.play()


    def drawBoard(self):
        # draws the board
        for x in range(6):
            for y in range(7):
                if not self.boardh[y][x]:
                    self.screen.blit(self.normallineh, [(x) * 64 + 5, (y) * 64])
                else:
                    self.screen.blit(self.bar_doneh, [(x) * 64 + 5, (y) * 64])

        for x in range(7):
            for y in range(6):
                if not self.boardv[y][x]:
                    self.screen.blit(self.normallinev, [(x) * 64, (y) * 64 + 5])
                else:
                    self.screen.blit(self.bar_donev, [(x) * 64, (y) * 64 + 5])

        for x in range(7):
            for y in range(7):
                self.screen.blit(self.separators, [x * 64, y * 64])

    def drawHUD(self):
        # draw the background for the bottom of the display
        self.screen.blit(self.score_panel, [0, 389])

        # create font
        myfont = pygame.font.SysFont(None, 32)

        # create tex surface
        label = myfont.render("Your Turn:", 1, (255, 255, 255))

        # draw surface
        self.screen.blit(label, (10, 400))

        # draws green indicator
        self.screen.blit(self.greenindicator if self.turn else self.redindicator, (130, 395))

        # adding other texts with different fonts
        myfont64 = pygame.font.SysFont(None, 64)
        myfont20 = pygame.font.SysFont(None, 20)
        # (255,255,255) == white
        scoreme = myfont64.render(str(self.me), 1, (255, 255, 255))
        scoreother = myfont64.render(str(self.otherplayer), 1, (255, 255, 255))
        scoretextme = myfont20.render("You", 1, (255, 255, 255))
        scoretextother = myfont20.render("Other Player", 1, (255, 255, 255))

        self.screen.blit(scoretextme, (10, 425))
        self.screen.blit(scoreme, (10, 435))
        self.screen.blit(scoretextother, (280, 425))
        self.screen.blit(scoreother, (340, 435))

    def drawOwnermap(self):
        for x in range(6):
            for y in range(6):
                if self.owner[x][y] != 0:
                    if self.owner[x][y] == "win":
                        self.screen.blit(self.marker, (x*64 + 5, y * 64 + 5))
                    if self.owner[x][y] == "lose":
                        self.screen.blit(self.othermarker, (x*64 + 5, y*64 + 5))
 

    def update(self):

        if self.me + self.otherplayer == 36:
            self.didiwin = self.me > self.otherplayer
            return 1

        self.justplaced -= 1
        # "pumps" the client and the server so it looks for new events/messages:
        connection.Pump()
        self.Pump()
        # sleep to make the game 60 fps
        self.clock.tick(60)

        # clear the screen
        self.screen.fill(0)
        # draws the lines of the game
        self.drawBoard()
        # draws the HUD
        self.drawHUD()
        # draws the boxes that are done
        self.drawOwnermap()

        for event in pygame.event.get():
            # quit if the quit button was pressed
            if event.type == pygame.QUIT:
                exit()

        #1 - get the mouse position with built-in function
        mouse = pygame.mouse.get_pos()

        #2 - get the position of the mouse on the grid(not sure why the -32)
        #  - i guess it gets always the lowest
        xpos = int(math.ceil((mouse[0] - 32) / 64.0))
        ypos = int(math.ceil((mouse[1] - 32) / 64.0))

        #3 - check if the mouse is closer to the top and bottom or left and right
        #    in order to determine whether the user is hovering over a horizontal or vertical line
        is_horizontal = abs(mouse[1] - ypos*64) < abs(mouse[0] - xpos*64)

        #4 - get the new position on the grid based on the is_horizontal variable
        ypos = ypos - 1 if mouse[1] - ypos*64 < 0 and not is_horizontal else ypos
        xpos = xpos - 1 if mouse[0] - xpos*64 < 0 and is_horizontal else xpos

        #5 - initialize the variable board as either boardh or boardv, whichever is correct 
        board = self.boardh if is_horizontal else self.boardv

        isoutofbounds = False

        #6 - try drawing the hover line to the screen. also checks if the line is out of bounds
        #    if it is, or the line has already been drawn, it doesn't draw the hover line
        try: 
            if not board[ypos][xpos]: self.screen.blit(self.hoverlineh if is_horizontal else self.hoverlinev, [xpos*64+5 if is_horizontal else xpos*64, ypos*64 if is_horizontal else ypos*64+5])
        except:
            isoutofbounds = True
            pass
        if not isoutofbounds:
            alreadyplaced = board[ypos][xpos]
        else:
            alreadyplaced = False       


        # Code that implements click-to-lay-down-line functionality

        if pygame.mouse.get_pressed()[0] and not alreadyplaced and not isoutofbounds and self.turn == True and self.justplaced <= 0:
            self.justplaced = 10
            if is_horizontal:
                self.boardh[ypos][xpos] = True
                connection.Send({"action": "place", "x": xpos, "y": ypos, "is_horizontal": is_horizontal, "gameid": self.gameid, "num": self.num})
            else:
                self.boardv[ypos][xpos] = True    
                connection.Send({"action": "place", "x": xpos, "y": ypos, "is_horizontal": is_horizontal, "gameid": self.gameid, "num": self.num})

        # update the screen
        pygame.display.flip()

    def finished(self):
        self.screen.blit(self.gameover if not self.didiwin else self.winningscreen, (0, 0))
        while 1:
            for event in pygame.event.get():
                if event == pygame.QUIT:
                    exit()
            pygame.display.flip()        


bg = BoxesGame() # __init__ is called right here
while 1:
    if bg.update() == 1:
        break

bg.finished()