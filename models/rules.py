from pydantic import BaseModel


class Rule(BaseModel):
    id: str
    colour_identity: list[str]
    mana_cost: str | None
    cmc: float
    power: str | None
    toughness: str | None
    loyalty: str | None
    defence: str | None
    type_line: str | None
    oracle_text: str | None
    colours: list[str] | None
    keywords: list[str] | None
    produced_mana: list[str] | None
    rulings_url: str | None
