import json
from datetime import datetime
from bs4 import BeautifulSoup

data = []

time_bell = {
    'monday_first': [
        '08:45 10:05',
        [
            '10:55 11:35',
            '11:35 12:10',
            '12:10 12:50',    
        ],
        '13:00 14:20',
        '14:30 15:50',
        '16:00 17:20',
        '17:30 18:50'
    ],
    'monday_second': [
        '08:45 10:05',
        [
          '10:55 12:15',
          '12:15 13:00'  
        ],
        '13:00 14:20',
        '14:30 15:50',
        '16:00 17:20',
        '17:30 18:50'
    ],
    'other_first': [
        '08:45 10:05',
        [
            '10:15 10:55',
            '10:55 12:25',
            '12:25 12:05',    
        ],
        '12:15 13:35',
        '13:45 15:05',
        '15:15 16:35',
        '16:45 18:05'
    ],
    'other_second': [
        '08:45 10:05',
        [
          '10:15 11:35',
          '11:35 12:12'  
        ],
        '12:15 13:35',
        '13:45 15:05',
        '15:15 16:35',
        '16:45 18:05'
    ]
}

def change_time(client, number, date):
    course = int(client[-2])
    # Есдт Понедельник
    if datetime.strptime(date, "%Y-%m-%d").weekday() == 0:
        if course <= 2:
            return time_bell['monday_first'][number - 1]
        elif course > 2: 
            return time_bell['monday_second'][number - 1]
    else:
        if course <= 2:
            return time_bell['other_first'][number - 1]
        elif course > 2: 
            return time_bell['other_second'][number - 1]
        
        
def add_to_data(class_info, date):
    schedule = []
    if schedule and schedule[-1]['date'] == date:
        schedule[-1]['classes'].append(class_info)
    else:
        schedule.append({
            'date': date,
            'classes': [class_info]
        })
    
    return schedule


def create_teachers(data):
    partner_data = []
    
    for item in data:
    
        client = item['client']
        for schedule in item['schedule']:
            date = schedule['date']
            for classes in schedule['classes']:
                number = classes['number']
                is_lunch = classes['is_lunch']
                time = classes['time']
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
                            'is_lunch': is_lunch,
                            'time': time,
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
                                'is_lunch': is_lunch,
                                'time': time,
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
                                'is_lunch': is_lunch,
                                'time': time,
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
    

def html_parse(path):
    with open(path, encoding='windows-1251') as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    clients = soup.find_all("h2")

    for client in clients:
        table = client.find_next_sibling("table")
        trs = table.find_all("tr")
        
        client_name = client.get_text().split(' ')[-1].strip('!*:.')
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
                    location == None

            if len(tds) == 3:
                # для цикла
                tds_info = [tds]
            elif len(tds) == 6:
                tds_info = [tds[0:3], tds[3:6]]
                
            
            for i in tds_info:
                if i[0] != "":
                    if number == 2:
                        if int(client_name[-2]) <= 2:
                            times = change_time(client_name, number, date)
                            class_info0= {
                                'number': number,
                                'is_lunch': False,
                                'time': times[0],
                                'title': i[0],
                                'type': i[1].strip('()'),
                                'partner': i[2],
                                'location': location
                            }
                            class_info1= {
                                'number': number,
                                'is_lunch': True,
                                'time': times[1],
                                'title': None,
                                'type': None,
                                'partner': None,
                                'location': None
                            } 
                            class_info2= {
                                'number': number,
                                'is_lunch': False,
                                'time': times[2],
                                'title': i[0],
                                'type': i[1].strip('()'),
                                'partner': i[2],
                                'location': location
                            }
                            if schedule and schedule[-1]['date'] == date:
                                schedule[-1]['classes'].append(class_info0)
                                schedule[-1]['classes'].append(class_info1)
                                schedule[-1]['classes'].append(class_info2)
                            else:
                                schedule.append({
                                    'date': date,
                                    'classes': [class_info0, class_info1, class_info2]
                                })
                        else:
                            times = change_time(client_name, number, date)
                            class_info0= {
                                'number': number,
                                'is_lunch': False,
                                'time': times[0],
                                'title': i[0],
                                'type': i[1].strip('()'),
                                'partner': i[2],
                                'location': location
                            }
                            class_info1= {
                                'number': number,
                                'is_lunch': True,
                                'time': times[1],
                                'title': None,
                                'type': None,
                                'partner': None,
                                'location': None
                            } 
                            if schedule and schedule[-1]['date'] == date:
                                schedule[-1]['classes'].append(class_info0)
                                schedule[-1]['classes'].append(class_info1)
                            else:
                                schedule.append({
                                    'date': date,
                                    'classes': [class_info0, class_info1]
                                })
                    else:
                        class_info= {
                                'number': number,
                                'is_lunch': False,
                                'time': change_time(client_name, number, date),
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

# with open("schedule.json", "w", encoding="utf-8") as file:
#     json.dump(html_parse("schedule.html"), file, ensure_ascii=False, indent=4)
