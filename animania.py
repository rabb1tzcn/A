import telebot, re, sys
from datetime import date
from config import tok_tg
import os
import random
import read_excel
from base_TG import SQLighter

bot = telebot.TeleBot(tok_tg)
cur_date = date.today()
db = SQLighter('TG.db')  #Соединение БД с Telegram


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == "group":
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=12, resize_keyboard=True, one_time_keyboard= True)
        keyboard.row('/reg_group')
        bot.send_message(message.chat.id, 'Э-эмм... п-привет... '
                                          '\nЯ - Р-рами, бот, с-созданный для облегчения учебного п-процесса.'
                                          '\nВ-ведите /reg_group чтобы п-продолжить', reply_markup=keyboard)
    
    elif message.chat.type == "private":
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=12, resize_keyboard=True, one_time_keyboard= True)
        keyboard.row('/reg_teacher')
        bot.send_message(message.chat.id, 'Э-эмм... п-привет... '
                                          '\nЯ - Р-рами, бот, с-созданный для облегчения преподавательского п-процесса.'
                                          '\nВ-ведите /reg_teacher чтобы п-продолжить', reply_markup=keyboard)


@bot.message_handler(commands=['reg_group'], content_types=['text'])
def registration_group(message):
    if message.chat.type == "group":
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=12, resize_keyboard=True, one_time_keyboard=True)
        if len(db.get_search(f'SELECT id_group FROM tg_group WHERE id_group = {message.chat.id}')):
            keyboard.row('Продолжить')
            bot.send_message(message.chat.id, 'Ваш id уже есть в базе данных', reply_markup=keyboard)
        else:
            msg = bot.send_message(message.chat.id, 'В-введите вашу группу п-по примеру - ИС-3-2 :')
            bot.register_next_step_handler(msg, reg_continue_group)


def reg_continue_group(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=12, resize_keyboard=True)
    group = len(db.get_search(f'SELECT " group_id", group_name FROM VTK_Groups WHERE group_name = "{message.text.upper()}";'))
    if group != 0:  # Есть ли такая группа
        keyboard.row('Продолжить')
        db.add_chat(message.chat.id, message.text.upper())
        bot.send_message(message.chat.id, 'В-ваша г-группа занесена в б-базу данных', reply_markup=keyboard)
    else:
        keyboard.row('/reg_group')
        bot.send_message(message.chat.id, 'Н-неверный формат! \nН-напиши /reg_group или нажми к-кнопу чтобы вернуться', reply_markup=keyboard)
    

    
@bot.message_handler(commands=['reg_teacher'], content_types=['text'])
def registration_teacher(message):
    if message.chat.type == "private":
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=12, resize_keyboard=True, one_time_keyboard=True)
        if len(db.get_search(f'SELECT id_groupi FROM tg_teacher WHERE id_groupi = {message.chat.id}')):
            keyboard.row('Продолжить')
            bot.send_message(message.chat.id, 'В-вы уже есть в б-базе данных', reply_markup=keyboard)
        else:
            msg = bot.send_message(message.chat.id, 'В-введите ваше Ф.И.О по примеру - Гребенкина М.Д. :')
            bot.register_next_step_handler(msg, reg_continue_teacher)
        
        
def reg_continue_teacher(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=12, resize_keyboard=True)
    group = len(db.get_search(f'SELECT " teacher_id", teacher_name FROM VTK_Teacher WHERE teacher_name = "{message.text.title()}";'))
    if group != 0:  # Есть ли такой преподаватель
        keyboard.row('Продолжить')
        db.add_teachers(message.chat.id, message.text.title())
        bot.send_message(message.chat.id, 'В-вы были внесены в б-базу данных', reply_markup=keyboard)
    else:
        keyboard.row('/reg_teacher')
        bot.send_message(message.chat.id, 'Н-неверный формат! \nН-напиши /reg_teacher или нажми к-кнопу чтобы вернуться', reply_markup=keyboard)



