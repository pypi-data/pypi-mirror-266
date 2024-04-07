from pydantic import BaseModel

class item(BaseModel):
    name: str
    description: str
