from bs4 import BeautifulSoup


data = []


def parse_for_teacher(data, teacher_data=[]):
    # Собираем все уникальные даты из всех клиентов
    all_dates = set()
    for data_item in data:
        for schedule in data_item.get("schedules", []):
            all_dates.add(schedule.get("date"))

    for data_item in data:
        client_name = data_item.get("client_name")

        for schedule_item in data_item.get("schedules", []):
            date = schedule_item["date"]
            lessons = schedule_item["lessons"]

            for lesson in lessons:
                number = lesson["number"]
                title = lesson["title"]
                _type = lesson["type"]
                partner = lesson["partner"]
                location = lesson["location"]

                new_client = next(
                    (t for t in teacher_data if t["client_name"] == partner), None
                )
                if not new_client:
                    new_client = {
                        "client_name": partner,
                        "is_teacher": True,
                        "schedules": [],
                    }
                    teacher_data.append(new_client)

                # Убедиться, что есть запись на дату
                date_entry = next(
                    (s for s in new_client["schedules"] if s["date"] == date), None
                )
                if not date_entry:
                    date_entry = {"date": date, "lessons": []}
                    new_client["schedules"].append(date_entry)

                item = {
                    "number": number,
                    "title": title,
                    "type": _type,
                    "partner": client_name,
                    "location": location,
                }
                if item not in date_entry["lessons"]:
                    date_entry["lessons"].append(item)

    # === Добавляем недостающие даты с пустыми lessons ===
    for teacher in teacher_data:
        existing_dates = {s["date"] for s in teacher.get("schedules", [])}
        missing_dates = all_dates - existing_dates
        for date in missing_dates:
            teacher["schedules"].append({"date": date, "lessons": []})

    return teacher_data


def html_parse(src):
    soup = BeautifulSoup(src, "lxml")

    clients = soup.find_all("h2")

    for client in clients:
        table = client.find_next_sibling("table")
        trs = table.find_all("tr")

        client_name = client.get_text().split(" ")[-1].strip("!*:.,")
        # Разделяем имя на буквы и цифры
        letters = "".join(c for c in client_name if c.isalpha())
        numbers = "".join(c for c in client_name if c.isdigit())
        client_name = f"{letters}-{numbers}" if numbers else letters
        schedule = []

        for tr in trs[1:]:
            ths = tr.find_all("th")
            if len(ths) == 2:
                pre_date = ths[0].get_text().split(" ")[-1].split(".")
                date = "-".join(reversed(pre_date))
                number = int(ths[1].get_text())
            else:
                number = int(ths[0].get_text())

            tds_soup = tr.find_all("td")
            tds = [
                line.strip()
                for line in tds_soup[0].decode_contents().split("<br/>")
                if line.strip() != ""
            ]

            location = None

            if len(tds_soup) > 1:
                location = tds_soup[1].get_text(separator="<br>").split("<br>")
                location = [i.replace("-", "") for i in location]

            # Проверяем, есть ли содержимое в ячейке
            if tds_soup[0].get_text().strip() == "&nbsp;" or not tds:
                # Если день уже существует, пропускаем
                if schedule and schedule[-1]["date"] == date:
                    continue
                # Добавляем пустой день
                schedule.append({"date": date, "lessons": []})
                continue

            tds_info = [tds]

            for i in tds_info:
                if i[0] != "":
                    if len(i) == 3:
                        lesson = [
                            {
                                "number": number,
                                "title": i[0].capitalize(),
                                "type": i[1].strip("()"),
                                "partner": i[2],
                                "location": location[0],
                            }
                        ]
                    elif len(i) == 6:
                        lesson = [
                            {
                                "number": number,
                                "title": i[0].capitalize(),
                                "type": i[1].strip("()"),
                                "partner": i[2],
                                "location": location[0],
                            },
                            {
                                "number": number,
                                "title": i[3].capitalize(),
                                "type": i[4].strip("()"),
                                "partner": i[5],
                                "location": location[1],
                            },
                        ]

                    if schedule and schedule[-1]["date"] == date:
                        schedule[-1]["lessons"].extend(lesson)
                    else:
                        schedule.append({"date": date, "lessons": lesson})
            tds_info = []

        for entry in data:
            if entry["client_name"] == client_name:
                entry["schedules"].extend(schedule)
                break
        else:
            data.append(
                {"client_name": client_name, "is_teacher": False, "schedules": schedule}
            )

    return data + parse_for_teacher(data)


# if __name__ == "__main__":
#     import json

#     # Читаем HTML файл
#     with open(
#         "17июня.html",
#         "r",
#         encoding="windows-1251",
#     ) as file:
#         html_content = file.read()

#     # Получаем результат парсинга
#     result = html_parse(html_content)

#     # Сохраняем результат в JSON файл
#     with open("scheduleт.json", "w", encoding="utf-8") as file:
#         json.dump(result, file, ensure_ascii=False, indent=4)
