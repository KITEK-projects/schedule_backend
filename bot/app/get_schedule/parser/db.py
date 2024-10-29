import psycopg2

from app.get_schedule.parser.config import *


# Функция для создания таблиц
def create_tables():
    connection = None
    try:
        connection = psycopg2.connect(
            host=host, user=user, password=password, database=db_name
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            # Создание таблицы Clients с уникальным ограничением на client_name
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS clients (
                    id SERIAL PRIMARY KEY,
                    client_name VARCHAR(255) NOT NULL UNIQUE,
                    is_teacher BOOLEAN
                );
                """
            )

            # Создание таблицы Schedules с уникальным ограничением на client_id и дату
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS schedules (
                    id SERIAL PRIMARY KEY,
                    client_id INTEGER REFERENCES clients(id),
                    date DATE NOT NULL,
                    UNIQUE(client_id, date)
                );
                """
            )

            # Создание таблицы Classes
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS classes (
                    id SERIAL PRIMARY KEY,
                    schedule_id INTEGER REFERENCES schedules(id),
                    number INTEGER NOT NULL,
                    title VARCHAR(255),
                    type VARCHAR(50),
                    partner VARCHAR(255),
                    location VARCHAR(50),
                    UNIQUE(schedule_id, number) -- уникальность по schedule_id и номеру занятия
                );
                """
            )

            # Список администраторов бота
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS admins_bot (
                    id INTEGER NOT NULL
                );
                """
            )

            print("[INFO] Tables created successfully")

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")


def insert_data(data):
    try:
        connection = psycopg2.connect(
            host=host, user=user, password=password, database=db_name
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            for item in data:
                client_name = item["client"]
                is_teacher = item["is_teacher"]

                # Вставка клиента с уникальной проверкой на конфликт
                cursor.execute(
                    """
                    INSERT INTO clients (client_name, is_teacher) 
                    VALUES (%s, %s)
                    ON CONFLICT (client_name) DO NOTHING
                    RETURNING id;
                    """,
                    (client_name, is_teacher),
                )
                # Проверка, если возвращаемое значение пустое (клиент уже существует)
                client_id = cursor.fetchone()
                if not client_id:
                    cursor.execute(
                        "SELECT id FROM clients WHERE client_name = %s;", (client_name,)
                    )
                    client_id = cursor.fetchone()[0]

                for schedule in item["schedule"]:
                    schedule_date = schedule["date"]

                    # Проверяем, существует ли расписание на указанную дату для клиента
                    cursor.execute(
                        """
                        SELECT id FROM schedules 
                        WHERE client_id = %s AND date = %s;
                        """,
                        (client_id, schedule_date),
                    )
                    existing_schedule = cursor.fetchone()

                    if existing_schedule:
                        schedule_id = existing_schedule[0]
                        print(
                            f"[INFO] Schedule for {schedule_date} already exists. Updating..."
                        )

                        # Удаление старых записей занятий для этой даты, если требуется обновление
                        cursor.execute(
                            "DELETE FROM classes WHERE schedule_id = %s;",
                            (schedule_id,),
                        )
                    else:
                        # Вставка нового расписания
                        cursor.execute(
                            """
                            INSERT INTO schedules (client_id, date)
                            VALUES (%s, %s)
                            RETURNING id;
                            """,
                            (client_id, schedule_date),
                        )
                        schedule_id = cursor.fetchone()[0]

                    # Вставка классов для расписания
                    for class_item in schedule["classes"]:
                        number = class_item["number"]
                        title = class_item["title"]
                        _type = class_item["type"]
                        partner = class_item["partner"]
                        location = class_item["location"]

                        cursor.execute(
                            """
                            INSERT INTO classes (schedule_id, number, title, type, partner, location)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (schedule_id, number) 
                            DO UPDATE SET title = EXCLUDED.title, type = EXCLUDED.type, partner = EXCLUDED.partner, location = EXCLUDED.location;
                            """,
                            (
                                schedule_id,
                                number,
                                title,
                                _type,
                                partner,
                                location,
                            ),
                        )

            print("[INFO] Data inserted/updated successfully")
            return "📚 Вау! Все студенты уже получили расписание! Теперь всё по плану, как здорово! 🎓✨"

    except Exception as _ex:
        return f"[INFO] Error while working with PostgreSQL {_ex}"
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")


def insert_admin(id):
    try:
        connection = psycopg2.connect(
            host=host, user=user, password=password, database=db_name
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            # Check if the admin ID already exists
            cursor.execute("SELECT COUNT(*) FROM admins_bot WHERE id = %s;", (id,))
            count = cursor.fetchone()[0]

            if count > 0:
                print(f"[INFO] Admin with ID {id} already exists.")
            else:
                cursor.execute("INSERT INTO admins_bot (id) VALUES (%s);", (id,))
                print(f"[INFO] Admin with ID {id} inserted successfully.")

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")


def delete_admin(id):
    try:
        connection = psycopg2.connect(
            host=host, user=user, password=password, database=db_name
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            # Проверяем, существует ли администратор с данным ID
            cursor.execute("SELECT COUNT(*) FROM admins_bot WHERE id = %s;", (id,))
            count = cursor.fetchone()[0]

            if count == 0:
                print(f"[INFO] Admin with ID {id} does not exist.")
            else:
                cursor.execute("DELETE FROM admins_bot WHERE id = %s;", (id,))
                print(f"[INFO] Admin with ID {id} deleted successfully.")

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")


def select_admin():
    try:
        connection = psycopg2.connect(
            host=host, user=user, password=password, database=db_name
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM admins_bot;")
            admins = cursor.fetchall()
            return [uid[0] for uid in admins]

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")


create_tables()
insert_admin(1509968545)
