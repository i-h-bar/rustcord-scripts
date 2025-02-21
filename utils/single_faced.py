import uuid
from datetime import datetime

from models.artists import Artist, MISSING_ID_ID, MISSING_ARTIST
from models.card_info import CardInfo
from models.cards import Card
from models.combos import Combo
from models.illustrations import Illustration
from models.images import Image
from models.legalities import Legality
from models.related_tokens import RelatedToken
from models.rules import Rule
from models.sets import Set
from utils.normalise import normalise


rule_cache: dict[str, Rule] = {}
legality_cache: dict[str, Legality] = {}


def produce_card(card: dict) -> CardInfo:
    artist = Artist(
        id=card.get("artist_ids", MISSING_ID_ID)[0],
        name=card["artist"] or MISSING_ARTIST,
        normalised_name=normalise(card["artist"] or MISSING_ARTIST),
    )

    if not (rule := rule_cache.get(card["oracle_id"])):
        rule = Rule(
            id=str(uuid.uuid4()),
            colour_identity=card["color_identity"],
            mana_cost=card["mana_cost"],
            cmc=card.get("cmc", 0.0),
            power=card.get("power"),
            toughness=card.get("toughness"),
            loyalty=card.get("loyalty"),
            defence=card.get("defense") or card.get("defence"),
            type_line=card["type_line"],
            oracle_text=card.get("oracle_text"),
            colours=card.get("colors", []),
            keywords=card.get("keywords", []),
            produced_mana=card.get("produced_mana"),
        )
        rule_cache[card["oracle_id"]] = rule

    if not (legality := legality_cache.get(card["oracle_id"])):
        legality = Legality(
            id=str(uuid.uuid4()),
            game_changer=card.get("game_changer"),
            **card["legalities"],
        )
        legality_cache[card["oracle_id"]] = legality

    image = Image(
        id=str(uuid.uuid4()),
        scryfall_url=card["image_uris"]["png"]
    )

    illustration = Illustration(
        id=card.get("illustration_id", str(uuid.uuid4())),
        illustration=card["image_uris"]["art_crop"]
    )

    set_ = Set(
        id=card["set_id"],
        name=card["set_name"],
        normalised_name=normalise(card["set_name"]),
        abbreviation=card["set"],
    )

    card_model = Card(
        id=card["id"],
        oracle_id=card.get("oracle_id", str(uuid.uuid4())),
        name=card["name"],
        normalised_name=normalise(card["name"]),
        scryfall_url=card["scryfall_uri"],
        flavour_text=card.get("flavor_text"),
        release_date=datetime.strptime(card["released_at"], "%Y-%m-%d"),
        reserved=card["reserved"],
        rarity=card["rarity"],
        artist_id=artist.id,
        image_id=image.id,
        illustration_id=illustration.id,
        legality_id=legality.id,
        rule_id=rule.id,
        set_id=set_.id,
    )

    combos = []
    related_tokens = []
    if parts := card.get("all_parts"):
        for part in parts:
            if part["component"] == "token":
                related_tokens.append(
                    RelatedToken(
                        token_id=part["id"],
                        card_id=card_model.id
                    )
                )
            elif part["component"] == "compo_piece":
                combos.append(
                    Combo(
                        card_id=card_model.id,
                        combo_card_id=part["id"]
                    )
                )

    return CardInfo(
        card=card_model,
        artist=artist,
        rule=rule,
        legality=legality,
        image=image,
        illustration=illustration,
        set=set_,
        related_tokens=related_tokens,
        combos=combos
    )
