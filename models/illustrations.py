from pydantic import BaseModel


class Illustration(BaseModel):
    id: str
    scryfall_url: str
