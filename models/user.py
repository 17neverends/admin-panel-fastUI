from pydantic import BaseModel, Field

class User(BaseModel):
    id: str = Field(title="ID")
    name: str = Field(title="Имя")
    age: str = Field(title="Возраст")