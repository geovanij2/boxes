import PodSixNet.Channel
import PodSixNet.Server
from time import sleep

class ClientChannel(PodSixNet.Channel.Channel):

	def Network(self, data):
		print(data)

	# it's called whenever some client sends a message with the keyword "place"
	def Network_place(self, data):
		# deconsolidate all of the data from the dictionary

		# horizontal or verticall?
		hv = data["is_horizontal"]
		# x of placed line
		x = data["x"]
		# y of placed line
		y = data['y']
		# player number (1 or 0)
		num = data['num']
		# id of game given by server at the start of game
		self.gameid = data["gameid"]
		# tells server to place line
		self._server.placeLine(hv, x, y, data, self.gameid, num)

	def Close(self):
		self._server.close(self.gameid)


class BoxesServer(PodSixNet.Server.Server):

	def __init__(self, *args, **kwargs):
		PodSixNet.Server.Server.__init__(self, *args, **kwargs)
		self.games = []
		self.queue = None
		self.currentIndex = 0

	channelClass = ClientChannel

	def Connected(self, channel, addr):
		print('new connection:', channel)
		'''
		The server checks if theres a game in the queue. if there isnt, then the server creates a new
		game and puts it in the queue so that the next time a client connects, they are assigned to that
		game. Otherwise, it sends a "start game" message to both players
		'''
		if self.queue == None:
			self.currentIndex += 1
			channel.gameid = self.currentIndex
			self.queue = Game(channel, self.currentIndex)
		else:
			channel.gameid = self.currentIndex
			self.queue.player1 = channel
			self.queue.player0.Send({"action": "startgame","player":0, "gameid": self.queue.gameid})
			self.queue.player1.Send({"action": "startgame","player":1, "gameid": self.queue.gameid})
			self.games.append(self.queue)
			self.queue=None

	def placeLine(self, is_h, x, y, data, gameid, num):
		game = [a for a in self.games if a.gameid == gameid]
		if len(game) == 1:
			game[0].placeLine(is_h, x, y, data, num)


	def tick(self):
		# Declaring some variables. index keeps track of which game to loop current is
		# 							change tells whether the turn should change or not
		#							and whose turn should it be
		index = 0
		change = 3
		# Loops through all the games and resets the change to 3, which means no change
		for game in self.games:
			change = 3
			for time in range(2):
				# loops through all of the possible squares. it is done twice because it's possible that
				# a player could get two squares at once by drawing a middle line between two boxes
				for y in range(6):
					for x in range(6):
						# for each possible square, checks if there is a square and if so, make sure it wasn't drawn on an earlier turn
						if game.boardh[y][x] and game.boardv[y][x] and game.boardh[y+1][x] and game.boardv[y][x+1] and not game.owner[x][y]:
							if self.games[index].turn == 0:
								self.games[index].owner[x][y] = 2
								game.player1.Send({'action': 'win', 'x': x, 'y': y})
								game.player0.Send({'action': 'lose', 'x': x, 'y': y})
								change = 1
							else:
								self.games[index].owner[x][y] = 1
								game.player0.Send({'action': 'win', 'x': x, 'y': y})
								game.player1.Send({'action': 'lose', 'x': x, 'y': y})
								change = 0
			# check to see who placed the line that made the square and set the change variable correctly
			self.games[index].turn = change if change != 3 else self.games[index].turn
			game.player1.Send({'action': 'yourturn', 'torf': True if self.games[index].turn == 1 else False})
			game.player0.Send({'action': 'yourturn', 'torf': True if self.games[index].turn == 0 else False})
			index += 1
		self.Pump()

	def close(self, gameid):
		try:
			game = [a for a in self.games if a.gameid == gameid][0]
			game.player0.Send({'action': 'close'})
			game.player1.Send({'action': 'close'})
		except:
			pass


class Game:

	def __init__(self, player0, currentIndex):
		# whose turn (1 or 0)
		self.turn = 0
		# owner map
		self.owner = [[False for x in range(6)] for y in range(6)]
		# Seven lines in each direction to make a six by six grid.
		self.boardh = [[False for x in range(6)] for y in range(7)]
		self.boardv = [[False for x in range(7)] for y in range(6)]
		# initialize the players including the one who started the game
		# player is a channel
		self.player0 = player0
		self.player1 = None
		#gameid of game
		self.gameid = currentIndex

	def placeLine(self, is_h, x, y, data, num):
		# make sure it's their turn
		if num == self.turn:
			self.turn = 0 if self.turn else 1
			self.player1.Send({"action":"yourturn", "torf": True if self.turn == 1 else False})
			self.player0.Send({"action":"yourturn", "torf": True if self.turn == 0 else False})
			# place line in game
			if is_h:
				self.boardh[y][x] = True
			else:
				self.boardv[y][x] = True
			# send data and turn data to each player
			self.player0.Send(data)
			self.player1.Send(data)	

'''
Creates a simple bare bones connection that listens for connections on a default port.
When someone connects, it prints out a message
'''

print('STARTING SERVER ON LOCALHOST')
# default
# boxesServe = BoxesServer()
# not default
# try:
address = input('Host:Port (localhost:8000): ')
if not address:
	host, port = 'localhost', 8000
else:
	host, port = address.split(':')
boxesServe = BoxesServer(localaddr=(host, int(port)))
while True:
	boxesServe.tick()
	sleep(0.01)