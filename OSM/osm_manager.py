import requests
import json

from DB import db_places
from requests.structures import CaseInsensitiveDict


def get_country(name):
    headers = CaseInsensitiveDict()
    headers["Accept-Language"] = "ru"
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    text = requests.get(f"https://nominatim.openstreetmap.org/search?q={name}&format=json&adressdetails=1", headers=headers).text
    countrys = json.loads(text)
    if len(countrys) == 0:
        return None

    for i in range(len(countrys)):
        adress_type = countrys[i]['addresstype']
        if adress_type == 'country':
            db_places.add_place_info(countrys[i]['place_id'], countrys[i]['lat'], countrys[i]['lon'])
            return countrys[i]['name'], countrys[i]['place_id']
    return None


def get_city(name, country_name):
    headers = CaseInsensitiveDict()
    headers["Accept-Language"] = "ru"
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    citys = json.loads(
        requests.get(f"https://nominatim.openstreetmap.org/search?q={name}&format=json&adressdetails=1", headers=headers).text)
    if len(citys) == 0:
        return None
    for i in range(len(citys)):
        adress_type = citys[i]['addresstype']
        if adress_type == 'city' or adress_type == 'town' or adress_type == 'village':
            if citys[i]['display_name'].split(',')[-1].lower().strip() == country_name.lower().strip():
                db_places.add_place_info(citys[i]['place_id'], citys[i]['lat'], citys[i]['lon'])
                return citys[i]['name'], citys[i]['place_id']
    return None
