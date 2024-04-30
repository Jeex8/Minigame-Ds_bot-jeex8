import asyncio
import logging
import random
import discord
from discord.ext import commands
from data import db_session
from data.users import User

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)


class RandomThings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.get_guild(1230771331067416676)

    @commands.command(name='randint')
    async def my_randint(self, ctx, min_int, max_int):
        num = random.randint(int(min_int), int(max_int))
        await ctx.send(num)
        await ctx.message.delete()

    @commands.command(name='ход')
    async def hod(self, ctx, row, column):
        dbsos = db_session.create_session()
        user = dbsos.query(User).filter(User.gaymer == ctx.author.id).first()
        opponent = dbsos.query(User).filter(User.gaymer == user.opponent).first()
        if user.stage == 'Игра, крестики нолики, вы ходите':
            hernia = eval(user.pole)
            hernia2 = eval(opponent.pole)
            pole = hernia[0]
            pole[int(row) - 1][int(column) - 1] = hernia[1]
            user.stage = 'Игра, крестики нолики, ходит соперник'
            user.pole = str([pole, hernia[1]])
            opponent.stage = 'Игра, крестики нолики, вы ходите'
            opponent.pole = str([pole, hernia2[1]])
            dbsos.commit()
            await ctx.send(f'\n---\n{"| ".join(pole[0])}\n---\n{"| ".join(pole[1])}\n---\n{"| ".join(pole[2])}\n')

    def tictactoe(self, ctx, username, turn):

        for row in range(0, 7, 3):
            if (TTT[row] == TTT[row + 1] == TTT[row + 2]) and (TTT[row] != 0):
                winner = TTT[row]
        for col in range(0, 3, 1):
            if (TTT[col] == TTT[col + 3] == TTT[col + 6]) and (TTT[col] != 0):
                winner = TTT[col]
        if (TTT[0] == TTT[4] == TTT[8]) and (TTT[0] != 0):
            winner = TTT[0]
        if (TTT[2] == TTT[4] == TTT[6]) and (TTT[2] != 0):
            winner = TTT[2]

    @commands.command(name='принять')
    async def prinyat(self, ctx):
        dbsos = db_session.create_session()
        user = dbsos.query(User).filter(User.gaymer == ctx.author.id).first()
        opponent = dbsos.query(User).filter(User.gaymer == user.opponent).first()
        if user.stage == 'Ожидание игры':
            await ctx.send('Игра началась')
            await ctx.send('Напишите /ход, и введите номер столбца и колонки в которой хотите поставить символ')
            user.pole = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
            await ctx.send(f'\n----\n{"| ".join(user.pole[:3])}\n----\n{"| ".join(user.pole[3:6])}\n----\n{"| ".join(user.pole[6:])}\n')
            opponent.pole = str([[['0', '0', '0'], ['0', '0', '0'], ['0', '0', '0']], '+'])
            user.pole = str([[['0', '0', '0'], ['0', '0', '0'], ['0', '0', '0']], 'O'])
            user.stage = 'Игра, крестики нолики, ходит соперник'
            opponent.stage = 'Игра, крестики нолики, вы ходите'
            dbsos.commit()




    @commands.command(name='cz')
    async def cz(self, ctx):
        dbsos = db_session.create_session()
        user = dbsos.query(User).filter(User.gaymer == ctx.author.id).first()
        if not user:
            user = User()
            user.gaymer = ctx.author.id
            dbsos.add(user)
            dbsos.commit()
        if user.opponent:
            await ctx.send('Вы уже играете с другим игроком.')
        else:
            opponent = dbsos.query(User).filter(User.gaymer == ctx.message.mentions[0].id).first()
            if not opponent:
                await ctx.send('Данный игрок ещё не зарегистрирован в системе, пусть он начнет игру')
            else:
                if opponent.opponent:
                    await ctx.send('Данный игрок занят.')
                else:
                    user.opponent = ctx.message.mentions[0].id
                    opponent.opponent = user.gaymer
                    user.stage = 'Ожидание игры'
                    opponent.stage = 'Ожидание игры'
                    dbsos.commit()
                    member = ctx.guild.get_member(ctx.message.mentions[0].id)
                    await ctx.send(f'{ctx.author.mention} вызывает {member.mention} на дуэль в крестики нолики')

        await ctx.message.delete()

    @commands.command(name='rps')
    async def rps(self, ctx, username):
        await ctx.send(f'{ctx.autor.mention} вызывает {username.mention} на дуэль в крестики нолики')
        if "принять" == message.content.lower() and ctx.username == username:
            pass


TOKEN = "MTIzMDc3MDMzMzYwMzA2OTk2Mw.GIu_w8.OEq3fsyulKe49rQMbUQtCd_hGNIksU3ksAXjFA"


async def main():
    db_session.global_init('bd')
    await bot.add_cog(RandomThings(bot))
    await bot.start(TOKEN)


asyncio.run(main())
