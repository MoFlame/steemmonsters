import random
import string
import hashlib
import math
from collections import OrderedDict


def generate_key(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def generate_team_hash(summoner, monsters, secret):
    m = hashlib.md5()
    m.update((summoner + ',' + ','.join(monsters) + ',' + secret).encode("utf-8"))
    team_hash = m.hexdigest()
    return team_hash


def get_summoner_level(summoner_card, cards, xp_level, max_level_rarity):
    card_id = summoner_card["card_detail_id"]
    for x in xp_level:
        if x["edition"] == summoner_card["edition"] and x["rarity"] == cards[card_id]["rarity"]:
            summoner_level = 0
            for l in x["xp_level"]:
                if summoner_card["xp"] >= x["xp_level"][l]:
                    summoner_level = l
    summoner_level = int(math.ceil(summoner_level / max_level_rarity[cards[card_id]["rarity"]] * 4))
    return summoner_level

def convert_team_id_to_string(response, cards):
    if not isinstance(response, list):
        response = [response]
        decks = None
    else:
        decks = {}
    for r in response:
        summoner = r["summoner"]
        monsters = r["monsters"]
        monsters_list = []
        for m in monsters:
            card_name = cards[m["id"]]["name"]
            if m["gold"]:
                card_name += ":gold"
            monsters_list.append(card_name)
        summoner_name = cards[summoner["id"]]["name"]
        if summoner["gold"]:
            summoner_name += ":gold"
        if decks is None:
            return [summoner_name] + monsters_list
        decks[r["name"]] = [summoner_name] + monsters_list
    return decks


def expand_short_form(deck, cards, output_type="string"):
    card_list = deck.split(",")
    summoner = {"name": cards[int(card_list[0].split("-")[0])]["name"], "level": int(card_list[0].split("-")[1])}
    summoner_id = {"id": int(card_list[0].split("-")[0]), "gold": False}
    summoner_str = "%s:%d" % (summoner["name"], summoner["level"])
    monsters = []
    monsters_id = []
    monster_str = ""
    for m in card_list[1:]:
        if monster_str != "":
            monster_str += ", "
        monsters.append({"name": cards[int(m.split("-")[0])]["name"], "level": int(m.split("-")[1])})
        monsters_id.append({"id": int(m.split("-")[0]), "gold": False})
        monster_str += "%s:%d" % (monsters[-1]["name"], monsters[-1]["level"])
    if output_type == "dict":
        return summoner, monsters
    elif output_type == "id":
        return summoner_id, monsters_id
    else:
        return summoner_str, monster_str


def convert_team_string_to_id(cardstringlist, cards_by_name):
    summoner = {}
    monsters = []
    if isinstance(cardstringlist, str):
        if len(cardstringlist.split(":")) > 0:
            summoner = {"id": cards_by_name[cardstringlist.split(":")[0]]["id"], "gold": False}
            monsters = []
            for m in cardstringlist[(len(cardstringlist.split(":")[0]) + 3):].split(","):
                monsters.append({"id": cards_by_name[m.lstrip().split(":")[0]]["id"], "gold": False})
        else:
            summoner = {"id": cards_by_name[cardstringlist.split(",")[0]]["id"], "gold": False}
            monsters = []
            for m in cardstringlist[(len(cardstringlist.split(",")[0]) + 1):].split(","):
                monsters.append({"id": cards_by_name[m.rstrip().lstrip()]["id"], "gold": False})
    elif isinstance(cardstringlist, list):
        summoner = {"id": cards_by_name[cardstringlist[0].split(":")[0]]["id"], "gold": False}
        monsters = []
        for m in cardstringlist[1:]:
            monsters.append({"id": cards_by_name[m.split(":")[0]]["id"], "gold": False})

    return summoner, monsters


def get_cards_collection(response, cards):
    mycards = {}
    for r in response["cards"]:
        if r["card_detail_id"] not in mycards:
            mycards[r["card_detail_id"]] = {"uid": r["uid"], "xp": r["xp"], "name": cards[r["card_detail_id"]]["name"],
                                            "edition": r["edition"], "id": r["card_detail_id"], "gold": r["gold"]}
        elif r["xp"] > mycards[r["card_detail_id"]]["xp"]:
            mycards[r["card_detail_id"]] = {"uid": r["uid"], "xp": r["xp"], "name": cards[r["card_detail_id"]]["name"],
                                            "edition": r["edition"], "id": r["card_detail_id"], "gold": r["gold"]}
    return mycards
