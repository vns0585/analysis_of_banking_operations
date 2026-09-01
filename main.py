import re
from datetime import datetime

from src import reports, services, utils, views


def main() -> None:
    """Предоставляет пользовательский интерфейс и связывает функциональности между собой"""
    print("Добро пожаловать в бэкенд для анализа банковских операций!")

    user_choice = None
    while True:
        try:
            user_choice = int(input(
                "Выберите необходимый пункт меню:\n"
                "1. Получить данные для главной страницы\n"
                "2. Получить транзакции с телефонными номерами в описании\n"
                "3. Получить средние траты по дням недели за 3 месяца с выбранной даты\n"
                "4. Выйти из программы\n"
            ))
            if user_choice == 4:
                return
            if user_choice not in (1, 2, 3):
                raise ValueError
        except ValueError:
            print("Введите номер одного из предложенных вариантов.")
            continue
        else:
            break

    user_date_time: str
    if user_choice == 2:
        print(services.find_phone_numbers())
        return
    else:
        while True:
            user_date_time = input("Введите дату в формате YYYY-MM-DD HH:MM:SS"
                                   " или нажмите Enter для использования текущей: ").strip()
            if not user_date_time:
                user_date_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                break
            if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", user_date_time):
                user_date, user_time = user_date_time.split(" ")
                user_year, user_month, user_day = [int(x) for x in user_date.split("-")]
                user_hour, user_minute, user_second = [int(x) for x in user_time.split(":")]
                if user_month not in range(1, 13)\
                        or user_day not in range(1, 32)\
                        or user_hour not in range(1, 24)\
                        or user_minute not in range(1, 60)\
                        or user_second not in range(1, 60):
                    continue
                break

    if user_choice == 1:
        print(views.process_data(user_date_time))
        return
    else:
        print(reports.spending_by_weekday(utils.read_xlsx(), user_date_time).to_json(
            orient="records",
            force_ascii=False,
            indent=4)
        )
        return


if __name__ == '__main__':
    main()
