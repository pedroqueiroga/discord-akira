import re

from enum import Enum
from discord.ext.commands import Cog, command


class TicTacToe(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @command()
    async def tictactoe(self, ctx):
        pass

    def init_table(self, player):
        return self.games[player]

    def delete_table(self, player):
        return self.games.pop(player, None)


class TicTacToeTable:
    """A tic tac toe table, created so that we can call str(table) hehehehe"""

    def __init__(self):
        self.state = [
            [TicTacToePieces.EMPTY for i in range(3)] for i in range(3)
        ]
        self.lost = None
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
                'Invalid move. A move has the following format: '
                '<PIECE><COLUMN><ROW>. Example: Oa1'
            )

        piece, column, row = move
        row = int(row) - 1
        column = 0 if column == 'A' else 1 if column == 'B' else 2
        if self.state[row][column] is not TicTacToePieces.EMPTY:
            raise OccupiedCell('This cell already has a piece')

        self.state[row][column] = TicTacToePieces(piece)

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