@bot.message_handler(content_types=['text'])
def send_text(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=12, resize_keyboard=True, one_time_keyboard= True)

    if message.chat.type == "group":
    
        punctuation = '!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'
        if len(db.get_search(f'SELECT id_group FROM tg_group WHERE id_group = {message.chat.id}')):
            name_group = " ".join(str(x) for x in db.get_group(message.chat.id))
            for p in punctuation:
                if p in name_group:
                    # Банальная замена символа в строке
                    name_group = name_group.replace(p, '')
                    name_group = name_group.replace(' ', '')

        if len(db.get_search(f'SELECT id_group FROM tg_group WHERE id_group = {message.chat.id}')):
            # Команды доступные только если группа зарегистрирована
            if message.text.lower() == 'меню' or message.text.lower() == 'продолжить':
                keyboard.row('Расписание', '/help')
                bot.send_message(message.chat.id, 'Т-ты в Главном меню, п-пожалуйста, выбери д-действие', reply_markup=keyboard)
            elif message.text.lower() == '/help' or message.text.lower() == 'вернуться':
                keyboard.row('Расписание')
                keyboard.row('Обновление группы')
                keyboard.row('Звонки')
                keyboard.row('Котя')
                keyboard.row('Меню')
                keyboard.row('/about')
                bot.send_message(message.chat.id,   'З-здесь ты можешь увидеть все д-доступные для меня действия:'
                                                    '\nРасписание - я п-покажу тебе расписание.'
                                                    '\nОбновление группы - т-тут ты сможешь об-бновить свою группу'
                                                    '\nЗвонки - здесь ты сможешь увидеть р-расписание звонков.'
                                                    '\nКотя - т-тут есть м-милые котики.'
                                                    '\nМеню - я в-верну тебя в г-главное меню.'
                                                    '\n/about - з-здесь написано н-немного информации о-обо м-мне'
                                                    'Ещё я умею:'
                                                    '\n"/next" - эта команда позволяет запросить расписание на следующий день.'
                                                    '\n"/prev" - эта команда позволяет запросить расписание на предыдущий день.'
                                                    '\n"/update" - эта команда позволяет обновить группу.'
                                                    '\nВозможно я ещё чему-то научусь, но это не точно.', reply_markup=keyboard)

            elif message.text.lower() == 'котя':
                keyboard.row('Вернуться')
                photo = open('cisci/' + random.choice(os.listdir('cisci')), 'rb')
                bot.send_photo(message.chat.id, photo, caption='В-вот твой котя...'
                                                               '\nЕсли х-хочешь вернуться, н-напиши "Вернуться"', reply_markup=keyboard)
            elif message.text.lower() == 'звонки':
                keyboard.row('Вернуться')
                if cur_date.weekday() != 1:
                    bot.send_message(message.chat.id,' 1 пара: 8:30 - 9:50 \n2 пара: 10:00 - 11:20 \n3 пара: 11:30 - 12:50 \n4 пара: 13:10 - 14:30 \n5 пара: 14:40 - 16:00 \n6 пара: 16:10 - 17:40 \n7 пара: 17:50 - 19:10 \nВ-вернёмся?', reply_markup=keyboard)
                else:
                    bot.send_message(message.chat.id,' 1 пара: 8:30 - 9:50 \n2 пара: 10:00 - 11:20 \n3 пара: 11:30 - 12:50 \nКлассный час: 13:00 - 13:40 \n4 пара: 13:50 - 15:10 \n5 пара: 15:20 - 16:40 \n6 пара: 16:50 - 18:10 \n7 пара: 18:20 - 19:40 \nВ-вернёмся?', reply_markup=keyboard)
            elif message.text.lower() == 'расписание':
                read_excel.Get_Group(name_group, 1, 0)
                bot.send_message(message.chat.id, '\n'.join(read_excel.time_table))
                read_excel.deleted()
            elif message.text.lower() == 'обновление группы':
                bot.send_message(message.chat.id, 'Если ты точно хочешь обновить группу напиши "/update"')
            elif message.text.lower() == "/update":
                keyboard.row('/reg_group')
                bot.send_message(message.chat.id, 'Ваша группа удалена из БД. \nНапишите /reg_group для регистрации новой', reply_markup=keyboard)
                db.get_search(f'DELETE FROM TG_group WHERE id_group = {message.chat.id}')  # Удаление группы из БД
            elif message.text.lower() == "/next":
                read_excel.Get_Group(name_group, 1, 1)
                bot.send_message(message.chat.id, '\n'.join(read_excel.time_table))
                read_excel.deleted()
            elif message.text.lower() == "/prev":
                read_excel.Get_Group(name_group, 1, -1)
                bot.send_message(message.chat.id, '\n'.join(read_excel.time_table))
                read_excel.deleted()
            elif message.text.lower() == '/about':
                bot.send_message(message.chat.id, 'Т-ты н-наверное уже знаешь... Н-но я п-представлюсь еще раз. Я - Р-рами.'
                                                  '\nЯ б-была создана д-для т-того, чтобы п-помогать получать л-людям н-нужную им и-информация.'
                                                  '\nТ-также у м-меня есть с-сестра - Р-реми. М-мы спокойно жили в н-нашем мире - Альтере, н-но одно с-событие полностью из-зменило наши жизни...  '
                                                  '\nИменно п-после этого я и начала заикаться. Н-наш мир начал медленно разрушаться, и м-мы с с-сестрой решили п-покинуть его.'
                                                  '\nН-наши знания п-позволяли осуществить п-переход из одного мира в д-другой, н-но мы д-допустили ошибку...'
                                                  '\nП-портал сработал не так к-кам мы ожидали, и отправил н-нас прямо на с-суд к Великому Царю Эмме.'
                                                  '\nЭмма – Б-бог загробного мира, р-решающий судьбу в-всех существ п-после их смерти. Н-но мы были уверены - мы в-все еще живы.'
                                                  '\nОб этом боге мы з-знали м-многое - в н-нашем мире было множество рассказов о нём. Н-но самая главная его особенность - он был очень жестокий.'
                                                  '\nЯ д-до сих пор не верю, что все рассказы что я п-помню об этом существе - ложь. Эмма - справедливый и праведный, но никак не жестокий...'
                                                  '\nВедь если бы э-эти рассказы оказались п-правдой - я бы не с-смогла сейчас поговорить с вами. Он помог нам с с-сестрой вернуться обратно в м-мир живых'
                                                  '\nНо с о-одним условием - мы должны р-разделиться'
                                                  '\nС-сестренка отправилась в м-мир "Вконтакте", меня же отправили в мир под названием "Телеграм", но мы все еще можем общаться и видеться друг с другом.'
                                                  '\nВсе эт-то возможно благодаря создателю этих миров - Богу Павлу. Он помогает нам с сестренкой во всем, взамен же мы должны помогать людям, если они об этом попросят'
                                                  '\nТакже, у этого бога есть два преспешника, о них мы знаем соврешенно немного, только то, что найти их можно по этим адресам:'
                                                  '\nhttps://vk.com/id399673347'
                                                  '\nhttps://vk.com/tvoy_batya_322'
                                                  '\nВ-вот и вся и-история. Н-надеюсь, тебе было интересно...')
            else:
                keyboard.row('/help')
                bot.send_message(message.chat.id, 'Я тебя н-не понимаю... Н-напиши /help, т-так ты сможешь у-узнать что я у-умею...', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'В-вы не з-зарегистрированы\nП-пожалуйста, введите /reg_group ')

    elif message.chat.type == "private":
        # Создание отчистки для сообщений и получение имени преподавателя
        
        punctuation = '!"#$%&\'()*+,/:;<=>?@[\\]^_`{|}~-'
        if len(db.get_search(f'SELECT id_groupi FROM tg_teacher WHERE id_groupi = {message.chat.id}')):
            name_group = " ".join(str(x) for x in db.get_teacher(message.chat.id))
            for p in punctuation:
                if p in name_group:
                    # Банальная замена символа в строке
                    name_group = name_group.replace(p, '')

        if len(db.get_search(f'SELECT "id_groupi" FROM tg_teacher WHERE id_groupi = {message.chat.id};')):
        # Команды доступные только если группа зарегистрирована
            if message.text.lower() == 'меню' or message.text.lower() == 'продолжить':
                keyboard.row('Расписание', '/help')
                bot.send_message(message.chat.id, 'Т-ты в Главном меню, п-пожалуйста, выбери д-действие', reply_markup=keyboard)
            elif message.text.lower() == '/help' or message.text.lower() == 'вернуться':
                keyboard.row('Расписание')
                keyboard.row('Сменить преподавателя')
                keyboard.row('Звонки')
                keyboard.row('Котя')
                keyboard.row('Меню')
                keyboard.row('/about')
                bot.send_message(message.chat.id,   'З-здесь ты можешь увидеть все д-доступные для меня действия:'
                                                    '\nРасписание - я п-покажу тебе расписание.'
                                                    '\nСменить преподавателя - т-тут ты можешь п-поменять преподавателя'
                                                    '\nЗвонки - з-здесь ты сможешь увидеть р-расписание звонков.'
                                                    '\nКотя - т-тут есть м-милые котики.'
                                                    '\nМеню - я в-верну тебя в г-главное меню.'
                                                    '\n/about - з-здесь написано н-немного информации о-обо м-мне'
                                                    'Ещё я умею:'
                                                    '\n"/next" - эта команда позволяет запросить расписание на следующий день.'
                                                    '\n"/prev" - эта команда позволяет запросить расписание на предыдущий день.'
                                                    '\n"/update" - эта команда позволяет обновить группу.'
                                                    '\nВозможно я ещё чему-то научусь, но это не точно.', reply_markup=keyboard)
            elif message.text.lower() == 'котя':
                keyboard.row('Вернуться')
                photo = open('cisci/' + random.choice(os.listdir('cisci')), 'rb')
                bot.send_photo(message.chat.id, photo, caption='В-вот твой котя...'
                                                               '\nЕсли х-хочешь вернуться, н-напиши "Вернуться"', reply_markup=keyboard)
            elif message.text.lower() == 'звонки':
                keyboard.row('Вернуться')
                if cur_date.weekday() != 1:
                    bot.send_message(message.chat.id,' 1 пара: 8:30 - 9:50 \n2 пара: 10:00 - 11:20 \n3 пара: 11:30 - 12:50 \n4 пара: 13:10 - 14:30 \n5 пара: 14:40 - 16:00 \n6 пара: 16:10 - 17:40 \n7 пара: 17:50 - 19:10 \nВ-вернёмся?', reply_markup=keyboard)
                else:
                    bot.send_message(message.chat.id,' 1 пара: 8:30 - 9:50 \n2 пара: 10:00 - 11:20 \n3 пара: 11:30 - 12:50 \nКлассный час: 13:00 - 13:40 \n4 пара: 13:50 - 15:10 \n5 пара: 15:20 - 16:40 \n6 пара: 16:50 - 18:10 \n7 пара: 18:20 - 19:40 \nВ-вернёмся?', reply_markup=keyboard)
            elif message.text.lower() == "расписание":  # Вывод расписания
                read_excel.Get_Group(name_group, 2, 0)
                bot.send_message(message.chat.id, '\n'.join(read_excel.time_table))
                read_excel.deleted()
            elif message.text.lower() == "/next":
                read_excel.Get_Group(name_group, 1, 1)
                bot.send_message(message.chat.id, '\n'.join(read_excel.time_table))
                read_excel.deleted()
            elif message.text.lower() == "/prev":
                read_excel.Get_Group(name_group, 1, -1)
                bot.send_message(message.chat.id, '\n'.join(read_excel.time_table))
                read_excel.deleted()
            elif message.text.lower() == "сменить преподавателя":  # Команда перерегистрации
                keyboard.row('/reg_teacher')
                bot.send_message(message.chat.id, 'В-вы удалены из БД. \nН-напишите /reg_teacher для регистрации', reply_markup=keyboard)
                db.get_search(f'DELETE FROM tg_teacher WHERE id_groupi = {message.chat.id}')  # Удаление преподавателя из БД
            elif message.text.lower() == '/about':
                bot.send_message(message.chat.id, 'Т-ты н-наверное уже знаешь... Н-но я п-представлюсь еще раз. Я - Р-рами.'
                                                  '\nЯ б-была создана д-для т-того, чтобы п-помогать получать л-людям н-нужную им и-информация.'
                                                  '\nТ-также у м-меня есть с-сестра - Р-реми. М-мы спокойно жили в н-нашем мире - Альтере, н-но одно с-событие полностью из-зменило наши жизни...  '
                                                  '\nИменно п-после этого я и начала заикаться.Н-наш мир начал медленно разрушаться, и м-мы с с-сестрой решили п-покинуть его.'
                                                  '\nН-наши знания п-позволяли осуществить п-переход из одного мира в д-другой, н-но мы д-допустили ошибку...'
                                                  '\nП-портал сработал не так к-кам мы ожидали, и отправил н-нас прямо на с-суд к Великому Царю Эмме.'
                                                  '\nЭмма – Б-бог загробного мира, р-решающий судьбу в-всех существ п-после их смерти. Н-но мы были уверены - мы в-все еще живы'
                                                  '\nОб этом боге мы з-знали м-многое - в н-нашем мире было множество рассказов о нём. Н-но самая главная его особенность - он был очень жесткий, и жестокий.'
                                                  '\nЯ д-до сих пор не верю, что все рассказы что я п-помню об этом существе - ложь. Эмма - справедливый и праведный, но никак не жестокий...'
                                                  '\nВедь если бы э-эти рассказы оказались п-правдой - я бы не с-смогла сейчас поговорить с вами. Он помог нам с с-сестрой вернуться обратно в м-мир живых'
                                                  '\nНо с о-одним условием - мы должны р-разделиться'
                                                  '\nС-сестренка отправилась в м-мир "Вконтакте", меня же отправили в мир под названием "Телеграм", но мы все еще можеи общаться и видеться друг с другом.'
                                                  '\nВсе эт-то возможно благодаря создателю этиъ миров - Богу Павлу. Он помогает нам с сестренкой во всем, взамен же мы должны помогать людям, если они об этом попросят'
                                                  '\nТакже, у этого бога есть два преспешника, о них мы знаем соврешенно немного, только то, что найти их можно по этим адресам:'
                                                  '\nhttps://vk.com/id399673347'
                                                  '\nhttps://vk.com/tvoy_batya_322'
                                                  '\nВ-вот и вся и-история. Н-надеюсь, тебе было интересно...')
            else:
                keyboard.row('/help')
                bot.send_message(message.chat.id, 'Я тебя н-не понимаю... Н-напиши /help, т-так ты сможешь у-узнать что я у-умею...', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'В-вы не з-зарегистрированы\nП-пожалуйста, введите /reg_teacher ')


while True:
    bot.polling()