"""
Отели, кафе и остановки рядом с местами проведения — для карты на сайте.

Данные берутся из OpenStreetMap (Overpass API) и сохраняются в frontend/nearby.json,
который build_site.py встраивает в страницу. Сайт сам в OpenStreetMap не ходит.
Обновить список (раз в несколько месяцев достаточно):

    python frontend/fetch_nearby.py
    python frontend/build_site.py
"""
import json
import math
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'nearby.json'
# основной сервер часто перегружен — пробуем по очереди
OVERPASS = ['https://overpass-api.de/api/interpreter', 'https://overpass.private.coffee/api/interpreter',
            'https://maps.mail.ru/osm/tools/overpass/api/interpreter']

# порядок — как в L.venues во фронте; координаты из OpenStreetMap
VENUES = [
    {'lat': 43.22209, 'lon': 76.92392, 'addr': 'проспект аль-Фараби, 71',
     **{"title": {"ru": "Научная библиотека «Аль-Фараби»", "kk": "«Әл-Фараби» ғылыми кітапханасы", "en": "Al-Farabi Scientific Library"}, "address": {"ru": "КазНУ имени аль-Фараби, пр. аль-Фараби, 71, г. Алматы", "kk": "Әл-Фараби атындағы ҚазҰУ, әл-Фараби даңғылы, 71, Алматы қ.", "en": "Al-Farabi Kazakh National University, 71 al-Farabi Avenue, Almaty"}, "day": {"ru": "6 ноября", "kk": "6 қараша", "en": "6 November"}}},
    {'lat': 43.24618, 'lon': 76.9523, 'addr': 'улица Шевченко, 28',
     **{"title": {"ru": "«Ғылым ордасы»", "kk": "«Ғылым ордасы»", "en": "Gylym Ordasy"}, "address": {"ru": "Комитет науки МНВО РК, ул. Шевченко, 28, г. Алматы", "kk": "ҚР ҒЖБМ Ғылым комитеті, Шевченко көшесі, 28, Алматы қ.", "en": "28 Shevchenko Street, Almaty"}, "day": {"ru": "7 ноября", "kk": "7 қараша", "en": "7 November"}}},
]
RADIUS = {'hotels': 1500, 'food': 700, 'stops': 900}   # метров
LIMIT = {'hotels': 15, 'food': 20, 'stops': 10}
FILTERS = {
    'hotels': ['nwr["tourism"~"^(hotel|hostel|guest_house|apartment)$"]["name"]'],
    'food': ['nwr["amenity"~"^(restaurant|cafe|fast_food)$"]["name"]'],
    'stops': ['node["highway"="bus_stop"]', 'node["public_transport"="platform"]["bus"="yes"]',
              'node["railway"="station"]["station"="subway"]'],
}


JUNK = re.compile(r'^(hotel|отель|гостиница|кафе|cafe|ЖК.*)$', re.I)


def dist(a, b):
    """Расстояние в метрах (для сортировки «ближайшие сначала»)."""
    dx = (a['lon'] - b['lon']) * 111320 * math.cos(math.radians(a['lat']))
    dy = (a['lat'] - b['lat']) * 110540
    return round(math.hypot(dx, dy))


def overpass(query):
    last = None
    for attempt in range(3):
        for url in OVERPASS:
            req = urllib.request.Request(url, data=urllib.parse.urlencode({'data': query}).encode(),
                                         headers={'User-Agent': 'afgs-2026-site/1.0'})
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    return json.load(r)['elements']
            except Exception as e:  # 429/504/таймаут — следующий сервер
                last = e
        time.sleep(5 * (attempt + 1))
    raise SystemExit(f'OpenStreetMap не ответил: {last}. Попробуйте позже.')


def fetch(venue, kind):
    parts = ''.join(f'{f}(around:{RADIUS[kind]},{venue["lat"]},{venue["lon"]});' for f in FILTERS[kind])
    query = f'[out:json][timeout:60];({parts});out center tags;'
    elements = overpass(query)
    items, seen = [], set()
    for e in elements:
        c = e.get('center', e)
        t = e.get('tags', {})
        name = t.get('name:ru') or t.get('name') or ''
        if not name or name in seen:   # у остановки бывает несколько точек с одним названием
            continue
        if JUNK.match(name):           # «Hotel», «ЖК …» — ошибки разметки, не заведения
            continue
        seen.add(name)
        p = {'lat': round(c['lat'], 6), 'lon': round(c['lon'], 6)}
        item = {'name': name, **p, 'm': dist(venue, p)}
        if t.get('name:en') and t['name:en'] != name:
            item['name_en'] = t['name:en']
        if t.get('name:kk') and t['name:kk'] != name:
            item['name_kk'] = t['name:kk']
        items.append(item)
    items.sort(key=lambda x: x['m'])
    return items[:LIMIT[kind]]


def main():
    data = []
    for v in VENUES:
        entry = dict(v)
        for kind in FILTERS:
            entry[kind] = fetch(v, kind)
            print(f'{v["addr"]}: {kind} — {len(entry[kind])}')
        data.append(entry)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'Сохранено: {OUT}')


if __name__ == '__main__':
    sys.exit(main())
