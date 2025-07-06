
from pydantic import BaseModel


class MemTx(BaseModel):
    hash: str
    sender: str
    to: str
    input: str


