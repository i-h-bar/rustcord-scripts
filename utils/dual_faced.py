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
from utils.single_faced import rule_cache, legality_cache


def produce_side(
        card: dict, side: dict, side_id: str, reverse_side_id: str, legality: Legality, set_: Set
) -> CardInfo:
    artist_id = (side.get("artist_ids") or card.get("artist_ids") or MISSING_ID_ID)[0]
    artist_name = side.get("artist") or card.get("artist") or MISSING_ARTIST
    artist = Artist(
        id=artist_id,
        name=artist_name,
        normalised_name=normalise(artist_name),
    )

    if not (rule := rule_cache.get(card.get("oracle_id") or card["name"])):
        rule = Rule(
            id=str(uuid.uuid4()),
            colour_identity=card["color_identity"],
            mana_cost=card.get("mana_cost"),
            cmc=card.get("cmc", 0.0),
            power=card.get("power"),
            toughness=card.get("toughness"),
            loyalty=card.get("loyalty"),
            defence=card.get("defense") or card.get("defence"),
            type_line=card.get("type_line"),
            oracle_text=card.get("oracle_text"),
            colours=card.get("colors", []),
            keywords=card.get("keywords", []),
            produced_mana=card.get("produced_mana"),
        )
        rule_cache[card.get("oracle_id") or card["name"]] = rule

    image_uris = side.get("image_uris") or card.get("image_uris")

    image = Image(
        id=str(uuid.uuid4()),
        scryfall_url=image_uris["png"]
    )

    illustration = Illustration(
        id=side.get("illustration_id") or card.get("illustration_id", str(uuid.uuid4())),
        illustration=image_uris["art_crop"]
    )

    card_model = Card(
        id=side_id,
        oracle_id=card.get("oracle_id", str(uuid.uuid4())),
        name=side["name"],
        normalised_name=normalise(side["name"]),
        scryfall_url=card["scryfall_uri"],
        flavour_text=side.get("flavor_text"),
        release_date=datetime.strptime(card["released_at"], "%Y-%m-%d"),
        reserved=card["reserved"],
        rarity=card["rarity"],
        artist_id=artist.id,
        image_id=image.id,
        illustration_id=illustration.id,
        legality_id=legality.id,
        rule_id=rule.id,
        set_id=set_.id,
        backside_id=reverse_side_id
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
            elif part["component"] == "combo_piece":
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
        image=image,
        illustration=illustration,
        legality=legality,
        set=set_,
        related_tokens=related_tokens,
        combos=combos
    )


def produce_dual_faced_card(card: dict, front: dict, back: dict) -> tuple[CardInfo, CardInfo]:
    back_id = str(uuid.uuid4())

    if not (legality := legality_cache.get(card["name"])):
        legality = Legality(
            id=str(uuid.uuid4()),
            game_changer=card.get("game_changer"),
            **card["legalities"],
        )
        legality_cache[card["name"]] = legality

    set_ = Set(
        id=card["set_id"],
        name=card["set_name"],
        normalised_name=normalise(card["set_name"]),
        abbreviation=card["set"],
    )

    front = produce_side(card, front, card["id"], back_id, legality, set_)
    back = produce_side(card, back, back_id, front.card.id, legality, set_)

    return front, back