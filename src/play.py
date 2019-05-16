__doc__ = """
Play connect four in the comfort of your terminal.

Player types are HUMANPLAYER, NETWORKPLAYER, and MINIMAXPLAYER.
Player difficulties are HARD, NORMAL, and EASY.
Ports and address are only used in network games.
Player difficulties are only used in case of using an AI.
When playing as a HUMANPLAYER, you can input `save <savefile>` to save the game and exit your client or `exit` to exit your client.

Usage:
  play.py [--debugging] [--verbose] load <savefile>
  play.py [--time-limit=TIMEINSECONDS]
          [--local-port=PORT] [--peer-address=ADDRESS] [--peer-port=PORT]
          [--debugging] [--verbose]
          [--p1-difficulty=DIFFICULTY] [--p2-difficulty=DIFFICULTY]
          <playertype> vs <playertype>
  play.py (-h | --help)

Options:
  -h --help                   Show this screen.
  --time-limit=TIMEINSECONDS  Maximum allowed time per player move in seconds [default: 180].
  --local-port=PORT           Local port [default: 3500].
  --peer-address=ADDRESS      Peer player's IP address.
  --peer-port=PORT            Peer player's port [default: 3500].
  --p1-difficulty=DIFFICULTY  First player difficulty [default: NORMAL].
  --p2-difficulty=DIFFICULTY  Second player difficulty [default: NORMAL].
  -d --debugging              Save debugging log.
  -v --verbose                Turn on verbose output mode.
"""


from sys import exit, stdout
import pickle
import platform

from colorama import Fore, init
from docopt import docopt
from loguru import logger
from tinydb import Query, TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
import numpy as np

from game.agents import Agents, Difficulty, RandomPlayer, agents
from game.board import ConnectFourBoard


if __name__ == "__main__":

    if platform.system() == 'Windows':
        init(convert=True)

    args = docopt(__doc__)

    logger.remove(0)

    if args["--verbose"]:
        logger.add(stdout, filter=lambda record: "verbose" in record["extra"])

    if args["--debugging"]:
        logger.add(
            "debug{time}.log", filter=lambda record: "verbose" not in record["extra"]
        )

    try:
        time_limit = int(args["--time-limit"])
    except:
        logger.error("Time limit must be an int value.")
        exit(Fore.RED + "Time limit must be an int value." + Fore.RESET)

    try:
        local_port = int(args["--local-port"])
    except:
        logger.error("Local port must be an int value.")
        exit(Fore.RED + "Local port must be an int value." + Fore.RESET)

    try:
        peer_port = int(args["--peer-port"])
    except:
        logger.error("Peer port must be an int value.")
        exit(Fore.RED + "Peer port must be an int value." + Fore.RESET)

    if args["load"]:

        db = TinyDB(args["<savefile>"], storage=CachingMiddleware(JSONStorage))
        q = Query()
        data = db.get(q.fname == args["<savefile>"])

        with open(data["player1"], "rb") as p1:
            player1 = pickle.load(p1)
        with open(data["player2"], "rb") as p2:
            player2 = pickle.load(p2)

        if data["current_player"] == 1:
            current_player = player1
        else:
            current_player = player2
        initial_state = np.array(data["board"], dtype=int)

        db.close()

        ConnectFourBoard(
            player1=player1,
            player2=player2,
            current_player=current_player,
            initial_state=initial_state,
        ).start_game_loop()

    elif args["vs"]:

        try:

            player1, player2 = (
                Agents(args["<playertype>"][0]),
                Agents(args["<playertype>"][1]),
            )

            try:
                if player1 not in [Agents.HumanPlayer, Agents.NetworkPlayer]:
                    diff1 = Difficulty(args["--p1-difficulty"])
                    diff2 = Difficulty(args["--p2-difficulty"])
                elif player2 not in [Agents.HumanPlayer, Agents.NetworkPlayer]:
                    diff1 = Difficulty(args["--p1-difficulty"])
                    diff2 = Difficulty(args["--p2-difficulty"])
            except:
                logger.error("You must enter a correct difficulty.")
                raise ValueError

            if player1 is Agents.NetworkPlayer and player2 is Agents.NetworkPlayer:
                logger.error("You must have at lease one local player.")
                raise ValueError
            elif player1 is Agents.NetworkPlayer or player2 is Agents.NetworkPlayer:
                if args["--peer-address"] is None:
                    logger.error(
                        "You must enter the peer player's IP address to play a network game."
                    )
                    raise ValueError

                if player1 is Agents.NetworkPlayer:
                    player1 = agents[player1](
                        local_port=local_port,
                        peer_address=args["--peer-address"],
                        peer_port=peer_port,
                        no=1,
                        time_limit=time_limit,
                    )
                    player2 = agents[player2](no=2, time_limit=time_limit)
                elif player2 is Agents.NetworkPlayer:
                    player1 = agents[player1](no=1, time_limit=time_limit)
                    player2 = agents[player2](
                        local_port=local_port,
                        peer_address=args["--peer-address"],
                        peer_port=peer_port,
                        no=2,
                        time_limit=time_limit,
                    )
            elif player1 not in [
                Agents.HumanPlayer,
                Agents.NetworkPlayer,
            ] and player2 not in [Agents.HumanPlayer, Agents.NetworkPlayer]:
                player1 = agents[player1](no=1, time_limit=time_limit, difficulty=diff1)
                player2 = agents[player2](no=2, time_limit=time_limit, difficulty=diff2)
            elif player1 not in [Agents.HumanPlayer, Agents.NetworkPlayer]:
                player1 = agents[player1](no=1, time_limit=time_limit, difficulty=diff1)
                player2 = agents[player2](no=2, time_limit=time_limit)
            elif player2 not in [Agents.HumanPlayer, Agents.NetworkPlayer]:
                player1 = agents[player1](no=1, time_limit=time_limit)
                player2 = agents[player2](no=2, time_limit=time_limit, difficulty=diff2)
            else:
                player1 = agents[player1](no=1, time_limit=time_limit)
                player2 = agents[player2](no=2, time_limit=time_limit)

        except:
            print(
                Fore.RED
                + "You must have at lease one local player.\nYou must enter a correct difficulty.\nYou must enter the peer player's IP address to play a network game."
                + Fore.RESET
            )
            exit(__doc__)

        ConnectFourBoard(player1=player1, player2=player2).start_game_loop()
