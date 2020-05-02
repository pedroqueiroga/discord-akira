import copy
import math
import numpy
import random
import re

from enum import Enum
from discord.ext.commands import Cog, command


class TicTacToe(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @command()
    async def tictactoe(self, ctx, move=None):
        player = ctx.message.author.id
        if move is None:
            if player in self.games:
                # game is ongoing, simply tell player to move
                await ctx.send('Já estamos jogando. Informe sua jogada!')
                await ctx.send(self.formatted_table(player))
                return

            # start a new game
            self.init_table(player)
            await ctx.send('Ok, eu vou primeiro.')
            first_column = 'abc'[random.randint(0, 2)]
            first_line = random.randint(1, 3)
            first_move = f"X{first_column}{first_line}"
            self.games[player].make_move(first_move)
            await ctx.send(first_move + '\n' + self.formatted_table(player))
            return

        if player not in self.games:
            # create a game before proceeding
            self.init_table(player)
            await ctx.send('Iniciamos um novo jogo.')

        try:
            self.games[player].make_move(move)
            result = self.games[player].calculate_result()
            if result is self.games[player].next_piece():
                # player won
                await ctx.send(
                    'Impossível, você venceu!!\n'
                    + self.formatted_table(player)
                )
                self.delete_table(player)
                return
            elif result is TicTacToePieces.EMPTY:
                # draw
                await ctx.send('Empate.\n' + self.formatted_table(player))
                self.delete_table(player)
                return
            best_move = self.games[player].find_best_move()
            self.games[player].make_move(best_move)
            result = self.games[player].calculate_result()
            if result is self.games[player].next_piece():
                # I WON
                await ctx.send(
                    'Hehehehe!\n'
                    + best_move
                    + '\n'
                    + self.formatted_table(player)
                )
                self.delete_table(player)
                return
            elif result is TicTacToePieces.EMPTY:
                await ctx.send(
                    'Empate!\n'
                    + best_move
                    + '\n'
                    + self.formatted_table(player)
                )
                self.delete_table(player)
                return

            await ctx.send(best_move + '\n' + self.formatted_table(player))
        except OccupiedCell:
            await ctx.send('Essa casa já está ocupada!')
            await ctx.send(self.formatted_table(player))
        except WrongPlayer:
            await ctx.send(
                f'É a vez do {self.games[player].current_piece.value}'
            )
        except InvalidMove:
            await ctx.send(
                'Movimento inválido. Exemplos válidos: oa1; xc3; OB2'
            )

    def formatted_table(self, player):
        return '```' + str(self.games[player]) + '```'

    def init_table(self, player):
        self.games[player] = TicTacToeTable()
        return self.games[player]

    def delete_table(self, player):
        return self.games.pop(player, None)


class TicTacToeTable:
    """A tic tac toe table, created so that we can call str(table) hehehehe"""

    def __init__(self):
        self.state = [
            [TicTacToePieces.EMPTY for i in range(3)] for i in range(3)
        ]
        self.current_piece = TicTacToePieces.CROSS
        self.move_regex = re.compile(
            f'[{TicTacToePieces.CIRCLE.value}{TicTacToePieces.CROSS.value}]'
            '[ABC][123]'
        )

    def make_move(self, move: str):
        """Makes a move on the table

        move examples: Oa1; OA2; xc3
        :param str move: string of the format '{piece}{column}{line}'
        """
        move = move.upper()
        if not self.move_regex.match(move):
            raise InvalidMove(
                f'Invalid move ({move}). A move has the following format: '
                '<PIECE><COLUMN><ROW>. Example: Oa1'
            )

        piece, column, row = move
        piece = TicTacToePieces(piece)

        if piece is not self.current_piece:
            raise WrongPlayer("You can't play twice in a row.")

        row = int(row) - 1
        column = 0 if column == 'A' else 1 if column == 'B' else 2
        if self.state[row][column] is not TicTacToePieces.EMPTY:
            raise OccupiedCell('This cell already has a piece')

        self.state[row][column] = piece
        self.current_piece = self.next_piece()

    def find_best_move(self):
        piece = self.current_piece
        best_move = None
        best_value = -math.inf
        for lidx, line in enumerate(self.state):
            for cidx, cell in enumerate(line):
                if cell is not TicTacToePieces.EMPTY:
                    continue
                new_table = copy.deepcopy(self)
                column = 'abc'[cidx]
                move = f'{piece.value}{column}{lidx+1}'
                new_table.make_move(move)
                value = new_table.minimax(0, False)
                if best_value < value:
                    best_value = value
                    best_move = move

        return best_move

    def minimax(self, n_moves, is_max):
        new_piece = self.next_piece()
        piece = self.current_piece
        result = self.calculate_result()
        if result is new_piece:
            # result is a loss for piece.
            # if is_max is True, this was a simulation of the mini player,
            # and it won. the mini player will prefer
            # picking this state the more negative it is
            # if is is_max is False, the maxi player won, so he will prefer
            # this state in the previous level the more positive it is

            # penalize for number of moves required to reach this state, and
            # the players will prefer moves that lead to a quicker win for them
            return (-100 + n_moves) if is_max else (100 - n_moves)
        elif result is TicTacToePieces.EMPTY:
            # a draw that takes longer is preferred because
            # the other player has more chances to make mistakes.
            # it will be preferred if it is more negative for is_max True,
            # because it means that the previous level was minimizing.
            return -n_moves if is_max else n_moves

        if is_max:
            best = -math.inf
            for lidx, line in enumerate(self.state):
                for cidx, cell in enumerate(line):
                    if cell is not TicTacToePieces.EMPTY:
                        continue
                    new_table = copy.deepcopy(self)
                    column = 'abc'[cidx]
                    move = f'{piece.value}{column}{lidx+1}'
                    new_table.make_move(move)
                    value = new_table.minimax(n_moves + 1, False)
                    best = max(best, value)
            return best
        else:
            best = math.inf
            for lidx, line in enumerate(self.state):
                for cidx, cell in enumerate(line):
                    if cell is not TicTacToePieces.EMPTY:
                        continue
                    new_table = copy.deepcopy(self)
                    column = 'abc'[cidx]
                    move = f'{piece.value}{column}{lidx+1}'
                    new_table.make_move(move)
                    value = new_table.minimax(n_moves + 1, True)
                    best = min(best, value)
            return best

    def next_piece(self):
        return (
            TicTacToePieces.CIRCLE
            if self.current_piece is TicTacToePieces.CROSS
            else TicTacToePieces.CROSS
        )

    def calculate_result(self):
        # check for line finish
        for line in self.state:
            piece = line[0]
            if piece is not TicTacToePieces.EMPTY and len(set(line)) == 1:
                return piece

        # check for column finish
        np_arr = numpy.array(self.state)
        transpose = np_arr.T
        transpose_state = transpose.tolist()
        for column in transpose_state:
            piece = column[0]
            if piece is not TicTacToePieces.EMPTY and len(set(column)) == 1:
                return piece

        # check for diagonals
        diagonal1 = [self.state[i][i] for i in range(3)]
        piece = diagonal1[0]
        if piece is not TicTacToePieces.EMPTY and len(set(diagonal1)) == 1:
            return piece

        diagonal2 = [self.state[i][2 - i] for i in range(3)]
        piece = diagonal2[0]
        if piece is not TicTacToePieces.EMPTY and len(set(diagonal2)) == 1:
            return piece

        # no winning state
        # check if more plays can be made
        for line in self.state:
            for cell in line:
                if cell is TicTacToePieces.EMPTY:
                    # yes, another play can be made
                    return None
        # draw, no play can be made
        return TicTacToePieces.EMPTY

    def __str__(self):
        table = """   a     b     c
      |     |
1  .  |  .  |  .
 _____|_____|_____
      |     |
2  .  |  .  |  .
  ____|_____|_____
      |     |
3  .  |  .  |  .
      |     |"""
        for line in self.state:
            for cell in line:
                table = table.replace('.', cell.value, 1)

        return table


class TicTacToePieces(Enum):
    """Enum for tic tac toe pieces
    """

    CIRCLE = 'O'
    CROSS = 'X'
    EMPTY = '-'


class TicTacToeError(Exception):
    pass


class InvalidMove(TicTacToeError):
    pass


class OccupiedCell(InvalidMove):
    pass


class WrongPlayer(InvalidMove):
    pass
