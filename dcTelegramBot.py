from time import sleep
from aiogram import *
from aiogram.types import *
import requests
from random import randint, shuffle

bot = Bot(
    token="5387222261:AAH5UW5JoUeyJqWma0pXvjzm7dIPN2560t8"
)  # BotFather-ın verdiyi token
dp = Dispatcher(bot)


is_game_start = False
players = (
    dict()
)  # Oyunçuların adlarının və id-lərinin tutulduğu dictinoary key: name, value: id
players_name = list(players.keys())  # Oyunçuların adlarının sırası
truth_questions = (
    requests.get(
        "https://raw.githubusercontent.com/AlifaghaSalmanov/DcTelegramBot/main/DogruluqSuallarFlitertxt"
    )
    .text[:-1]
    .split("\n")
)  # Dogruluq sualları
dare_questions = (
    requests.get(
        "https://raw.githubusercontent.com/AlifaghaSalmanov/DcTelegramBot/main/CesaretSuallar.txt"
    )
    .text[:-1]
    .split("\n")
)  # Cesaret sualları

# inline yəni, ekranda göstrəndə açılan buttonlar
# callback_data -da olan string text formasında callback_query tərəfindən tutulur

button1 = InlineKeyboardButton(text="Oyuna qatıl", callback_data="joinGame")
button2 = InlineKeyboardButton(text="Oyuna başlat", callback_data="nextQuestion")

keyboard_inline = InlineKeyboardMarkup(resize_keyboard=True).add(button1).add(button2)

button3 = InlineKeyboardButton(text="Doğruluq", callback_data="Truth")
button4 = InlineKeyboardButton(text="Cəsarət", callback_data="Dare")

keyboard_inline_Truth_Dare = (
    InlineKeyboardMarkup(resize_keyboard=True).add(button3).add(button4)
)

button5 = InlineKeyboardButton(text="Hazır", callback_data="nextQuestion")

keyboard_inline_next = InlineKeyboardMarkup(resize_keyboard=True).add(button5)


msg_id = int()  # nəyə işə yaradığını mən bilə unutdum
chatId = (
    int()
)  # hər telegram qrupun id-si olur. bot-a hansı id-yə nəyi yazması üçün grupun id-sini tutur
prvs_msg_id = (
    int()
)  # özündən əvvəlki buttonlu mesajın id-sini tutur və o buttonu silir ki, təzədən basıla bilməsin
first = True  # oyun ilk başlayanda Bir çox problemin qabağını almaq üçün işlədirəm
skip = False  # skip komutunu basanda true olub hazırki sualı keçir

question_type = ""  # istənilən sualın doğruluq yoxsa cəsarət olduğunu tutub, ona uyğun sual və animasya göstərir
choosen_name = str()  # suala cavab verməli olan nəfərin adını tutur
choosen_id = (
    int()
)  # suala cavab verməli olan nəfərin id-sini tutub, onun mention eləməkdə kömək eləyir

# anlıq iştirakçıların sayı
def numberOfPlayers():
    return f"\n\n🏄‍♂️İştirakçı say:{len(players)}"


# oyun ilk başlananda çıxan mesaj
def startTemplate():
    str = (
        f"✨Oyuna qeydiyyat başladı :\n"
        + numberOfPlayers()
        + "\n"
        + ", ".join(players.keys())
    )
    return str


# ilk başlayanda oyuna oyunçu əlavə ediləndə və ya join yazıb girəndə
# ilk mesajdakı oyunçu sayını dəyişməyi və oyunçunun adını yazması üçündü
def editStartMessage():
    return bot.edit_message_text(
        startTemplate(),
        reply_markup=keyboard_inline,
        message_id=msg_id,
        chat_id=chatId,
    )


# oyundakı hamının sırası bitdikdə təzədən oyun sırası yaradır
def randomPlayer():
    global players_name
    players_name = list(players.keys())
    shuffle(players_name)


# start yazanda oyun başlama mesajları filan üçün
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    global is_game_start
    if not is_game_start:
        msg = await message.answer(
            startTemplate(),
            reply_markup=keyboard_inline,
        )
        global msg_id
        global chat_id
        msg_id = msg["message_id"]
        chat_id = msg["chat"]["id"]  # id-ni götürürük ki, gələcəkdə silə bilək
        is_game_start = True


# oyuna /join yazıb daxil olmaq üçün
@dp.message_handler(commands=["join"])
async def joinGame(message: types.Message):
    if is_game_start:
        global players_name
        name = message.from_user.first_name
        if not name in players.keys():
            id = message.from_user.id
            players[name] = id
            players_name.append(name)
            await message.answer(f"🎉{name} oyuna qatıldı" + numberOfPlayers())
            await editStartMessage()


# oyundan çıxmaq üçündü
@dp.message_handler(commands=["quit"])
async def quitGame(message: types.Message):
    if is_game_start:
        name = message.from_user.first_name
        del players[name]
        await message.reply(f"😕{name} oyundan çıxdı" + numberOfPlayers())
        await editStartMessage()


# oyunu dayandırmaq üçün
@dp.message_handler(commands=["stop"])
async def stop(message: types.Message):
    global is_game_start, first
    is_game_start = False
    first = True
    players.clear()
    await message.answer("❌OYUN BİTDİ!")


# hazırkı oyununçunun sırasını pas keçib digərinə keçmək
@dp.message_handler(commands=["skip"])
async def skip(message: types.Message):
    global skip, question_type
    question_type = "ask"
    skip = True
    await editReplyMarkup()
    await askQuestion(message.from_user.first_name, bot.send_animation)


