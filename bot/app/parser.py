import json
from datetime import datetime
from bs4 import BeautifulSoup


data = []    

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

            tds_info = [tds]
                
            
            for i in tds_info:
                if i[0] != "":
                    if len(i) == 3:
                        class_info = [
                                {
                                    'number': number,
                                    'title': i[0].capitalize(),
                                    'type': i[1].strip('()'),
                                    'partner': i[2],
                                    'location': location
                                }
                            ]
                    elif len(i) == 6:
                        class_info = [
                                {
                                    'number': number,
                                    'title': i[0].capitalize(),
                                    'type': i[1].strip('()'),
                                    'partner': i[2],
                                    'location': location
                                },
                                {
                                    'number': number,
                                    'title': i[3].capitalize(),
                                    'type': i[4].strip('()'),
                                    'partner': i[5],
                                    'location': location
                                }
                            ]

                    
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
        
    return data 


if __name__ == "__main__":
    # Читаем HTML файл
    with open("16дек-главное.html", "r", encoding="windows-1251") as file:
        html_content = file.read()
    
    # Получаем результат парсинга
    result = html_parse(html_content)
    
    # Сохраняем результат в JSON файл
    with open("scheduleYA.json", "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=4)

