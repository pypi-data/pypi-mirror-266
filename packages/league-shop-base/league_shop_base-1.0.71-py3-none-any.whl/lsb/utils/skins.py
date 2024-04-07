import json

import requests
import urllib3

from lsb import ddragon
from lsb import models
from lsb.exceptions import SkinParseException
from lsb.utils.champion_rates import get_champion_rates
from lsb.views import get_top_sold_skin_values

urllib3.disable_warnings()


def get_rarity_by_value(skin_value):
    if skin_value in ["Special", "special"]:
        return "LIMITED"
    if isinstance(skin_value, int) and skin_value >= 1350:
        return "EPIC"
    if isinstance(skin_value, int) and skin_value >= 975:
        return "STANDARD"
    return "BUDGET"


DEFAULT_RARITIES = [
    "Mythic",
    "Epic",
    "Legendary",
    "Ultimate",
]


def ger_merai_analytics_data():
    try:
        res = requests.get(
            "https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/champions.json",
            timeout=30,
        )
        meraianalytics = res.json()
    except (
        requests.exceptions.RequestException,
        json.decoder.JSONDecodeError,
    ):
        return None

    mapped_data = {}
    for champ in meraianalytics.values():
        for skin in champ["skins"]:
            rarity = skin["rarity"]
            value = skin["cost"]

            release = skin["release"]
            if rarity not in DEFAULT_RARITIES:
                rarity = get_rarity_by_value(value)
            if value == "special":
                value = -1

            mapped_data[skin["id"]] = {
                "id": skin["id"],
                "value": value,
                "rarity": rarity,
                "release": release,
            }
    return mapped_data


def get_community_dragon_data():
    print("Parsing skin data...")
    try:
        res = requests.get(
            "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/skins.json",
            timeout=30,
        )
        skins_data = res.json()
    except (
        requests.exceptions.RequestException,
        json.decoder.JSONDecodeError,
    ):
        return None

    non_base_skins = [s for s in skins_data.values() if not s["isBase"]]

    print("Parsing meraianalytics...")
    meraianalytics = ger_merai_analytics_data()

    if meraianalytics is None:
        return None

    skins = {}
    for skin in non_base_skins:
        skin_id = skin["id"]
        skin_name = skin["name"]
        skin_data = meraianalytics.get(skin_id)
        if skin_data is None:
            print(f"Could not find skin {skin_id}, {skin_name}")
            return

        if skin_name == "Annie-Versary":
            skin_data["rarity"] = "LIMITED"

        skins[f"{skin_id}"] = {
            "skin_id": skin_id,
            "skin_name": skin_name,
            "skin_rarity": skin_data["rarity"].upper(),
            "skin_value": skin_data["value"],
            "release_date": skin_data["release"],
        }
    return skins


def create_or_update_skins():
    community_dragon_data = get_community_dragon_data()
    if community_dragon_data is None:
        raise SkinParseException()
    patch = ddragon.get_patch()
    if patch is None:
        raise SkinParseException(
            "Could not fetch champions data from ddragon."
        )
    champion_rates = get_champion_rates()
    if champion_rates is None:
        raise SkinParseException("Could not parse lane data.")
    champions = ddragon.get_champions(patch)
    if champions is None:
        raise SkinParseException(
            "Could not fetch champions data from ddragon."
        )
    skin_objects = ddragon.get_skins(patch, champions, champion_rates)
    if skin_objects is None:
        raise SkinParseException(
            "Could not fetch champions data from ddragon."
        )
    created_count = 0
    updated_count = 0
    top_sold_value_mapping = get_top_sold_skin_values()

    for skin_object in skin_objects:
        try:
            skin_id = skin_object["id"]
            lol_client_data = community_dragon_data.get(skin_id)
            mythic_skins = ["Ashen Knight Pyke"]
            if skin_object["name"] in mythic_skins:
                tier = "MYTHIC"
            elif "Prestige" in skin_object["name"]:
                tier = "MYTHIC"
            else:
                tier = (
                    lol_client_data["skin_rarity"]
                    if lol_client_data is not None
                    else "UNKNOWN"
                )
            release_date = (
                None
                if lol_client_data is None
                else lol_client_data["release_date"]
            )
            value = ddragon.get_skin_value(
                skin_id, tier, top_sold_value_mapping, release_date
            )
            champion_data = skin_object["champion"]

            try:
                champion = models.Champion.objects.get(pk=champion_data["id"])
                champion.roles = champion_data["roles"]
                champion.lanes = champion_data["lanes"]
                champion.save()
            except models.Champion.DoesNotExist:
                champion = models.Champion.objects.create(**champion_data)

            skin_object["tier"] = tier
            skin_object["value"] = value
            skin_object["champion"] = champion
            obj = models.Skin.objects.get(id=skin_object["id"])
            obj.name = skin_object["name"]
            obj.champion = skin_object["champion"]
            obj.tier = skin_object["tier"]
            obj.value = skin_object["value"]
            obj.save()
            updated_count += 1
        except models.Skin.DoesNotExist:
            models.Skin.objects.create(**skin_object)
            created_count += 1
    return created_count, updated_count
