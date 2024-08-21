import requests
from bs4 import BeautifulSoup
from utils import get_eng_name, get_rus_month_from_name


def get_month_weather(month_number, lat, long):
    headers = {'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/111.0.0.0 Safari/537.36')}

    soup = BeautifulSoup(
        requests.get(f'https://yandex.ru/pogoda/month/{get_eng_name(month_number)}?lat={lat}&lon={long}&via=cnav', headers=headers).text,
        'html.parser')
    climate_calendar = soup.select('table.climate-calendar > tr')
    datas = []
    for i in range(1, len(climate_calendar)):
        tags_a = climate_calendar[i].select("td.climate-calendar__cell > a")
        for j in range(len(tags_a)):
            spans = tags_a[j].select("a.i-bem > span")
            datas.append(spans[0].text)
    return datas


def get_weather_interval(day_start, month_start, day_end, month_end, lat, long):
    result = []
    day_start = int(day_start)
    day_end = int(day_end)
    month_start = int(month_start)
    month_end = int(month_end)

    temp_interval = []
    if month_end < month_start:
        temp_interval = get_weather_interval(1,1,day_end, month_end, lat, long)
        day_end = 31
        month_end = 12

    if month_end == month_start:
        datas = get_month_weather(month_start, lat, long)
        for i in range(len(datas)):
            day = int(datas[i].split(',')[0].split(' ')[0])
            month = get_rus_month_from_name(datas[i].split(',')[0].split(' ')[1].strip())
            if day_start <= day <= day_end and month == month_start:
                result.append(datas[i])
    else:
        for current_month in range(month_start, month_end + 1):
            datas = get_month_weather(current_month, lat, long)
            for i in range(len(datas)):
                day = int(datas[i].split(',')[0].split(' ')[0])
                month = get_rus_month_from_name(datas[i].split(',')[0].split(' ')[1].strip())
                if month_start != month != month_end and month_end > month > month_start:
                    result.append(datas[i])
                elif month_start == month and day >= day_start:
                    result.append(datas[i])
                elif month_end == month and day <= day_end:
                    result.append(datas[i])
    final_result = []

    for res in result:
        adding = ""
        adding += f"<b>{res.split('.')[0]}</b>\n"
        adding += f"Днём: {res.split('.')[1].split(',')[1].split(';')[0].strip()}C\n"
        adding += f"Ночью: {res.split(';')[1].split(',')[1]}C\n"
        adding += f"Погода: {res.split(';')[2]}"
        final_result.append(adding)

    for temp in temp_interval:
        final_result.append(temp)

    return final_result

