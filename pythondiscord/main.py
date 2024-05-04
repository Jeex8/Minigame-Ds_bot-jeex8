import asyncio
import logging
import random
import discord
from discord.ext import commands
from data import db_session
from data.users import User
from dadata import Dadata
from config import TOKEN, token, secret

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

    @commands.command(name='Викторина')
    async def victorina(self, ctx):
        dbsos = db_session.create_session()
        user = dbsos.query(User).filter(User.gaymer == ctx.author.id, User.server_id == ctx.message.guild.id).first()
        if not user:
            user = User()
            user.gaymer = ctx.author.id
            user.server_id = ctx.message.guild.id
            user.channel_id = ctx.message.channel.id
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
                    user.stage = 'Ожидание игры викторины'
                    opponent.stage = 'Ожидание игры викторины'
                    dbsos.commit()
                    member = ctx.guild.get_member(ctx.message.mentions[0].id)
                    await ctx.send(f'{ctx.author.mention} вызывает {member.mention} на дуэль в викторину "города"')

    @commands.command(name='Ход_викторина')
    async def step_victorina(self, ctx, city):
        dbsos = db_session.create_session()
        user = dbsos.query(User).filter(User.gaymer == ctx.author.id, User.server_id == ctx.message.guild.id).first()
        opponent = dbsos.query(User).filter(User.gaymer == user.opponent).first()
        pole = eval(user.pole)
        city = city.lower()
        if user.stage == 'Ход викторины':
            if not pole or pole[-1][-1] == city[0]:
                if city not in pole:
                    dadata = Dadata(token, secret)
                    result = dadata.clean("address", city)
                    if result['country'] == 'Россия' and (
                            result['city_type_full'] == 'город' or result['region_type_full'] == 'город'
                            or result['area_type_full'] == 'город'):
                        pole.append(city)
                        user.stage = 'Ожидание хода противника'
                        opponent.stage = 'Ход викторины'
                        user.pole = str(pole)
                        opponent.pole = str(pole)
                        dbsos.commit()
                        await ctx.send('Ход переходит противнику')
                    else:
                        await ctx.send('Такого города не существует')
                else:
                    await ctx.send('Такой город был назван')
            else:
                await ctx.send('Не соответствует правилам игры')
        else:
            await ctx.send('Сейчас не ваш ход')

    @commands.command(name='стоп_викторина')
    async def stop_victorina(self, ctx):
        dbsos = db_session.create_session()
        user = dbsos.query(User).filter(User.gaymer == ctx.author.id, User.server_id == ctx.message.guild.id).first()
        opponent = dbsos.query(User).filter(User.gaymer == user.opponent).first()
        member1 = ctx.guild.get_member(user.gaymer)
        member2 = ctx.guild.get_member(user.opponent)
        opponent.pole = None
        opponent.stage = None
        opponent.opponent = None
        user.pole = None
        user.stage = None
        user.opponent = None
        dbsos.commit()
        await ctx.send(f'{member1.mention} - проиграл,  {member2.mention} - выиграл в викторину "города"')

    @commands.command(name='randint')
    async def my_randint(self, ctx, min_int, max_int):
        num = random.randint(int(min_int), int(max_int))
        await ctx.send(num)
        await ctx.message.delete()

    @commands.command(name='Готов')
    async def rps_ready(self, ctx, option):
        dbsos = db_session.create_session()
        users = dbsos.query(User).filter(User.gaymer == ctx.author.id).all()
        user = users[0]
        for user in users:
            if user.stage == 'Игра, камень ножницы бумага':
                user = user
                break
        opponent = dbsos.query(User).filter(User.gaymer == user.opponent).first()
        channel = bot.get_channel(user.channel_id)
        server = bot.get_guild(user.server_id)
        member1 = server.get_member(user.gaymer)
        member2 = server.get_member(user.opponent)
        if discord.ChannelType.private == ctx.channel.type:
            if user.stage == 'Игра, камень ножницы бумага':
                if not user.pole:
                    if option.lower() in ['камень', 'ножницы', 'бумага']:
                        if opponent.pole:
                            if option == 'камень' and opponent.pole == 'ножницы':
                                await channel.send(f'{member1.mention} победил {member2.mention}'
                                                   f' в дуэли камень ножницы бумага! Выигрышный предмет: Камень')
                            if option == 'ножницы' and opponent.pole == 'бумага':
                                await channel.send(f'{member1.mention} победил {member2.mention}'
                                                   f' в дуэли камень ножницы бумага! Выигрышный предмет: Ножницы')
                            if option == 'бумага' and opponent.pole == 'камень':
                                await channel.send(f'{member1.mention} победил {member2.mention}'
                                                   f' в дуэли камень ножницы бумага! Выигрышный предмет: Бумага')
                            if option == 'камень' and opponent.pole == 'бумага':
                                await channel.send(f'{member2.mention} победил {member1.mention}'
                                                   f' в дуэли камень ножницы бумага! Выигрышный предмет: Бумага')
                            if option == 'ножницы' and opponent.pole == 'камень':
                                await channel.send(f'{member2.mention} победил {member1.mention}'
                                                   f' в дуэли камень ножницы бумага! Выигрышный предмет: Камень')
                            if option == 'бумага' and opponent.pole == 'ножницы':
                                await channel.send(f'{member2.mention} победил {member1.mention}'
                                                   f' в дуэли камень ножницы бумага! Выигрышный предмет: Ножницы')
                            if option.lower() == opponent.pole:
                                await channel.send(f'{member1.mention} - {member2.mention} ничья!'
                                                   f' в дуэли камень ножницы бумага! Предмет: {option}')
                            user.pole = None
                            user.stage = None
                            user.opponent = None
                            opponent.pole = None
                            opponent.stage = None
                            opponent.opponent = None
                            dbsos.commit()
                        else:
                            user.pole = option.lower()
                            dbsos.commit()
                            await ctx.send('Вы сделали ход')
                    else:
                        await ctx.send('Некоректный ввод')
                else:
                    await ctx.send('Вы уже сделали ход')
            else:
                await ctx.send('Вы не находитесь в игре')
        else:
            await ctx.send('НАПИШИТЕ БОТУ В ЛИЧКУ!1111!!!111')

    @commands.command(name='ход')
    async def hod(self, ctx, row, column):
        dbsos = db_session.create_session()
        user = dbsos.query(User).filter(User.gaymer == ctx.author.id, User.server_id == ctx.message.guild.id).first()
        opponent = dbsos.query(User).filter(User.gaymer == user.opponent).first()
        if user.stage == 'Игра, крестики нолики, вы ходите':
            lol = eval(user.pole)
            lol2 = eval(opponent.pole)
            pole = lol[0]
            if pole[row - 1][column - 1] != '0' and pole[row - 1][column - 1] != '+':
                pole[int(row) - 1][int(column) - 1] = lol[1]
                user.stage = 'Игра, крестики нолики, ходит соперник'
                user.pole = str([pole, lol[1]])
                opponent.stage = 'Игра, крестики нолики, вы ходите'
                opponent.pole = str([pole, lol2[1]])
                dbsos.commit()
                await ctx.send(f'{"| ".join(pole[0])}\n{"| ".join(pole[1])}\n{"| ".join(pole[2])}')
            else:
                await ctx.send('Клетка занята')

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
        user = dbsos.query(User).filter(User.gaymer == ctx.author.id, User.server_id == ctx.message.guild.id).first()
        opponent = dbsos.query(User).filter(User.gaymer == user.opponent).first()
        member = ctx.guild.get_member(user.gaymer)
        if user.stage == 'Ожидание игры крестики нолики':
            await ctx.send('Игра началась')
            await ctx.send('Напишите /ход, и введите номер столбца и колонки в которой хотите поставить символ')
            user.pole = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
            await ctx.send(
                f'\n----\n{"| ".join(user.pole[:3])}'
                f'\n----\n{"| ".join(user.pole[3:6])}\n----\n{"| ".join(user.pole[6:])}\n')
            opponent.pole = str([[['0', '0', '0'], ['0', '0', '0'], ['0', '0', '0']], '+'])
            user.pole = str([[['0', '0', '0'], ['0', '0', '0'], ['0', '0', '0']], 'O'])
            pervoh = random.randint(0, 1)
            if pervoh == 0:
                opponent.stage = 'Игра, крестики нолики, ходит соперник'
                user.stage = 'Игра, крестики нолики, вы ходите'
            elif pervoh == 1:
                user.stage = 'Игра, крестики нолики, ходит соперник'
                opponent.stage = 'Игра, крестики нолики, вы ходите'
            dbsos.commit()
        elif user.stage == 'Ожидание игры камень ножницы бумага':
            await ctx.send('Игра началась')
            await ctx.send('Напишите боту в личку "камень", "ножницы" или "бумага" для хода')
            user.stage = 'Игра, камень ножницы бумага'
            opponent.stage = 'Игра, камень ножницы бумага'
            dbsos.commit()
        elif user.stage == 'Ожидание игры викторины':
            user.stage = 'Ход викторины'
            opponent.stage = 'Ожидание хода противника'
            user.pole = '[]'
            opponent.pole = '[]'
            user.server_id = opponent.server_id
            user.channel_id = opponent.channel_id
            dbsos.commit()
            await ctx.send(f'Викторина началась {member.mention} ходит первым')

    @commands.command(name='cz')
    async def cz(self, ctx):
        dbsos = db_session.create_session()
        user = dbsos.query(User).filter(User.gaymer == ctx.author.id, User.server_id == ctx.message.guild.id).first()
        if not user:
            user = User()
            user.gaymer = ctx.author.id
            user.server_id = ctx.message.guild.id
            user.channel_id = ctx.message.channel.id
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
                    user.stage = 'Ожидание игры крестики нолики'
                    opponent.stage = 'Ожидание игры крестики нолики'
                    dbsos.commit()
                    member = ctx.guild.get_member(ctx.message.mentions[0].id)
                    await ctx.send(f'{ctx.author.mention} вызывает {member.mention} на дуэль в крестики нолики')

        await ctx.message.delete()

    @commands.command(name='rps')
    async def rps(self, ctx):
        dbsos = db_session.create_session()
        user = dbsos.query(User).filter(User.gaymer == ctx.author.id, User.server_id == ctx.message.guild.id).first()
        if not user:
            user = User()
            user.gaymer = ctx.author.id
            user.server_id = ctx.message.guild.id
            user.channel_id = ctx.message.channel.id
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
                    user.stage = 'Ожидание игры камень ножницы бумага'
                    opponent.stage = 'Ожидание игры камень ножницы бумага'
                    dbsos.commit()
                    member = ctx.guild.get_member(ctx.message.mentions[0].id)
                    await ctx.send(f'{ctx.author.mention} вызывает {member.mention} на дуэль в камень ножницы бумага')


async def main():
    db_session.global_init('bd')
    await bot.add_cog(RandomThings(bot))
    await bot.start(TOKEN)


asyncio.run(main())
