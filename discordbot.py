# coding=utf-8

import discord
from discord.ext import commands
import asyncio
import sqlite3
import random
import re
import configparser

conn = sqlite3.connect('chat_messages_discord.db')
cur = conn.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS messages (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    user_id INTEGER,
    text    TEXT,
    date    INTEGER,
    msg_id  INTEGER
);

''')
cur.execute("""
CREATE TABLE IF NOT EXISTS cfg (
    chat_id  INTEGER,
    respond  INTEGER DEFAULT (0),
    channel  INTEGER,
    enabled  INTEGER DEFAULT (1),
    credited INTEGER DEFAULT (0),
    chance   INTEGER DEFAULT (25),
    global   INTEGER DEFAULT (0),
    filter   INTEGER DEFAULT (1234) 
);

""")
cur.execute("""
CREATE TABLE IF NOT EXISTS banned_words (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT
);

""")
conn.commit()

configparser = configparser.ConfigParser()
configparser.read('cfg.ini')

client = commands.Bot(intents=discord.Intents.all())
GROUP_settings = client.create_group("настройки", "Настройки сервера")

LEARNING_MAX_MSG = configparser['CONFIG']['LEARNING_MAX_MSG']
token = configparser['CONFIG']['TOKEN']
chars_list = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", " ", "!", "\"", "#", "$", "%", "&", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<", "=", ">", "?", "@", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~", "\n", "\t", "\r", "\f", "\v", "á", "é", "í", "ó", "ú", "ü", "ñ", "ç", "ß", "ø", "å", "æ", "œ", "þ", "ð", "ø", "ā", "ē", "ī", "ō", "ū", "¡", "¿", "£", "€", "¥", "©", "®", "ª", "º", "µ", "¶", "·", "÷", "×", "°", "º", "¹", "²", "³", "¼", "½", "¾", "∂", "∑", "∏", "π", "−", "√", "∞", "∫", "≈", "≠", "≤", "≥", "∈", "∉", "∩", "∪", "⊂", "⊃", "⊆", "⊇", "⊕", "⊗", "⊥", "⋅", "⋆", "⌂", "⌐", "⌠", "⌡", "⌢", "⌣", "⌧", "⌫", "⌦", "⌬", "⌭", "⌮", "⌯", "⌰", "⌱", "⌲", "⌳", "⌴", "⌵", "⌶", "⌷", "⌸", "⌹", "⌺", "⌻", "⌼", "⌽", "⌾", "⌿", "⍀", "⍁", "⍂", "⍃", "⍄", "⍅", "⍆", "⍇", "⍈", "⍉", "⍊", "⍋", "⍌", "⍍", "⍎", "⍏", "⍐", "⍑", "⍒", "⍓", "⍔", "⍕", "⍖", "⍗", "⍘", "⍙", "⍚", "⍛", "⍜", "⍝", "⍞", "⍟", "⍠", "⍡", "⍢", "⍣", "⍤", "⍥", "⍦", "⍧", "⍨", "⍩", "⍪", "⍫", "⍬", "⍭", "⍮", "⍯", "⍰", "⍱", "⍲", "⍳", "⍴", "⍵", "⍶", "⍷", "⍸", "⍹", "⍺", "⍻", "⍼", "⍽", "⍾", "⍿", "⎀", "⎁", "⎂", "⎃", "⎄", "⎅", "⎆", "⎇", "⎈", "⎉", "⎊", "⎋", "⎌", "⎍", "⎎", "⎏", "⎐", "⎑", "⎒", "⎓", "⎔", "⎕", "⎖", "⎗", "⎘", "⎙", "⎚", "⎛", "⎜", "⎝", "⎞", "⎟", "⎠", "⎡", "⎢", "⎣", "⎤", "⎥", "⎦", "⎧", "⎨", "⎩", "⎪", "⎫", "⎬", "⎭", "⎮", "⎯", "⎰", "⎱", "⎲", "⎳", "⎴", "⎵", "⎶", "⎷", "⎸", "⎹", "⎺", "⎻", "⎼", "⎽", "⎾", "⎿", "⏀", "⏁", "⏂", "⏃", "⏄", "⏅", "⏆", "⏇", "⏈", "⏉", "⏊", "⏋", "⏌", "⏍", "⏎", "⏏", "⏐", "⏑", "⏒", "⏓", "⏔", "⏕", "⏖", "⏗", "⏘", "⏙", "⏚", "⏛", "⏜", "⏝", "⏞", "⏟", "⏠", "⏡", "⏢", "⏣", "⏤", "⏥", "⏦", "⏧", "⏨", "⏩", "⏪", "⏫", "⏬", "⏭", "⏮", "⏯", "⏰", "⏱", "⏲", "⏳", "⏴", "⏵", "⏶", "⏷", "⏸", "⏹", "⏺", "⏻", "⏼", "⏽", "⏾", "⏿", "☀", "☁", "☂", "☃", "☄", "★", "☆", "☇", "☈", "☉", "☊", "☋", "☌", "☍", "☎", "☏", "☐", "☑", "☒", "☓", "☔", "☕", "☖", "☗", "☘", "☙", "☚", "☛", "☜", "☝", "☞", "☟", "☠", "☡", "☢", "☣", "☤", "☥", "☦", "☧", "☨", "☩", "☪", "☫", "☬", "☭", "☮", "☯", "☸", "☹", "☺", "☻", "☼", "☽", "☾", "☿", "♀", "♂", "♁", "♂", "♃", "♄", "♅", "♆", "♇", "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓", "♔", "♕", "♖", "♗", "♘", "♙", "♚", "♛", "♜", "♝", "♞", "♟", "♠", "♡", "♢", "♣", "♤", "♥", "♦", "♧", "♨", "♩", "♪", "♫", "♬", "♭", "♮", "♯", "♰", "♱", "♲", "♳", "♴", "♵", "♶", "♷", "♸", "♹", "♺", "♻", "♼", "♽", "♾", "♿", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅", "⚆", "⚇", "⚈", "⚉", "⚊", "⚋", "⚌", "⚍", "⚎", "⚏", "⚐", "⚑", "⚒", "⚓", "⚔", "⚕", "⚖", "⚗", "⚘", "⚙", "⚚", "⚛", "⚜"]


def update():
    for guild in client.guilds:
        if cur.execute(f"SELECT * FROM cfg WHERE chat_id = {guild.id}").fetchone() is None:
            cur.execute(f"INSERT INTO cfg(chat_id) VALUES ({guild.id})")
    
    conn.commit()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.change_presence(activity=discord.Activity(name="за сообщениями", type=discord.ActivityType.watching), status=discord.Status.dnd)
    update()

async def upd_message(message, old_message):
    cur.execute("UPDATE messages SET text = ? WHERE msg_id = ?", (message.content, old_message.id))
    conn.commit()
    
async def save_message(message):
    data = (
        message.guild.id,
        message.author.id,
        message.content,
        int(message.created_at.timestamp())
    )
    cur.execute('INSERT INTO messages (chat_id, user_id, text, date) VALUES (?, ?, ?, ?)', data)
    conn.commit()

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        return

    if message.content is None or message.content == "":
        return
    
    enabled = cur.execute(f"SELECT enabled FROM cfg WHERE chat_id = {message.guild.id}").fetchone()[0]
    respond = cur.execute(f"SELECT respond FROM cfg WHERE chat_id = {message.guild.id}").fetchone()[0]
    channelid = cur.execute(f"SELECT channel FROM cfg WHERE chat_id = {message.guild.id}").fetchone()[0]

    await save_message(message)
    if enabled == 1:
        if respond == 0:
            await random_reply(message.guild.id, message)
        else:
            if message.channel.id == channelid:
                await random_reply(message.guild.id, message)


    count = len(cur.execute('SELECT * FROM messages WHERE chat_id = ?', (message.guild.id,)).fetchall())

    if count == LEARNING_MAX_MSG:
        await message.reply("Начиная с этого сообщения я начну цитировать всё что я запомнил. Удачи :3")

    if message.content.lower() == str(client.user.mention):
        await message.add_reaction("👋")
        await message.reply("Привет!")

def sanitize_message(text, filter):
    filter = str(filter)
    if "1" in filter:
        text = re.sub(r'<@\d+>', '[пользователь]', text)
    if "2" in filter:
        text = re.sub(r'<@$\d+>', '[роль]', text)
    if "3" in filter:
        text = re.sub(r'http[s]?://\S+', '[ссылка]', text)
    text = text.replace("@everyone", "[все]")
    text = text.replace("@here", "[онлайн]")
    text = text.replace("rule34.xxx", "[rule34]")

    if "4" in filter:
        banwords = cur.execute("SELECT * FROM banned_words").fetchall()
        for banword in banwords:
            text = re.sub(banword[1], "[бан-ворд]", text, flags=re.IGNORECASE)

    return text

def decode_filter_settings(filter):
    filter = str(filter)
    string = ""
    if "1" in filter:
        string += "✅ Фильтр пингов | "
    else:
        string += "❌ Фильтр пингов | "
    if "2" in filter:
        string += "✅ Фильтр упоминаний ролей | "
    else:
        string += "❌ Фильтр упоминаний ролей | "
    if "3" in filter:
        string += "✅ Фильтр ссылок | "
    else:
        string += "❌ Фильтр ссылок | "
    if "4" in filter:
        string += "✅ Бан-ворд фильтр"
    else:
        string += "❌ Бан-ворд фильтр"

    return string


async def random_reply(chat_id, message):
    credited = cur.execute(f"SELECT credited FROM cfg WHERE chat_id = {chat_id}").fetchone()[0]
    chance = cur.execute(f"SELECT chance FROM cfg WHERE chat_id = {chat_id}").fetchone()[0]
    use_global = cur.execute(f"SELECT global FROM cfg WHERE chat_id = {chat_id}").fetchone()[0]
    filt = cur.execute(f"SELECT filter FROM cfg WHERE chat_id = {chat_id}").fetchone()[0]

    if use_global == 0:
        cur.execute('SELECT * FROM messages WHERE chat_id = ?', (chat_id,))
    else:
        cur.execute('SELECT * FROM messages')
    messages = cur.fetchall()
    
    if not messages:
        return 
    
    selected_msg = messages[random.randint(0, len(messages) - 1)]

    
    if len(messages) > LEARNING_MAX_MSG:
        if random.random() < chance / 100:
            random_message = sanitize_message(selected_msg[3], filt)
            if credited == 1:
                author = await client.fetch_user(selected_msg[2])
                guild = await client.fetch_guild(selected_msg[1])
                random_message = f"{random_message}\n\n> ***Автор мысли: {author} {'с сервера ' + guild.name if guild.id != chat_id else ''}***\n> ***ID {selected_msg[0]}***"
            await message.channel.send(random_message)


@client.event
async def on_message_edit(before, after):
    await upd_message(after, before)

@client.event
async def on_guild_remove(guild: discord.Guild):
    cur.execute('DELETE FROM messages WHERE chat_id = ?', (guild.id,))
    cur.execute('DELETE FROM cfg WHERE chat_id = ?', (guild.id,))
    conn.commit()

TEXT_added = "Окей, меня добавили. Чтож... Я Сквазимабзабза))! Бот который может повторять сообщения участников с этого сервера или вообще со всех серверов!\n✏️ Разработчик: [**kararasenok_gd**](<https://t.me/kararasenokk>)\n🔗 Исходный код бота: [**GitHub**](<https://github.com/kararasenok-gd/skvbz>)\nℹ️ Тут уже имеются некоторые настройки. Из них:\n- Включённый фильтры пингов, ссылок и бан-вордов\n- Уже Включённый модуль повторения сообщений\nОстальное можно настройть введя /настройки\n\n\n⚠️ Продолжая использовать этого бота вы соглашаетесь на то, что **все** сообщения с этого сервера будут записыватся и **любой** пользователь этого бота может случайно увидеть их.\n🗑️ Если сообщение удалить, бот удалит его из системы. Если изменить сообщение, бот перезапишет его.\n🗑️ Для очистки вы можете написать **/очистить_сообщения** или удалить бота с сервера. Все сообщения будут полностью удалены из системы.\n🔗 Если вы не верите что сообщения бесследно пропадут, то у бота есть открытый исходный код. Ссылка на него чуть выше"

@client.event
async def on_guild_join(guild: discord.Guild):
    update()
    
    if guild.system_channel is not None:
        await guild.system_channel.send(TEXT_added)
    else:
        await guild.text_channels[0].send(TEXT_added)
        
        
@client.event
async def on_message_delete(message):
    cur.execute('DELETE FROM messages WHERE msg_id = ?', (message.id,))
    conn.commit()






@client.slash_command(name="обучение", description = "Посмотреть процесс обучения бота (ну или сколько сообщений он может цитировать)")
async def learn(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral = True)
    
    
    cfg = cur.execute(f"SELECT * FROM cfg WHERE chat_id = {ctx.guild.id}").fetchone()
    
    cur.execute('SELECT COUNT(*) FROM messages WHERE chat_id = {}'.format(ctx.guild.id))
    messages = cur.fetchone()[0]

    if messages < LEARNING_MAX_MSG and cfg[6] == 0:
        await ctx.respond(f"Вашим сервером было отправлено: {messages}. Модуль будет активен когда число тут будет больше {LEARNING_MAX_MSG}", ephemeral = True)
    else:
        await ctx.respond(f"Вашим сервером было отправлено: {messages} сообщений. Это вполне достаточно для нормальной работы модуля!\nШанс получить конкретное сообщение: {round(1/messages*100, 5)}%", ephemeral = True)
        return

class ClearDB(discord.ui.Button):
    def __init__(self, label, **kwargs):
        super().__init__(label=label, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        cur.execute('DELETE FROM messages WHERE chat_id = ?', (interaction.guild.id,))
        conn.commit()
        await interaction.response.edit_message(content=f"🗑️ Очищено\n🔁 Обучение начато сначало", view=None)

@client.slash_command(name="очистить_сообщения", description = "удаляет все сообщения что могут цитироваться")
@commands.has_permissions(manage_messages=True)
async def clear_db(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral = True)
    
    
    view = discord.ui.View()
    button = ClearDB(label="Очистить")
    view.add_item(button)

    messages = cur.execute('SELECT COUNT(*) FROM messages WHERE chat_id = ?', (ctx.guild.id,)).fetchone()[0]
    if messages == 0:
        await ctx.respond("❌ Нет сообщений для удаления", ephemeral = True)
        return
    
    await ctx.respond(f"❌ Ты точно хочешь удалить все сообщения ({messages})?", ephemeral = True, view=view)

@client.slash_command(name="информация", description = "ну там сколько серверов и т.д")
async def info(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral = True)
    
    
    cur.execute('SELECT COUNT(*) FROM messages')
    allmsgs = cur.fetchone()[0]
    guilds = len(client.guilds)
    ping = client.latency * 1000

    await ctx.respond(embed=discord.Embed(title="Информация", description=f"Пинг: {ping}\nСервера: {guilds}\nВсего цитируемых сообщений: {allmsgs}\n\nШанс получить конкретное сообщение (Глобал БД): {round(1/allmsgs*100, 5)}%", color=0x0000ff), ephemeral = True)

@client.slash_command(name="добавить_рандом", description = "Заполнить БД случайными символами")
@commands.has_permissions(manage_messages=True)
async def fill_db(ctx: discord.ApplicationContext, string_nums: discord.Option(int, "Количество строк", min_value=1, max_value=100, required=True)):
    await ctx.defer(ephemeral=True)

    for __ in range(string_nums):
        random_string = ''.join(random.choice(chars_list) for _ in range(random.randint(1, 250)))
        cur.execute("INSERT INTO messages VALUES (NULL, {}, {}, '{}', NULL)".format(ctx.guild.id, client.user.id, random_string))
    
    conn.commit()
    await ctx.respond("Таблица заполнена!", ephemeral = True)

@client.slash_command(name="добавить_банворд", description = "Предложить добавить слово в банворд лист")
async def add_banword(ctx: discord.ApplicationContext, word_or_words: discord.Option(str, description="Само слово или слова (все слова разделяются пробелом)", required=True)):
    await ctx.defer(ephemeral = True)
    
    
    words = word_or_words.split()

    existWords = ""
    notExistWords = ""

    for word in words:
        if cur.execute(f"SELECT * FROM banned_words WHERE word = '{word}'").fetchone() is not None:
            existWords += f"{word}\n"
        else:
            notExistWords += f"{word}\n"
            if ctx.author.id == 1060236728595648532:
                cur.execute(f"INSERT INTO banned_words VALUES (NULL, '{word}')")
    if ctx.author.id == 1060236728595648532:
        conn.commit()

    if existWords == "":
        existWords = "*нету*"
    if notExistWords == "":
        notExistWords = "*нету*"
    
    await ctx.respond(f"Перебрав все слова, я составил это:\n\n## Слова, которые будут добавлены\n{notExistWords}\n\n## Слова которые уже есть\n{existWords}", ephemeral = True)
    if ctx.author.id == 1060236728595648532:
        await ctx.respond("Слова были добавлены", ephemeral = True)
    else:
        creator = await client.fetch_user(1060236728595648532)
        await creator.send(f"Поступили слова в банлист:\n{notExistWords}")
        await ctx.respond("Отправлено разработчику", ephemeral = True)

@client.slash_command(name="удалить_банворд", description = "Удалить банворд (ТОЛЬКО ДЛЯ СОЗДАТЕЛЯ)", guilds = [998279210110038096])
async def delete_bw(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral = True)
    
    
    if ctx.author.id != 1060236728595648532:
        return

    select = discord.ui.Select(
        placeholder="Выбери слово что удалить надо",
        options=[discord.SelectOption(label=f"{word[1]} ({word[0]})", value=str(word[1])) for word in cur.execute("SELECT * FROM banned_words").fetchall()]
    )

    async def select_callback(interaction):
        word = select.values[0]
        
        cur.execute(f"DELETE FROM banned_words WHERE word = '{word}'")
        conn.commit()
        await interaction.response.send_message(f"{word} удалён из БД!", ephemeral=True)

    select.callback = select_callback

    view = discord.ui.View()
    view.add_item(select)

    await ctx.respond("Выбери слово:", view=view, ephemeral=True)

@client.slash_command(name="сообщение", description = "Получает сообщение по айди в боте")
async def get_message(ctx: discord.ApplicationContext, msgid: discord.Option(int, description="АйДи", required = True)):
    await ctx.defer(ephemeral = True)
    
    
    selected_msg = cur.execute(f"SELECT * FROM messages WHERE id = {msgid}").fetchone()
    if selected_msg is None:
        await ctx.respond("Сообщение не найдено", ephemeral = True)

    author = await client.fetch_user(selected_msg[2])
    guild = await client.fetch_guild(selected_msg[1])
    random_message = f"{selected_msg[3]}\n\n> ***Автор мысли: {author} {'с сервера ' + guild.name if guild.id != ctx.guild.id else ''}***\n> ***ID {selected_msg[0]}***"
    await ctx.respond(random_message, ephemeral = True)








@GROUP_settings.command(name="просмотр", description = "Настройки бота на сервере")
async def settings(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral = True)
    
    
    settings = cur.execute(f"SELECT * FROM cfg WHERE chat_id = {ctx.guild.id}").fetchone()

    embed = discord.Embed(title="Настройки сервера", color=0x0000ff)

    embed.add_field(name="Состояние", value="✅ Включено" if settings[3] == 1 else "❌ Выключено")
    embed.add_field(name="Ответ в спец. канале", value="✅ Включено" if settings[1] == 1 else "❌ Выключено")
    embed.add_field(name="Спец. канал", value=f"<#{settings[2]}>" if settings[2] is not None else "❌ Не установлен")
    embed.add_field(name="Подпись авторов цитируемых сообщений", value="✅ Включено" if settings[4] == 1 else "❌ Выключено")
    embed.add_field(name="Шанс ответа", value=f"{settings[5]}%")
    embed.add_field(name="Глобальная БД", value="✅ Включено" if settings[6] == 1 else "❌ Выключено")
    embed.add_field(name="Фильтры", value=decode_filter_settings(settings[7]))

    await ctx.respond(embed=embed, ephemeral = True)

@GROUP_settings.command(name="отвечать_в_спец_канале", description = "Меняет канал для реагирования на сообщения")
@commands.has_permissions(manage_messages=True)
async def settings__reply_specific_channel(ctx: discord.ApplicationContext, value: discord.Option(bool, "Отвечать в определённом канале?", required=True)):
    await ctx.defer(ephemeral = True)
    
    
    if value is True:
        cur.execute(f"UPDATE cfg SET respond = 1 WHERE chat_id = {ctx.guild.id}")
        conn.commit()
        await ctx.respond("✅ Бот будет отвечать в специальном канале, поставленным в настройках\n✏️ Бот продолжит записывать сообщения с сервера, но не будет работать в других каналах\n\n💡 Для очистки сообщения удалите бота с сервера или напишите /очистить_сообщения", ephemeral = True)
    elif value is False:
        cur.execute(f"UPDATE cfg SET respond = 0 WHERE chat_id = {ctx.guild.id}")
        conn.commit()
        await ctx.respond("✅ Бот будет отвечать везде", ephemeral = True)

@GROUP_settings.command(name="канал", description = "Канал где будет бот отвечать")
@commands.has_permissions(manage_messages=True)
async def settings__channel(ctx: discord.ApplicationContext, value: discord.Option(discord.TextChannel, "Канал", required=True)):
    await ctx.defer(ephemeral = True)
    
    
    cur.execute(f"UPDATE cfg SET channel = {value.id} WHERE chat_id = {ctx.guild.id}")
    conn.commit()
    await ctx.respond("✅ Канал изменён!", ephemeral = True)

@GROUP_settings.command(name="включить_выключить", description = "Включить/Выключить бота")
@commands.has_permissions(manage_messages=True)
async def settings__toggle(ctx: discord.ApplicationContext, value: discord.Option(bool, "Включить?", required=True)):
    await ctx.defer(ephemeral = True)
    
    
    if value is True:
        cur.execute(f"UPDATE cfg SET enabled = 1 WHERE chat_id = {ctx.guild.id}")
        conn.commit()
        await ctx.respond("✅ Бот теперь будет отвечать", ephemeral = True)
    elif value is False:
        cur.execute(f"UPDATE cfg SET enabled = 0 WHERE chat_id = {ctx.guild.id}")
        conn.commit()
        await ctx.respond("❌ Бот теперь не будет отвечать", ephemeral = True)

@GROUP_settings.command(name="подпись", description = "Подписывать авторов сообщений")
@commands.has_permissions(manage_messages=True)
async def settings__tag(ctx: discord.ApplicationContext, value: discord.Option(bool, "Включить?", required=True)):
    await ctx.defer(ephemeral = True)
    
    
    if value is True:
        cur.execute(f"UPDATE cfg SET credited = 1 WHERE chat_id = {ctx.guild.id}")
        conn.commit()
        await ctx.respond("✅ Бот теперь будет подписывать авторов сообщений", ephemeral = True)
    elif value is False:
        cur.execute(f"UPDATE cfg SET credited = 0 WHERE chat_id = {ctx.guild.id}")
        conn.commit()
        await ctx.respond("❌ Бот теперь не будет подписывать авторов сообщений", ephemeral = True)

@GROUP_settings.command(name="шанс", description = "Изменить шанс ответа")
@commands.has_permissions(manage_messages=True)
async def settings__chance(ctx: discord.ApplicationContext, value: discord.Option(int, "шанс", required=True, min_value = 1, max_value = 100)):
    await ctx.defer(ephemeral = True)
    
    
    cur.execute(f"UPDATE cfg SET chance = {value} WHERE chat_id = {ctx.guild.id}")
    conn.commit()
    await ctx.respond("✅ Шанс изменён!", ephemeral = True)

@GROUP_settings.command(name="глобальная_бд", description = "Использовать все сообщения из Базы Данных")
@commands.has_permissions(manage_messages=True)
async def settings__global(ctx: discord.ApplicationContext, value: discord.Option(bool, "Включить?", required=True)):
    await ctx.defer(ephemeral = True)
    
    
    if value is True:
        cur.execute(f"UPDATE cfg SET global = 1 WHERE chat_id = {ctx.guild.id}")
        conn.commit()
        await ctx.respond("✅ Бот теперь будет использовать глобальную БД", ephemeral = True)
    elif value is False:
        cur.execute(f"UPDATE cfg SET global = 0 WHERE chat_id = {ctx.guild.id}")
        conn.commit()
        await ctx.respond("✅ Бот теперь будет использовать локальную БД", ephemeral = True)

@GROUP_settings.command(name="фильтр", description = "Изменить фильтры (True - фильтр будет работать | False - фильтр не будет работать)")
@commands.has_permissions(manage_messages=True)
async def settings__filters(ctx: discord.ApplicationContext, user_ping: discord.Option(bool, "пинг", required=True), role_ping: discord.Option(bool, "пинг ролей", required=True), links: discord.Option(bool, "ссылки", required=True), ban_words: discord.Option(bool, "Бан ворды (маты, расистские выражения и т.д)", required=True)):
    await ctx.defer(ephemeral = True)
    
    params = ""

    if user_ping is True:
        params += "1"
    if role_ping is True:
        params += "2"
    if links is True:
        params += "3"
    if ban_words is True:
        params += "4"

    if params == "":
        params = "0"

    cur.execute(f"UPDATE cfg SET filter = {params} WHERE chat_id = {ctx.guild.id}")
    conn.commit()
    await ctx.respond("✅ Параметры фильтров применены", ephemeral = True)




client.run(token)
