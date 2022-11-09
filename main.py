import pandas as pd
import telebot
from telebot import types
import cv2
import random
from PIL import ImageFile, Image
# ImageFile.LOAD_TRUNCATED_IMAGES = True

# Определяем константы
puzzle_txt = "txt/puzzle.txt"
puzzle_img = r"img/puzzle.png"
start_stack = "000000000000000000000000"
full_stack = "111111111111111111111111"
img_full = r"img/FP_puzzle_full.png"
img0_full_q = "img/img0_full_q.png"

arr_rnd_old = ["Это уже было!",
               "Давай, найдем что-то новенькое!",
               "Не успел, кто-то нашел это слово раньше!",
               "Хороший вариант, правда его уже нашли",
               "Правильно, но найдено",
               "Может есть еще варианты? Этот мы уже зачли."]

arr_rnd_ans = ["Откуда это вообще?",
               "Что-то не похоже на ключ",
               "Определенно нужно поискать где-то еще",
               "Лучше не пытаться угадать",
               "Близко, но всё же не то",
               "Холодно"]

kw = pd.read_csv('txt/kw.csv')

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton("Посмотреть мозайку")
btn2 = types.KeyboardButton("Кто молодец?")
markup.add(btn1, btn2)

def create_puzzle(el):
    f = open(puzzle_txt, "r+")  # открытие в режиме записи
    stack = f.read()
    f.close()
    if stack == full_stack:
        puzzle = Image.open(img_full)
        puzzle.save(puzzle_img, format="png")
        puzzle.close()
    else:
        puzzle = Image.open(img0_full_q).convert('RGBA')
        for i in range(len(kw)):
            if (stack[i] == "1"):
                element_name = r"img/img" + str(kw["num"][i]) + ".png"
                element = Image.open(element_name).convert('RGBA')
                puzzle.paste(element, (kw["x"][i], kw["y"][i]), mask=element)
                element.close()
        puzzle.save(puzzle_img, format="png")
        puzzle.close()

# Создаем экземпляр бота
bot = telebot.TeleBot('5285556970:AAGHWxhjE7opKN85NP6eaXfYBPmm4n5qwjE')
# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    create_puzzle(-1)
    puzzle = open(puzzle_img, 'rb')
    bot.send_photo(m.chat.id,
                   puzzle,
                   caption="Привет, мы хотим сыграть с тобой в одну игру. "
                           "Находи специальные коды и открывай пазл, чтобы узнать что здесь спрятано.",
                   reply_markup=markup)
    puzzle.close()

# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.lower() in kw["kw"].tolist():
        ind = kw["kw"].tolist().index(message.text.lower())
        f = open(puzzle_txt, "r+")  # открытие в режиме записи
        s = f.read()
        if (s[ind] == "1"):
            bot.send_message(message.chat.id, arr_rnd_old[random.randint(0, 5)], reply_markup=markup)
        else:
            new_stack = s[:ind] + '1' + s[ind + 1:]
            f.seek(0)
            f.write(new_stack)
            f.close()
            user_list = pd.read_csv('txt/users.csv')
            #if user_list[user_list['num'] == message.chat.id]:
            #    user_list[user_list['num'] == message.chat.id][''] += 1
            #else:
            #user_list.loc[len(user_list.index)] = [message.chat.id, 'AAAAA', kw["kw"][ind]]
            #new_row = pd.Series(data=[message.chat.id, 'AAAAA', kw["kw"][ind]], index=['num', 'name', 'word'])
            user_name = message.chat.first_name
            if isinstance(message.chat.last_name, str):
                user_name += ' ' + message.chat.last_name
            if isinstance(message.chat.username, str):
                user_name += ' (' + message.chat.username + ')'
            new_row = {'num': message.chat.id,
                        'name': user_name,
                        'word': kw["kw"][ind]}
            #print(new_row)
            user_list = user_list.append(new_row, ignore_index=True)
            user_list.to_csv('txt/users.csv', index=False)

            create_puzzle(ind)
            puzzle = open(puzzle_img, 'rb')
            bot.send_photo(message.chat.id, photo=puzzle, caption=kw["kw_ans"][ind], reply_markup=markup)
            puzzle.close()
    elif message.text == "Посмотреть мозайку":
            while True:
                try:
                    Image.open(puzzle_img).load()
                    puzzle = open(puzzle_img, 'rb')
                    print(str(message.chat.id) + " - show puzzle. Ok")
                    break
                except:
                    create_puzzle(-1)
                    puzzle = open(puzzle_img, 'rb')
                    print(str(message.chat.id) + " - show puzzle. Error. Rebuild")
            bot.send_photo(message.chat.id, photo=puzzle, caption="Как-то так", reply_markup=markup)
            puzzle.close()
    elif message.text == "Кто молодец?":
            user_list = pd.read_csv('txt/users.csv')
            top_user = user_list.groupby('name')[['num']].count().sort_values(by='num', ascending=False)
            # print(top_user.to_string(header=False))
            bot.send_message(message.chat.id, top_user.to_string(header=False, index_names=False), reply_markup=markup)
    elif message.text == "ccclear":
        f = open(puzzle_txt, 'w')  # открытие в режиме записи
        f.write(start_stack)
        f.close()
        user_list = pd.read_csv('txt/users0.csv')
        user_list.to_csv('txt/users.csv', index=False)
        puzzle = Image.open(img0_full_q)
        puzzle.save(puzzle_img, format="png")
        bot.send_photo(message.chat.id,
                       puzzle,
                       caption="Пазл был очищен! Давай попробуем начать всё с начала.",
                       reply_markup=markup)
        puzzle.close()
    else:
        bot.send_message(message.chat.id, arr_rnd_ans[random.randint(0, 5)], reply_markup=markup)
# Запускаем бота
bot.polling(none_stop=True, interval=0)