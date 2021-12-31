import sqlite3

class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS vk_group(
        id INTEGER PRIMARY KEY,
        id_group INTEGER,
        name_group VARCHAR
        );""")
        self.connection.commit()

    def get_search(self, SQL_search):
        """Любой запрос"""
        with self.connection:
            return self.cursor.execute(SQL_search).fetchall()
    
    def get_group(self, id_group):
        """Получаем все группы студентов"""
        with self.connection:
            return self.cursor.execute("SELECT name_group FROM vk_group WHERE id_group = ?", (id_group,)).fetchall()
            
    def get_teacher(self, id_group):
        """Получаем всех преподавателей"""
        with self.connection:
            return self.cursor.execute("SELECT name_teacher FROM vk_teacher WHERE id_groupi = ?", (id_group,)).fetchall()

    def add_chat(self, id_group, name_group):
        """Добавляем новую беседу"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `vk_group` (`id_group`, `name_group`) VALUES(?,?)", (id_group, name_group))
    
    def add_teachers(self, id_group, name_group):
        """Добавляем нового препода"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `vk_teacher` (`id_groupi`, `name_teacher`) VALUES(?,?)", (id_group, name_group))