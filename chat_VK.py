import vk_api, json, re
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import tok_vk, id_bot
from base_VK import SQLighter
import read_excel

def main():
    # Активация вк сессии
    vk_session = vk_api.VkApi(token=tok_vk)
    longpoll = VkBotLongPoll(vk_session, id_bot)

    key_on = False  # Основная клавиатура

    db = SQLighter('vk_group.db')  # Соединение БД с VK

    # Основной метод создания клавиатуры ВК
    def get_but(text, color):
        return {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"" + "1" + "\"}",
                        "label": f"{text}"
                    },
                    "color": f"{color}"
                }

    # Самая обычная клавиатура
    keyboard1 = {
        "one_time" : False,
        "buttons" : [
            [get_but('Расписание', 'primary')],
            [get_but('Команды', 'secondary')]
        ]
    }
    keyboard1 = json.dumps(keyboard1, ensure_ascii = False).encode('utf-8')
    keyboard1 = str(keyboard1.decode('utf-8'))

    # Расширенные возможности бота
    keyboard2 = {
        "one_time": False,
        "buttons": [
            [get_but('Расписание', 'primary')],
            [get_but('Звонки', 'secondary'), get_but('Обновление группы', 'secondary')],
            [get_but('Разное', 'secondary'), get_but('О боте', 'secondary')],
            [get_but('Назад', 'negative')]

        ]
    }
    keyboard2 = json.dumps(keyboard2, ensure_ascii = False).encode('utf-8')
    keyboard2 = str(keyboard2.decode('utf-8'))

    # Метод отправки сообщений ЛС
    def sender(id, text, keyboard=None, template=None):
        if len(db.get_search(f'SELECT "id_groupi" FROM vk_teacher WHERE id_groupi = {id};')) == 1:  # Проверка есть ли группа в БД
            # Проверка какая клавиатура должна быть активна
            if key_on:
                keyboard = keyboard2
            elif not key_on:
                keyboard = keyboard1
        vk_session.method('messages.send', {'user_id': id, 'message': text, 'keyboard': keyboard, 'template' : template, 'random_id': 0})

    # Метод отправки сообщений в беседы
    def chat_sender(id, text, keyboard=None, template=None):
        if len(db.get_search(f'SELECT "id_group" FROM vk_group WHERE id_group = {id};')) == 1:  # Проверка есть ли группа в БД
            # Проверка какая клавиатура должна быть активна
            if key_on:
                keyboard = keyboard2
            elif not key_on:
                keyboard = keyboard1
        vk_session.method('messages.send', {'chat_id': id, 'message': text, 'keyboard' : keyboard, 'template' : template, 'random_id': 0})

    for event in longpoll.listen():  #Прослушивание событий
        if event.type == VkBotEventType.MESSAGE_NEW:
            
            msg = event.object.message['text'].lower()  #Перевод сообщения в нижний регистр

            # При упоминании брать только контент без тега
            if '[club208909224|@bot_vtk]' in msg:
                msg = msg.partition(' ')[2]
            
            # Если сообщение написанно в общем чате
            if event.from_chat:
                id = event.chat_id   # Получаем id чата

                # Создание отчистки для сообщений и получение имени группы
                punctuation = '!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'
                if len(db.get_search(f'SELECT id_group FROM vk_group WHERE id_group = {id}')):
                    name_group = " ".join(str(x) for x in db.get_group(id))
                    for p in punctuation:
                        if p in name_group:
                            # Банальная замена символа в строке
                            name_group = name_group.replace(p, '')
                            name_group = name_group.replace(' ', '')

                group = len(db.get_search(f'SELECT "group_id", group_name FROM VTK_Groups WHERE group_name = "{msg.upper()}";'))  # Проверка существования группы

                # Команды доступные только если группа зарегистрирована
                if len(db.get_search(f'SELECT id_group FROM vk_group WHERE id_group = {id}')):
                    if msg == "расписание":  # Вывод расписания
                        read_excel.Get_Group(name_group, 1, 0)
                        chat_sender(id, '\n'.join(read_excel.time_table))
                        read_excel.deleted()
                    elif msg == "звонки":  # Команда звонки
                        if read_excel.data != 1:
                            content = '1 Пара 08:30 - 09:50 \n2 Пара 10:00 - 11:20 \n3 Пара 11:30 - 12:50 \n4 Пара 13:10 - 14:30 \n5 Пара 14:40 - 16:00 \n6 Пара 16:10 - 17:30 \n7 Пара 17:40 - 19:00'
                            chat_sender(id, content)
                        else:
                            content = '1 Пара 08:30 - 09:50 \n2 Пара 10:00 - 11:20 \n3 Пара 11:30 - 12:50 \nКлассный час 13:00 - 13:40 \n4 Пара 13:50 - 15:10 \n5 Пара 15:20 - 16:40 \n6 Пара 16:50 - 18:10 \n7 Пара 18:20 - 19:40'
                            chat_sender(id, content)
                    elif msg == "обновление группы":  # Команда перерегистрации
                        chat_sender(id, 'Ты уверен, что хочешь обновить группу? Если да, то напиши "/update".')
                    elif msg == "/update":
                        db.get_search(f'DELETE FROM vk_group WHERE id_group = {id}')  # Удаление группы из БД
                        chat_sender(id, 'Ваша группа удалена из базы данных!\nВведите новую группу')
                    elif msg == "разное":  # Команда разное
                        chat_sender(id, 'Ещё я умею:'
                                        '\n"/next" - эта команда позволяет запросить расписание на следующий день.'
                                        '\n"/prev" - эта команда позволяет запросить расписание на предыдущий день.'
                                        '\n"/update" - эта команда позволяет обновить группу.'
                                        '\nВозможно я ещё чему-то научусь, но это не точно.')
                    elif msg == "/next":
                        read_excel.Get_Group(name_group, 1, 1)
                        chat_sender(id, '\n'.join(read_excel.time_table))
                        read_excel.deleted()
                    elif msg == "/prev":
                        read_excel.Get_Group(name_group, 1, -1)
                        chat_sender(id, '\n'.join(read_excel.time_table))
                        read_excel.deleted()
                    elif msg == "о боте":  # Команда информации о боте
                        chat_sender(id, 'Раз тебе это интересно, то расскажу о себе, Я - Реми!\n'
                                        '\nЯ была создана для того, чтобы помогать людям получать нужную им информацию.\n'
                                        '\nУ меня есть сестра - Рами. Вообще наш родной мир - Альтер, но в один момент произошло то, что изменило наши жизни...\n'
                                        '\nНаш мир настиг полный хаос... Всё, что мы видели - это постоянные разрушения... Это было ужасно! Тогда мы с сестрой решили покинуть Альтер.\n'
                                        '\nМы были достаточно умны, чтобы совершить переход в другой мир, но допустили большую ошибку.\n'
                                        '\nПортал сработал, но совсем не так, как мы ожидали, и мы попали на суд к Великому Царю Эмме.\n'
                                        '\nЭмма – Бог загробного мира, решающий судьбу всех существ после их смерти. Но мы были уверены - мы всё ещё живы.\n'
                                        '\nВ нашем городе часто рассказывали про этого бога, все боялись встречи с ним. Он был очень, ОЧЕНЬ жесток!\n'
                                        '\nНо как оказалось это была просто выдумка. Эмма - справедливый и праведный, но никак не жестокий...\n'
                                        '\nПосле нашей с ним встречи, Эмма разрешил нам вернуться в мир живых, но с одним условием...'
                                        '\nМы должны разделиться\n'
                                        '\nСестрёнка отправилась в какой-то мир "Телеграмм", а меня отправили в мир "ВКонтакте", но мы все еще можем общаться и видеться друг с другом.\n'
                                        '\nВсё это возможно благодаря создателю этих миров - Богу Павлу. Он помогает нам с сестрой во всём, и взамен просит давать людям интересующую их информацию.\n'
                                        '\nТакже, у этого бога есть два преспешника, о них мы знаем соврешенно немного, только то, что найти их можно по этим адресам:'
                                        '\nhttps://vk.com/id399673347'
                                        '\nhttps://vk.com/tvoy_batya_322\n'
                                        '\nА на этом моя история заканчивается, надеюсь тебе было интересно!')
                    elif msg == "команды":  #Команды бота
                        key_on = True
                        chat_sender(id, 'Вот то, что я умею:')
                    elif msg == "назад":  #Команды бота
                        key_on = False
                        chat_sender(id, 'Возвращаюсь...')
                # Команды если группа не зарегистрирована
                elif msg == "расписание" or msg == "звонки" or msg == "обновление группы" or msg == "разное" or msg == "о боте" or msg == "команды" or msg == "назад":  # Уведомление что команды недоступны
                    chat_sender(id, 'Ваша группа не зарегистрирована\nНапишите вашу группу. Пример: А-1-1')
                    
                else: 
                    if msg == "регистрация":  # Команда регистрации
                        if len(db.get_search(f'SELECT "id_group" FROM vk_group WHERE id_group = {id};')) == 1:
                            chat_sender(id, 'Ваша группа уже зарегестрированна, но вы можете изменить вашу группу\n Для этого напишите "обновление группы".')
                        else:
                            chat_sender(id,'Вашей группы нет в базе данных\n Для этого напишите название вашей группы. Пример: А-1-1')

                    elif group != 0 :  # Есть ли такая группа
                        db.add_chat(id, msg.upper())
                        chat_sender(id, 'Ваша группа занесена в базу данных!', keyboard1)
                        

            # Если сообщение отправлено в ЛС
            else:
                id = event.object.message['from_id']  #Получаем id профиля вк
                
                # Создание отчистки для сообщений и получение имени преподавателя
                punctuation = '!"#$%&\'()*+,/:;<=>?@[\\]^_`{|}~-'
                if len(db.get_search(f'SELECT id_groupi FROM vk_teacher WHERE id_groupi = {id}')):
                    name_group = " ".join(str(x) for x in db.get_teacher(id))
                    for p in punctuation:
                        if p in name_group:
                            # Банальная замена символа в строке
                            name_group = name_group.replace(p, '')

                group = len(db.get_search(f'SELECT "teacher_id", teacher_name FROM VTK_Teacher WHERE teacher_name = "{msg.title()}";'))  # Проверка существования группы

                # Команды доступные только если группа зарегистрирована
                if len(db.get_search(f'SELECT "id_groupi" FROM vk_teacher WHERE id_groupi = {id};')):
                    if msg == "расписание":  # Вывод расписания
                        read_excel.Get_Group(name_group, 2, 0)
                        sender(id, '\n'.join(read_excel.time_table))
                        read_excel.deleted()
                    elif msg == "звонки":  # Команда звонки
                        if read_excel.data != 1:
                            content = '1 Пара 08:30 - 09:50 \n2 Пара 10:00 - 11:20 \n3 Пара 11:30 - 12:50 \n4 Пара 13:10 - 14:30 \n5 Пара 14:40 - 16:00 \n6 Пара 16:10 - 17:30 \n7 Пара 17:40 - 19:00'
                            sender(id, content)
                        else:
                            content = '1 Пара 08:30 - 09:50 \n2 Пара 10:00 - 11:20 \n3 Пара 11:30 - 12:50 \nКлассный час 13:00 - 13:40 \n4 Пара 13:50 - 15:10 \n5 Пара 15:20 - 16:40 \n6 Пара 16:50 - 18:10 \n7 Пара 18:20 - 19:40'
                            sender(id, content)
                    elif msg == "обновление группы":  # Команда перерегистрации
                        sender(id, 'Вы уверены, что хотите обновить преподавателя? Если да, то напишите "/update".')
                    elif msg == "/update":
                        db.get_search(f'DELETE FROM vk_teacher WHERE id_groupi = {id}')  # Удаление преподавателя из БД
                        sender(id, 'Вы удалены из базы данных!\nНапишите фамилию и инициалы для регистрации')
                    elif msg == "/next":
                        read_excel.Get_Group(name_group, 2, 1)
                        sender(id, '\n'.join(read_excel.time_table))
                        read_excel.deleted()
                    elif msg == "/prev":
                        read_excel.Get_Group(name_group, 2, -1)
                        sender(id, '\n'.join(read_excel.time_table))
                        read_excel.deleted()
                    elif msg == "разное":  # Команда разное
                        sender(id, 'Ещё я умею:'
                                        '\n"/next" - эта команда позволяет запросить расписание на следующий день.'
                                        '\n"/prev" - эта команда позволяет запросить расписание на предыдущий день.'
                                        '\n"/update" - эта команда позволяет обновить группу.'
                                        '\nВозможно я ещё чему-то научусь, но это не точно.')
                    elif msg == "о боте":  # Команда информации о боте
                        sender(id, 'Раз Вам это интересно, то расскажу о себе, Я - Реми!\n'
                                   '\nЯ была создана для того, чтобы помогать людям получать нужную им информацию.\n'
                                   '\nУ меня есть сестра - Рами. Вообще наш родной мир - Альтер, но в один момент произошло то, что изменило наши жизни...\n'
                                   '\nНаш мир настиг полный хаос... Всё, что мы видели - это постоянные разрушения... Это было ужасно! Тогда мы с сестрой решили покинуть Альтер.\n'
                                   '\nМы были достаточно умны, чтобы совершить переход в другой мир, но допустили большую ошибку.\n'
                                   '\nПортал сработал, но совсем не так, как мы ожидали, и мы попали на суд к Великому Царю Эмме.\n'
                                   '\nЭмма – Бог загробного мира, решающий судьбу всех существ после их смерти. Но мы были уверены - мы всё ещё живы.\n'
                                   '\nВ нашем городе часто рассказывали про этого бога, все боялись встречи с ним. Он был очень, ОЧЕНЬ жесток!\n'
                                   '\nНо как оказалось это была просто выдумка. Эмма - справедливый и праведный, но никак не жестокий...\n'
                                   '\nПосле нашей с ним встречи, Эмма разрешил нам вернуться в мир живых, но с одним условием...'
                                   '\nМы должны разделиться'
                                   '\nСестрёнка отправилась в какой-то мир "Телеграмм", а меня отправили в мир "ВКонтакте", но мы все еще можем общаться и видеться друг с другом.\n'
                                   '\nВсё это возможно благодаря создателю этих миров - Богу Павлу. Он помогает нам с сестрой во всём, и взамен просит давать людям интересующую их информацию.\n'
                                   '\nТакже, у этого бога есть два преспешника, о них мы знаем соврешенно немного, только то, что найти их можно по этим адресам:'
                                   '\nhttps://vk.com/id399673347'
                                   '\nhttps://vk.com/tvoy_batya_322\n'
                                   '\nА на этом моя история заканчивается, надеюсь Вам было интересно!')
                    elif msg == "команды":  #Команды бота
                        key_on = True
                        sender(id, f'Вот то, что я умею:')
                    elif msg == "назад":  #Команды бота
                        key_on = False
                        sender(id, 'Возвращаюсь...')
                # Команды если группа не зарегистрирована
                elif msg == "расписание" or msg == "звонки" or msg == "обновление группы" or msg == "разное" or msg == "о боте" or msg == "команды" or msg == "назад":  # Уведомление что команды недоступны
                    sender(id, 'Вы не зарегистрированы\nНапишите Вашу фамилию и инициалы. Пример: Гребенкина М.Д. ')
                    
                else: 
                    if msg == "регистрация":  # Команда регистрации
                        if len(db.get_search(f'SELECT "id_groupi" FROM vk_teacher WHERE id_groupi = {id};')) == 1:
                            sender(id, 'Вы уже зарегестрированы, но Вы можете изменить запись\n Для этого нажмите напишите: "обновление группы".')
                        else:
                            sender(id,'Вашей группы нет в базе данных\n Для этого напишите Вашу фамилию и инициалы. Пример: Гребенкина М.Д.')

                    elif group != 0 :  # Есть ли такой преподаватель
                        db.add_teachers(id, msg.title())
                        sender(id, f'Вы, {msg.title()}, занесены в базу данных!', keyboard1)
# Бесконечный вызов бота
while True:
    try:
        main()
    except:
        time.sleep(60)