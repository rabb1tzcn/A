import openpyxl
from datetime import date
from base_VK import SQLighter

db = SQLighter('vk_group.db')  #Соединение с БД

# Определение даты от 0 до 6
time = date.today()
data = time.weekday()

# Выбор страницы для парсинга
book = openpyxl.open('Расписание.xlsx', read_only=True)
sheet = book.worksheets[1]

number = []  # Хранит номер пар
today = []  # Хранит все что написанно в ячейке
time_table = []  # Полностью готовое расписание

# Определение какой стоблик нужно пробежать
dicts = {
    0: 'B',
    1: 'C',
    2: 'D',
    3: 'E',
    4: 'F',
    5: 'G',
    6: 'H'}

# Определение названия недели по ключу
week = {
    0: 'Понедельник',
    1: 'Вторник',
    2: 'Среда',
    3: 'Четверг',
    4: 'Пятница',
    5: 'Суббота',
    6: 'Воскресенье'}

weekday = ['08:30 - 09:50', '10:00 - 11:20', '11:30 - 12:50', '13:10 - 14:30', '14:40 - 16:00', '16:10 - 17:30', '17:40 - 19:00']
vtornik = ['08:30 - 09:50', '10:00 - 11:20', '11:30 - 12:50', '13:00 - 13:40', '13:50 - 15:10', '15:20 - 16:40', '16:50 - 18:10', '18:20 - 19:40']

# Метод для нахождения ячейки расписания
def Get_Group(name_group, chat, day):
    data_s = data
    # Проверка на следующее/предыдущее расписание
    if day == 1:
        data_s = data_s + 1
    elif day == - 1:
        data_s = data_s - 1   

    if data_s == 6:  # Вывод если воскресенье
        time_table.append('Как вы можете думать об учёбе')
        time_table.append('Сегодня же воскресенье - Отдыхайте')
    elif data_s > 6:
        time_table.append('Новое расписание ещё не готово...\nСтоит подождать или посмотреть его на сайте колледжа:\nhttps://vtk-portal.ru/studentam/raspisanie-zanyatiy.php')
    elif data_s < 0:
        time_table.append('Думаю это не имеет смысла, вчера было воскресенье')
    else:
        # Нахождение нужного диапозонга расписания
        if  chat == 1:
            sheet = book.worksheets[1]
        elif chat == 2:
            sheet = book.worksheets[0]
         
        for x in range(2,9000,19):
            if sheet[f'C{x}'].value == name_group:
                cell = x + 3
                end_cell = cell + 14  # Первая ячейка диапозона
                numerator(cell, end_cell, chat, day, data_s)  # Заполнение неотформатированного расписания
                break

def numerator(cell, end_cell, chat, day, data_s):
    jail = dicts[data_s]  # Ячейка, которую нужно парсить
    # Парсинг нужного расписания
    if  chat == 1:
        sheet = book.worksheets[1]
    elif chat == 2:
        sheet = book.worksheets[0]
        
    while cell <= end_cell:  # Диапозон поиска
        if data_s != 6:
            if sheet[f'A{cell}'].value != None:  # Заполнение номера пары
                number.append(sheet[f'A{cell}'].value)  
                if sheet[f'{jail}{cell}'].value == None:
                    if sheet[f'{jail}{cell + 1}'].value == None:  # Просмотр след. ячейки на случай если в нужной нет значения
                        today.append('отсутствует')
                    else:
                        today.append(sheet[f'{jail}{cell + 1}'].value)
                else:
                    today.append(sheet[f'{jail}{cell}'].value)  # Добавление значения в ячейке
        cell += 1
    merge(number, today, chat, day, data_s)

    
def merge(number, today, chat, day, data_s):
    # Группа или преподаватель
    if  chat == 1:
        last = "Преподаватель"
    elif chat == 2:
        last = "Группа"
    week_day = week[data_s]  # Письменно день недели 
        
    for kotik in range(0, len(number)):  # Перебираю все пары
        todays = today[kotik]
        if kotik == 0:
            time_table.append(f'Расписание на {week_day}')
            time_table.append('\n')
        if todays != 'отсутствует' and data != 1:
            time_table.append(number[kotik] + ':' + '  ' + todays[todays.find('.') + 1 : todays.find('\n')] + '\n' + 'Время' + ':' + '  ' + weekday[kotik] + '\n' + 'Аудитория' + ':' + '  ' + todays[todays.find(' а.') + 3:] + '\n' + last + ':' + '  ' + todays[todays.find('\n') + 1 : todays.find(' а.')])
        elif todays != 'отсутствует' and data == 1:  # Проверка случая когда вторник
            if kotik == 3:
                time_table.append('Классный час' + '\n' + 'Время' + ':' + '  ' + vtornik[kotik])
            else:
                time_table.append(number[kotik] + ':' + '  ' + todays[todays.find('.') + 1 : todays.find('\n')] + '\n' + 'Время' + ':' + '  ' + vtornik[kotik] + '\n' + 'Аудитория' + ':' + '  ' + todays[todays.find(' а.') + 3:] + '\n' + last + ':' + '  ' + todays[todays.find('\n') + 1 : todays.find(' а.')])
        else:
            time_table.append(number[kotik] + ':' + '  ' + todays)  # Если нет пары, вывод что она отсутсвует
        time_table.append('\n')

# Метод для очистки всех списков
def deleted():
    number.clear()
    today.clear()
    time_table.clear()