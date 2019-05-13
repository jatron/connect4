from enum import Enum
from random import choice, randint
from sys import stdout
import datetime
import pickle

from colorama import Fore
from gevent.server import DatagramServer
from loguru import logger
from prompt_toolkit import PromptSession
from prompt_toolkit.application.current import get_app
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import InMemoryHistory
from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
import gevent
import numpy as np
import ujson as json


class Agents(Enum):

    ComputerPlayer = "COMPUTERPLAYER"
    HumanPlayer = "HUMANPLAYER"
    NetworkPlayer = "NETWORKPLAYER"


class Player(object):
    def __init__(self, no: int, time_limit: int = None, color=None):

        self.no = no

        if time_limit is None:
            self.time_limit = 180  # Seconds
        else:
            self.time_limit = time_limit

        if color is None:
            if self.no == 1:
                self.color = Fore.RED
            elif self.no == 2:
                self.color = Fore.YELLOW
            else:
                self.color = Fore.GREEN
        else:
            self.color = color

    def next_move(self, connect4_board):

        raise NotImplementedError

    def game_finished(self, connect4_board, won: bool):

        raise NotImplementedError


class ComputerPlayer(Player):
    def next_move(self, connect4_board):

        raise NotImplementedError

    def game_finished(self, connect4_board, won: bool):

        raise NotImplementedError


class HumanPlayer(Player):
    def next_move(self, connect4_board):

        connect4_board.print_board()

        self.start_time = datetime.datetime.now()
        self.time_remaining = self.time_limit
        self.prt_str = None
        command_completer = WordCompleter(
            ["exit", "logout", "end", "forfeit", "save savefile.c4"], ignore_case=True
        )
        history = InMemoryHistory()
        for msg in ["exit", "logout", "end", "forfeit", "save savefile.c4"]:
            history.append_string(msg)
        session = PromptSession(
            completer=command_completer,
            complete_while_typing=False,
            history=history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,
            erase_when_done=True,
        )
        mv = self._next_move(connect4_board=connect4_board, prm_session=session)

        connect4_board.delete_board_from_stdout()

        return mv

    def _next_move(self, connect4_board, prm_session):

        if self.prt_str is None:
            self.prt_str = (
                self.color + "Player {}'s next move: ".format(self.no) + Fore.RESET
            )

        try:
            inp = "-1"

            g = gevent.spawn(self._threaded_time_remaining)
            inp = prm_session.prompt(self._input_prompt, refresh_interval=0.5)

            if g.started:
                g.kill()

            if inp is None:
                inp = randint(1, 7)
                while not connect4_board.is_valid(inp):
                    inp = randint(1, 7)
                inp = str(inp)

            move = int(inp)
            if not connect4_board.is_valid(move):
                raise ValueError
        except:
            handled = self._input_handler(inp=inp, connect4_board=connect4_board)
            if handled:
                exit()
            self.prt_str = (
                Fore.CYAN
                + "Wrong input `{}`, please try again. ".format(inp)
                + self.color
                + "Player {}'s next move: ".format(self.no)
                + Fore.RESET
            )
            move = self._next_move(
                connect4_board=connect4_board, prm_session=prm_session
            )

        return move

    @staticmethod
    def _input_handler(inp, connect4_board):

        inp = inp.split(" ")
        if inp[0] == "save" and len(inp) == 2:

            if isinstance(connect4_board.player1, NetworkPlayer) or isinstance(
                connect4_board.player2, NetworkPlayer
            ):

                connect4_board.delete_board_from_stdout()
                print(Fore.RED + "You cannot save a network game." + Fore.RESET)
                connect4_board.print_board()

                return False

            save_file = TinyDB(inp[1], storage=CachingMiddleware(JSONStorage))
            save_file.purge()

            with open("{}.player".format(hash(connect4_board.player1)), "wb") as p1:
                pickle.dump(connect4_board.player1, p1)
            with open("{}.player".format(hash(connect4_board.player2)), "wb") as p2:
                pickle.dump(connect4_board.player2, p2)

            save_file.insert(
                {
                    "fname": inp[1],
                    "board": connect4_board.current_grid_state.tolist(),
                    "current_player": connect4_board.current_player.no,
                    "player1": "{}.player".format(hash(connect4_board.player1)),
                    "player2": "{}.player".format(hash(connect4_board.player2)),
                }
            )
            save_file.close()

            return True

        elif inp[0] in ("exit", "logout", "end", "forfeit"):

            exit(Fore.GREEN + "Sorry to see you go." + Fore.RESET)

            return True

        return False

    def _threaded_time_remaining(self):

        while self.time_remaining > 0:
            self.time_remaining = (
                self.time_limit - (datetime.datetime.now() - self.start_time).seconds
            )
            gevent.sleep(0)

        get_app().exit()

    def _input_prompt(self):

        r = ANSI("{} ".format(self.time_remaining) + self.prt_str)
        gevent.sleep(0)

        return r

    def game_finished(self, connect4_board, won: bool):

        connect4_board.print_board()

        if won:
            logger.bind(verbose=True).success("Player {} have won.".format(self.no))
            print(
                self.color
                + "Congratulations, player {}. you won.".format(self.no)
                + Fore.RESET
            )
        else:
            logger.bind(verbose=True).success("Player {} have lost.".format(self.no))
            print(
                Fore.CYAN
                + "Good luck next time, player {}. you lost.".format(self.no)
                + Fore.RESET
            )


