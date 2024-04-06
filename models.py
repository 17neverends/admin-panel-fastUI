from pydantic import BaseModel, Field

class User(BaseModel):
    id: str = Field(title="ID")
    name: str = Field(title="Имя")
    age: str = Field(title="Возраст")

class getBackupStep(BaseModel):
    steps: int = Field(title="Иногда для прыжка вперёд требуется отступить на два шага назад. — А иногда надо лишь иметь желание прыгнуть.")

class Actions(BaseModel):
    backup_id: str = Field(title="ID")
    operation_type: str = Field(title="Тип операции")
    column_name: str = Field(title="Поле")
    old_value: str = Field(title="Прошлое значение")
    new_value: str = Field(title="Новое значение")