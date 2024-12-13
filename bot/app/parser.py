import json
from datetime import datetime
from bs4 import BeautifulSoup


data = []


def create_teachers(data):
    partner_data = []
    
    for item in data:
    
        client = item['client']
        for schedule in item['schedule']:
            date = schedule['date']
            for classes in schedule['classes']:
                number = classes['number']
                title = classes['title']
                type_ = classes['type']
                partner = classes['partner']
                location = classes['location']
                
                if partner == None:
                    continue
                # Проверяем, есть ли партнер уже в partner_data
                partner_item = next((p for p in partner_data if p['client'] == partner), None)
                
                if partner_item:
                    # Партнер уже есть, ищем, есть ли расписание на эту дату
                    schedule_item = next((s for s in partner_item['schedule'] if s['date'] == date), None)
                    
                    if schedule_item:
                        # Добавляем класс в существующее расписание
                        schedule_item['classes'].append({
                            'number': number,
                            'title': title,
                            'type': type_,
                            'partner': client,
                            'location': location
                        })
                    else:
                        # Добавляем новое расписание для этого партнера
                        partner_item['schedule'].append({
                            'date': date,
                            'classes': [{
                                'number': number,
                                'title': title,
                                'type': type_,
                                'partner': client,
                                'location': location
                            }]
                        })
                else:
                    # Если партнера нет, добавляем его с расписанием
                    partner_data.append({
                        'client': partner,
                        'is_teacher': True,
                        'schedule': [{
                            'date': date,
                            'classes': [{
                                'number': number,
                                'title': title,
                                'type': type_,
                                'partner': client,
                                'location': location
                            }]
                        }]
                    })
    
    # Сортировка расписаний по дате и классов по номеру
    for partner_item in partner_data:
        # Сортируем расписания по дате
        partner_item['schedule'].sort(key=lambda x: x['date'])
        for schedule_item in partner_item['schedule']:
            # Сортируем классы по номеру занятия
            schedule_item['classes'].sort(key=lambda x: x['number'])
    
    return partner_data
    

def html_parse(src):


    soup = BeautifulSoup(src, "lxml")

    clients = soup.find_all("h2")

    for client in clients:
        table = client.find_next_sibling("table")
        trs = table.find_all("tr")
        
        client_name = client.get_text().split(' ')[-1].strip('!*:.,')
        # Разделяем имя на буквы и цифры
        letters = ''.join(c for c in client_name if c.isalpha())
        numbers = ''.join(c for c in client_name if c.isdigit())
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
                location = tds_soup[1].get_text().strip("-")
                if location == "":
                    location = None

            # Проверяем, есть ли содержимое в ячейке
            if tds_soup[0].get_text().strip() == "&nbsp;" or not tds:
                # Если день уже существует, пропускаем
                if schedule and schedule[-1]['date'] == date:
                    continue
                # Добавляем пустой день
                schedule.append({
                    'date': date,
                    'classes': []
                })
                continue

            if len(tds) == 3:
                tds_info = [tds]
            elif len(tds) == 6:
                tds_info = [tds[0:3], tds[3:6]]
                
            
            for i in tds_info:
                if i[0] != "":
                    class_info= {
                        'number': number,
                        'title': i[0],
                        'type': i[1].strip('()'),
                        'partner': i[2],
                        'location': location
                    }
                    if schedule and schedule[-1]['date'] == date:
                        schedule[-1]['classes'].append(class_info)

                    else:
                        schedule.append({
                            'date': date,
                            'classes': [class_info]
                        })
            tds_info = []

            

        for entry in data:
            if entry['client'] == client_name:
                entry['schedule'].extend(schedule)
                break
        else:
            data.append({
                'client': client_name,
                'is_teacher': False,
                'schedule': schedule
            })
        
    return data + create_teachers(data)


# if __name__ == "__main__":
#     # Читаем HTML файл
#     with open("12дек-главный.html", "r", encoding="windows-1251") as file:
#         html_content = file.read()
    
#     # Получаем результат парсинга
#     result = html_parse(html_content)
    
#     # Сохраняем результат в JSON файл
#     with open("scheduleYA.json", "w", encoding="utf-8") as file:
#         json.dump(result, file, ensure_ascii=False, indent=4)