class NetworkPlayer(Player):
    class Data(Enum):

        Null = None
        Move = "MV"
        Board = "BR"
        ResendBoard = "RB"
        Resend = "RS"
        Log = "LG"
        FinishedWin = "FW"
        FinishedLose = "FL"

    class Server(DatagramServer):
        def __init__(self, owner, *args, **kwargs):

            super(NetworkPlayer.Server, self).__init__(*args, **kwargs)

            self.owner = owner
            self.latest_recieved_board = None
            self.latest_recieved_move = None

        def handle(self, data, address):

            logger.debug("Recieved {} from {}.".format(data, address[0]))

            if address[0] == self.owner.peer_address:

                data = json.loads(data.decode())

                for elm in data:

                    latest_recieved_data = NetworkPlayer.Data(elm["type"])

                    if latest_recieved_data is NetworkPlayer.Data.Move:
                        self.latest_recieved_move = elm["content"]
                        logger.debug(
                            "Recieved {}:{}.".format(
                                latest_recieved_data, self.latest_recieved_move
                            )
                        )
                    elif latest_recieved_data is NetworkPlayer.Data.Board:
                        self.latest_recieved_board = np.array(elm["content"], dtype=int)
                        logger.debug(
                            "Recieved {}:\n{}.".format(
                                latest_recieved_data,
                                np.array(self.latest_recieved_board, dtype=int),
                            )
                        )
                    elif latest_recieved_data is NetworkPlayer.Data.ResendBoard:
                        NetworkPlayer.Server.send(
                            data=[
                                {
                                    "type": NetworkPlayer.Data.Board.value,
                                    "content": self.owner.latest_connect4_board,
                                }
                            ],
                            address=self.owner.peer_address,
                            port=self.owner.peer_port,
                        )
                    elif latest_recieved_data is NetworkPlayer.Data.Resend:
                        NetworkPlayer.Server.send(
                            data=self.owner.latest_sent_message,
                            address=self.owner.peer_address,
                            port=self.owner.peer_port,
                        )
                    elif latest_recieved_data is NetworkPlayer.Data.Log:
                        logger.bind(verbose=True).info("```" + elm["content"] + "```")
                    elif latest_recieved_data in (
                        NetworkPlayer.Data.Null,
                        NetworkPlayer.Data.FinishedWin,
                        NetworkPlayer.Data.FinishedLose,
                    ):
                        pass

        @staticmethod
        def send(data, address, port):

            data = json.dumps(data).encode()

            sock = gevent.socket.socket(type=gevent.socket.SOCK_DGRAM)
            sock.connect((address, port))
            sock.send(data)
            sock.close()

    def __init__(self, peer_address, peer_port=3500, local_port=3500, *args, **kwargs):

        super(NetworkPlayer, self).__init__(*args, **kwargs)

        self.latest_connect4_board = None

        self.peer_address = peer_address
        self.peer_port = peer_port
        self.server = NetworkPlayer.Server(
            listener=":{}".format(local_port), owner=self
        )
        self.server.start()
        self.latest_sent_message = [
            {"type": NetworkPlayer.Data.Null.value, "content": None}
        ]

    def next_move(self, connect4_board):

        self.latest_connect4_board = connect4_board.current_grid_state.tolist()

        self.latest_sent_message = [
            {
                "type": NetworkPlayer.Data.Move.value,
                "content": connect4_board.latest_move,
            },
            {
                "type": NetworkPlayer.Data.Board.value,
                "content": self.latest_connect4_board,
            },
        ]

        NetworkPlayer.Server.send(
            data=self.latest_sent_message,
            address=self.peer_address,
            port=self.peer_port,
        )

        connect4_board.print_board()
        print(
            self.color + "Waiting for player{}'s response".format(self.no) + Fore.RESET
        )

        while True:
            while self.server.latest_recieved_move is None:
                gevent.sleep(0)

            nxt_mv = self.server.latest_recieved_move
            self.server.latest_recieved_move = None
            if connect4_board.is_valid(nxt_mv):
                break

        stdout.write("\x1b[1A")
        stdout.write("\x1b[2K")
        connect4_board.delete_board_from_stdout()

        return nxt_mv

    def game_finished(self, connect4_board, won: bool):

        self.latest_connect4_board = connect4_board.current_grid_state.tolist()

        self.latest_sent_message = [
            {"type": NetworkPlayer.Data.Null.value, "content": None},
            {
                "type": NetworkPlayer.Data.Move.value,
                "content": connect4_board.latest_move,
            },
            {
                "type": NetworkPlayer.Data.Board.value,
                "content": self.latest_connect4_board,
            },
        ]

        if won:
            logger.bind(verbose=True).success("Player {} have won.".format(self.no))
            self.latest_sent_message[0]["type"] = NetworkPlayer.Data.FinishedLose.value
        else:
            logger.bind(verbose=True).success("Player {} have lost.".format(self.no))
            self.latest_sent_message[0]["type"] = NetworkPlayer.Data.FinishedWin.value

        self.server.send(
            data=self.latest_sent_message,
            address=self.peer_address,
            port=self.peer_port,
        )


def RandomPlayer(*args, **kwargs):

    return choice([ComputerPlayer])(*args, **kwargs)


agents = {
    Agents.ComputerPlayer: ComputerPlayer,
    Agents.HumanPlayer: HumanPlayer,
    Agents.NetworkPlayer: NetworkPlayer,
}
