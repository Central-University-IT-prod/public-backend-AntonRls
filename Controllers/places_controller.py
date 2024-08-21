from DB import db_places, db_locations, db_places


def create_link_from_home(travel_id, user_id):
    home_id = db_places.get_city_id(user_id)

    locations = db_locations.get_information(travel_id)

    cords = []
    home_cords = db_places.get_cord(home_id)

    cords.append(f"{home_cords[0]},{home_cords[1]}")
    for location in locations:
        place_id = location[2]
        place_cord = db_places.get_cord(place_id)
        cords.append(f"{place_cord[0]},{place_cord[1]}")

    return f"https://yandex.ru/maps/?rtext={'~'.join(cords)}&rtt=auto"


def create_link_from_first(travel_id):
    locations = db_locations.get_information(travel_id)

    cords = []
    for location in locations:
        place_id = location[2]
        place_cord = db_places.get_cord(place_id)
        cords.append(f"{place_cord[0]},{place_cord[1]}")

    return f"https://yandex.ru/maps/?rtext={'~'.join(cords)}&rtt=auto"
