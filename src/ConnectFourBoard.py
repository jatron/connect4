from colorama import Fore, Back, Style
import numpy as np
from os import system
from connect4 import HumanPlayer,ComputerPlayer


def check_consecutive_indices(l):
    d = np.diff(l) == 1
    return sum(d) >= 3


def horizontal_four(grid):
    for row in grid:
        if len(np.nonzero(row)[0]) != 0:
            cnt_of_one = len(np.nonzero(row == 1)[0])  # get the number of occurrences of one
            cnt_of_two = len(np.nonzero(row == 2)[0])  # get the number of occurrences of two

            if cnt_of_one >= 4:
                y_indices = np.nonzero(row == 1)[0]
                if check_consecutive_indices(y_indices):
                    win_situation = True
                    return win_situation
                else:
                    continue
            elif cnt_of_two >= 4:
                y_indices = np.nonzero(row == 2)[0]
                if check_consecutive_indices(y_indices):
                    win_situation = True
                    return win_situation
                else:
                    continue
            else:
                continue
    return False


def vertical_four(grid):
    grid_transp = np.transpose(grid)
    return horizontal_four(grid_transp)

def diagonal_four(grid):
    # TODO
    pass


# for the print board function
def check_color(x):
    if x == 1:
        color = Fore.RED
    elif x == 2:
        color = Fore.YELLOW
    else:
        color = Fore.RESET
    return color


class ConnectFourBoard(object):
    '''
        Suppose the game is a numpy array of 6*7, initially all cells are filled with zeros
        when it's player 1's turn, a "1" is put into the cell
        when it's player 2's turn, a "2" is put into the cell
    '''

    def __init__(self, player1, player2, current_player, initial_state=None):
        self.player1 = HumanPlayer()
        self.player2 = ComputerPlayer()
        self.current_player = player1  # initially
        initial_state = np.zeros((6, 7), dtype=int)  # grid size of the connect four game is 6*7
        self.current_grid_state = initial_state  # All zeros
        self.next_move = None  # a number in the range [1,7] indicating the coloumn the player decides to play in
        self.game_ended = False  # becomes true when a winning state is found
        self.winner = None

    def check_board_for_a_win(self, current_grid_state):
        cnt_nonzero = len(np.nonzero(current_grid_state))
        if cnt_nonzero > 6:  # only at the seventh game does the probability of a win appear
            if (horizontal_four(current_grid_state)
                    or vertical_four(current_grid_state)
                    or diagonal_four(current_grid_state)):
                self.game_ended = True
                self.winner = self.current_player

    def toggle_players_and_get_next_move(self):
        # toggle players
        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1

        # get the next move (still to be improved/removed)
        print(Fore.GREEN + "It's player ", self.current_player, "\'s turn:")
        # prompting the user to enter their next move which is the number of coloumn at which they wish to play
        self.next_move = int(input())

    '''
    Board should look like this: (with red and yellow 'O's)

      1   2   3   4   5   6   7
    +---+---+---+---+---+---+---+
    |   +   +   +   +   +   +   |
    +---+---+---+---+---+---+---+
    |   +   +   +   +   +   +   |
    +---+---+---+---+---+---+---+
    |   +   +   +   +   +   +   |
    +---+---+---+---+---+---+---+
    |   +   +   +   +   + O +   |
    +---+---+---+---+---+---+---+
    |   +   +   +   + O + O +   |
    +---+---+---+---+---+---+---+
    |   +   +   + O + O + O +   |
    +---+---+---+---+---+---+---+
    '''

    def print_board(self):
        frame = "+---+---+---+---+---+---+---+"
        next_col_symbol = "|"
        print(Fore.BLUE + "  1   2   3   4   5   6   7")  # Number of columns
        print(frame)

        for x in range(0, 6):
            for y in range(0, 7):

                if y == 0:  # first col
                    print(next_col_symbol, end=" ")
                    next_col_symbol = "+"

                if self.current_grid_state[x, y] != 0:  # 1 or 2
                    current_color = check_color(self.current_grid_state[x, y])
                    print(current_color + 'O' + Fore.BLUE, end=" ")
                else:
                    print(" ", end=" ")

                if y != 6:
                    print(next_col_symbol, end=" ")
                else:
                    print("|")
                    next_col_symbol = "|"
            print(frame)

    def delete_board_from_stdout(self):
        system("clear")  # not sure if this is exactlty what we want
