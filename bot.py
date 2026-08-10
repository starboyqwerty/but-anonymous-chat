import config
import telebot
from telebot import types
from database import Database

db = Database('db.db')
bot = telebot.TeleBot(config.TOKEN)

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('👤 Поиск собеседника')
    markup.add (item1)
    return markup

def stop_dialog():
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('🗣 Сказать свой профиль')
    item2 = types.KeyboardButton('/stop')
    markup.add(item1, item2)
    return markup

def stop_search():
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('❌ Остановить поиск')
    markup.add(item1)
    return markup

@bot.message_handler(commands = ['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('🙋‍♂️ Я Парень')
    item2 = types.KeyboardButton('🙋‍♀️ Я Девушка')
    markup.add (item1, item2)

    bot.send_message(message.chat.id, 'Привет {0.first_name}! Добро пожаловать в анонимный чат BUT Family! Укажите ваш пол!' .format(message.from_user), reply_markup=markup)

@bot.message_handler(commands = ['search'])
def search(message):
    if message.chat.type == 'private' and db.get_active_chat(message.chat.id) == False:
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            item1 = types.KeyboardButton('🔎 Парень')
            item2 = types.KeyboardButton('🔎 Девушка')
            item3 = types.KeyboardButton('👫 Рандом')
            markup.add(item1, item2, item3)

            bot.send_message(message.chat.id, 'Кого искать?', reply_markup = markup)
        
    else:
        if db.get_active_chat(message.chat.id) != False:
            chat_info = db.get_active_chat(message.chat.id)
            bot.send_message(message.chat.id, "У вас уже есть собеседник!")
        else:
            bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

@bot.message_handler(commands=['menu'])
def menu(message):
    # Получаем информацию о текущем активном чате
    chat_info = db.get_active_chat(message.chat.id)

    # Создаем клавиатуру для меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('👤 Поиск собеседника')
    markup.add(item1)

    # Если активный чат существует
    if chat_info:
        chat_partner_id = chat_info[1]  # ID собеседника
        db.delete_chat(chat_info[0])  # Удаляем чат из базы данных
        
        # Отправляем сообщение собеседнику и пользователю о завершении чата
        bot.send_message(chat_partner_id, '❌ Собеседник покинул чат!')
        bot.send_message(message.chat.id, '❌ Вы вышли из чата!')
    
    # Отправляем меню
    bot.send_message(message.chat.id, 'Меню', reply_markup=markup)


@bot.message_handler(commands = ['stop'])
def stop(message):
    chat_info = db.get_active_chat(message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('👉 Следующий диалог')
    item2 = types.KeyboardButton('/menu')
    markup.add (item1, item2)

    if chat_info != False:
        db.delete_chat(chat_info[0])
        
        bot.send_message(chat_info[1], '❌ Собеседник покинул чат!', reply_markup=markup)
        bot.send_message(message.chat.id, '❌ Вы вышли из чата!', reply_markup=markup)

    else:
        bot.send_message(message.chat.id, '❌ Вы не начали чат!', reply_markup=markup)

@bot.message_handler(commands=['sendall'])
def sendall(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id == 1399472216:
            text = message.text[9:]  # Извлекаем текст после команды
            users = db.get_users()
            successful_count = 0  # Счетчик успешных рассылок
            failed_users = []  # Список неудачных отправок

            for row in users:
                try:
                    bot.send_message(row[0], text)
                    successful_count += 1
                except Exception as e:
                    # Логируем ошибки в консоль
                    print(f"Ошибка при отправке сообщения пользователю chat_id {row[0]}: {e}")
                    failed_users.append(row[0])  # Добавляем в список неудачных

            # Отправляем администратору результат рассылки
            bot.send_message(message.from_user.id, f'Успешная рассылка! Сообщение отправлено {successful_count} пользователям.')
            if failed_users:
                bot.send_message(message.from_user.id, f'Не удалось отправить сообщение следующим пользователям: {failed_users}')

@bot.message_handler(content_types=['photo'])
def bot_photo(message):
    if message.chat.type == 'private':
        # Проверка, если фото с командой /sendall
        if message.caption and message.caption.startswith('/sendall') and message.from_user.id == 1399472216:
            text = message.caption[9:] if len(message.caption) > 9 else ''
            users = db.get_users()
            successful_count = 0  # Счетчик успешных рассылок
            failed_users = []  # Список неудачных отправок

            for row in users:
                try:
                    bot.send_photo(row[0], message.photo[-1].file_id, caption=text)
                    successful_count += 1
                except Exception as e:
                    # Логируем ошибки в консоль
                    print(f"Ошибка при отправке фото пользователю chat_id {row[0]}: {e}")
                    failed_users.append(row[0])  # Добавляем в список неудачных

            bot.send_message(message.from_user.id, f'Успешная рассылка фото! Отправлено {successful_count} пользователям.')
            if failed_users:
                bot.send_message(message.from_user.id, f'Не удалось отправить фото следующим пользователям: {failed_users}')

        else:
            chat_info = db.get_active_chat(message.chat.id)
            if chat_info:
                try:
                    bot.send_photo(chat_info[1], message.photo[-1].file_id)
                    if message.caption:
                        caption_text = message.caption
                        bot.send_message(chat_info[1], caption_text)
                except Exception as e:
                    # Логируем ошибки в консоль
                    print(f"Ошибка при отправке фото в чат {chat_info[1]}: {e}")
                    bot.send_message(message.chat.id, 'Ошибка при отправке фото')
            else:
                bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

@bot.message_handler(content_types=['video'])
def bot_video(message):
    if message.chat.type == 'private':
        # Проверка, если видео с командой /sendall
        if message.caption and message.caption.startswith('/sendall') and message.from_user.id == 1399472216:
            text = message.caption[9:] if len(message.caption) > 9 else ''
            users = db.get_users()
            successful_count = 0  # Счетчик успешных рассылок
            failed_users = []  # Список неудачных отправок

            for row in users:
                try:
                    bot.send_video(row[0], message.video.file_id, caption=text)
                    successful_count += 1
                except Exception as e:
                    # Логируем ошибки в консоль
                    print(f"Ошибка при отправке видео пользователю chat_id {row[0]}: {e}")
                    failed_users.append(row[0])  # Добавляем в список неудачных

            bot.send_message(message.from_user.id, f'Успешная рассылка видео! Отправлено {successful_count} пользователям.')
            if failed_users:
                bot.send_message(message.from_user.id, f'Не удалось отправить видео следующим пользователям: {failed_users}')

        else:
            chat_info = db.get_active_chat(message.chat.id)
            if chat_info:
                try:
                    bot.send_video(chat_info[1], message.video.file_id)
                    if message.caption:
                        caption_text = message.caption[9:] if len(message.caption) > 9 else ''
                        bot.send_message(chat_info[1], caption_text)
                except Exception as e:
                    # Логируем ошибки в консоль
                    print(f"Ошибка при отправке видео в чат {chat_info[1]}: {e}")
                    bot.send_message(message.chat.id, 'Ошибка при отправке видео')
            else:
                bot.send_message(message.chat.id, '❌ Вы не начали диалог!')







@bot.message_handler(commands = ['showuserid'])
def showuserid(message):
    myuserid = db.get_user(message.chat.id)
    chat_info = db.get_active_chat(message.chat.id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('👤 Поиск собеседника')
    markup.add (item1)

    if chat_info != False:
        db.delete_chat(chat_info[0])
        
        bot.send_message(chat_info[1], '❌ Собеседник покинул чат!', reply_markup=markup)
        bot.send_message(message.chat.id, myuserid, reply_markup=markup)
        bot.send_message(message.chat.id, '❌ Вы покинули чат!', reply_markup=markup)

    else:
        bot.send_message(message.chat.id, myuserid, reply_markup=markup)

@bot.message_handler(commands=['showusername'])
def showusername(message):
    if message.from_user.id == 1399472216:  # проверка, что команда введена админом
        chat_info = db.get_active_chat(message.chat.id)
        
        if chat_info:  # если чат активен
            chat_partner_id = chat_info[1]
            username = db.get_username(chat_partner_id)
            
            if username:  # если у собеседника есть username
                bot.send_message(message.chat.id, f"Username собеседника: @{username[0]}")
            else:
                bot.send_message(message.chat.id, "У собеседника нет username.")
        else:
            bot.send_message(message.chat.id, "Вы не в активном чате!")
    else:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")



@bot.message_handler(commands=['maxuserid'])
def max_user_id(message):
    if message.from_user.id == 1399472216:  # проверка, что команда введена админом
        max_id = db.get_max_user_id()
        bot.send_message(message.chat.id, f"Максимальный ID в таблице users: {max_id}")
    else:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

@bot.message_handler(commands=['count'])
def show_counts(message):
    if message.from_user.id == 1399472216:  # проверка, что команда введена админом
        queue_count = db.get_queue_count()
        chats_count = db.get_chats_count()
        bot.reply_to(message, f"Количество записей в таблице queue: {queue_count}\nКоличество записей в таблице chats: {chats_count}")
    else:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")


@bot.message_handler(commands=['donate'])
def donate(message):
    # Текст сообщения с реквизитами
    donation_text = """
    Спасибо за ваше желание поддержать мой проект! 
    Вы можете сделать пожертвование на карту:

    Uzcard:
    """

    # Номер карты (отправляется отдельно для удобного копирования)
    card_number = "5614 6818 1690 1387"

    # Отправляем сообщение с текстом и отдельно с номером карты
    bot.send_message(message.chat.id, donation_text)
    bot.send_message(message.chat.id, card_number)



@bot.message_handler(commands=['banuser'])
def ban_user(message):
    if message.from_user.id == 1399472216:  # проверка, что команду выполняет админ
        try:
            users = db.get_all_users()  # получаем всех пользователей с их полом и статусом блокировки

            for user in users:
                chat_id = user[0]
                
                # Проверяем, заблокировал ли бот пользователя
                try:
                    bot.send_message(chat_id, 'Проверка блокировки...')
                except telebot.apihelper.ApiTelegramException as e:
                    if e.error_code == 403:
                        # Если бот заблокирован пользователем, обновляем информацию в базе данных
                        db.update_user_ban(chat_id, 1)  # Устанавливаем ban = 1
                        print(f"Пользователь {chat_id} заблокировал бота, обновляем ban в БД.")
                    else:
                        print(f"Ошибка при отправке сообщения пользователю {chat_id}: {e}")

            bot.send_message(message.chat.id, 'Проверка завершена.')
        except Exception as e:
            print(f"Ошибка при выполнении команды /banuser: {e}")
            bot.send_message(message.chat.id, 'Произошла ошибка при проверке пользователей.')
    else:
        bot.send_message(message.chat.id, 'У вас нет прав для выполнения этой команды.')


@bot.message_handler(commands=['searchall'])
def search_all(message):
    import random
    if message.from_user.id == 1399472216:  # проверка, что команду выполняет админ
        try:
            users = db.get_all_users()  # получаем всех пользователей с их полом и статусом блокировки
            available_users = []  # список доступных пользователей для поиска

            # Собираем всех пользователей с их полом, пропуская тех, кто заблокировал бота
            for user in users:
                chat_id = user[0]
                gender = user[1]
                ban_status = user[2]  # получаем статус бана
                
                # Проверяем, заблокирован ли пользователь
                if ban_status == 1:  # Проверяем колонку ban
                    print(f"Пользователь {chat_id} заблокировал бота, пропускаем его.")
                    continue
                
                available_users.append((chat_id, gender))  # добавляем в список доступных пользователей

            # Смешиваем пользователей для поиска собеседников
            random.shuffle(available_users)

            # Пары для поиска собеседников
            while len(available_users) >= 2:
                user_one = available_users.pop()
                user_two = available_users.pop()

                # Пытаемся создать чат между двумя пользователями
                if not db.create_chat(user_one[0], user_two[0]):
                    # Если не удалось создать чат, проверяем пользователей на блокировку и добавляем в очередь
                    for user in [user_one, user_two]:
                        try:
                            bot.send_message(user[0], '👻 Поиск собеседника', reply_markup=stop_search())
                        except telebot.apihelper.ApiTelegramException as e:
                            if e.error_code == 403:
                                print(f"Пользователь {user[0]} заблокировал бота, пропускаем его.")
                                # Если пользователь заблокировал бота, просто пропустим его без выхода из цикла
                                continue
                    # Добавляем пользователей в очередь, если сообщение успешно отправлено
                    db.add_queue(user_one[0], user_one[1])
                    db.add_queue(user_two[0], user_two[1])
                else:
                    # Уведомляем пользователей о том, что собеседник найден
                    mess = 'Собеседник найден! Чтобы остановить диалог, напишите /stop'
                    for user in [user_one, user_two]:
                        try:
                            bot.send_message(user[0], mess, reply_markup=stop_dialog())
                        except telebot.apihelper.ApiTelegramException as e:
                            if e.error_code == 403:
                                print(f"Пользователь {user[0]} заблокировал бота, пропускаем его.")
                                continue  # Пропускаем пользователя

            bot.send_message(message.chat.id, 'Поиск запущен для всех пользователей!')
        except Exception as e:
            print(f"Ошибка при запуске поиска: {e}")
            bot.send_message(message.chat.id, 'Произошла ошибка при запуске поиска.')
    else:
        bot.send_message(message.chat.id, 'У вас нет прав для выполнения этой команды.')









@bot.message_handler(commands=['stopall'])
def stop_all(message):
    if message.from_user.id == 1399472216:  # проверка, что команду выполняет админ
        try:
            # Удаляем все записи из таблицы chats и queue
            db.delete_active_chats()
            db.clear_queue()

            bot.send_message(message.chat.id, 'Все активные чаты и очередь удалены!')
        except Exception as e:
            print(f"Ошибка при удалении активных чатов и очереди: {e}")
            bot.send_message(message.chat.id, 'Произошла ошибка при удалении.')
    else:
        bot.send_message(message.chat.id, 'У вас нет прав для выполнения этой команды.')







@bot.message_handler(commands=['support'])
def support(message):
    support_text = "По вопросам багов, предложений или рекламы вы можете обратиться сюда 👉 @amar_farkhadi"
    bot.send_message(message.chat.id, support_text)

@bot.message_handler(content_types = ['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == '👤 Поиск собеседника' or message.text == '👉 Следующий диалог':
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            item1 = types.KeyboardButton('🔎 Парень')
            item2 = types.KeyboardButton('🔎 Девушка')
            item3 = types.KeyboardButton('👫 Рандом')
            markup.add(item1, item2, item3)

            bot.send_message(message.chat.id, 'Кого искать?', reply_markup = markup)
            

        elif message.text == '❌ Остановить поиск':
            db.delete_queue(message.chat.id)
            bot.send_message(message.chat.id, '❌ Поиск остановлен', reply_markup = main_menu())

        elif message.text == '🔎 Парень':
            user_info = db.get_gender_chat('male')
            chat_two = user_info[0]

            if db.create_chat(message.chat.id, chat_two) == False:
                # Получаем значение пола в отдельную переменную
                gender = db.get_gender(message.chat.id)
                # Передаём переменную gender в add_queue
                db.add_queue(message.chat.id, gender)
                bot.send_message(message.chat.id, '👻 Поиск собеседника', reply_markup=stop_search())
            else:
                mess = 'Собеседник найден! Чтобы остановить диалог, напишите /stop'
                bot.send_message(message.chat.id, mess, reply_markup=stop_dialog())
                bot.send_message(chat_two, mess, reply_markup=stop_dialog())

        elif message.text == '🔎 Девушка':
            user_info = db.get_gender_chat('female')
            chat_two = user_info[0]

            if db.create_chat(message.chat.id, chat_two) == False:
                # Получаем значение пола в отдельную переменную
                gender = db.get_gender(message.chat.id)
                # Передаём переменную gender в add_queue
                db.add_queue(message.chat.id, gender)
                bot.send_message(message.chat.id, '👻 Поиск собеседника', reply_markup=stop_search())
            else:
                mess = 'Собеседник найден! Чтобы остановить диалог, напишите /stop'
                bot.send_message(message.chat.id, mess, reply_markup=stop_dialog())
                bot.send_message(chat_two, mess, reply_markup=stop_dialog())

        elif message.text == '👫 Рандом':
            user_info = db.get_gender_chat('male' or 'female')
            chat_two = user_info[0]

            if db.create_chat(message.chat.id, chat_two) == False:
                # Получаем значение пола в отдельную переменную
                gender = db.get_gender(message.chat.id)
                # Передаём переменную gender в add_queue
                db.add_queue(message.chat.id, gender)
                bot.send_message(message.chat.id, '👻 Поиск собеседника', reply_markup=stop_search())
            else:
                mess = 'Собеседник найден! Чтобы остановить диалог, напишите /stop'
                bot.send_message(message.chat.id, mess, reply_markup=stop_dialog())
                bot.send_message(chat_two, mess, reply_markup=stop_dialog())

        elif message.text == '🗣 Сказать свой профиль':
            chat_info = db.get_active_chat(message.chat.id)
            if chat_info != False:
                if message.from_user.username:
                    bot.send_message(chat_info[1], '@' + message.from_user.username)
                    bot.send_message(message.chat.id, '🗣 Вы сказали свой профиль')
                else:
                    bot.send_message(message.chat.id, '🗣 В вашем аккаунте не указан username')
            else:
                bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

        elif message.text == '🙋‍♂️ Я Парень':
            if db.set_gender(message.chat.id, 'male', message.chat.username):
                bot.send_message(message.chat.id, '✅ Ваш пол успешно добавлен!', reply_markup = main_menu())
            else:
                bot.send_message(message.chat.id, '❌ Вы уже указали свой пол, обратитесь в поддержку @amar_farkhadi')

        elif message.text == '🙋‍♀️ Я Девушка':
            if db.set_gender(message.chat.id, 'female', message.chat.username):
                bot.send_message(message.chat.id, '✅ Ваш пол успешно добавлен!', reply_markup = main_menu())
            else:
                bot.send_message(message.chat.id, '❌ Вы уже указали свой пол, обратитесь в поддержку @amar_farkhadi')

        else:
            if db.get_active_chat(message.chat.id) != False:
                chat_info = db.get_active_chat(message.chat.id)
                bot.send_message(chat_info[1], message.text)
            else:
                bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

@bot.message_handler(content_types=['sticker'])
def bot_stickers(message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            try:
                bot.send_sticker(chat_info[1], message.sticker.file_id)
            except Exception as e:
                bot.send_message(message.chat.id, f"Ошибка при отправке стикера:")
        else:
            bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

@bot.message_handler(content_types=['voice'])
def bot_voice(message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            try:
                bot.send_voice(chat_info[1], message.voice.file_id)
            except Exception as e:
                bot.send_message(message.chat.id, f"Ошибка при отправке голосового сообщения")
        else:
            bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

@bot.message_handler(content_types=['video_note'])
def bot_video_note(message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            try:
                bot.send_video_note(chat_info[1], message.video_note.file_id)
            except Exception as e:
                bot.send_message(message.chat.id, f"Ошибка при отправке круглого видео")
        else:
            bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

@bot.message_handler(content_types=['animation'])
def bot_gif(message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            try:
                bot.send_animation(chat_info[1], message.animation.file_id)
            except Exception as e:
                bot.send_message(message.chat.id, f"Ошибка при отправке GIF")
        else:
            bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

@bot.message_handler(content_types=['audio'])
def bot_audio(message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            try:
                bot.send_audio(chat_info[1], message.audio.file_id)
            except Exception as e:
                bot.send_message(message.chat.id, "Ошибка при отправке аудио")
        else:
            bot.send_message(message.chat.id, '❌ Вы не начали диалог!')


bot.polling(none_stop = True)
