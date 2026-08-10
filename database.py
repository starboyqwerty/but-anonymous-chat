import sqlite3

class Database:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file, check_same_thread = False)
        self.cursor = self.connection.cursor()

    def add_queue(self, chat_id, gender):
        with self.connection:
            return self.cursor.execute("INSERT INTO 'queue' ('chat_id', 'gender') VALUES (?, ?)", (chat_id, gender,))
        
    def delete_queue(self, chat_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM queue WHERE chat_id = ?", (chat_id,))
        
    def delete_chat(self, id_chat):
        with self.connection:
            return self.cursor.execute("DELETE FROM chats WHERE id = ?", (id_chat,))
        
    def set_gender(self, chat_id, gender, username):
        with self.connection:
            user = self.cursor.execute("SELECT * FROM users WHERE chat_id = ?",(chat_id,)).fetchmany(1)
            if bool(len(user)) == False:
                self.cursor.execute("INSERT INTO 'users' ('chat_id','gender', 'username') VALUES (?, ?, ?)",(chat_id, gender,username))
                return True
            else:
                return False
    def get_user(self, chat_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users WHERE chat_id =  ?", (chat_id,)).fetchmany(1)
        
    def get_username(self, chat_id):
        with self.connection:
            result = self.cursor.execute("SELECT username FROM users WHERE chat_id = ?", (chat_id,)).fetchone()
            return result if result else None

            
    def get_gender(self, chat_id):
        with self.connection:
            user = self.cursor.execute("SELECT * FROM users WHERE chat_id = ?",(chat_id,)).fetchmany(1)
            if bool(len(user)):
                for row in user:
                    return row[2]
            else:
                return False
            
    def get_gender_chat(self, gender):
        with self.connection:
            chat = self.cursor.execute("SELECT * FROM queue WHERE gender = ?", (gender,)).fetchmany(1)
            if bool(len(chat)):
                for row in chat:
                    user_info = [row[1], row[2]]
                    return user_info
            else:
                return [0]

    def get_chat(self):
        with self.connection:
            chat = self.cursor.execute("SELECT * FROM 'queue'", ()).fetchmany(1)
            if bool(len(chat)):
                for row in chat:
                    user_info = [row[1], row[2]]
                    return user_info
            else:
                return [0]
        
    def create_chat(self, chat_one, chat_two):
        with self.connection:
            if chat_two != 0:
                #Creating chat
                self.cursor.execute("DELETE FROM queue WHERE chat_id = ?", (chat_two,))
                self.cursor.execute("INSERT INTO 'chats' ('chat_one', 'chat_two') VALUES (?,?)", (chat_one, chat_two,))
                return True
            else:
                #queue
                return False

    def get_active_chat(self,chat_id):
        with self.connection:
            chat = self.cursor.execute("SELECT * FROM chats WHERE chat_one = ?", (chat_id,))
            id_chat = 0
            for row in chat:
                id_chat = row[0]
                chat_info = [row[0], row[2]]

            if id_chat == 0:
                chat = self.cursor.execute("SELECT * FROM chats WHERE chat_two = ?", (chat_id,))
                for row in chat:
                    id_chat = row[0]
                    chat_info = [row[0], row[1]]
                if id_chat == 0:
                    return False
                else:
                    return chat_info
            else:
                return chat_info
            
    def get_active_chats(self):
    # Проверяем наличие активного чата для каждого пользователя
        users = self.get_users()  # Получаем список всех пользователей
        active_chats = []

        for user in users:
            chat_id = user[0]
            chat_info = self.get_active_chat(chat_id)  # Получаем активный чат для пользователя
            if chat_info:
                active_chats.append(chat_info)  # Если чат найден, добавляем его в список активных чатов

        return active_chats if active_chats else False
    
    def delete_active_chats(self):
        # Получаем все активные чаты
        active_chats = self.get_active_chats()

        if active_chats:
            for chat in active_chats:
                chat_id = chat[0]
                # Удаляем чат по его ID
                self.cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
            self.connection.commit()  # Подтверждаем изменения в базе данных
            return True
        else:
            return False



    def get_users(self):
        with self.connection:
            return self.cursor.execute("SELECT chat_id FROM 'users'").fetchall()

    def get_max_user_id(self):
        with self.connection:
            result = self.cursor.execute("SELECT MAX(id) FROM users").fetchone()
            return result[0] if result[0] is not None else 0  # Возвращаем 0, если таблица пуста

    def get_queue_count(self):
        connection = sqlite3.connect('db.db')  # Замените на имя вашей базы данных
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM queue")
        count = cursor.fetchone()[0]
        connection.close()
        return count

    def get_chats_count(self):
        connection = sqlite3.connect('db.db')  # Замените на имя вашей базы данных
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM chats")
        count = cursor.fetchone()[0]
        connection.close()
        return count
    
    def clear_queue(self):
        with self.connection:
            try:
                # Удаляем все записи из таблицы 'queue'
                self.cursor.execute("DELETE FROM queue")
                self.connection.commit()  # Подтверждаем изменения в базе данных
                print("Очередь успешно очищена!")
            except Exception as e:
                print(f"Ошибка при очистке очереди: {e}")

    def delete_all_chats(self):
        with self.connection:
            return self.cursor.execute("DELETE FROM chats")  # Удаляем все записи из таблицы chats



    

