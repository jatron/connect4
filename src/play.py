from argparse import ArgumentParser

from colorama import Fore
from loguru import logger
from tinydb import TinyDB, Query
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
import numpy as np

from .game.board import ConnectFourBoard
from .game.agents import Agents, ComputerPlayer, HumanPlayer, NetworkPlayer, RandomPlayer


if __name__ == '__main__':

    parser = ArgumentParser(description='Play connect four in the comfort of your terminal.')
    parser.add_argument('--load', '-l', type=str, help='Load saved game from a file.')
    parser.add_argument('--time-limit', '-t', type=int, default=180, help='Maximum allowed time per player move.')
    parser.add_argument('--networking', '-n', action='store_true', help='Use the network to play.')
    parser.add_argument('--debugging', '-d', action='store_true', help='Turn on debugging data.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show addition output data.')
    parser.add_argument('--pvp', '-pvp', action='store_true', help='Player vs player.')
    parser.add_argument('--pvc', '-pvc', action='store_true', help='Player vs computer.')
    parser.add_argument('--cvc', '-cvc', action='store_true', help='Computer vs computer.')
    args = parser.parse_args()

    if not args.debugging:
        logger.disable('__main__')

    if args.load is not None:

        db = TinyDB(args.load, storage=CachingMiddleware(JSONStorage))
        q = Query()
        data = db.get(q.fname==args.load)

        agents = {
            Agents.ComputerPlayer: ComputerPlayer,
            Agents.HumanPlayer: HumanPlayer,
            Agents.NetworkPlayer: NetworkPlayer,
        }
        player1 = agents[Agents(data['player1'])](no=1, time_limit=data['time_limit'], color=data['color1'])
        player2 = agents[Agents(data['player2'])](no=2, time_limit=data['time_limit'], color=data['color2'])
        if data['current_player'] == 1: ## TODO, Fix numbering
            current_player = player2
        else:
            current_player = player1
        initial_state = np.array(data['board'], dtype=int)

        db.close()

        ConnectFourBoard(player1=player1, player2=player2, current_player=current_player, initial_state=initial_state)


    if args.pvp ^ args.pvc ^ args.cvc:
        if args.pvp and args.pvc and args.cvc:
            logger.error('You must choose exactly one of the pvp, pvc, or cvc options.')
            exit(Fore.RED + 'You must choose exactly one of the pvp, pvc, or cvc options.' + Fore.RESET)
    else:
        logger.error('You must choose exactly one of the pvp, pvc, or cvc options.')
        exit(Fore.RED + 'You must choose exactly one of the pvp, pvc, or cvc options.' + Fore.RESET)


    if args.pvp:
        if args.networking:
            pass
        else:
            ConnectFourBoard(player1=HumanPlayer(no=1, time_limit=args.time_limit), player2=HumanPlayer(no=2, time_limit=args.time_limit))
    elif args.pvc:
        if args.networking:
            pass
        else:
            pass
    elif args.cvc:
        if args.networking:
            pass
        else:
            pass
