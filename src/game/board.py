from sys import stdout

from colorama import Fore, Back, Style
import numpy as np


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
    cnt = 0
    for i in range(0, len(d)):  # [True True False True] for example --> should return False
        if d[i] == 1:
            cnt = cnt + 1
        else:
            cnt = 0

    if cnt >= 3:
        return True
    else:
        return False


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


class ConnectFourBoard(object):
    '''
        Suppose the game is a numpy array of 6*7, initially all cells are filled with zeros
        when it's player 1's turn, a "1" is put into the cell
        when it's player 2's turn, a "2" is put into the cell
    '''

    def __init__(self, player1, player2, current_player=None, initial_state=None):
        self.player1 = player1
        self.player2 = player2

        if current_player is None:
            current_player = player1  # initially
        self.current_player = current_player

        if initial_state is None:
            initial_state = np.zeros((6, 7), dtype=int)  # grid size of the connect four game is 6*7
        self.current_grid_state = initial_state  # All zeros

        self.latest_move = None

    def copy(self):
        return ConnectFourBoard(player1=self.player1, player2=self.player2, current_player=self.current_player,
                                initial_state=self.current_grid_state.copy())

    def start_game_loop(self):
        tie = False
        while not self.is_finished():
            if self.is_full():  # game not finished (no one won) but grid is all full
                tie = True
                break
            else:
                move = self._get_next_move()
                if self.is_valid(move):
                    self.make_move(move)
                    self.latest_move = move
                    self.toggle_players()
        if not tie:
            if self.current_player == self.player2:
                self.player1.game_finished(connect4_board=self, won=True)
                self.player2.game_finished(connect4_board=self, won=False)

            elif self.current_player == self.player1:
                self.player1.game_finished(connect4_board=self, won=False)
                self.player2.game_finished(connect4_board=self, won=True)
        else:
            print(Fore.WHITE + "It's a tie, no one won!" + Fore.RESET)

    def is_finished(self):

        cnt_nonzero = len(np.nonzero(self.current_grid_state)[0])

        if cnt_nonzero > 6:  # only at the seventh game does the probability of a win appear
            if (horizontal_four(self.current_grid_state)
                    or vertical_four(self.current_grid_state)
                    or diagonal_four(self.current_grid_state)):
                return True
        return False

    def is_full(self):
        cnt_nonzero = len(np.nonzero(self.current_grid_state)[0])
        if cnt_nonzero == 6 * 7:
            return True

    def is_winning_move(self, move):

        fake_board = self.current_grid_state.copy()
        fake_board[self.get_height(move)][move - 1] = self.current_player.no
        cnt_nonzero = len(np.nonzero(fake_board)[0])
        if cnt_nonzero > 6:  # only at the seventh game does the probability of a win appear
            if (horizontal_four(fake_board)
                    or vertical_four(fake_board)
                    or diagonal_four(fake_board)):
                return True

        return False

    def toggle_players(self):

        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1

    def make_move(self, move):

        for row in range(5, -1, -1):
            if self.current_grid_state[row][move - 1] == 0:
                self.current_grid_state[row][move - 1] = self.current_player.no
                break

    def _get_next_move(self):

        return self.current_player.next_move(self)

    #  returns True if a winning state was found and sets the winner to the current player as well as a game ended flag
    def check_board_for_a_win(self, current_grid_state):
        cnt_nonzero = len(np.nonzero(self.current_grid_state)[0])
        if cnt_nonzero > 6:  # only at the seventh game does the probability of a win appear
            if (horizontal_four(self.current_grid_state)
                    or vertical_four(self.current_grid_state)
                    or diagonal_four(self.current_grid_state)):
                self.game_ended = True
                self.winner = self.current_player
                if self.current_player == self.player1:
                    self.player1.game_finished(connect4_board=self, won=True)
                    self.player2.game_finished(connect4_board=self, won=False)
                elif self.current_player == self.player2:
                    self.player1.game_finished(connect4_board=self, won=False)
                    self.player2.game_finished(connect4_board=self, won=True)
                return True
        self.toggle_players_and_get_next_move()
        return False

    def toggle_players_and_get_next_move(self):
        # toggle players
        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1

        # get the next move (still to be improved/removed)
        # print(Fore.GREEN + "It's player ", self.current_player, "\'s turn:")
        # prompting the user to enter their next move which is the number of coloumn at which they wish to play
        self.next_move = self.current_player.next_move(self)
        for row in range(5, -1, -1):
            if self.current_grid_state[row][self.next_move - 1] == 0:
                self.current_grid_state[row][self.next_move - 1] = self.current_player.no
                break
        self.check_board_for_a_win()

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
        for i in range(14):
            stdout.write('\x1b[1A')
            stdout.write('\x1b[2K')

    def get_height(self, column):
        grid_transp = np.transpose(self.current_grid_state)
        d = len(np.nonzero(grid_transp[column - 1])[0])
        return d

    def is_valid(self, move):
        if self.current_grid_state[0][move - 1] == 0:
            return True
        return False
