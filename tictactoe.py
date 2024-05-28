import tkinter as tk

from tkinter import font
from dataclasses import dataclass
from itertools import cycle

@dataclass
class Player:
    username: str
    label: str
    colour: str

@dataclass
class Move:
    row: int
    column: int
    label: str = ""

BOARD_SIZE = int(input('Введите размерность доски: '))
DEFAULT_PLAYERS = (
    Player(username=input('Введите имя игрока: '), label="х", colour="cyan"),
    Player(username=input('Введите имя игрока: '), label="о", colour="pink"),
)

class TicTacToe:
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self.board_size = board_size
        self._players = cycle(players)
        self.cur_player = next(self._players)
        self._cur_moves = []
        self._win_conditions = []
        self.win_combo = []
        self._has_winner = False
        self._setup_board()

    def _setup_board(self):
        self._cur_moves = [
            [Move(row, column) for column in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._win_conditions = self._get_win()

    def _get_win(self):
        rows = [
            [(move.row, move.column) for move in row]
            for row in self._cur_moves
        ]
        columns = [
            [(row[i].row, i) for row in self._cur_moves] for i in range(self.board_size)
        ]
        diagonal = [(i, i) for i in range(self.board_size)]
        invert_diagonal = [(i, self.board_size - 1 - i) for i in range(self.board_size)]

        return rows + columns + [diagonal, invert_diagonal]

    def next_player(self):
        self.cur_player = next(self._players)

    def is_valid_move(self, move):
        row, column = move.row, move.column
        no_move = self._cur_moves[row][column].label == ""
        no_winner = not self._has_winner
        return no_winner and no_move

    def process_move(self, move):
        row, column = move.row, move.column
        self._cur_moves[row][column] = move
        for combo in self._win_conditions:
            result = set(
                self._cur_moves[n][m].label for n, m in combo
            )
            is_win = (len(result) == 1) and ("" not in result)
            if is_win:
                self._has_winner = True
                self.win_combo = combo
                break

    def has_winner(self):
        return self._has_winner

    def is_tie(self):
        no_winner = not self._has_winner
        played_moves = (
            move.label for row in self._cur_moves for move in row
        )
        return no_winner and all(played_moves)

class GamingBoard(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title('Крестики-нолики')
        self._squares = {}
        self._game = game
        self._create_board()
        self._create_grid()
        self.play_again_button = None

    def _create_board(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)

        players_list = list(DEFAULT_PLAYERS)

        player1_label = tk.Label(
            master=display_frame,
            text=f"{players_list[0].username} ({players_list[0].label})",
            font=font.Font(family="Helvetica", size=12),
            anchor="w"
            )
        player1_label.pack(side=tk.LEFT)

        player2_label = tk.Label(
            master=display_frame,
            text=f"{players_list[1].username} ({players_list[1].label})",
            font=font.Font(family="Helvetica", size=12),
            anchor="e"
            )
        player2_label.pack(side=tk.RIGHT)
        
        self.display = tk.Label(
            master=display_frame,
            text="Сыграем?",
            font=font.Font(family="Helvetica", size=20, weight="bold"),
        )
        self.display.pack()

    def _create_grid(self):
        grid_frame = tk.Frame(master=self)
        grid_frame.pack()
        
        for row in range(self._game.board_size):
            self.rowconfigure(row, weight=1, minsize=25, uniform='x')
            self.columnconfigure(row, weight=1, minsize=35, uniform='x')
            
            for column in range(self._game.board_size):
                cell_button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(size=40, weight="bold"),
                    fg="black",
                    width=3,
                    height=2,
                )

                self._squares[cell_button] = (row, column)
                cell_button.bind("<ButtonPress-1>", self.play)
                cell_button.grid(
                    row=row,
                    column=column,
                    padx=5,
                    pady=5,
                    sticky="nsew"
                )

    def play(self, event):
        used_sqr = event.widget
        row, column = self._squares[used_sqr]
        move = Move(row, column, self._game.cur_player.label)
        if self._game.is_valid_move(move):
            self._update_cell_button(used_sqr)
            self._game.process_move(move)
            if self._game.is_tie():
                self._update_display(msg="Ничья.", colour="black")
                self._show_play_again_button()
            elif self._game.has_winner():
                msg = f'Игрок {self._game.cur_player.username} выиграл.'
                colour = self._game.cur_player.colour
                self._update_display(msg, colour)
                self._show_play_again_button()
            else:
                self._game.next_player()
                msg = f"Сейчас ходит {self._game.cur_player.username}. Его фигура - {self._game.cur_player.label}."
                self._update_display(msg)

    def _show_play_again_button(self):
        if self.play_again_button is None:
            display_frame = self.display.master
            self.play_again_button = tk.Button(
                master=display_frame,
                text="Играть ещё.",
                font=font.Font(family="Helvetica", size=12),
                command=self._play_again,
            )
            self.play_again_button.pack()

    def _play_again(self):
        self._game = TicTacToe()
        self.display["text"] = "Сыграем?"
        self.display["fg"] = "black"
        for button in self._squares:
            button.config(text="")
            button.config(fg="black")
        self.play_again_button.pack_forget()
        self.play_again_button = None

    def _update_cell_button(self, used_sqr):
        used_sqr.config(text=self._game.cur_player.label)
        used_sqr.config(fg=self._game.cur_player.colour)

    def _update_display(self, msg, colour="black"):
        self.display["text"] = msg
        self.display["fg"] = colour


def main():
    game = TicTacToe()
    board = GamingBoard(game)
    board.mainloop()

if __name__ == "__main__":
    main()
