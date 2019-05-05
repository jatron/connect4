from random import Random

from colorama import Fore
from loguru import logger


class ConnectFour(object):

    pass

class Player(object):

    def __init__(self, no:int, color=None):
        self.no = no

        colors = [ Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE ]
        if color in colors:
            self.disk = color + 'O' + Fore.RESET
        else:
            self.disk = Random.choice([ Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]) + 'O' + Fore.RESET

    def next_move(self, connect4_board):
        raise NotImplementedError

class HumanPlayer(Player):

    def next_move(self, connect4_board):

        try:
            move = int(input(Fore.GREEN + 'Player {}\'s next move: '.format(self.no) + Fore.RESET))
            connect4_board.is_valid(move)
        except:
            logger.error(Fore.RED + 'Wrong input `{}`, please try again.'.format(move) + Fore.RESET)
            move = self.next_move(connect4_board=connect4_board)

        return move

class NetworkPlayer(Player):

    def next_move(self, connect4_board):
        raise NotImplementedError

class ComputerPlayer(Player):

    def next_move(self, connect4_board):
        raise NotImplementedError
