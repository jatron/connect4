from enum import Enum
from random import Random
from sys import stdout
from time import sleep
import json

from colorama import Fore
from gevent.server import DatagramServer
from gevent import socket
from loguru import logger
from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
import numpy as np


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
            logger.bind(to_file=True).success('Player {} have won.'.format(self.no))
            print(self.color + 'Congratulations, player {}. you won.'.format(self.no) + Fore.RESET)
        else:
            logger.bind(to_file=True).success('Player {} have lost.'.format(self.no))
            print(Fore.CYAN + 'Good luck next time, player {}. you lost.'.format(self.no) + Fore.RESET)

class NetworkPlayer(Player):

    class Data(Enum):

        Null = None
        Move = 'MV'
        Board = 'BR'
        ResendBoard = 'RB'
        Resend = 'RS'
        Log = 'LG'
        FinishedWin = 'FW'
        FinishedLose = 'FL'

    class Server(DatagramServer):

        def __init__(self, owner, **kwargs):

            super().__init__(self, **kwargs)

            self.owner = owner
            self.latest_recieved_board = None
            self.latest_recieved_move = None

        def handle(self, data, address):

            logger.debug('Recieved {} from {}.'.format(data, address[0]))

            if address == self.owner.peer_address:

                data = json.loads(data.decode())

                for elm in data:

                    latest_recieved_data = NetworkPlayer.Data(elm['type'])
                    if latest_recieved_data is NetworkPlayer.Data.Move:
                        self.latest_recieved_move = elm['content']
                    elif latest_recieved_data is NetworkPlayer.Data.Board:
                        self.latest_recieved_board = np.array(elm['content'], dtype=int)
                    elif latest_recieved_data is NetworkPlayer.Data.ResendBoard:
                        NetworkPlayer.Server.send(
                            data=[{
                                'type': NetworkPlayer.Data.Board,
                                'content': self.owner.latest_connect4_board
                            }],
                            address=self.owner.peer_address,
                            port=self.owner.peer_port
                        )
                    elif latest_recieved_data is NetworkPlayer.Data.Resend:
                        NetworkPlayer.Server.send(
                            data=self.owner.latest_sent_message,
                            address=self.owner.peer_address,
                            port=self.owner.peer_port
                        )
                    elif latest_recieved_data is NetworkPlayer.Data.Log:
                        logger.bind(to_file=True).info('```' + elm['content'] + '```')
                    elif latest_recieved_data is NetworkPlayer.Data.FinishedWin:
                        logger.bind(to_file=True).success('Player {} have won.'.format(self.owner.no))
                        print(self.owner.color + 'Congratulations, player {}. you won.'.format(self.owner.no) + Fore.RESET)
                    elif latest_recieved_data is NetworkPlayer.Data.FinishedLose:
                        logger.bind(to_file=True).success('Player {} have lost.'.format(self.owner.no))
                        print(Fore.CYAN + 'Good luck next time, player {}. you lost.'.format(self.owner.no) + Fore.RESET)

                self.stop()
                self.start()

        @staticmethod
        def send(data, address, port):

            data = json.dumps(data).encode()

            sock = socket.socket(type=socket.SOCK_DGRAM)
            sock.connect((address, port))
            sock.send(data)
            sock.close()

    def __init__(self, peer_address='127.0.0.1', peer_port=3500, local_port=3500, **kwargs):

        super().__init__(self, **kwargs)

        self.type = Agents.NetworkPlayer
        self.latest_connect4_board = None

        self.peer_address = peer_address
        self.peer_port = peer_address
        self.server = NetworkPlayer.Server(listener=':{}'.format(local_port), owner=self)
        self.server.start()
        self.latest_sent_message = [{
            'type': NetworkPlayer.Data.Null,
            'content': None
        }]

    def next_move(self, connect4_board):

        self.latest_connect4_board = connect4_board.tolist()

        self.latest_sent_message = [
            {
                'type': NetworkPlayer.Data.Move,
                'content': connect4_board.next_move
            },
            {
                'type': NetworkPlayer.Data.Board,
                'content': self.latest_connect4_board
            }
        ]

        NetworkPlayer.Server.send(data=self.latest_sent_message, address=self.peer_address, port=self.peer_port)

        while self.server.latest_recieved_move is None:
            self.server.serve_forever()

        nxt_mv = self.server.latest_recieved_move
        self.server.latest_recieved_move = None

        return nxt_mv

    def game_finished(self, connect4_board, won:bool):

        self.latest_connect4_board = connect4_board.tolist()

        self.latest_sent_message = [
            {
                'type': NetworkPlayer.Data.Null,
                'content': None
            },
            {
                'type': NetworkPlayer.Data.Move,
                'content': connect4_board.next_move
            },
            {
                'type': NetworkPlayer.Data.Board,
                'content': self.latest_connect4_board
            }
        ]

        if won:
            logger.bind(to_file=True).success('Player {} have lost.'.format(self.no))
            print(self.color + 'Congratulations, player {}. you won.'.format(self.no) + Fore.RESET)
            self.latest_sent_message[0]['type'] = NetworkPlayer.Data.FinishedLose
        else:
            logger.bind(to_file=True).success('Player {} have lost.'.format(self.no))
            print(Fore.CYAN + 'Good luck next time, player {}. you lost.'.format(self.no) + Fore.RESET)
            self.latest_sent_message[0]['type'] = NetworkPlayer.Data.FinishedWin


def RandomPlayer(**kwargs):

    raise NotImplementedError


agents = {
    Agents.ComputerPlayer: ComputerPlayer,
    Agents.HumanPlayer: HumanPlayer,
    Agents.NetworkPlayer: NetworkPlayer
}
