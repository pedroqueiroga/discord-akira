import random

from discord.ext.commands import Cog, command

from .tictactoe import (
    InvalidMove,
    OccupiedCell,
    TicTacToePieces,
    TicTacToeTable,
    WrongPlayer,
)


class JogoDaVelha(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @command()
    async def jdv(self, ctx, move=None):
        """Joga jogo da velha com Akira.
        Apenas $jdv pede para Akira jogar primeiro. Para jogar primeiro,
        $jdv <jogada>. Jogadas são do tipo <PEÇA><COLUNA><LINHA>.
        Exemplo: xa1 (XA1, Xa1, xA1); Xc2, Ob3."""
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
