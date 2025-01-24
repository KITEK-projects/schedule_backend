from bs4 import BeautifulSoup


data = []


def parse_for_teacher(data, teacher_data=[]):
    for data_item in data:
        client = data_item.get("client_name", None)

        # Process each schedule item for the current client
        for schedule_item in data_item.get("schedules", []):
            date = schedule_item["date"]
            lessons = schedule_item["lessons"]

            # Process each class item in the schedule
            for lesson in lessons:
                number = lesson["number"]

                for class_item in lesson["items"]:
                    title = class_item["title"]
                    _type = class_item["type"]
                    partner = class_item["partner"]
                    location = class_item["location"]

                    # Find the corresponding teacher based on the partner
                    new_client = next(
                        (obj for obj in teacher_data if obj["client_name"] == partner),
                        None,
                    )

                    if new_client:
                        # Check if the date exists in the teacher's schedule
                        (new_date, date_index) = next(
                            (
                                (obj, i)
                                for i, obj in enumerate(new_client.get("schedules", []))
                                if obj.get("date") == date
                            ),
                            (None, None),
                        )

                        if new_date:
                            # Find or create a class entry for this date
                            (new_classes, classes_index) = next(
                                (
                                    (obj, i)
                                    for i, obj in enumerate(new_date.get("lessons", []))
                                    if obj.get("number") == number
                                ),
                                (None, None),
                            )

                            if new_classes:
                                # If a class already exists, append new information
                                new_classes["items"].append(
                                    {
                                        "title": title,
                                        "type": _type,
                                        "partner": client,
                                        "location": location,
                                    }
                                )
                            else:
                                # Create a new class entry if it doesn't exist
                                new_date["lessons"].append(
                                    {
                                        "number": number,
                                        "items": [
                                            {
                                                "title": title,
                                                "type": _type,
                                                "partner": client,
                                                "location": location,
                                            }
                                        ],
                                    }
                                )
                        else:
                            # If no date exists, create a new entry
                            new_client["schedules"].append(
                                {
                                    "date": date,
                                    "lessons": [
                                        {
                                            "number": number,
                                            "items": [
                                                {
                                                    "title": title,
                                                    "type": _type,
                                                    "partner": client,
                                                    "location": location,
                                                }
                                            ],
                                        }
                                    ],
                                }
                            )

                        # Update the teacher's schedule with the modified client data

                        teacher_index = next(
                            (
                                i
                                for i, obj in enumerate(teacher_data)
                                if obj.get("client_name") == partner
                            ),
                            0,
                        )
                        teacher_data[teacher_index] = new_client

                    else:
                        # Create a new client entry if not found
                        new_teacher_data = {
                            "client_name": partner,
                            "is_teacher": True,
                            "schedules": [
                                {
                                    "date": date,
                                    "lessons": [
                                        {
                                            "number": number,
                                            "items": [
                                                {
                                                    "title": title,
                                                    "type": _type,
                                                    "partner": client,
                                                    "location": location,
                                                }
                                            ],
                                        }
                                    ],
                                }
                            ],
                        }
                        teacher_data.append(new_teacher_data)

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
                        class_info = {
                            "number": number,
                            "items": [
                                {
                                    "title": i[0].capitalize(),
                                    "type": i[1].strip("()"),
                                    "partner": i[2],
                                    "location": location[0],
                                }
                            ],
                        }
                    elif len(i) == 6:
                        class_info = {
                            "number": number,
                            "items": [
                                {
                                    "title": i[0].capitalize(),
                                    "type": i[1].strip("()"),
                                    "partner": i[2],
                                    "location": location[0],
                                },
                                {
                                    "title": i[3].capitalize(),
                                    "type": i[4].strip("()"),
                                    "partner": i[5],
                                    "location": location[1],
                                },
                            ],
                        }

                    if schedule and schedule[-1]["date"] == date:
                        schedule[-1]["lessons"].append(class_info)
                    else:
                        schedule.append({"date": date, "lessons": [class_info]})
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


if __name__ == "__main__":
    import json

    # Читаем HTML файл
    with open("16дек-главное.html", "r", encoding="windows-1251") as file:
        html_content = file.read()

    # Получаем результат парсинга
    result = html_parse(html_content)

    # Сохраняем результат в JSON файл
    with open("scheduleYA.json", "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=4)
