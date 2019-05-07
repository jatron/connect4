from enum import Enum
from random import Random
from sys import stdout

from colorama import Fore
from loguru import logger
from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage


class Agents(Enum):

    ComputerPlayer = 'COMPUTERPLAYER'
    HumanPlayer = 'HUMANPLAYER'
    NetworkPlayer = 'NETWORKPLAYER'

class Player(object):

    def __init__(self, no:int, time_limit:int=None, color=None):

        self.no = no

        if time_limit is None:
            self.time_limit = 180 # Seconds
        else:
            self.time_limit = time_limit

        if color == None:
            if self.no == 1:
                self.color = Fore.RED
            elif self.no == 2:
                self.color = Fore.YELLOW
            else:
                self.color = Fore.GREEN
        else:
            self.color = color

        # colors = [ Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE ]
        # if color in colors:
        #     self.disk = color + 'O' + Fore.RESET
        # else:
        #     self.disk = Random.choice([ Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]) + 'O' + Fore.RESET

    def next_move(self, connect4_board):

        raise NotImplementedError

    def game_finished(self, connect4_board, won:bool):

        raise NotImplementedError

class ComputerPlayer(Player):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = Agents.ComputerPlayer

    def next_move(self, connect4_board):

        raise NotImplementedError

    def game_finished(self, connect4_board, won:bool):

        raise NotImplementedError

class HumanPlayer(Player):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = Agents.HumanPlayer

    def next_move(self, connect4_board):

        connect4_board.print_board()

        mv = self._next_move(connect4_board)

        connect4_board.delete_board_from_stdout()

        return mv

    def _next_move(self, connect4_board, prt_str=None):

        if prt_str is None:
            prt_str = self.color + 'Player {}\'s next move: '.format(self.no) + Fore.RESET

        try:
            inp = input(prt_str)
            stdout.write('\x1b[1A')
            stdout.write('\x1b[2K')

            move = int(inp)
            if not connect4_board.is_valid(move):
                raise ValueError
        except:
            handled = self._input_handler(inp=inp, connect4_board=connect4_board)
            if handled:
                exit()
            move = self._next_move(connect4_board, Fore.CYAN + 'Wrong input `{}`, please try again. '.format(inp) + self.color + 'Player {}\'s next move: '.format(self.no) + Fore.RESET)

        return move

    @staticmethod
    def _input_handler(inp, connect4_board):

        inp = inp.split(' ')
        if inp[0] == 'save' and len(inp) == 2:

            save_file = TinyDB(inp[1], storage=CachingMiddleware(JSONStorage))
            save_file.purge()
            save_file.insert({
                'fname': inp[1],
                'board': connect4_board.current_grid_state.tolist(),
                'player1': connect4_board.player1.type.value,
                'color1': connect4_board.player1.color,
                'player2': connect4_board.player2.type.value,
                'color2': connect4_board.player1.color,
                'current_player': connect4_board.current_player.no,
                'time_limit': connect4_board.player1.time_limit
            })
            save_file.close()

            return True

        elif inp[0] in ('exit', 'logout', 'end'):

            exit(Fore.GREEN + 'Sorry to see you go.' + Fore.RESET)

            return True

        return False

    def game_finished(self, connect4_board, won:bool):

        connect4_board.print_board()

        if won:
            print(self.color + 'Congratulations, player {}. you won.'.format(self.no) + Fore.RESET)
        else:
            print(Fore.CYAN + 'Good luck next time, player {}. you lost.'.format(self.no) + Fore.RESET)

class NetworkPlayer(Player):

    def __init__(self, **kwargs):
        super().__init__(self, **kwargs)
        self.type = Agents.NetworkPlayer

    def next_move(self, connect4_board):

        raise NotImplementedError

    def game_finished(self, connect4_board, won:bool):

        raise NotImplementedError

def RandomPlayer(**kwargs):

    raise NotImplementedError