# Sualın tipinə baxıb hansı gif-i işlədəcəyini seçir
def animation():
    global question_type
    if question_type == "ask":
        return "https://s.yimg.com/ny/api/res/1.2/Wy0iRGCDEDB0WYuqs7UBfg--/YXBwaWQ9aGlnaGxhbmRlcjt3PTY0MDtoPTMyMA--/https://s.yimg.com/uu/api/res/1.2/xIreTrVONTn58HosFX.NwA--~B/aD03MjA7dz0xNDQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/cosmo_633/2077cd9584a6323a0947e622fde511f6"
    elif question_type == "truth":
        return "https://i.gifer.com/VbTy.gif"
    return "https://i.imgur.com/6mE5aTP.gif"  # dare olanda


# Dogruluq yoxsa Cəsarət seçimini verən funksiyion
async def askQuestion(user_name, func):
    global first, skip, choosen_name, msg_id, chatId, prvs_msg_id
    # sırası olan oyunçu list-in ən başından seçilir
    choosen_name = players_name[0]

    # Hazıra basan oyunçunun sırası olan oyunuçunun olub-olmamasını yoxlayır
    # skip yazılıb yazılmamsını yoxlayır
    # oyun ilk başlayanda heç kimin sırası olmadığına görə "first" yəni oyuna ilk başlayanda keçə bilsin
    if choosen_name == user_name or skip or first:
        # ikinci oyundan artıq digər oyunçuların sırası gəlməsi üçün
        # ilk başdakı seçilən oyunçunun adı silinmək üçündür
        if not first:
            try:
                players_name.pop(0)  # ilk oyunçunu silir
                choosen_name = players_name[0]  # yeni bir oyunçunun sırası gəlir
            except:
                randomPlayer()  # bütün oyunçuların sırası bitdikdə təzədən sıraya salmaq üçün
                choosen_name = players_name[0]  # yenidən ilk oyunçunu seçir

        await editReplyMarkup()
        choosen_id = players[players_name[0]]
        msg = await func(
            animation=animation(),
            caption=f"[{choosen_name}](tg://user?id={choosen_id}), Seçimini et..\n\n",
            parse_mode="markdown",  # oyunçunu mention eləmək üçündü
            reply_markup=keyboard_inline_Truth_Dare,  # əlavə edilən buttonları göstərmək üçün
            chat_id=chatId,
        )
        msg_id = msg["message_id"]
        prvs_msg_id = msg["message_id"]
        first = False


# Özündən əvvəlki buttonlu mesajdakı buttonu ləğv eləyir ki
# təzədən ona basıla bilməsin
async def editReplyMarkup():
    global chatId, prvs_msg_id
    try:
        await bot.edit_message_reply_markup(
            chat_id=chatId, message_id=prvs_msg_id, reply_markup=None
        )
    except:
        pass


# Doğruluq və ya Cəsarət button-nuna basanda işləyir
# nəyi seçdiyini tutub, ona uyğun sual verir
@dp.callback_query_handler(text=["Truth", "Dare"])
async def truthDare(call: types.CallbackQuery):
    global first, skip, question_type, msg_id, chatId, prvs_msg_id, choosen_name, players_name
    if call.from_user.first_name == choosen_name:
        await editReplyMarkup()

        # özündən əvvəlki "Seçimini elə" yerini silir ki, boşa yer tutmasın
        await bot.delete_message(message_id=msg_id, chat_id=chatId)
        string = str()
        # Dogru ya da Cəsarət seçdiyini yoxlayır
        if call.data == "Truth":
            question_type = "truth"
            choosen_question = truth_questions[randint(0, len(truth_questions) - 1)]
            string = "Mənim sualım:"
        else:
            question_type = "dare"
            choosen_question = dare_questions[randint(0, len(dare_questions) - 1)]
            string = "Cəsarətini sübut et:"

        msg = await bot.send_animation(
            animation=animation(),
            caption=f"Əla [{choosen_name}](tg://user?id={choosen_id}), {string}\n\n{choosen_question}\n\n-",
            parse_mode="markdown",
            reply_markup=keyboard_inline_next,
            chat_id=chatId,
        )
        prvs_msg_id = msg["message_id"]
        first = False
        skip = False


# oyuna start elədikdən sonra girəndə "Oyuna qatıl"-a basanda (joinGame işləyir)
# ya da "Hazır" düyməsinə basanda işləyir (nextQuestion işləyir)
@dp.callback_query_handler(text=["joinGame", "nextQuestion"])
async def nextQuestion(call: types.CallbackQuery):
    if is_game_start:
        global first, players_name, question_type, chatId, msg_id
        chatId = call.message.chat.id
        # Oyuna qatılırsa oyunçuları əlavə eləyir və ilk mesajı editləyir
        if call.data == "joinGame":
            name = call.from_user.first_name
            if not name in players.keys():  # əgər eyni adlı başqa adam yoxdusa.
                id = call.from_user.id
                players[name] = id
                await editStartMessage()  # ilk mesajı editləyir
        # hazır-a basanda digər sualı göstərmək üçündü
        if call.data == "nextQuestion" and len(players):
            question_type = "ask"  # sualın tipi dəyişir

            # ilk başda olan ("start" yazanda gələn) mesaj bölməsini boş yer tutmasın deyə silir
            # və Oyunçuların oynama sırasını qurur
            if first:
                await bot.delete_message(
                    message_id=msg_id, chat_id=chatId
                )  # ilk mesajı silmək
                randomPlayer()  # oyunçuların oynama sırası
            # "Dogruluq yoxsa Cəsarət ?" sualını soruşmaq üçün göndərilən funksiyon
            await askQuestion(
                call.from_user.first_name,  # adını hazıra basanın sırası olan oynuçunun olub-olmaması üçün götürürk
                bot.send_animation,
            )


# Kodun axırnda olmalıdı ki, kod işləsin
executor.start_polling(dp)
