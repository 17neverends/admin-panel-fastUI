from pydantic import BaseModel, Field

class Actions(BaseModel):
    backup_id: str = Field(title="ID")
    operation_type: str = Field(title="Тип операции")
    column_name: str = Field(title="Поле")
    old_value: str = Field(title="Прошлое значение")
    new_value: str = Field(title="Новое значение")