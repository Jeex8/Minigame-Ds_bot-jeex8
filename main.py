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

        await ctx.message.delete()

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

        await ctx.message.delete()

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

        await ctx.message.delete()

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
                            if option.lower() == 'камень' and opponent.pole.lower() == 'ножницы':
                                await channel.send(f'{member1.mention} победил {member2.mention}'
                                                   f' в дуэли камень ножницы бумага! Выигрышный предмет: Камень')
                            if option.lower() == 'ножницы' and opponent.pole.lower() == 'бумага':
                                await channel.send(f'{member1.mention} победил {member2.mention}'
                                                   f' в дуэли камень ножницы бумага! Выигрышный предмет: Ножницы')
                            if option.lower() == 'бумага' and opponent.pole.lower() == 'камень':
                                await channel.send(f'{member1.mention} победил {member2.mention}'
                                                   f' в дуэли камень ножницы бумага! Выигрышный предмет: Бумага')
                            if option.lower() == 'камень' and opponent.pole.lower() == 'бумага':
                                await channel.send(f'{member2.mention} победил {member1.mention}'
                                                   f' в дуэли камень ножницы бумага! Выигрышный предмет: Бумага')
                            if option.lower() == 'ножницы' and opponent.pole.lower() == 'камень':
                                await channel.send(f'{member2.mention} победил {member1.mention}'
                                                   f' в дуэли камень ножницы бумага! Выигрышный предмет: Камень')
                            if option.lower() == 'бумага' and opponent.pole.lower() == 'ножницы':
                                await channel.send(f'{member2.mention} победил {member1.mention}'
                                                   f' в дуэли камень ножницы бумага! Выигрышный предмет: Ножницы')
                            if option.lower() == opponent.pole.lower():
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
            if pole[int(row) - 1][int(column) - 1] != 'O' and pole[int(row) - 1][int(column) - 1] != '+':
                pole[int(row) - 1][int(column) - 1] = lol[1]
                user.stage = 'Игра, крестики нолики, ходит соперник'
                user.pole = str([pole, lol[1]])
                opponent.stage = 'Игра, крестики нолики, вы ходите'
                opponent.pole = str([pole, lol2[1]])
                yuser = ctx.guild.get_member(user.gaymer)
                oppo = ctx.guild.get_member(opponent.gaymer)
                dbsos.commit()
                await ctx.send(f'{"| ".join(pole[0])}\n{"| ".join(pole[1])}\n{"| ".join(pole[2])}')
                for row in range(3):
                    if (pole[row][0] == pole[row][1] == pole[row][2]) and (pole[row][0] != ' '):
                        await ctx.send(f'{yuser.mention} побеждает в "Крестики нолики" {oppo.mention}')
                        user.pole = None
                        user.stage = None
                        user.opponent = None
                        opponent.pole = None
                        opponent.stage = None
                        opponent.opponent = None
                        dbsos.commit()
                for column in range(3):
                    if (pole[0][column] == pole[1][column] == pole[2][column]) and (pole[0][column] != ' '):
                        await ctx.send(f'{yuser.mention} побеждает в "Крестики нолики" {oppo.mention}')
                        user.pole = None
                        user.stage = None
                        user.opponent = None
                        opponent.pole = None
                        opponent.stage = None
                        opponent.opponent = None
                        dbsos.commit()
                if (pole[0][0] == pole[1][1] == pole[2][2]) and (pole[0][0] != ' '):
                    await ctx.send(f'{yuser.mention} побеждает в "Крестики нолики" {oppo.mention}')
                    user.pole = None
                    user.stage = None
                    user.opponent = None
                    opponent.pole = None
                    opponent.stage = None
                    opponent.opponent = None
                    dbsos.commit()
                if (pole[0][2] == pole[1][1] == pole[2][0]) and (pole[0][2] != ' '):
                    await ctx.send(f'{yuser.mention} побеждает в "Крестики нолики" {oppo.mention}')
                    user.pole = None
                    user.stage = None
                    user.opponent = None
                    opponent.pole = None
                    opponent.stage = None
                    opponent.opponent = None
                    dbsos.commit()
                if user.pole:
                    flag = False
                    for i in range(3):
                        for j in range(3):
                            if pole[i][j] == ' ':
                                flag = True
                                break
                    if not flag:
                        await ctx.send(f'{yuser.mention} вышел в ничью с {oppo.mention} в "Крестики нолики"')
                        user.pole = None
                        user.stage = None
                        user.opponent = None
                        opponent.pole = None
                        opponent.stage = None
                        opponent.opponent = None
                        dbsos.commit()
            else:
                await ctx.send('Клетка занята')

        await ctx.message.delete()

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
            await ctx.send(f'{"| ".join(user.pole[:3])}\n{"| ".join(user.pole[3:6])}\n{"| ".join(user.pole[6:])}')
            opponent.pole = str([[[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']], '+'])
            user.pole = str([[[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']], 'O'])
            pervoh = random.randint(0, 1)
            yuser = ctx.guild.get_member(user.gaymer)
            oppo = ctx.guild.get_member(opponent.gaymer)
            if pervoh == 0:
                opponent.stage = 'Игра, крестики нолики, ходит соперник'
                user.stage = 'Игра, крестики нолики, вы ходите'
                await ctx.send(f'Первым ходит {yuser}')
            elif pervoh == 1:
                user.stage = 'Игра, крестики нолики, ходит соперник'
                opponent.stage = 'Игра, крестики нолики, вы ходите'
                await ctx.send(f'Первым ходит {oppo}')
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

        await ctx.message.delete()

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

        await ctx.message.delete()

    @commands.command(name='help')
    async def help(self, ctx):
        await ctx.send('/Викторина "@ping" - Приглашение игрока в викторину города'
                       '/Ход_викторина "город" - Делает ход в викторине'
                       '/стоп_викторина - Игрок написавший это, проигрывает в викторине'
                       '/randint "первое число" "второе число" - выбирает рандомное число из заданного промежутка'
                       '/rps "@ping" - Приглашение игрока в камень ножницы бумага'
                       '/cz "@ping" - Приглашение игрока в крестики нолики'
                       '/принять - Принимает приглашение в любую игру'
                       '/ход "первое число - ряд" "второе число - столб" - Делает ход в игре крестики нолики'
                       '/Готов "Камень" или "Ножницы" или "Бумага" - Пишется боту в личку, делает ход в КНБ')
        await ctx.message.delete()


async def main():
    db_session.global_init('bd')
    await bot.add_cog(RandomThings(bot))
    await bot.start(TOKEN)


asyncio.run(main())
