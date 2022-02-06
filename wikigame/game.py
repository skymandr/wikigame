from functools import lru_cache
from json import dump, load

from wikigame.wiki import get_page_info, get_random_page_name

_LOCATION = '/persistance/games.json'
_KNOWN_GAMES = {}


def init_game():
    try:
        with open(_LOCATION, 'r') as fh:
            for key, value in load(fh):
                _KNOWN_GAMES[tuple(key)] = value
    except FileNotFoundError:
        pass


def _record_chosen(wiki, gamename, which, page):
    language = wiki.language
    key = (language, gamename, which)
    _KNOWN_GAMES[key] = page
    with open(_LOCATION, 'w') as fh:
        dump(list(_KNOWN_GAMES.items()), fh)
    


@lru_cache(maxsize=200)
def get_target(wiki, gamename):
    if (page:=_KNOWN_GAMES.get((wiki.language, gamename, "target"))) is not None:
        return get_page_info(wiki, gamename, page)
    i = 0
    while True:
        page = get_random_page_name(wiki)
        info = get_page_info(wiki, gamename, page) 
        if len(info['links']) > 30:
            break
        i += 1
        if i > 30:
            raise ValueError()
    _record_chosen(wiki, gamename, "target", page)
    return info


@lru_cache(maxsize=200)
def get_start(wiki, gamename, target):
    if (page:=_KNOWN_GAMES.get((wiki.language, gamename, "start"))) is not None:
        return get_page_info(wiki, gamename, page)
    i = 0
    while True:
        page = get_random_page_name(wiki)
        info = get_page_info(wiki, gamename, page, target) 
        if len(info['links']) > 15 and target not in info['links']:
            break
        i += 1
        if i > 20:
            raise ValueError()
    _record_chosen(wiki, gamename, "start", page)
    return info


def get_game_page(wiki, gamename, page):
    target = get_target(wiki, gamename)
    if target is None:
        return None
    info = get_page_info(wiki, gamename, page, target['title'])
    if info is None:
        return None 
    info['links'] = info['links'][:25]
    return info