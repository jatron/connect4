from argparse import ArgumentParser

from colorama import Fore
from loguru import logger

from game import ConnectFour, HumanPlayer


if __name__ == '__main__':

    parser = ArgumentParser(description='Play connect four in the comfort of your terminal.')
    parser.add_argument('--load', '-l', type=str, help='Load saved game from a file.')
    parser.add_argument('--time-limit', '-t', type=int, help='Maximum allowed time per player move.')
    parser.add_argument('--networking', '-n', action='store_true', help='Use the network to play.')
    parser.add_argument('--debugging', '-d', action='store_true', help='Turn on debugging data.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show addition output data.')
    parser.add_argument('--pvp', '-pvp', action='store_true', help='Player vs player.')
    parser.add_argument('--pvc', '-pvc', action='store_true', help='Player vs computer.')
    parser.add_argument('--cvc', '-cvc', action='store_true', help='Computer vs computer.')
    args = parser.parse_args()

    if not args.debugging:
        logger.disable('__main__')

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
            pass
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
