from colorama import Fore
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


class ConnectFourBoard(object):
    """
        Suppose the game is a numpy array of 6*7, initially all cells are filled with zeros
        when it's player 1's turn, a "1" is put into the cell
        when it's player 2's turn, a "2" is put into the cell
    """

    def __init__(self, player1, player2, current_player=None, initial_state=None):
        self.player1 = player1
        self.player2 = player2

        if current_player is None:
            current_player = player1  # initially
        self.current_player = current_player

        if initial_state is None:
            initial_state = np.zeros(
                (6, 7), dtype=int
            )  # grid size of the connect four game is 6*7
        self.current_grid_state = initial_state  # All zeros

        self.latest_move = None

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

    def toggle_players(self):

        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1

    def _get_next_move(self):

        return self.current_player.next_move(self)

    def make_move(self, move):

        for row in range(5, -1, -1):
            if self.current_grid_state[row][move - 1] == 0:
                self.current_grid_state[row][move - 1] = self.current_player.no
                break

    @staticmethod
    def _row_streak(row, player_no, streak):

        score = 0

        if len(row) >= streak:
            for i in range(len(row) - streak + 1):
                true_streak = True
                for no in range(streak):
                    if row[i + no] != player_no:
                        true_streak = False
                        break
                if true_streak:
                    score += 1

        return score

    @staticmethod
    def _diag_streak(board, player_no, streak):

        """Gets the -ve sloop diagonals of the input board and checks it for streaks

        Returns:
            int -- number of streaks in the diagonals of the given board
        """

        score = 0

        for i in range(0, -len(board), -1):
            score += ConnectFourBoard._row_streak(
                np.diagonal(board, i), player_no, streak
            )
        for i in range(1, len(board[0])):
            score += ConnectFourBoard._row_streak(
                np.diagonal(board, i), player_no, streak
            )

        return score

    @staticmethod
    def _total_diag_streak(board, player_no, streak):

        return ConnectFourBoard._diag_streak(
            board, player_no, streak
        ) + ConnectFourBoard._diag_streak(np.flip(board, 1), player_no, streak)

    @staticmethod
    def _horz_streak(board, player_no, streak):

        score = 0

        for i in range(len(board)):
            score += ConnectFourBoard._row_streak(board[i], player_no, streak)

        return score

    @staticmethod
    def _vert_streak(board, player_no, streak):

        return ConnectFourBoard._horz_streak(np.transpose(board), player_no, streak)

    def streak(self, player_no, streak):

        board = self.current_grid_state

        return (
            ConnectFourBoard._total_diag_streak(board, player_no, streak)
            + ConnectFourBoard._horz_streak(board, player_no, streak)
            + ConnectFourBoard._vert_streak(board, player_no, streak)
        )

    def is_valid(self, move):
        if self.current_grid_state[0][move - 1] == 0:
            return True
        return False

    def is_full(self):

        cnt_nonzero = len(np.nonzero(self.current_grid_state)[0])

        if cnt_nonzero == 6 * 7:
            return True

    def is_finished(self):

        if self.current_player == self.player1:
            if self.streak(self.player2.no, 4):
                return True
        elif self.current_player == self.player2:
            if self.streak(self.player1.no, 4):
                return True

        return False

    def copy(self):
        return ConnectFourBoard(
            player1=self.player1,
            player2=self.player2,
            current_player=self.current_player,
            initial_state=self.current_grid_state.copy(),
        )

    """
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
    """

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
                    print(current_color + "O" + Fore.BLUE, end=" ")
                else:
                    print(" ", end=" ")

                if y != 6:
                    print(next_col_symbol, end=" ")
                else:
                    print("|")
                    next_col_symbol = "|"
            print(frame)
        print(Fore.RESET, end="")

    def delete_board_from_stdout(self):
        for _ in range(14):
            print("\x1b[1A", end="")
            print("\x1b[2K", end="")
