from colorama import Fore, Back, Style
import numpy as np
from os import system
from .agents import HumanPlayer, ComputerPlayer


# for the print board function
def check_color(x):
    if x == 1:
        color = Fore.RED
    elif x == 2:
        color = Fore.YELLOW
    else:
        color = Fore.RESET
    return color


def check_consecutive_indices(l):
    d = np.diff(l) == 1
    return sum(d) >= 3


# returns True if there're 4 consecutive 1's or 2's (hence if a player wins)
def check_win_from_row(row):
    if len(np.nonzero(row)[0]) != 0:
        cnt_of_one = len(np.nonzero(row == 1)[0])  # get the number of occurrences of one
        cnt_of_two = len(np.nonzero(row == 2)[0])  # get the number of occurrences of two

        if cnt_of_one >= 4:
            y_indices = np.nonzero(row == 1)[0]
            if check_consecutive_indices(y_indices):
                win_situation = True
                return win_situation

        elif cnt_of_two >= 4:
            y_indices = np.nonzero(row == 2)[0]
            if check_consecutive_indices(y_indices):
                win_situation = True
                return win_situation
        else:
            return False
    else:
        return False


def check_diagonal_four(grid, min_range, max_range):
    for offset in range(min_range, max_range):
        current_diag = np.diagonal(grid, offset)
        if check_win_from_row(current_diag):
            return True
    return False


# returns True for horizontal connect 4 winning state
def horizontal_four(grid):
    for row in grid:
        if check_win_from_row(row):
            return True
    return False


# returns True for vertical connect 4 winning state
def vertical_four(grid):
    grid_transp = np.transpose(grid)
    return horizontal_four(grid_transp)


# returns True for diagonal connect 4 winning state
def diagonal_four(grid):
    # Check for the -45 degree diagonals
    if check_diagonal_four(grid, -2, 3):  # from -2->3 thus excluding diagonals with less than 4 cells
        return True
    # Check for the +45 degree diagonals
    elif check_diagonal_four(np.fliplr(grid), -2, 3):
        return True
    else:
        return False


def move_is_valid(column_num):
    if 1 <= column_num <= 7:
        return True
    else:
        print(Fore.RED + "Wrong choice of coloumn!")


def get_row_for_move(column_num, grid):
    column_arr = grid[:, column_num - 1]
    non_zero_indices = np.nonzero(column_arr)[0]
    if len(non_zero_indices) is not 0:
        row_index = non_zero_indices[len(non_zero_indices) - 1]  # The last non zero element
    else:  # Column is already full
        row_index = -1  # A flag meaning col is already full hence it's a wasted move
    return row_index


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

    #  returns True if a winning state was found and sets the winner to the current player as well as a game ended flag
    def check_board_for_a_win(self, current_grid_state):
        cnt_nonzero = len(np.nonzero(current_grid_state)[0])
        if cnt_nonzero > 6:  # only at the seventh game does the probability of a win appear
            if (horizontal_four(current_grid_state)
                    or vertical_four(current_grid_state)
                    or diagonal_four(current_grid_state)):
                self.game_ended = True
                self.winner = self.current_player
                return True
            else:
                return False
        else:
            return False

    def make_move(self, column_num):
        if move_is_valid(column_num):
            if self.current_player == self.player1:
                disk_to_be_inserted = 1
            else:
                disk_to_be_inserted = 2

            row_index = get_row_for_move(column_num, self.current_grid_state)
            if row_index != -1:
                self.current_grid_state[row_index][column_num - 1] = disk_to_be_inserted
            else:
                print(Fore.RED + "This column is already full! :o")

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
