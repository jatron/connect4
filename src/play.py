__doc__ = """
Play connect four in the comfort of your terminal.

Player types are COMPUTERPLAYER, HUMANPLAYER, and NETWORKPLAYER

Usage:
  play.py load <savefile> [--log-steps=FILE] [--verbose]
  play.py players <type> <type> [--time-limit=TIMEINSECONDS] [--log-steps=FILE] [--verbose] [--networked] [--local-port=PORT] [--peer-address=ADDRESS] [--peer-port=PORT]
  play.py (-h | --help)

Options:
  -h --help                   Show this screen.
  --time-limit=TIMEINSECONDS  Maximum allowed time per player move in seconds [default: 180].
  --log-steps=FILE            Save game log to a file.
  --local-port=PORT           Local port [default: 3500].
  --peer-address=ADDRESS      Peer player's IP address.
  --peer-port=PORT            Peer player's port [default: 3500].
  -v --verbose                Turn on debugging data.
"""


from colorama import Fore
from docopt import docopt
from loguru import logger
from tinydb import TinyDB, Query
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
import numpy as np

from game.board import ConnectFourBoard
from game.agents import Agents, ComputerPlayer, HumanPlayer, NetworkPlayer, RandomPlayer, agents


if __name__ == '__main__':

    args = docopt(__doc__)

    if not args['--verbose']:
        logger.remove(0)

    if args['--log-steps'] is not None:
        logger.add(args['--log-steps'], filter=lambda record: "to_file" in record["extra"])

    try:
        time_limit = int(args['--time-limit'])
    except:
        logger.error('Time limit must be an int value.')
        exit(Fore.RED + 'Time limit must be an int value.' + Fore.RESET)

    try:
        local_port = int(args['--local-port'])
    except:
        logger.error('Local port must be an int value.')
        exit(Fore.RED + 'Local port must be an int value.' + Fore.RESET)

    try:
        peer_port = int(args['--peer-port'])
    except:
        logger.error('Peer port must be an int value.')
        exit(Fore.RED + 'Peer port must be an int value.' + Fore.RESET)

    if args['load']:

        db = TinyDB(args['<savefile>'], storage=CachingMiddleware(JSONStorage))
        q = Query()
        data = db.get(q.fname==args['<savefile>'])

        player1 = agents[Agents(data['player1'])](no=1, time_limit=data['time_limit'], color=data['color1'])
        player2 = agents[Agents(data['player2'])](no=2, time_limit=data['time_limit'], color=data['color2'])
        if data['current_player'] == 1: ## TODO, Fix numbering
            current_player = player2
        else:
            current_player = player1
        initial_state = np.array(data['board'], dtype=int)

        db.close()

        ConnectFourBoard(player1=player1, player2=player2, current_player=current_player, initial_state=initial_state)

    elif args['players']:

        try:

            player1, player2= Agents(args['<type>'][0]), Agents(args['<type>'][1])

            if player1 is Agents.NetworkPlayer and player2 is Agents.NetworkPlayer:
                logger.error('You must have at lease one local player.')
                exit(Fore.RED + 'You must have at lease one local player.' + Fore.RESET)
            elif player1 is Agents.NetworkPlayer or player2 is Agents.NetworkPlayer:
                if args['--peer-address'] is None:
                    logger.error('You must enter the peer player\'s IP address to play a network game.')
                    exit(Fore.RED + 'You must enter the peer player\'s IP address to play a network game.' + Fore.RESET)

                if player1 is Agents.NetworkPlayer:
                    player1 = agents[player1](no=1, time_limit=time_limit, local_port=local_port, peer_address=args['--peer-address'], peer_port=peer_port)
                    player2 = agents[player2](no=2, time_limit=time_limit)
                elif player2 is Agents.NetworkPlayer:
                    player1 = agents[player1](no=1, time_limit=time_limit)
                    player2 = agents[player2](no=2, time_limit=time_limit, local_port=local_port, peer_address=args['--peer-address'], peer_port=peer_port)
            else:
                player1 = agents[player1](no=1, time_limit=time_limit)
                player2 = agents[player2](no=2, time_limit=time_limit)

        except:
            exit(__doc__)

        ConnectFourBoard(player1=player1, player2=player2)
